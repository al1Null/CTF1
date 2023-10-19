from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder
import time
import random

# Connect to OpenPLC
client = ModbusTcpClient('localhost', port=502)

# Constants for Simulation
TANK_VOLUME_ML = 900
DOSE_VOLUME_ML = 5

# Actuator and Sensor mappings for Simulation
ACT = {
    "red_doser": 6,
    "blue_doser": 7,
    "pump": 4,
}

SENS = {
    "water_level": -1,
    "red_RGB": 0,
    "green_RGB": 1,
    "blue_RGB": 2,
    "range_sensor": 3 
}

# Initial state for Simulation
water_volume_ml = 0
range_sensor = 100
red_ml = 0
blue_ml = 0
red_concentration = 0
blue_concentration = 0
fill_rate_mlph = 45000
step = 0

try:
    while True:
        # Simulation Logic
        step += 1
        range_sensor = 100 * (1 - water_volume_ml/TANK_VOLUME_ML)
        pump_result = client.read_coils(ACT['pump'])
        if not pump_result.isError() and pump_result.bits[0]:
            water_volume_ml += fill_rate_mlph / 3600
        response = client.read_coils(ACT["red_doser"], 2)
        if not response.isError():
            red_dose, blue_dose = response.bits[0], response.bits[1]
            if red_dose:
                red_ml += DOSE_VOLUME_ML
                water_volume_ml += DOSE_VOLUME_ML
            if blue_dose:
                blue_ml += DOSE_VOLUME_ML
                water_volume_ml += DOSE_VOLUME_ML

            if water_volume_ml > TANK_VOLUME_ML:
                overflow = water_volume_ml - TANK_VOLUME_ML
                red_ml -= .5 * overflow * red_concentration
                blue_ml -= .5 * overflow * blue_concentration
                water_volume_ml = TANK_VOLUME_ML

            if water_volume_ml > 0:
                red_concentration = red_ml / water_volume_ml
                blue_concentration = blue_ml / water_volume_ml

            client.write_registers(SENS["red_RGB"], [int(red_concentration * 255), 0, int(blue_concentration * 255)])
            client.write_registers(SENS["range_sensor"], int(range_sensor * 100))

            print(f'Water Vol: {water_volume_ml:.2f} ml (range={range_sensor:.2f}), Red Conc: {red_concentration:.2f}, Blue Conc: {blue_concentration:.2f}, ([{int(red_dose)},{int(blue_dose)}],t={step},r={red_ml:.2f},b={blue_ml:.2f})')
        else:
            print(f'Error reading from OpenPLC: {response}')

        # Manipulation Logic
        #time.sleep(1.6 + random.uniform(-0.3, 0.3))
        red_value = client.read_holding_registers(SENS["red_RGB"], 1).registers[0]
        if random.random() < 0.20:  # 20% chance
            time.sleep(1.3 + random.uniform(-0.3, 0.3))
            new_red_value = red_value + random.randint(5, 10)
            client.write_register(SENS["red_RGB"], new_red_value)

        #time.sleep(1.2 + random.uniform(-0.2, 0.2))

except KeyboardInterrupt:
    pass

client.close()

