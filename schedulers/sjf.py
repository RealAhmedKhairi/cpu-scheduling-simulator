import copy


def run_sjf(processes, preemptive=True):
    """Run preemptive Shortest Job First (SRTF) scheduling.

    Args:
        processes: list of Process objects.
        preemptive: ignored for this implementation; the scheduler is always preemptive.

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

        selected = min(available, key=lambda p: (p.remaining, p.arrival, p.pid))

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

    if current_pid is not None:
        timeline.append((current_pid, segment_start, current_time))

    return timeline, ps