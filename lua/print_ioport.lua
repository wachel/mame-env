local ioport = manager.machine.ioport
local label = {}
for tag,port in pairs(ioport.ports) do 
    for fname,field in pairs(port.fields) do 
        type_token = manager.machine.ioport:input_type_to_token(field.type, field.player)
        print('tag="' .. tag .. '", mask=' .. field.mask .. ', type="' .. type_token .. '",')
        label[type_token] = {tag=tag, field=field}
    end
end

print("---for python define---")
-- for tag,port in pairs(ioport.ports) do 
--     for fname,field in pairs(port.fields) do 
--         type_token = manager.machine.ioport:input_type_to_token(field.type, field.player)
--         print(type_token .. ' = IOPort(tag="' .. tag .. '", mask=' .. field.mask .. ')')
--     end
-- end

for token, value in pairs(label) do
    print(token .. ' = IOPort(tag="' .. value.tag .. '", mask=' .. value.field.mask .. ')')
end
