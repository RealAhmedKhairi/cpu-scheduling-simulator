import copy

def run_priority(processes, preemptive=True):
    # deepcopy so we never modify the original list passed in
    ps = copy.deepcopy(processes)
    n = len(ps)
    
    # edge case: no processes to schedule
    if n == 0:
        return [], []

    # ── HEAP HELPERS ────────────────────────────────────────────

    def insert(Heap, value, heapsize):
        # place the new process at the next available heap slot
        start = heapsize[0] # no processes in the heap
        # we use a list because integers are immutable in python 
        Heap[start] = value
        heapsize[0] += 1 # added one process 
        # bubble up: keep swapping with parent until heap property is restored
        # (parent has lower priority number = higher priority than child)
        # the parent is always at position (start-1) / 2 
        # if parent has a worse priority than the child, swap
        while start != 0 and Heap[(start-1)//2].priority > Heap[start].priority:
            temp = Heap[(start-1)//2]
            Heap[(start-1)//2] = Heap[start]
            Heap[start] = temp
            start = (start-1)//2

    def order(Heap, heapsize, start):
        # find the smallest priority among current node and its two children
        smallest = start
        left = 2 * start + 1
        right = 2 * start + 2
        if left < heapsize[0] and Heap[left].priority < Heap[smallest].priority:
            smallest = left
        if right < heapsize[0] and Heap[right].priority < Heap[smallest].priority:
            smallest = right
        # if a child has smaller priority, swap and recurse down
        if smallest != start:
            Heap[start], Heap[smallest] = Heap[smallest], Heap[start]
            order(Heap, heapsize, smallest)

    def extract(Heap, heapsize, current_time):
        # the root of a min-heap is always the highest priority process
        p = Heap[0]
        # response time = first time on CPU - arrival time
        # only set once (when it's -1), never overwritten
        if p.response_time == -1:
            p.response_time = current_time - p.arrival
        # shrink the heap and move the last element to root
        heapsize[0] -= 1
        if heapsize[0] >= 1:
            Heap[0] = Heap[heapsize[0]]
            # restore heap property by sifting the new root down
            order(Heap, heapsize, 0)
        return p

    # ── INITIALIZATION ──────────────────────────────────────────

    # sort by arrival time so we insert processes in the right order
    ps.sort(key=lambda x: x.arrival)
    
    for p in ps:
        # remaining tracks how much burst is left (decrements each time unit)
        p.remaining = p.burst
        # -1 means response time hasn't been recorded yet
        p.response_time = -1
        # will hold the time unit when the process last finishes on CPU
        p.finish = 0

    Heap = [None] * (4 * n)  # heap array, sized generously for re-insertions
    heap_size = [0]           # wrapped in list so helpers can mutate it
    timeline = []             # list of (pid, start, end) segments for the GUI
    current_pid = None        # pid of the process currently running
    segment_start = 0         # when the current segment started
    inserted = 0              # how many processes have been inserted so far
    current_time = 0          # simulation clock, advances one unit per iteration

    # ── MAIN SIMULATION LOOP ────────────────────────────────────

    while True:
        # check all processes: insert any that have arrived at this time unit
        for p in ps:
            if p.arrival == current_time:
                inserted += 1
                insert(Heap, p, heap_size)

        if heap_size[0] == 0:
            # no process is ready — CPU is idle this time unit
            executed_pid = "Idle"
        else:
            # extract the highest priority process from the heap
            p = extract(Heap, heap_size, current_time)
            executed_pid = p.pid
            
            # run it for exactly 1 time unit (preemptive = time-sliced by 1)
            p.remaining -= 1
            
            # record the time this unit ends as the latest finish time
            p.finish = current_time + 1

            if p.remaining > 0:
                # process not done yet — put it back in the heap
                insert(Heap, p, heap_size)
            else:
                # process finished — update it in the main ps list
                for i in range(n):
                    if ps[i].pid == p.pid:
                        ps[i] = p
                        break

        # detect a context switch (different process running than last unit)
        if executed_pid != current_pid:
            # close off the previous segment and add it to the timeline
            if current_pid is not None:
                timeline.append((current_pid, segment_start, current_time))
            # start a new segment for the newly running process
            current_pid = executed_pid
            segment_start = current_time

        # advance the clock by one time unit
        current_time += 1
        
        # stop when all processes are inserted and the heap is empty (all done)
        if heap_size[0] == 0 and inserted == n:
            break

    # ── CLOSE FINAL SEGMENT ─────────────────────────────────────

    # the last running process never triggered a context switch to close it
    if current_pid is not None:
        timeline.append((current_pid, segment_start, current_time))

    # ── COMPUTE METRICS ─────────────────────────────────────────

    for p in ps:
        # turnaround = total time from arrival to completion
        p.turnaround = p.finish - p.arrival
        # waiting = turnaround minus the actual time spent on CPU
        p.waiting = p.turnaround - p.burst

    # return both the timeline (for Gantt chart) and the processes (for metrics table)
    return timeline, ps