from AMX_TCP_CLASS import AMX_TCP
import yaml

with open("setup.yaml", "r", encoding="utf-8") as file:
    info = yaml.safe_load(file)

IP = info["PLC"]["HOST"]
PORT = info["PLC"]["PORT"]
unit_id = info["PLC"]["Address"]

plc = AMX_TCP(IP,PORT,unit_id)

while True:
    try:
        msg_1 = int(input("Select mode 1(Read)/2(Write): ").strip())
        
        if msg_1 == 1:
            msg_2 = int(input("Select 1(Bit)/2(Word): ").strip())
            
            if msg_2 == 1: 
                msg_3 = input("Bit address: ").strip()
                msg = plc.read_bit(msg_3)
                if msg is not None:
                    print(f"Value at {msg_3}: {msg}")
                else:
                    print(f"Error reading bit at {msg_3}")
                    
            elif msg_2 == 2:
                msg_3 = input("Word address: ").strip()
                msg = plc.read_word(msg_3)
                if msg is not None:
                    print(f"Value at {msg_3}: {msg}")
                else:
                    print(f"Error reading word at {msg_3}")

        elif msg_1 == 2:
            msg_2 = int(input("Select 1(Bit)/2(Word): ").strip())

            if msg_2 == 1:
                msg_3 = input("Bit address: ").strip()
                msg_4 = input("True/false (1/0): ").strip() == "1"
                result = plc.write_bit(msg_3, msg_4)
                if result:
                    print(f"Successfully wrote {msg_4} to {msg_3}")
                else:
                    print(f"Failed to write {msg_4} to {msg_3}")

            elif msg_2 == 2:
                msg_3 = input("Word address: ").strip()
                msg_4 = int(input("Value: ").strip())
                result = plc.write_word(msg_3, msg_4)
                if result:
                    print(f"Successfully write {msg_4} to {msg_3}")
                else:
                    print(f"Failed to write {msg_4} to {msg_3}")
                    
        else:
            print("Invalid selection. Try again.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")
