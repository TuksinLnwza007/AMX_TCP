# AMX_TCP Class – Modbus TCP Client Wrapper
This Python class, AMX_TCP, provides a simple interface for communicating with a Mitsubishi PLC (or compatible devices) over Modbus TCP using the pymodbus library (version 2.5.3). It supports reading and writing both bit-level (coils and inputs) and word-level (registers) data based on the Mitsubishi memory mapping (M, Y, X, D devices).

📌 Supported Modbus Function Codes:
Function Code	Description	Address Type	PLC Devices
01 (0x01)	Read Coils	Output Bits	M, Y
02 (0x02)	Read Discrete Inputs	Input Bits	X, M, Y
03 (0x03)	Read Holding Registers	Registers	D
04 (0x04)	Read Input Registers	Read-only Registers	D
05 (0x05)	Write Single Coil	Output Bits	M, Y
06 (0x06)	Write Single Register	Registers	D
15 (0x0F)	Write Multiple Coils	Output Bits	M, Y
16 (0x10)	Write Multiple Registers	Registers	D

🧠 Memory Mapping:
PLC Address	Modbus Address	Range	Type	Modbus Function
M0–M8511	0–8191	8192 values	Bit	01, 02, 05, 0F
Y0–Y377	8192–8447	256 values	Bit	01
X0–X377	8448–8703	256 values	Bit	02
D0–D7999	0–7999		Word	03, 04, 06, 10
D8000–D8511	8000–8511		Word	03, 04, 06, 10

🔧 Class Methods
__init__(ip: str, port: int, unit_id: int)
Initializes the Modbus TCP connection to the PLC.
read_bit(address: str) -> bool
Reads a single bit from M, Y, or X devices.
write_bit(address: str, value: bool)
Writes a single bit to M or Y devices.
read_word(address: str) -> int
Reads a 16-bit word (register) from D devices.
write_word(address: str, value: int)
Writes a 16-bit value to a D register.

📥 Example Usage
plc = AMX_TCP("192.168.1.10", 502, 1)
# Read a bit from X0
x0_state = plc.read_bit("X0")
# Write True to M100
plc.write_bit("M100", True)
# Read value from D500
d500_val = plc.read_word("D500")
# Write value to D1000
plc.write_word("D1000", 123)

📦 Dependencies
# pymodbus==2.5.3
pip install pymodbus==2.5.3
