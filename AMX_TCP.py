from pymodbus.client.sync import ModbusTcpClient #2.5.3
from time import sleep
import yaml

'''
>>>>>>>>>>>>>>> AMX-FX3U-M-Series-PLC <<<<<<<<<<<<<<<<<<<
M0~M8511 -> Modbus 0~8191 -> Function 01, 02, 05, 0F
Y0~Y377 -> Modbus 8192~8447 -> Function 01
X0~X377 -> Modbus 8448~8703 -> Function 02
D0~D7999 -> Modbus D8000~D8511 -> Function 03, 04, 06, 10
'''

with open("setup.yaml", "r", encoding="utf-8") as file:
    info = yaml.safe_load(file)

IP = info["PLC"]["HOST"]
PORT = info["PLC"]["PORT"]
unit_id = info["PLC"]["Address"]

print(f"IP: {IP}\nPORT: {PORT}\nunit_id: {unit_id}")

def connect_modbus():
    """Connect to Modbus TCP Server"""
    client = ModbusTcpClient(IP,PORT)
    connection = client.connect()
    if connection:
        print(f"Connected to {IP}:{PORT} successfully.")
    else:
        print(f"Failed to connect to {IP}:{PORT}.")
    return client

def read_coil(client, address, count=1): #01H -> Read Coil (0x) → M, Y
    type_bit = get_bit_address(address)
    try:
        response = client.read_coils(address=address, count=count, unit=unit_id)
        if not response.isError():
            return response.bits[0]
        else:
            print(f"Read Coil {type_bit}: {address} Error: {response}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_discrete_input(client, address, count=1): #02H -> Read Input Discrete (1x) → M, Y, X
    type_bit = get_bit_address(address)
    try:
        response = client.read_discrete_inputs(address=address, count=count, unit=unit_id)
        if not response.isError():
            return response.bits
        else:
            print(f"Read Input {type_bit} at {address} Error: {response}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def read_holding_register(client, address, count=1): #03H -> Read Holding Register (4x) → D
    type_word = get_word_address(address)
    try:
        response = client.read_holding_registers(address=address, count=count, unit=unit_id)
        if not response.isError():
            return response.registers
        else:
            print(f"Read {type_word}: {address} Error: {response}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_input_register(client, address, count=1): #04H -> Read Input Register (3x) → D
    type_word = get_word_address(address)
    try:
        response = client.read_input_registers(address=address, count=count, unit=unit_id)
        if not response.isError():
            return response.registers
        else:
            print(f"Read Input Register {type_word}: {address} Error: {response}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def write_single_coil(client, address, value): #05H -> Write Single Coil (0x) → M, Y
    type_bit = get_bit_address(address)
    try:
        response = client.write_coil(address=address, value=value, unit=unit_id)
        if not response.isError():
            print(f"Write {type_bit}: {address} = {value}")
        else:
            print(f"Write {type_bit}: {address} Error: {response}")
    except Exception as e:
        print(f"Error: {e}")

def write_single_register(client, address, value): #06H -> Write Single Register (4x) → D
    type_word = get_word_address(address)
    try:
        response = client.write_register(address=address, value=value, unit=unit_id)
        if not response.isError():
            print(f"Write {type_word}: {address} = {value}")
        else:
            print(f"Write {type_word}: {address} Error: {response}")
    except Exception as e:
        print(f"Error: {e}")

def write_multiple_coils(client, address, values): #0FH -> Write Multiple Coils (0x) → M, Y
    type_bit = get_bit_address(address)
    try:
        response = client.write_coils(address=address, values=values, unit=unit_id)
        if not response.isError():
            print(f"Write Coil {type_bit} start {address} = {values}")
        else:
            print(f"Write Coil Error: {response}")
    except Exception as e:
        print(f"Error: {e}")

def write_multiple_registers(client, address, values): #10H -> Write Multiple Registers (4x) → D
    type_word = get_word_address(address)
    try:
        response = client.write_registers(address=address, values=values, unit=unit_id)
        if not response.isError():
            print(f"Write {type_word} start {type_word}{address} = {values}")
        else:
            print(f"Write {type_word} Error: {response}")
    except Exception as e:
        print(f"Error: {e}")
        
def get_bit_address(address:int) -> str:
    if 0 <= address <= 1535:
        return "M"
    elif 1536 <= address <= 7679:
        return "M"
    elif 7680 <= address <= 8191:
        return "M"
    elif 8192 <= address <= 8447:
        return "Y"
    elif 8448 <= address <= 8703:
        return "X"
    else:
        return "Unknown"
    
def get_word_address(address:int) -> str:
    if 0 <= address <= 8511:
        return "D"
    else:
        return "Unknown"

def main():
    
    client = connect_modbus()
    
    if client.is_socket_open():
        try:
            while True :
                
                for i in range(8192, 8192+11, 1):
                    write_single_coil(client, i, True) 
                    sleep(0.3)
                    if i > 0:
                        write_single_coil(client, i-1, False) 
                        y = read_discrete_input(client, i, 1)
                        if y is not None:
                            pass

                for j in range(0, 100, 1):
                    write_single_register(client, 1, j)  
                    d1 = read_holding_register(client, 1, 1)
                    if d1 is not None:
                        print(f"D1 = {d1[0]}")
                    sleep(0.3)

        except Exception as e:
            print(f"main err:{e}")
        finally:
            client.close()

if __name__ == "__main__":
    main()