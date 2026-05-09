# CPU Scheduling Simulator

A Python desktop application built with `tkinter` that compares Shortest Job First (SJF / SRJF) and Priority Scheduling (Preemptive / Non-preemptive).

## Features

- Add, edit, and remove processes using an input panel
- Support for both Preemptive (SRJF/Priority) and Non-preemptive (SJF/Priority) modes
- Run both algorithms simultaneously
- View separate Gantt charts for each algorithm
- Display per-process metrics and averages
- Compare average waiting time, turnaround time, and response time side-by-side
- Auto-generate a conclusion summary after each simulation
- Four built-in test scenarios for fast validation
- Validation for missing fields, non-numeric values, duplicate PIDs, invalid arrival/burst/priority values
- Scrollable, resizable window with clean section headers

## Project Structure

```
cpu-scheduling-simulator/
├── main.py
├── process.py
├── schedulers/
│   ├── __init__.py
│   ├── sjf.py
│   └── priority.py
└── gui/
    ├── __init__.py
    ├── app.py
    ├── gantt.py
    └── input_form.py
```

## Installation

This application uses only Python standard library modules, including `tkinter`.

### Windows

1. Install Python 3 if needed: https://www.python.org/downloads/
2. Make sure the `python` command is available in your PATH.
3. `tkinter` is included with standard Python on Windows.
4. Open a command prompt and run:
5. We built it using Python 3.14.4

```bash
cd path\to\cpu-scheduling-simulator
python main.py
```

### Fedora

```bash
sudo dnf install python3 python3-tkinter
python main.py
```

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-tk
python main.py
```

## Running the App

From the project root:

```bash
python main.py
```

The main window includes:

- Input Panel
- Process Table
- SJF Gantt Chart and results
- Priority Scheduling Gantt Chart and results
- Comparison Summary
- Final Conclusion

## Input Panel

Fields:

- PID
- Arrival Time
- Burst Time
- Priority

Buttons:

- Add Process
- Remove Process
- Clear All
- Run Simulation
- Scenario A / B / C / D

## Process Table

Displays all added processes with columns:

- PID
- Arrival
- Burst
- Priority

Rows are editable by double-clicking.
<img width="1104" height="845" alt="image" src="https://github.com/user-attachments/assets/e761a9bf-0233-43e7-b529-289312b49273" />
<img width="1104" height="845" alt="image" src="https://github.com/user-attachments/assets/ca325953-548f-40a6-94de-2374a0a7ff72" />


## Gantt Charts

Each algorithm has a dedicated `tkinter.Canvas` chart with:

- unique process colors
- idle segments rendered in gray
- time markers on the x-axis
- algorithm title text above the chart

## Results Tables

Each algorithm has a results table containing:

- PID
- Arrival
- Burst
- Priority
- Start
- Finish
- Waiting Time
- Turnaround Time
- Response Time

The last row displays averages in bold.

## Comparison Summary

The comparison section shows:

- Average Waiting Time
- Average Turnaround Time
- Average Response Time

The better value is highlighted in green.

## Final Conclusion

A read-only conclusion area summarizes:

- which algorithm has lower average waiting time
- which algorithm has lower average turnaround time
- which algorithm is more responsive
- the trade-off between efficiency and urgency

## Preloaded Scenarios

### Scenario A: Basic mixed workload

- `P1`: arrival=0, burst=6, priority=3
- `P2`: arrival=1, burst=3, priority=1
- `P3`: arrival=2, burst=8, priority=4
- `P4`: arrival=3, burst=1, priority=2

### Scenario B: Burst vs Priority conflict

- `P1`: arrival=0, burst=2, priority=5
- `P2`: arrival=0, burst=9, priority=1
- `P3`: arrival=3, burst=4, priority=2

### Scenario C: Starvation-sensitive

- `P1`: arrival=0, burst=3, priority=1
- `P2`: arrival=1, burst=4, priority=1
- `P3`: arrival=2, burst=2, priority=5
- `P4`: arrival=3, burst=6, priority=1

### Scenario D: Validation case

- `P1`: arrival=-1, burst=0, priority=0
- `P1`: arrival=2, burst=4, priority=2

This scenario demonstrates invalid input handling.
<img width="1104" height="845" alt="image" src="https://github.com/user-attachments/assets/2ff560e4-6fcf-4b53-852d-07b7f2418b80" />


## Scheduler Behavior

### SJF (`schedulers/sjf.py`)

- Implements preemptive Shortest Remaining Time First (SRTF)
- Chooses the ready process with the smallest remaining burst time each time unit
- Preempts the current process if a shorter one arrives
- Returns a timeline and metrics for each process

### Priority (`schedulers/priority.py`)

- Implements preemptive priority scheduling
- Chooses the ready process with the highest priority (lowest numeric value) each time unit
- Preempts the current process if a higher-priority process arrives
- Returns a timeline and metrics for each process

<img width="1104" height="845" alt="image" src="https://github.com/user-attachments/assets/dbac2f2c-d642-41f3-85a7-9c65c3e2dba2" />
<img width="1104" height="845" alt="image" src="https://github.com/user-attachments/assets/e2a3b93a-c489-486a-ac30-e25631a00f43" />

## Notes

- The app is designed to run without external dependencies beyond Python and `tkinter`.
- Validation prevents invalid scheduling input.
- If a scheduler fails, the GUI shows an error message instead of crashing.

## Contributing

You can extend this project by adding:

- non-preemptive scheduler modes
- additional scheduling algorithms
- performance metrics charts
- export of results to CSV or PDF
