from FX5U_TCP_CLASS import FX5U_TCP
import yaml
import time

def parse_bool_list(s: str):
    parts = [p.strip().lower() for p in s.split(",") if p.strip() != ""]
    return [p in ("1", "true", "t", "on", "yes", "y") for p in parts]

def parse_int_list(s: str):
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    return [int(p) for p in parts]

def main():
    with open("setup.yaml", "r", encoding="utf-8") as f:
        info = yaml.safe_load(f)
    IP = info["PLC"]["HOST"]
    PORT = info["PLC"]["PORT"]
    unit_id = info["PLC"]["Address"]

    plc = FX5U_TCP(IP, PORT, unit_id)

    menu = """
    0  - Show connection status
    1  - Read single bit (read_bit)
    2  - Read multiple bits (read_bits)
    3  - Write single coil (write_coil)
    4  - Write multiple coils (write_coils)
    5  - Read single input register (read_word)
    6  - Read multiple input registers (read_input_registers)
    7  - Read single holding register (read_holding)
    8  - Read multiple holding registers (read_holding_registers)
    9  - Write single register (write_word)
    10 - Write multiple registers (write_registers)
    11 - Toggle example (simple loop example)
    99 - Close & Exit
    """

    try:
        while True:
            print(menu)
            try:
                sel = int(input("Select option: ").strip())
            except ValueError:
                print("Invalid selection — enter a number.")
                continue

            if sel == 0:
                print("Connected?", plc.is_connected())

            elif sel == 1:
                addr = input("Bit address (e.g. Y0, M10, X5): ").strip()
                v = plc.read_bit(addr)
                print(f"{addr} -> {v}")

            elif sel == 2:
                addr = input("Start bit address (e.g. Y0, M20, X0): ").strip()
                try:
                    count = int(input("Count: ").strip())
                except ValueError:
                    print("Invalid count")
                    continue
                vals = plc.read_bits(addr, count=count)
                print(f"{addr} x{count} -> {vals}")

            elif sel == 3:
                addr = input("Bit address to write (M/Y only, e.g. M10, Y0): ").strip()
                raw = input("Value (1/0 or True/False): ").strip()
                val = raw in ("1", "true", "True", "t", "on", "yes")
                ok = plc.write_coil(addr, val)
                print("OK" if ok else "Failed")

            elif sel == 4:
                addr = input("Start coil address to write (M/Y only, e.g. M20): ").strip()
                raw = input("Values comma separated (e.g. 1,0,1,1 or True,False): ").strip()
                try:
                    values = parse_bool_list(raw)
                except Exception as e:
                    print("Invalid values:", e)
                    continue
                ok = plc.write_coils(addr, values)
                print("OK" if ok else "Failed")

            elif sel == 5:
                addr = input("Input register address (Dxxx): ").strip()
                v = plc.read_word(addr)
                print(f"{addr} -> {v}")

            elif sel == 6:
                addr = input("Start input register address (Dxxx): ").strip()
                try:
                    count = int(input("Count: ").strip())
                except ValueError:
                    print("Invalid count")
                    continue
                vals = plc.read_input_registers(addr, count=count)
                print(f"{addr} x{count} -> {vals}")

            elif sel == 7:
                addr = input("Holding register address (Dxxx): ").strip()
                v = plc.read_holding(addr)
                print(f"{addr} -> {v}")

            elif sel == 8:
                addr = input("Start holding register address (Dxxx): ").strip()
                try:
                    count = int(input("Count: ").strip())
                except ValueError:
                    print("Invalid count")
                    continue
                vals = plc.read_holding_registers(addr, count=count)
                print(f"{addr} x{count} -> {vals}")

            elif sel == 9:
                addr = input("Register address to write (Dxxx): ").strip()
                try:
                    val = int(input("Value (int): ").strip())
                except ValueError:
                    print("Invalid value")
                    continue
                ok = plc.write_word(addr, val)
                print("OK" if ok else "Failed")

            elif sel == 10:
                addr = input("Start register address to write (Dxxx): ").strip()
                raw = input("Values comma separated (e.g. 10,20,30): ").strip()
                try:
                    values = parse_int_list(raw)
                except Exception as e:
                    print("Invalid values:", e)
                    continue
                ok = plc.write_registers(addr, values)
                print("OK" if ok else "Failed")

            elif sel == 11:
                # simple toggle example: toggle a coil and read a register
                addr_coil = input("Toggle coil address (M/Y): ").strip()
                addr_reg = input("Read holding reg address (Dxxx): ").strip()
                times = input("How many cycles (default 5): ").strip()
                try:
                    cycles = int(times) if times else 5
                except ValueError:
                    cycles = 5
                for i in range(cycles):
                    val = (i % 2 == 0)
                    plc.write_coil(addr_coil, val)
                    time.sleep(0.1)
                    status = plc.read_bit(addr_coil)
                    reg = plc.read_holding(addr_reg)
                    print(f"[{i+1}/{cycles}] {addr_coil}={status} | {addr_reg}={reg}")
                    time.sleep(1)

            elif sel == 99:
                print("Closing connection and exiting.")
                plc.close()
                break

            else:
                print("Unknown selection.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Closing connection.")
        plc.close()

if __name__ == "__main__":
    main()
