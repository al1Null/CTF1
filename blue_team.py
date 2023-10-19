import time
import sys
from pymodbus.client import ModbusTcpClient as ModbusClient
from monitor import monitor as check_robustness


def read_traces(client, num_registers=16):
    rr = client.read_holding_registers(1, num_registers)
    if rr.isError():
        print(f'Error reading from ModbusClient: {rr}')
        return []
    else:
        return rr.registers


def log_traces(elapsed_time, traces, old_traces):
    diff = [cur - old for cur, old in zip(traces, old_traces)]
    with open("blue_team_traces.txt", "a") as f:
        f.write(f"{elapsed_time},{','.join(map(str, traces))}\n")
        f.write(f"{elapsed_time},{','.join(map(str, diff))}\n")


def stop_pumps_and_plant(client):
    # BLUE_DOSER_REGISTER =
    # RED_DOSER_REGISTER =
    PLANT_POWER_REGISTER = 16
    # client.write_register(RED_DOSER_REGISTER, 0)
    # client.write_register(BLUE_DOSER_REGISTER, 0)
    client.write_register(PLANT_POWER_REGISTER, 0)
    print("Pumps and Plant Stopped!")


def monitor(ip_add, d, s_time, num_registers=16):
    client = ModbusClient(ip_add, port=502)
    client.connect()

    start_time = time.time()
    old_traces = [0] * num_registers
    while time.time() - start_time < d:
        traces = read_traces(client, num_registers)
        elapsed_time = time.time() - start_time
        log_traces(elapsed_time, traces, old_traces)

        rob = check_robustness(traces)
        if rob < 0:
            stop_pumps_and_plant(client)
            break

        old_traces = traces
        time.sleep(s_time)

    client.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 blue_team.py [IP] [Duration] [Sample Time]")
        sys.exit()

    ip = sys.argv[1]
    duration = float(sys.argv[2])
    sample_time = float(sys.argv[3])

    monitor(ip, duration, sample_time)
