from FX5U_TCP_CLASS import FX5U_TCP
import yaml
import time

plc = FX5U_TCP("192.168.3.200", port=502, unit_id=1)
print("Connected?", plc.is_connected())
        
def main():
    while True:

        coil_addr = plc.read_bit("M0")
        print("M0 =", coil_addr)
        time.sleep(0.1)

if __name__ == "__main__":
    main()