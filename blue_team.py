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

def log_traces(elapsed_time, traces, old_traces, water_volume_ml, red_ml, blue_ml):
    diff = [cur - old for cur, old in zip(traces, old_traces)]
    
    with open("blue_team_traces.txt", "a") as f:
        f.write(f"{elapsed_time},{','.join(map(str, traces))},{water_volume_ml},{red_ml},{blue_ml}\n")
        f.write(f"{elapsed_time},{','.join(map(str, diff))},,,\n")

    # Display formatting
    max_width = max(max(map(len, map(lambda x: "{:07.3f}".format(x), traces))), max(map(len, map(lambda x: "{:07.3f}".format(x), diff))))
    format_str = "{:>" + str(max_width) + "}"
    
    header = f"Elapsed Time  | Vol. | Red  | Blue | " + " | ".join([f"  {i+1:02}   " for i in range(len(traces))])
    header = header.ljust(len(header) + (max_width - 7) * len(traces))
    
    values = "{:<13.2f} | {:<3.2f} | {:<3.2f} | {:<3.2f} | ".format(elapsed_time, water_volume_ml, red_ml, blue_ml) + " | ".join([format_str.format("{:07.3f}".format(val)) for val in traces])
    rate_diff = "Rate Diff     |      |      |      | " + " | ".join([format_str.format("{:07.3f}".format(val)) for val in diff])

    print("-" * len(header))
    print(header)
    print(values)
    print(rate_diff)
    print("-" * len(header))

def stop_pumps_and_plant(client):
    BLUE_DOSER_REGISTER = 7
    RED_DOSER_REGISTER = 6
    PUMP_REGISTER = 4
    PLANT_POWER_REGISTER = 16
    
    client.write_register(PUMP_REGISTER, 0)
    client.write_register(RED_DOSER_REGISTER, 0)
    client.write_register(BLUE_DOSER_REGISTER, 0)
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
        log_traces(elapsed_time, traces, old_traces, traces[3], traces[5], traces[6])  # Using 0-based indices
    
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
