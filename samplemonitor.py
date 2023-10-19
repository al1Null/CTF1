import sys
import rtamt

# Monitor for STL traces
# Registers Description: TODO: map out the rest of the registers
# Registry 1: bottle sensor         (1 --> bottle is under the nozzle)
# Registry 2: water level sensor    (1 --> bottle is full)
# Registry 3: roller output         (1 --> moving)
# Registry 4: nozzle output         (1 --> nozzle is open)
# ......
# Registry 16: plant power switch   (1 --> plant turns on)
# Registry N: ?????

def monitor(spec_num : str):
    # Read the traces
    with open('traces.txt', 'r') as file:
        traces = [list(map(float, line.strip().split(','))) for line in file]

    # Split the traces into timestamps and register values
    timestamps = [trace[0] for trace in traces]
    register_values = [trace[1:] for trace in traces]

    r1_values = [[timestamps[i], register_values[i][0]] for i in range(len(timestamps))]
    r2_values = [[timestamps[i], register_values[i][1]] for i in range(len(timestamps))]
    r3_values = [[timestamps[i], register_values[i][2]] for i in range(len(timestamps))]
    r4_values = [[timestamps[i], register_values[i][3]] for i in range(len(timestamps))]
    r16_values = [[timestamps[i], register_values[i][15]] for i in range(len(timestamps))]

    spec = rtamt.StlDenseTimeSpecification()
    spec.name = 'Plant Monitoring'
    spec.declare_var('r1', 'float')
    spec.declare_var('r2', 'float')
    spec.declare_var('r3', 'float')
    spec.declare_var('r4', 'float')
    spec.declare_var('r16', 'float')
    spec.set_var_io_type('r1', 'input')
    spec.set_var_io_type('r2', 'input')
    spec.set_var_io_type('r3', 'output')
    spec.set_var_io_type('r4', 'output')
    spec.set_var_io_type('r16', 'output')


    # STL specifications (#2 was given).
    if spec_num == '1':  # init phase
        #spec.spec = '((r3 ==1) and (r4 ==0)) until (r1 ==1)'
        spec.spec = 'always(((r3 ==1) and (r4 ==0)) until (r1 ==1))' #testme
        #spec.spec = 'always[0,T_init]((r3 ==1) and (r4 ==0))' #testme
    elif spec_num == '2': # filling phase
        spec.spec = 'always((r1 ==1) implies ((r3 ==0) and (r4 == 1)))'
    elif spec_num == '3': # moving phase
        spec.spec = 'always((r2 ==1) implies ((r3 ==1) and (r4 ==0)))'#testme
    elif spec_num == '4': # start/stop
        spec.spec = 'always((r16 ==0) implies ((r3 ==0) and (r4 ==0)))'#test
    else:
        print_input_error_and_exit()

    try:
        spec.parse()
    except rtamt.RTAMTException as err:
        print('RTAMT Exception: {}'.format(err))
        sys.exit()

    rob = spec.evaluate(['r1', r1_values], ['r2', r2_values], ['r3', r3_values], ['r4', r4_values], ['r16', r16_values])

    print('Robustness: {}'.format(rob))

def print_input_error_and_exit():
    print('Please pass a parameter (spec_num = [1-4]) via argv \
                \n\t(e.g. "python3 samplemonitor.py 4"')
    sys.exit()


if __name__ == '__main__':
    # Process arguments
    if len(sys.argv) < 2:
        print_input_error_and_exit()

    spec_num = sys.argv[1]
    monitor(spec_num)