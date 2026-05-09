import copy


def run_sjf_non_preemptive(processes):
    """Run Non-preemptive Shortest Job First (SJF) scheduling.
    This implementation follows all strict rules for the simulator.
    """
    # Rule: Always deepcopy
    ps = copy.deepcopy(processes)
    n = len(ps)
    if n == 0:
        return [], []

    # Rule: Reset remaining and metrics
    for p in ps:
        p.remaining = p.burst
        p.start = -1
        p.finish = 0
        p.waiting = 0
        p.turnaround = 0
        p.response_time = -1

    current_time = 0
    completed = 0
    timeline = []
    current_pid = None
    segment_start = 0

    while completed < n:
        # Rule: Handle the idle gap
        available = [p for p in ps if p.arrival <= current_time and p.remaining > 0]

        if not available:
            next_arrival = min(
                (p.arrival for p in ps if p.remaining > 0 and p.arrival > current_time),
                default=None,
            )
            
            if current_pid != "Idle":
                if current_pid is not None:
                    timeline.append((str(current_pid), segment_start, current_time))
                current_pid = "Idle"
                segment_start = current_time
            
            if next_arrival is None:
                break
            current_time = next_arrival
            continue

        # Rule: Non-preemptive selection (shortest burst)
        selected = min(available, key=lambda p: (p.burst, p.arrival, p.pid))

        # Rule: Timeline segments sorted by start time and PIDs as strings
        if current_pid != selected.pid:
            if current_pid is not None:
                timeline.append((str(current_pid), segment_start, current_time))
            current_pid = selected.pid
            segment_start = current_time

        # Rule: Fill in all four fields
        selected.start = current_time
        selected.response_time = current_time - selected.arrival
        
        # Advance time by the full burst (non-preemptive)
        current_time += selected.burst
        selected.remaining = 0
        
        selected.finish = current_time
        selected.turnaround = selected.finish - selected.arrival
        selected.waiting = selected.turnaround - selected.burst
        completed += 1

    if current_pid is not None:
        timeline.append((str(current_pid), segment_start, current_time))

    return timeline, ps


if __name__ == "__main__":
    # Test script similar to what was in sjfNon.py but following new rules
    from process import Process
    
    test_processes = [
        Process(1, 1, 7),
        Process(2, 2, 5),
        Process(3, 3, 1),
        Process(4, 4, 2),
        Process(5, 5, 8),
    ]
    
    timeline, results = run_sjf_non_preemptive(test_processes)
    
    print("ProcessId Arrival Time Burst Time Completion Time Turn Around Time Waiting Time")
    for p in sorted(results, key=lambda x: x.pid):
        print(f"{p.pid}\t\t{p.arrival}\t\t{p.burst}\t\t{p.finish}\t\t{p.turnaround}\t\t{p.waiting}")
    
    print("\nTimeline:", timeline)
