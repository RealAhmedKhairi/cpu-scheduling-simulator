import tkinter as tk
from tkinter import ttk


class InputPanel(ttk.LabelFrame):
    def __init__(self, parent, on_add, on_remove, on_clear, on_run, on_scenario_selected):
        super().__init__(parent, text="Input Panel", padding=12)
        self.pid_var = tk.StringVar()
        self.arrival_var = tk.StringVar()
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar()
        self.sjf_preemptive = tk.BooleanVar(value=True)
        self.priority_preemptive = tk.BooleanVar(value=True)

        self._build_fields(on_add, on_remove, on_clear, on_run, on_scenario_selected)

    def _build_fields(self, on_add, on_remove, on_clear, on_run, on_scenario_selected):
        label_config = {"font": ("Arial", 10)}

        ttk.Label(self, text="PID:", **label_config).grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(self, textvariable=self.pid_var, width=12).grid(row=0, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(self, text="Arrival Time:", **label_config).grid(row=0, column=2, sticky="w", padx=5, pady=4)
        ttk.Entry(self, textvariable=self.arrival_var, width=12).grid(row=0, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(self, text="Burst Time:", **label_config).grid(row=0, column=4, sticky="w", padx=5, pady=4)
        ttk.Entry(self, textvariable=self.burst_var, width=12).grid(row=0, column=5, sticky="w", padx=5, pady=4)

        ttk.Label(self, text="Priority:", **label_config).grid(row=0, column=6, sticky="w", padx=5, pady=4)
        ttk.Entry(self, textvariable=self.priority_var, width=12).grid(row=0, column=7, sticky="w", padx=5, pady=4)

        # Mode Toggles
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=1, column=0, columnspan=8, sticky="w", padx=5, pady=5)
        
        ttk.Label(mode_frame, text="SJF Mode:", **label_config).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="SJF (Non-preemptive)", variable=self.sjf_preemptive, value=False).grid(row=0, column=1, padx=5)
        ttk.Radiobutton(mode_frame, text="SRJF (Preemptive)", variable=self.sjf_preemptive, value=True).grid(row=0, column=2, padx=5)

        ttk.Label(mode_frame, text="Priority Mode:", **label_config).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        ttk.Radiobutton(mode_frame, text="Non-preemptive", variable=self.priority_preemptive, value=False).grid(row=1, column=1, padx=5, pady=(5, 0))
        ttk.Radiobutton(mode_frame, text="Preemptive", variable=self.priority_preemptive, value=True).grid(row=1, column=2, padx=5, pady=(5, 0))

        ttk.Button(self, text="Add Process", command=on_add).grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        ttk.Button(self, text="Remove Process", command=on_remove).grid(row=2, column=2, columnspan=2, padx=5, pady=10, sticky="ew")
        ttk.Button(self, text="Clear All", command=on_clear).grid(row=2, column=4, columnspan=2, padx=5, pady=10, sticky="ew")
        ttk.Button(self, text="Run Simulation", command=on_run).grid(row=2, column=6, columnspan=2, padx=5, pady=10, sticky="ew")

        scenario_frame = ttk.Frame(self)
        scenario_frame.grid(row=3, column=0, columnspan=8, sticky="ew", padx=5, pady=5)
        for index in range(4):
            scenario_frame.columnconfigure(index, weight=1)

        ttk.Button(scenario_frame, text="Scenario A", command=lambda: on_scenario_selected("Scenario A")).grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        ttk.Button(scenario_frame, text="Scenario B", command=lambda: on_scenario_selected("Scenario B")).grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        ttk.Button(scenario_frame, text="Scenario C", command=lambda: on_scenario_selected("Scenario C")).grid(row=0, column=2, padx=3, pady=3, sticky="ew")
        ttk.Button(scenario_frame, text="Scenario D", command=lambda: on_scenario_selected("Scenario D")).grid(row=0, column=3, padx=3, pady=3, sticky="ew")

    def get_input(self):
        return {
            "pid": self.pid_var.get().strip(),
            "arrival": self.arrival_var.get().strip(),
            "burst": self.burst_var.get().strip(),
            "priority": self.priority_var.get().strip(),
            "sjf_preemptive": self.sjf_preemptive.get(),
            "priority_preemptive": self.priority_preemptive.get(),
        }

    def clear_fields(self):
        self.pid_var.set("")
        self.arrival_var.set("")
        self.burst_var.set("")
        self.priority_var.set("")
