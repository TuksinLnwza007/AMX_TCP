from pymodbus.client.sync import ModbusTcpClient  #pymodbus version 2.5.3

class FX5U_TCP:

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
            return 8192 + int(data[1:])
        elif data.startswith(("Y", "y")):
            return int(data[1:])
        elif data.startswith(("X", "x")):
            return int(data[1:])
        else:
            raise ValueError(f"Invalid coil address prefix in: {data}")
        
    def __offset_word(self, data: str) -> int:
        if data.startswith(("D", "d")):
            index = int(data[1:])
            if 0 <= index <= 8000:
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
            
    def read_holding(self, address: str) -> int:
        try:
            word_address = self.__offset_word(address)
            response = self.client.read_holding_registers(
                word_address, 
                count=1, 
                unit=self.__unit_id
            )  # 03H Read Holding Registers

            if not response.isError():
                return response.registers[0]
            else:
                print(f"Read Holding Register Error at address {address}: {response}")
                return None

        except Exception as e:
            print(f"Error: {e}")
            return None
            
    def write_holding(self, address: str, value: int):
        try:
            word_address = self.__offset_word(address)
            response = self.client.write_register(
                word_address,
                value,
                unit=self.__unit_id
            )  # 06H Write Single Register

            if response.isError():
                print(f"Failed to write {value} to {address}")
                return False
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def __del__(self):
        if self.client:
            self.client.close()
            print(f"Connection to {self.__ip}:{self.__port} closed.")
