from pymodbus.client.sync import ModbusTcpClient
import random, time

client = ModbusTcpClient('localhost', port=502)

ACT = {
    "Pump": 4,
    "Doser_RED": 6,
    "Doser_BLUE": 7
}

while True:
    time.sleep(2.2 + random.uniform(-0.3, 0.3))    
    if random.random() < 0.60:  # 60% chance
         
        client.write_coil(ACT['Pump'], 1)
        time.sleep(1 + random.uniform(-0.1, 0.1))
        print("[+] Everything seems good! Kudos to the Blue Team! [Waiting...]")
        client.write_coil(ACT['Pump'], 0)  

