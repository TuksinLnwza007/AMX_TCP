from pymodbus.client.sync import ModbusTcpClient  # pymodbus version 2.5.3
from typing import List, Optional, Union

class FX5U_TCP:
    """
    FX5U_TCP - Modbus TCP helper for FX5U PLC mapping (M, Y, X, D)
    Default mapping assumptions (ตามภาพ Allocation):
      - Y start modbus no. = 0 (Coils)
      - X start modbus no. = 0 (Discrete Inputs)
      - D start modbus no. = 0 (Input/Holding Registers)
      - M mapping: uses Modbus addresses starting at 8192 (ตามตัวอย่างก่อนหน้า)
    หากต้องการปรับ start offsets ให้ส่งพารามิเตอร์ตอนสร้าง instance
    
    from FX5U_TCP_CLASS import FX5U_TCP
    import time

    plc = FX5U_TCP("192.168.XXX.XXX", port=502, unit_id=1)
    """
    
    def __init__(self, ip: str, port: int = 502, unit_id: int = 1,
                 start_Y: int = 0, start_X: int = 0, start_D: int = 0, start_M_modbus: int = 8192): #--> ค่าเริ่มต้นตาม Mapping ของ FX5U
        self.__ip = ip
        self.__port = port
        self.__unit_id = unit_id
        self.start_Y = start_Y
        self.start_X = start_X
        self.start_D = start_D
        self.start_M_modbus = start_M_modbus

        self.client = ModbusTcpClient(self.__ip, port=self.__port)
        connection = self.client.connect()
        if connection:
            print(f"Connected to {self.__ip}:{self.__port} successfully.")
        else:
            print(f"Failed to connect to {self.__ip}:{self.__port}.")

    def __offset_coil(self, data: str) -> int:
        if not data or len(data) < 2:
            raise ValueError("Invalid coil address format")
        prefix = data[0].upper()
        idx = int(data[1:])

        if prefix == "M":
            return self.start_M_modbus + idx
        elif prefix == "Y":
            return self.start_Y + idx
        elif prefix == "X":
            return self.start_X + idx
        else:
            raise ValueError(f"Invalid coil address prefix in: {data}")

    def __offset_word(self, data: str) -> int:
        if not data or len(data) < 2:
            raise ValueError("Invalid word/register address format")
        prefix = data[0].upper()
        if prefix != "D":
            raise ValueError(f"Invalid word address prefix in: {data}")
        idx = int(data[1:])
        return self.start_D + idx

    # ----------------- Coils / Discrete Inputs -----------------
    def read_bit(self, address: str) -> Optional[bool]:
        '''
        plc.read_bit("M0") -> True/False
        '''
        try:
            prefix = address[0].upper()
            if prefix == "X":
                mb_addr = self.__offset_coil(address)
                resp = self.client.read_discrete_inputs(mb_addr, count=1, unit=self.__unit_id)
            else:
                mb_addr = self.__offset_coil(address)
                resp = self.client.read_coils(mb_addr, count=1, unit=self.__unit_id)

            if not resp.isError():
                return bool(resp.bits[0])
            else:
                print(f"Read bit Error at {address}: {resp}")
                return None
        except Exception as e:
            print(f"Error in read_bit: {e}")
            return None

    def read_bits(self, address: str, count: int = 1) -> Optional[List[bool]]:
        '''
        plc.read_bits("M0", count=8) -> [True, False, ...]
        '''
        try:
            prefix = address[0].upper()
            mb_addr = self.__offset_coil(address)
            if prefix == "X":
                resp = self.client.read_discrete_inputs(mb_addr, count=count, unit=self.__unit_id)
            else:
                resp = self.client.read_coils(mb_addr, count=count, unit=self.__unit_id)

            if not resp.isError():
                return [bool(b) for b in resp.bits[:count]]
            else:
                print(f"Read bits Error at {address}: {resp}")
                return None
        except Exception as e:
            print(f"Error in read_bits: {e}")
            return None

    def write_coil(self, address: str, value: Union[bool, int]) -> bool:
        '''
        plc.write_coil("M0", True) -> True/False
        '''
        try:
            if address[0].upper() == "X":
                raise ValueError("Cannot write to discrete input (X).")
            mb_addr = self.__offset_coil(address)
            resp = self.client.write_coil(mb_addr, bool(value), unit=self.__unit_id)
            if resp.isError():
                print(f"Failed to write coil {address} <- {value}")
                return False
            return True
        except Exception as e:
            print(f"Error in write_coil: {e}")
            return False

    def write_coils(self, address: str, values: List[Union[bool, int]]) -> bool:
        '''
        plc.write_coils("M0", [True, False, True, True]) -> True/False
        '''
        try:
            if address[0].upper() == "X":
                raise ValueError("Cannot write to discrete input (X).")
            mb_addr = self.__offset_coil(address)
            bools = [bool(v) for v in values]
            resp = self.client.write_coils(mb_addr, bools, unit=self.__unit_id)
            if resp.isError():
                print(f"Failed to write coils {address} <- {values}")
                return False
            return True
        except Exception as e:
            print(f"Error in write_coils: {e}")
            return False

    # ----------------- Registers (Input / Holding) -----------------
    def read_word(self, address: str) -> Optional[int]:
        '''
        plc.read_word("D100") -> 1234
        '''
        try:
            mb_addr = self.__offset_word(address)
            resp = self.client.read_input_registers(mb_addr, count=1, unit=self.__unit_id)
            if not resp.isError():
                return int(resp.registers[0])
            else:
                print(f"Read Input Register Error at {address}: {resp}")
                return None
        except Exception as e:
            print(f"Error in read_word: {e}")
            return None

    def read_input_registers(self, address: str, count: int = 1) -> Optional[List[int]]:
        '''
        plc.read_input_registers("D200", count=4) -> [123, 456, 789, 0]
        '''
        try:
            mb_addr = self.__offset_word(address)
            resp = self.client.read_input_registers(mb_addr, count=count, unit=self.__unit_id)
            if not resp.isError():
                return [int(r) for r in resp.registers[:count]]
            else:
                print(f"Read input regs Error at {address}: {resp}")
                return None
        except Exception as e:
            print(f"Error in read_input_registers: {e}")
            return None

    def read_holding(self, address: str) -> Optional[int]:
        '''
        plc.read_holding("D300") -> 5678
        '''
        try:
            mb_addr = self.__offset_word(address)
            resp = self.client.read_holding_registers(mb_addr, count=1, unit=self.__unit_id)
            if not resp.isError():
                return int(resp.registers[0])
            else:
                print(f"Read Holding Register Error at {address}: {resp}")
                return None
        except Exception as e:
            print(f"Error in read_holding: {e}")
            return None

    def read_holding_registers(self, address: str, count: int = 1) -> Optional[List[int]]:
        '''
        plc.read_holding_registers("D400", count=3) -> [111, 222, 333]
        '''
        try:
            mb_addr = self.__offset_word(address)
            resp = self.client.read_holding_registers(mb_addr, count=count, unit=self.__unit_id)
            if not resp.isError():
                return [int(r) for r in resp.registers[:count]]
            else:
                print(f"Read holding regs Error at {address}: {resp}")
                return None
        except Exception as e:
            print(f"Error in read_holding_registers: {e}")
            return None

    def write_word(self, address: str, value: int) -> bool:
        '''
        plc.write_word("D500", 12345)-> True/False
        '''
        try:
            mb_addr = self.__offset_word(address)
            resp = self.client.write_register(mb_addr, int(value), unit=self.__unit_id)
            if resp.isError():
                print(f"Failed to write register {address} <- {value}")
                return False
            return True
        except Exception as e:
            print(f"Error in write_word: {e}")
            return False

    def write_registers(self, address: str, values: List[int]) -> bool:
        '''
        plc.write_registers("D600", [10, 20, 30]) -> True/False
        '''
        try:
            mb_addr = self.__offset_word(address)
            resp = self.client.write_registers(mb_addr, [int(v) for v in values], unit=self.__unit_id)
            if resp.isError():
                print(f"Failed to write registers {address} <- {values}")
                return False
            return True
        except Exception as e:
            print(f"Error in write_registers: {e}")
            return False

    # ----------------- utilities -----------------
    def is_connected(self) -> bool:
        '''
        print("Connected?", plc.is_connected())
        '''
        try:
            return self.client.connect()  # reconnects if needed; returns bool
        except Exception:
            return False

    def close(self):
        '''
        plc.close()
        '''
        if self.client:
            self.client.close()
            print(f"Connection to {self.__ip}:{self.__port} closed.")

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass