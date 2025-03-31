from pymodbus.client.sync import ModbusTcpClient  #pymodbus version 2.5.3
'''
Function Code	คำสั่ง Modbus	            Modbus Address	  ใช้กับ Component	 
01H	            Read Coils	              0x (00001)	    M, Y	          
02H	            Read Discrete Inputs	  1x (10001)	    M, Y, X	          
03H	            Read Holding Registers	  4x (40001)	    D	              
04H	            Read Input Registers	  3x (30001)	    D	              
05H	            Write Single Coil	      0x (00001)	    M, Y	          
06H	            Write Single Register	  4x (40001)	    D	              
0FH	            Write Multiple Coils	  0x (00001)	    M, Y	          
10H	            Write Multiple Reg	      4x (40001)	    D	             

ฟังก์ชัน	                ใช้กับอะไร	            อ่าน/เขียน	        ต้องการอะไร
read_coils()	            Output Bit (M/Y)    อ่าน	            address, count, unit
write_coil()	            Output Bit	        เขียน	            address, value, unit
read_discrete_inputs()	    Input Bit (X)	    อ่าน	            address, count, unit
read_holding_registers()	ค่าพารามิเตอร์ (D)	    อ่าน	            address, count, unit
write_register()	        Register (D)	    เขียน 1 ค่า	        address, value, unit
write_registers()	        Register (D)	    เขียนหลายค่า	    address, values[], unit
read_input_registers()	    Read-only Register	อ่าน	            address, count, unit

M0~M8511 -> Modbus 0~8191 -> Function 01, 02, 05, 0F
Y0~Y377 -> Modbus 8192~8447 -> Function 01
X0~X377 -> Modbus 8448~8703 -> Function 02
D0~D7999 -> Modbus D8000~D8511 -> Function 03, 04, 06, 10

'''
class AMX_TCP:

    def __init__(self,ip:str,port:int,unit_id:int):
        self.__ip = ip
        self.__port = port
        self.__unit_id = unit_id
        self.client = ModbusTcpClient(self.__ip, self.__port)
        connection = self.client.connect()
        if connection:
            print(f"Connected to {self.__ip}:{self.__port} successfully.")
        else:
            print(f"Failed to connect to {self.__ip}:{self.__port}.")
    
    def __offset_coil(self, data: str) -> int:
        if data.startswith(("M", "m")):
            return int(data[1:])
        elif data.startswith(("Y", "y")):
            return 8192 + int(data[1:])
        elif data.startswith(("X", "x")):
            return 8448 + int(data[1:])
        else:
            raise ValueError(f"Invalid coil address prefix in: {data}")
        
    def __offset_word(self, data: str) -> int:
        if data.startswith(("D", "d")):
            index = int(data[1:])
            if 0 <= index <= 8511:
                return index
            else:
                raise ValueError(f"D address out of range: {data}")
        else:
            raise ValueError(f"Invalid word address prefix in: {data}")

    def read_bit(self,address:str) -> bool:
        try:
            coil_address = self.__offset_coil(address)
            response = self.client.read_discrete_inputs(coil_address,count=1,unit=self.__unit_id) #02H Read Discrete Inputs MXY
            if not response.isError():
                return response.bits[0]
            else:
                print(f"Read Coil Error at address {address}: {response}")
                return None
            
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def read_word(self,address:str) -> int:
        try:
            word_address = self.__offset_word(address)
            response = self.client.read_input_registers(word_address,count=1,unit=self.__unit_id) #04H Read Input Registers D
            if not response.isError():
                return response.registers[0]
            else:
                print(f"Read Word Error at address {address}: {response}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def write_bit(self,address:str,value:bool):
        try:
            coil_address = self.__offset_coil(address)
            response = self.client.write_coil(coil_address,value,unit=self.__unit_id) #05H Single Coil MY
            if response.isError():
                print(f"Failed to write {value} to {address}")
                return False
            return True
        except Exception as e:
            print(f"Error: {e}")
            
    def write_word(self,address:str,value:int):
        try:
            word_address = self.__offset_word(address)
            response = self.client.write_register(word_address,value,unit=self.__unit_id) #06H Single Register D
            if response.isError():
                print(f"Failed to write {value} to {address}")
                return False
            return True
        except Exception as e:
            print(f"Error: {e}")
            
    def __del__(self):
        if self.client:
            self.client.close()
            print(f"Connection to {self.__ip}:{self.__port} closed.")
