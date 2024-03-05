local json = require("json")

function log(...)
    local args = {...}
    local message = "[lua]"
    for _, v in ipairs(args) do
        message = message .. " " .. tostring(v)
    end
    print(message)
end

local function log_actions()
    local ioport = manager.machine.ioport
    for portkey,port in pairs(ioport.ports) do 
        for filedkey,field in pairs(port.fields) do 
            log("port=" .. portkey .. ";field=" .. filedkey) 
        end
    end
end

--log_actions()

--connect to server
local socket = emu.file("rw")
socket:open("socket." .. os.getenv("SERVER_IP") .. ":" .. os.getenv("SERVER_PORT"))

MsgID_AddressInfo = "ADDR"
MsgID_MemoryData = "MDAT"
MsgID_Action = "ACTN"

local function send(msgid, content)
    socket:write(string.pack("c4I4", msgid, string.len(content)) .. content)
end

local current_buffer = ""
local function receive()
    current_buffer = current_buffer .. socket:read(1024)
    if string.len(current_buffer) >= 8 then
        local msgid,len = string.unpack("c4I4", current_buffer)
        if string.len(current_buffer) >= 8 + len then
            local content = string.sub(current_buffer, 9,9+len-1)
            current_buffer = string.sub(current_buffer, 9+len)
            return msgid, content
        end
    end
    return nil,""
end

local mem_address = {}
local function read_mem_address(content)
    log("read_mem_address")
    local map = {
        u8 = {read_func="read_u8", format = "I1"},
        s8 = {read_func="read_i8", format = "i1"},
        u16 = {read_func="read_u16", format = "I2"},
        s16 = {read_func="read_i16", format = "i2"},
    }
    for addr_info in string.gmatch(content, "[^|]+") do
        local name, address, fmt = string.match(addr_info, "([^,]+),([^,]+),([^,]+)")
        mem_address[name] = {address = tonumber(address), read_func=map[fmt].read_func, format=map[fmt].format}
    end
end

--send observation data to server
local function send_mem_data()
    local mem = manager.machine.devices[":maincpu"].spaces["program"]
    local binary_string = ""
    for key, addr_info in pairs(mem_address) do
        local value = mem[addr_info.read_func](mem, addr_info.address)
        binary_string = binary_string .. string.pack(addr_info.format, value)
    end
    send(MsgID_MemoryData, binary_string)
end

-- send(MsgID_AddressInfo, "")

releaseQueue = {}

local function process_frame_done()
    local ioport = manager.machine.ioport
    local screen = manager.machine.screens:at(1)

    --release input
    for i=1,#releaseQueue do
        local port,field = releaseQueue[i][1],releaseQueue[i][2];
        ioport.ports[port].fields[field]:set_value(0);
    end;
    releaseQueue = {};

    --read action from server
    msgid, content = receive()
    while true do
        if msgid == MsgID_AddressInfo then
            read_mem_address(content)
            send_mem_data()
        elseif msgid == MsgID_Action then--apply input
            for port_field in string.gmatch(content, "[^|]+") do
                local port, field = string.match(port_field, "(.-)%+(.+)")
                --log(port,field)
                ioport.ports[port].fields[field]:set_value(1)
                table.insert(releaseQueue, {port, field}); --record for release next frame
            end
            send_mem_data()
            break
        end
        msgid, content = receive()
    end
end

emu.register_frame_done(process_frame_done)