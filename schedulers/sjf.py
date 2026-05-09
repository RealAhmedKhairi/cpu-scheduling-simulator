import copy


def run_sjf(processes, preemptive=True):
    """Run Shortest Job First (SJF) scheduling.

    Args:
        processes: list of Process objects.
        preemptive: if True, runs SRJF (preemptive); if False, runs SJF (non-preemptive).

    Returns:
        tuple: (timeline, results) where timeline is a list of (pid, start, end)
        segments and results is a deep-copied list of Process objects with metrics.
    """
    ps = copy.deepcopy(processes)
    n = len(ps)
    if n == 0:
        return [], []

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
    active_process = None

    while completed < n:
        available = [p for p in ps if p.arrival <= current_time and p.remaining > 0]

        if not available:
            next_arrival = min(
                (p.arrival for p in ps if p.remaining > 0 and p.arrival > current_time),
                default=None,
            )
            if current_pid != "Idle":
                if current_pid is not None:
                    timeline.append((current_pid, segment_start, current_time))
                current_pid = "Idle"
                segment_start = current_time
            if next_arrival is None:
                break
            current_time = next_arrival
            continue

        if preemptive or active_process is None or active_process.remaining == 0:
            selected = min(available, key=lambda p: (p.remaining, p.arrival, p.pid))
            active_process = selected
        else:
            selected = active_process

        if current_pid != selected.pid:
            if current_pid is not None:
                timeline.append((current_pid, segment_start, current_time))
            current_pid = selected.pid
            segment_start = current_time

        if selected.start == -1:
            selected.start = current_time
            selected.response_time = current_time - selected.arrival

        selected.remaining -= 1
        current_time += 1

        if selected.remaining == 0:
            selected.finish = current_time
            selected.turnaround = selected.finish - selected.arrival
            selected.waiting = selected.turnaround - selected.burst
            completed += 1
            active_process = None

    if current_pid is not None:
        timeline.append((current_pid, segment_start, current_time))

    return timeline, ps