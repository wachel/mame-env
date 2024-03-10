function log(...)
    local args = {...}
    local message = "[lua]"
    for _, v in ipairs(args) do
        message = message .. " " .. tostring(v)
    end
    print(message)
end

--connect to server
local socket = emu.file("rw")
socket:open("socket." .. os.getenv("SERVER_IP") .. ":" .. os.getenv("SERVER_PORT"))

MsgID_AddressInfo = "ADDR"
MsgID_MemoryData = "DATA"
MsgID_Actions = "ACTS"
MsgID_WriteMemoryValue = "WMem"
MsgID_ExecuteLuaString = "ExLS"

local function send(msgid, content)
    socket:write(string.pack("c4I4", msgid, string.len(content)) .. content)
end

local current_buffer = ""
local function receive()
    repeat
        local read = socket:read(100)
        current_buffer = current_buffer .. read
    until #read == 0
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
local function set_mem_address(content)
    local map = {
        u8 = {read_func="read_u8", format = "I1"},
        s8 = {read_func="read_i8", format = "i1"},
        u16 = {read_func="read_u16", format = "I2"},
        s16 = {read_func="read_i16", format = "i2"},
    }
    for addr_info in string.gmatch(content, "[^|]+") do
        local name, address, fmt = string.match(addr_info, "([^,]+),([^,]+),([^,]+)")
        table.insert(mem_address, {name = name, address = tonumber(address), read_func=map[fmt].read_func, format=map[fmt].format})
    end
end

local function write_memory(content)
    local map = {
        u8 =  "write_u8",
        s8 =  "write_i8",
        u16 = "write_u16",
        s16 = "write_i16",
    }
    for value_info in string.gmatch(content, "[^|]+") do
        local address, fmt, value = string.match(value_info, "([^,]+),([^,]+),([^,]+)")
        mem[map[fmt]](mem, tonumber(address), tonumber(value))
    end
end

local function execute_lua_string(content)
    --log('execute_lua_string', content)
    load(content)()
end

--send observation data to server
local function send_mem_data()
    local mem = manager.machine.devices[":maincpu"].spaces["program"]
    local binary_string = ""
    for i, addr_info in ipairs(mem_address) do
        local value = mem[addr_info.read_func](mem, addr_info.address)
        binary_string = binary_string .. string.pack(addr_info.format, value)
    end
    send(MsgID_MemoryData, binary_string)
end

releaseQueue = {}

local function process_frame_done()
    local ioport = manager.machine.ioport
    local screen = manager.machine.screens:at(1)

    --release input
    for i=1,#releaseQueue do
        local tag,mask = releaseQueue[i][1],releaseQueue[i][2];
        ioport.ports[tag]:field(mask):set_value(0);
    end;
    releaseQueue = {};

    --read action from server
    msgid, content = receive()
    while true do
        if msgid == MsgID_AddressInfo then
            set_mem_address(content)
        elseif msgid == MsgID_WriteMemoryValue then
            write_memory(content)
        elseif msgid == MsgID_ExecuteLuaString then
            execute_lua_string(content)
        elseif msgid == MsgID_Actions then--apply input
            for tag_mask in string.gmatch(content, "[^|]+") do
                local tag, mask = string.match(tag_mask, "(.-)%+(.+)")
                ioport.ports[tag]:field(mask):set_value(1)
                table.insert(releaseQueue, {tag, mask}); --record for release next frame
            end
            send_mem_data()
            break
        end
        --pipe:read(1)
        msgid, content = receive()
    end
end

emu.register_frame_done(process_frame_done)