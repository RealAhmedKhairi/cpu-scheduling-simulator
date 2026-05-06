class Process:
    def __init__ (this, pid, arrival, burst, priority = 0):
        this.pid = pid
        this.arrival = arrival
        this.burst = burst
        this.priority = priority
        this.start = 0
        this.finish = 0
        this.waiting = 0
        this.turnaround = 0
        this.response_time = -1 