class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = str(pid)
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.priority = int(priority)
        self.remaining = self.burst
        self.start = -1
        self.finish = 0
        self.waiting = 0
        self.turnaround = 0
        self.response_time = -1

    def reset(self):
        self.remaining = self.burst
        self.start = -1
        self.finish = 0
        self.waiting = 0
        self.turnaround = 0
        self.response_time = -1

    def __repr__(self):
        return (
            f"Process(pid={self.pid!r}, arrival={self.arrival}, burst={self.burst}, "
            f"priority={self.priority}, remaining={self.remaining}, start={self.start}, "
            f"finish={self.finish}, waiting={self.waiting}, turnaround={self.turnaround}, "
            f"response_time={self.response_time})"
        ) 