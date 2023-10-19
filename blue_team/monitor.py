import time


class RobustMonitor:
    def __init__(self):
        self.previous_traces = []
        self.pump_toggles = 0
        self.last_update_time = time.time()
        self.MAX_PUMP_TOGGLES = 5  # Arbitrarily chosen
        self.MAX_SENSOR_JUMP = 10  # This threshold can be adjusted as per your need
        self.TIME_WINDOW = 10  # 10 seconds, for instance

    def monitor(self, traces):
        THRESHOLD = 20

        # Check for frequent pump toggling
        if self.previous_traces:
            if self.previous_traces[0] != traces[0]:  # Assuming pump trace is at index 0
                self.pump_toggles += 1

        if time.time() - self.last_update_time > self.TIME_WINDOW:
            self.pump_toggles = 0
            self.last_update_time = time.time()

        if self.pump_toggles > self.MAX_PUMP_TOGGLES:
            return -1  # Negative robustness due to frequent toggling

        # Check for unnatural jumps in sensor readings
        if self.previous_traces:
            for prev, curr in zip(self.previous_traces[1:], traces[1:]):  # Excluding pump trace
                if abs(prev - curr) > self.MAX_SENSOR_JUMP:
                    return -1  # Negative robustness due to unnatural jump

        # Original monitor logic
        total_value = sum(traces)
        if total_value > THRESHOLD:
            return -1

        # Update the state
        self.previous_traces = traces
        return 1  # Positive robustness
