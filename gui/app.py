import copy
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import tkinter.font as tkfont

from gui.gantt import draw_gantt_chart
from gui.input_form import InputPanel
from process import Process
from schedulers.sjf import run_sjf
from schedulers.priority import run_priority


class App:
    COLOR_PALETTE = [
        "#72B7B2",
        "#FFB347",
        "#8EA9DB",
        "#D292E8",
        "#A7C957",
        "#FF6961",
        "#77DD77",
        "#FDFD96",
        "#CB99C9",
        "#AEC6CF",
        "#FFB6C1",
        "#B39EB5",
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CPU Scheduling Simulator")
        self.root.minsize(1100, 800)
        self.root.option_add("*Font", ("Arial", 10))
        self.root.configure(bg="#f2f2f2")

        self.editing_entry = None
        self.summary_labels = {}
        self.latest_sjf_timeline = None
        self.latest_priority_timeline = None
        self.latest_pid_colors = None

        self._build_styles()
        self._build_ui()
        self._load_scenarios()

    def _build_styles(self):
        style = ttk.Style(self.root)
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Treeview", rowheight=26, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("TFrame", background="#f2f2f2")
        style.configure("TLabelframe", background="#f2f2f2")
        style.configure("TLabelframe.Label", font=("Arial", 12, "bold"))

    def _build_ui(self):
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(container, background="#f2f2f2", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.content_frame = ttk.Frame(self.main_canvas)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda event: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        self.content_frame.columnconfigure(0, weight=1)

        self.input_panel = InputPanel(
            self.content_frame,
            on_add=self.add_process,
            on_remove=self.remove_process,
            on_clear=self.clear_processes,
            on_run=self.run_simulation,
            on_scenario_selected=self.load_scenario,
        )
        self.input_panel.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self._build_process_table()
        self._build_sjf_section()
        self._build_priority_section()
        self._build_comparison_section()
        self._build_conclusion_section()

    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        delta = 0
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        elif hasattr(event, "delta"):
            delta = -1 * int(event.delta / 120)
        self.main_canvas.yview_scroll(delta, "units")

    def _build_process_table(self):
        frame = ttk.LabelFrame(self.content_frame, text="Process Table", padding=10)
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        columns = ("PID", "Arrival", "Burst", "Priority")
        self.process_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse", height=8)
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=110, anchor="center")
        self.process_tree.bind("<Double-1>", self._on_process_table_double_click)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)

        self.process_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_sjf_section(self):
        frame = ttk.LabelFrame(self.content_frame, text="Shortest Job First", padding=10)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        self.sjf_canvas = tk.Canvas(frame, height=180, background="white", bd=1, relief="solid")
        self.sjf_canvas.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.sjf_canvas.bind("<Configure>", lambda event: self._draw_gantt_sections())

        self.sjf_result_tree = ttk.Treeview(
            frame,
            columns=("PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting", "Turnaround", "Response"),
            show="headings",
            height=6,
        )
        headings = ["PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting Time", "Turnaround Time", "Response Time"]
        for col, heading in zip(self.sjf_result_tree["columns"], headings):
            self.sjf_result_tree.heading(col, text=heading)
            self.sjf_result_tree.column(col, width=100, anchor="center")
        self.sjf_result_tree.tag_configure("avg", font=("Arial", 10, "bold"))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.sjf_result_tree.yview)
        self.sjf_result_tree.configure(yscrollcommand=scrollbar.set)
        self.sjf_result_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

    def _build_priority_section(self):
        frame = ttk.LabelFrame(self.content_frame, text="Priority Scheduling", padding=10)
        frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        self.priority_canvas = tk.Canvas(frame, height=180, background="white", bd=1, relief="solid")
        self.priority_canvas.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.priority_canvas.bind("<Configure>", lambda event: self._draw_gantt_sections())

        self.priority_result_tree = ttk.Treeview(
            frame,
            columns=("PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting", "Turnaround", "Response"),
            show="headings",
            height=6,
        )
        headings = ["PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting Time", "Turnaround Time", "Response Time"]
        for col, heading in zip(self.priority_result_tree["columns"], headings):
            self.priority_result_tree.heading(col, text=heading)
            self.priority_result_tree.column(col, width=100, anchor="center")
        self.priority_result_tree.tag_configure("avg", font=("Arial", 10, "bold"))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.priority_result_tree.yview)
        self.priority_result_tree.configure(yscrollcommand=scrollbar.set)
        self.priority_result_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

    def _build_comparison_section(self):
        frame = ttk.LabelFrame(self.content_frame, text="Comparison Summary", padding=10)
        frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        header_style = {"font": ("Arial", 10, "bold")}
        ttk.Label(frame, text="Metric", **header_style).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text="SJF", **header_style).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(frame, text="Priority", **header_style).grid(row=0, column=2, sticky="w", padx=5, pady=5)

        metrics = ["Average Waiting Time", "Average Turnaround Time", "Average Response Time"]
        keys = ["waiting", "turnaround", "response"]
        for row, (metric, key) in enumerate(zip(metrics, keys), start=1):
            ttk.Label(frame, text=metric).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.summary_labels[key] = {
                "SJF": tk.Label(frame, text="N/A", bg="#ffffff", anchor="w", font=("Arial", 10)),
                "Priority": tk.Label(frame, text="N/A", bg="#ffffff", anchor="w", font=("Arial", 10)),
            }
            self.summary_labels[key]["SJF"].grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            self.summary_labels[key]["Priority"].grid(row=row, column=2, sticky="ew", padx=5, pady=5)

    def _build_conclusion_section(self):
        frame = ttk.LabelFrame(self.content_frame, text="Final Conclusion", padding=10)
        frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        self.conclusion_text = tk.Text(frame, height=6, wrap="word", font=("Arial", 10), state="disabled", bg="#f9f9f9")
        self.conclusion_text.grid(row=0, column=0, sticky="nsew")

    def _load_scenarios(self):
        self.scenarios = {
            "Scenario A": [
                {"pid": "P1", "arrival": "0", "burst": "6", "priority": "3"},
                {"pid": "P2", "arrival": "1", "burst": "3", "priority": "1"},
                {"pid": "P3", "arrival": "2", "burst": "8", "priority": "4"},
                {"pid": "P4", "arrival": "3", "burst": "1", "priority": "2"},
            ],
            "Scenario B": [
                {"pid": "P1", "arrival": "0", "burst": "2", "priority": "5"},
                {"pid": "P2", "arrival": "0", "burst": "9", "priority": "1"},
                {"pid": "P3", "arrival": "3", "burst": "4", "priority": "2"},
            ],
            "Scenario C": [
                {"pid": "P1", "arrival": "0", "burst": "3", "priority": "1"},
                {"pid": "P2", "arrival": "1", "burst": "4", "priority": "1"},
                {"pid": "P3", "arrival": "2", "burst": "2", "priority": "5"},
                {"pid": "P4", "arrival": "3", "burst": "6", "priority": "1"},
            ],
            "Scenario D": [
                {"pid": "P1", "arrival": "-1", "burst": "0", "priority": "0"},
                {"pid": "P1", "arrival": "2", "burst": "4", "priority": "2"},
            ],
        }

    def load_scenario(self, name):
        scenario = self.scenarios.get(name)
        if not scenario:
            return
        self.clear_processes()
        for row in scenario:
            self.process_tree.insert("", "end", values=(row["pid"], row["arrival"], row["burst"], row["priority"]))
        self.input_panel.clear_fields()

    def add_process(self):
        values = self.input_panel.get_input()
        if not values:
            return
        error = self.validate_process_row(values)
        if error:
            messagebox.showerror("Input Error", error)
            return
        if self._pid_exists(values["pid"]):
            messagebox.showerror("Input Error", f"PID {values['pid']} already exists.")
            return
        self.process_tree.insert("", "end", values=(values["pid"], values["arrival"], values["burst"], values["priority"]))
        self.input_panel.clear_fields()

    def remove_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a process to remove.")
            return
        self.process_tree.delete(selected[0])

    def clear_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

    def get_process_list(self):
        processes = []
        for index, item in enumerate(self.process_tree.get_children(), start=1):
            pid, arrival, burst, priority = self.process_tree.item(item, "values")
            row = {
                "pid": str(pid).strip(),
                "arrival": str(arrival).strip(),
                "burst": str(burst).strip(),
                "priority": str(priority).strip(),
            }
            error = self.validate_process_row(row, row_number=index)
            if error:
                raise ValueError(error)
            processes.append(row)
        if not processes:
            raise ValueError("No processes have been added.")
        duplicate = self.find_duplicate_pids(processes)
        if duplicate:
            raise ValueError(f"Duplicate PID detected: {duplicate}")
        return processes

    def validate_process_row(self, row, row_number=None):
        label = f"Row {row_number}: " if row_number is not None else ""
        if not row["pid"] or not row["arrival"] or not row["burst"] or not row["priority"]:
            return f"{label}All fields are required."
        try:
            arrival = int(row["arrival"])
            burst = int(row["burst"])
            priority = int(row["priority"])
        except ValueError:
            return f"{label}Arrival, Burst, and Priority must be numeric."
        if arrival < 0:
            return f"{label}Arrival time cannot be negative."
        if burst <= 0:
            return f"{label}Burst time must be greater than 0."
        if priority < 1:
            return f"{label}Priority must be 1 or higher."
        return None

    def _pid_exists(self, pid):
        pid = str(pid).strip()
        for item in self.process_tree.get_children():
            if self.process_tree.item(item, "values")[0] == pid:
                return True
        return False

    def find_duplicate_pids(self, rows):
        seen = set()
        for row in rows:
            pid = row["pid"]
            if pid in seen:
                return pid
            seen.add(pid)
        return None

    def run_simulation(self):
        try:
            process_rows = self.get_process_list()
        except ValueError as error:
            messagebox.showerror("Validation Error", str(error))
            return

        processes = [Process(row["pid"], row["arrival"], row["burst"], row["priority"]) for row in process_rows]

        sjf_timeline, sjf_results = self._safe_run_scheduler(run_sjf, processes, "SJF")
        if sjf_timeline is None:
            return
        priority_timeline, priority_results = self._safe_run_scheduler(run_priority, processes, "Priority")
        if priority_timeline is None:
            return

        pid_colors = self._build_pid_colors([p.pid for p in processes])
        self.latest_sjf_timeline = sjf_timeline
        self.latest_priority_timeline = priority_timeline
        self.latest_pid_colors = pid_colors
        self._populate_results(self.sjf_result_tree, sjf_results, pid_colors)
        self._populate_results(self.priority_result_tree, priority_results, pid_colors)
        self._draw_gantt_sections(sjf_timeline, priority_timeline, pid_colors)
        self._update_comparison(sjf_results, priority_results)
        self._update_conclusion(sjf_results, priority_results)

    def _safe_run_scheduler(self, func, processes, name):
        try:
            result = func(processes, preemptive=True)
        except Exception as exc:
            messagebox.showerror("Simulation Error", f"{name} scheduler failed: {exc}")
            return None, None
        if not isinstance(result, tuple) or len(result) != 2:
            messagebox.showerror("Simulation Error", f"{name} scheduler returned invalid output.")
            return None, None
        return result

    def _build_pid_colors(self, pids):
        colors = {}
        unique_pids = sorted(set(pids), key=lambda pid: str(pid))
        for index, pid in enumerate(unique_pids):
            colors[pid] = self.COLOR_PALETTE[index % len(self.COLOR_PALETTE)]
        return colors

    def _populate_results(self, tree, results, pid_colors):
        for item in tree.get_children():
            tree.delete(item)
        for p in results:
            tree.insert(
                "",
                "end",
                values=(
                    p.pid,
                    p.arrival,
                    p.burst,
                    p.priority,
                    p.start,
                    p.finish,
                    p.waiting,
                    p.turnaround,
                    p.response_time,
                ),
                tags=(p.pid,),
            )
            tree.tag_configure(p.pid, background=pid_colors.get(p.pid, "#ffffff"), foreground="#000000")
        if results:
            avg_wait = sum(p.waiting for p in results) / len(results)
            avg_turn = sum(p.turnaround for p in results) / len(results)
            avg_response = sum(p.response_time for p in results) / len(results)
            tree.insert(
                "",
                "end",
                values=(
                    "Average",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    f"{avg_wait:.2f}",
                    f"{avg_turn:.2f}",
                    f"{avg_response:.2f}",
                ),
                tags=("avg",),
            )

    def _draw_gantt_sections(self, sjf_timeline=None, priority_timeline=None, pid_colors=None):
        sjf_timeline = sjf_timeline if sjf_timeline is not None else self.latest_sjf_timeline
        priority_timeline = priority_timeline if priority_timeline is not None else self.latest_priority_timeline
        pid_colors = pid_colors if pid_colors is not None else self.latest_pid_colors
        if sjf_timeline is not None and pid_colors is not None:
            draw_gantt_chart(self.sjf_canvas, sjf_timeline, pid_colors, "Shortest Job First")
        if priority_timeline is not None and pid_colors is not None:
            draw_gantt_chart(self.priority_canvas, priority_timeline, pid_colors, "Priority Scheduling")

    def _update_comparison(self, sjf_results, priority_results):
        sjf_average = self._compute_averages(sjf_results)
        priority_average = self._compute_averages(priority_results)

        for key, metric in (("waiting", "Average Waiting Time"), ("turnaround", "Average Turnaround Time"), ("response", "Average Response Time")):
            sjf_value = sjf_average[key]
            priority_value = priority_average[key]
            self.summary_labels[key]["SJF"].configure(text=f"{sjf_value:.2f}")
            self.summary_labels[key]["Priority"].configure(text=f"{priority_value:.2f}")
            if sjf_value < priority_value:
                self.summary_labels[key]["SJF"].configure(bg="#d6f5d6")
                self.summary_labels[key]["Priority"].configure(bg="#ffffff")
            elif priority_value < sjf_value:
                self.summary_labels[key]["Priority"].configure(bg="#d6f5d6")
                self.summary_labels[key]["SJF"].configure(bg="#ffffff")
            else:
                self.summary_labels[key]["SJF"].configure(bg="#ffffff")
                self.summary_labels[key]["Priority"].configure(bg="#ffffff")

    def _compute_averages(self, results):
        count = len(results)
        if count == 0:
            return {"waiting": 0.0, "turnaround": 0.0, "response": 0.0}
        return {
            "waiting": sum(p.waiting for p in results) / count,
            "turnaround": sum(p.turnaround for p in results) / count,
            "response": sum(p.response_time for p in results) / count,
        }

    def _update_conclusion(self, sjf_results, priority_results):
        sjf_avg = self._compute_averages(sjf_results)
        priority_avg = self._compute_averages(priority_results)
        lines = []

        if sjf_avg["waiting"] < priority_avg["waiting"]:
            lines.append("SJF has the lower average waiting time.")
        elif priority_avg["waiting"] < sjf_avg["waiting"]:
            lines.append("Priority Scheduling has the lower average waiting time.")
        else:
            lines.append("Both algorithms deliver the same average waiting time.")

        if sjf_avg["turnaround"] < priority_avg["turnaround"]:
            lines.append("SJF achieves a lower average turnaround time.")
        elif priority_avg["turnaround"] < sjf_avg["turnaround"]:
            lines.append("Priority Scheduling achieves a lower average turnaround time.")
        else:
            lines.append("Both algorithms achieve the same average turnaround time.")

        if sjf_avg["response"] < priority_avg["response"]:
            lines.append("SJF is more responsive on average.")
        elif priority_avg["response"] < sjf_avg["response"]:
            lines.append("Priority Scheduling responds faster on average.")
        else:
            lines.append("Both algorithms have equal average response time.")

        lines.append(
            "SJF focuses on efficiency by minimizing remaining burst time, while Priority Scheduling" \
            " prioritizes urgency. In practice, SJF often reduces waiting and turnaround, but Priority" \
            " Scheduling can better serve high-urgency tasks at the cost of possible lower-priority delays."
        )

        conclusion = "\n".join(lines)
        self.conclusion_text.configure(state="normal")
        self.conclusion_text.delete("1.0", "end")
        self.conclusion_text.insert("end", conclusion)
        self.conclusion_text.configure(state="disabled")

    def _on_process_table_double_click(self, event):
        if self.editing_entry is not None:
            self.editing_entry.destroy()
            self.editing_entry = None

        region = self.process_tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        row_id = self.process_tree.identify_row(event.y)
        column_id = self.process_tree.identify_column(event.x)
        if not row_id or not column_id:
            return

        column_index = int(column_id.replace("#", "")) - 1
        column_key = self.process_tree["columns"][column_index]
        bbox = self.process_tree.bbox(row_id, column=column_id)
        if not bbox:
            return

        value = self.process_tree.set(row_id, column_key)
        entry = ttk.Entry(self.process_tree)
        entry.insert(0, value)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.focus_set()

        def save_edit(event=None):
            new_value = entry.get().strip()
            if not new_value:
                messagebox.showerror("Edit Error", "Field cannot be empty.")
                return
            if column_key == "PID":
                if new_value != value and self._pid_exists(new_value):
                    messagebox.showerror("Edit Error", f"PID {new_value} already exists.")
                    return
            if column_key in ("Arrival", "Burst", "Priority"):
                try:
                    number = int(new_value)
                except ValueError:
                    messagebox.showerror("Edit Error", "Arrival, Burst, and Priority must be numeric.")
                    return
                if column_key == "Arrival" and number < 0:
                    messagebox.showerror("Edit Error", "Arrival time cannot be negative.")
                    return
                if column_key == "Burst" and number <= 0:
                    messagebox.showerror("Edit Error", "Burst time must be greater than 0.")
                    return
                if column_key == "Priority" and number < 1:
                    messagebox.showerror("Edit Error", "Priority must be 1 or higher.")
                    return
            self.process_tree.set(row_id, column=column_key, value=new_value)
            entry.destroy()
            self.editing_entry = None

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        self.editing_entry = entry

    def run(self):
        self.root.mainloop()
