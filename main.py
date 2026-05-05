# temporary main to test the logic.
from process import Process
from schedulers.sjf import run_sjf
from schedulers.priority import run_priority

processes = [
    Process("P1", arrival=0, burst=6, priority=3),
    Process("P2", arrival=1, burst=3, priority=1),
    Process("P3", arrival=2, burst=8, priority=4),
    Process("P4", arrival=3, burst=1, priority=2),
]

timeline, results = run_sjf(processes, preemptive=False)
print("SJF timeline:", timeline)
for p in results:
    print(f"  {p.pid} | start={p.start} finish={p.finish} wait={p.waiting} tat={p.turnaround}")