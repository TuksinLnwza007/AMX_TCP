from AMX_TCP_CLASS import Amx_tcp

plc = Amx_tcp("192.168.3.200",502)

test = plc.read_coil("M10")
print(test)



