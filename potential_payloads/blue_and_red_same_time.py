from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder
import random, time

client = ModbusTcpClient('localhost', port=502)

ACT = {
    "red_doser": 6, # QX0.6
    "blue_doser": 7, # QX0.7
    "pump": 4, # QX0.4
}

while True:
    time.sleep(8 + random.uniform(-0.2, 0.2))
    red_dose = random.choice([0,1])
    blue_dose = random.choice([0,1])
    client.write_coil(ACT['red_doser'], red_dose)
    client.write_coil(ACT['blue_doser'], blue_dose)
    #time.sleep(2 + random.uniform(-0.2, 0.2))

