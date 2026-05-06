import copy


def run_srtf(processes):

    ps = copy.deepcopy(processes)
    
    for p in ps:
        p.remaining = p.burst
        p.start = -1  
        p.finish = 0
        p.waiting = 0
        p.turnaround = 0
        p.response_time = 0

    timeline = []
    current_time = 0
    completed = 0
    
    current_pid = None
    chunk_start = 0
    
    while completed < len(ps):
        available = [p for p in ps if p.arrival <= current_time and p.remaining > 0]
        
        if not available:
            if current_pid != "idle":
                if current_pid is not None:
                    timeline.append((current_pid, chunk_start, current_time))
                current_pid = "idle"
                chunk_start = current_time
            
            next_arrivals = [p.arrival for p in ps if p.arrival > current_time]
            current_time = min(next_arrivals)
            continue
            
        available.sort(key=lambda x: (x.remaining, x.arrival, x.id))
        selected = available[0]
        
        pid_string = f"P{selected.id}"
        
        if current_pid != pid_string:
            if current_pid is not None:
                timeline.append((current_pid, chunk_start, current_time))
            current_pid = pid_string
            chunk_start = current_time
            
        if selected.start == -1:
            selected.start = current_time
            selected.response_time = selected.start - selected.arrival 
            
        next_arrivals = [p.arrival for p in ps if p.arrival > current_time]
        next_arrival_time = min(next_arrivals) if next_arrivals else float('inf')
        
        run_time = min(selected.remaining, next_arrival_time - current_time)
        if run_time == 0: 
            run_time = 1
            
        selected.remaining -= run_time
        current_time += run_time
        
        if selected.remaining == 0:
            selected.finish = current_time
            selected.turnaround = selected.finish - selected.arrival
            selected.waiting = selected.turnaround - selected.burst
            completed += 1

    if current_pid is not None:
        timeline.append((current_pid, chunk_start, current_time))
        
    return timeline, ps