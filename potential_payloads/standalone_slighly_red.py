from pymodbus.client.sync import ModbusTcpClient
import random, time

client = ModbusTcpClient('localhost', port=502)

SENSOR = {
    "ColorSensor_RED": 0,
    "ColorSensor_BLUE": 2,
    "ColorSensor_GREEN": 1,
    "RangeSensor": 3,
}
ACT = {
    "Pump": 4,
    "Doser_RED": 6,
    "Doser_BLUE": 7
}

while True:
    time.sleep(3.2 + random.uniform(-0.3, 0.3)) 
    red_value = client.read_holding_registers(SENSOR["ColorSensor_RED"], 1).registers[0]
    blue_value = client.read_holding_registers(SENSOR["ColorSensor_BLUE"], 1).registers[0]

    
    if random.random() < 0.50:  # 50% chance
         
        new_red_value = red_value + random.randint(5, 10)
        client.write_register(SENSOR["ColorSensor_RED"], new_red_value)
        print("[+] Everything seems good! Kudos to the Blue Team! [Waiting...]")
	    
    
    time.sleep(2.2 + random.uniform(-0.2, 0.2))  

