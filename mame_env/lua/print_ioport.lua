local ioport = manager.machine.ioport
local labels = {}
for tag,port in pairs(ioport.ports) do 
    for fname,field in pairs(port.fields) do 
        token = manager.machine.ioport:input_type_to_token(field.type, field.player)
        print('tag="' .. tag .. '", mask=' .. field.mask .. ', token="' .. token .. '",')
        table.insert(labels, {tag=tag, field=field, token=token})
    end
end

local function compare(a, b)
    if a.tag == b.tag then
        return a.field.mask < b.field.mask
    else
        return a.tag < b.tag
    end
end

table.sort(labels, compare)

for i, value in ipairs(labels) do
    print(value.token .. ' = IOPort(tag="' .. value.tag .. '", mask=' .. value.field.mask .. ')')
end
