import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.ttk import Progressbar

# =========================
# PROCESS MANAGEMENT CLASSES
# =========================
class Process:
    def __init__(self, pid, name, burst_time, arrival_time=0, priority=1, queue_level=1):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.arrival_time = arrival_time
        self.priority = priority
        self.queue_level = queue_level
        self.completed = False

class Scheduler:
    def __init__(self):
        self.processes = []
        self.output = ""
        self.timeline = []

    def reset(self):
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.completed = False
        self.output = ""
        self.timeline = []

    def fcfs(self):
        self.reset()
        self.processes.sort(key=lambda p: p.arrival_time)
        time_elapsed = 0
        for p in self.processes:
            start = time_elapsed
            time_elapsed += p.burst_time
            self.output += f"{p.name} | Start: {start}, End: {time_elapsed}\n"
            self.timeline.append((p.name, start, time_elapsed))

    def sjf(self):
        self.reset()
        time_elapsed = 0
        completed = 0
        n = len(self.processes)
        while completed < n:
            ready = [p for p in self.processes if not p.completed and p.arrival_time <= time_elapsed]
            if ready:
                p = min(ready, key=lambda x: x.burst_time)
                start = time_elapsed
                time_elapsed += p.burst_time
                p.completed = True
                completed += 1
                self.output += f"{p.name} | Start: {start}, End: {time_elapsed}\n"
                self.timeline.append((p.name, start, time_elapsed))
            else:
                time_elapsed += 1

    def priority_scheduling(self):
        self.reset()
        time_elapsed = 0
        completed = 0
        n = len(self.processes)
        while completed < n:
            ready = [p for p in self.processes if not p.completed and p.arrival_time <= time_elapsed]
            if ready:
                p = min(ready, key=lambda x: x.priority)
                start = time_elapsed
                time_elapsed += p.burst_time
                p.completed = True
                completed += 1
                self.output += f"{p.name} | Start: {start}, End: {time_elapsed}\n"
                self.timeline.append((p.name, start, time_elapsed))
            else:
                time_elapsed += 1

    def round_robin(self, quantum=2):
        self.reset()
        time_elapsed = 0
        queue = self.processes[:]
        while any(p.remaining_time > 0 for p in queue):
            for p in queue:
                if p.remaining_time > 0:
                    start = time_elapsed
                    exec_time = min(quantum, p.remaining_time)
                    time_elapsed += exec_time
                    p.remaining_time -= exec_time
                    self.output += f"{p.name} | Start: {start}, End: {time_elapsed}\n"
                    self.timeline.append((p.name, start, time_elapsed))

    def srtf(self):
        self.reset()
        time_elapsed = 0
        completed = 0
        n = len(self.processes)
        while completed < n:
            ready = [p for p in self.processes if not p.completed and p.arrival_time <= time_elapsed]
            if ready:
                p = min(ready, key=lambda x: x.remaining_time)
                p.remaining_time -= 1
                self.timeline.append((p.name, time_elapsed, time_elapsed+1))
                time_elapsed += 1
                if p.remaining_time == 0:
                    p.completed = True
                    completed += 1
            else:
                time_elapsed += 1

    def multilevel_queue(self):
        self.reset()
        q1 = [p for p in self.processes if p.queue_level == 1]
        q2 = [p for p in self.processes if p.queue_level == 2]
        self.processes = q1 + q2
        self.round_robin(2)
        self.output += "\n-- Queue 2 (FCFS) --\n"
        self.processes = q2
        self.fcfs()

# =========================
# MEMORY MANAGEMENT CLASSES
# =========================
class MemoryBlock:
    def __init__(self, start, size, is_free=True, process_id=None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_id = process_id

class MemoryManager:
    def __init__(self, total_size):
        self.total_size = total_size
        self.blocks = [MemoryBlock(0, total_size)]

    def allocate(self, process_id, process_size, algo='First Fit'):
        candidates = [b for b in self.blocks if b.is_free and b.size >= process_size]
        if not candidates:
            return False

        if algo == 'Best Fit':
            candidates.sort(key=lambda b: b.size)
        elif algo == 'Worst Fit':
            candidates.sort(key=lambda b: -b.size)

        selected = candidates[0]
        index = self.blocks.index(selected)
        allocated = MemoryBlock(selected.start, process_size, False, process_id)
        remaining = selected.size - process_size

        if remaining > 0:
            leftover = MemoryBlock(selected.start + process_size, remaining)
            self.blocks[index:index+1] = [allocated, leftover]
        else:
            self.blocks[index] = allocated

        return True

    def get_memory_table(self):
        return [{
            'Start': b.start,
            'Size': b.size,
            'Free': b.is_free,
            'PID': b.process_id if not b.is_free else '-'
        } for b in self.blocks]

# =========================
# FILE MANAGEMENT CLASSES
# =========================
class File:
    def __init__(self, name, size):
        self.name = name
        self.size = size

class FileManager:
    def __init__(self):
        self.files = []

    def create_file(self, name, size):
        if any(f.name == name for f in self.files):
            return False
        self.files.append(File(name, size))
        return True

    def delete_file(self, name):
        for f in self.files:
            if f.name == name:
                self.files.remove(f)
                return True
        return False

    def list_files(self):
        return [(f.name, f.size) for f in self.files]

class VirtualOSManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual OS Manager")
        self.scheduler = Scheduler()
        self.memory_manager = MemoryManager(1000)
        self.file_manager = FileManager()

        # === Process Management Frame ===
        proc_frame = ttk.LabelFrame(root, text="Process Management")
        proc_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(proc_frame, text="PID").grid(row=0, column=0)
        self.pid_entry = ttk.Entry(proc_frame)
        self.pid_entry.grid(row=0, column=1)

        ttk.Label(proc_frame, text="Name").grid(row=1, column=0)
        self.name_entry = ttk.Entry(proc_frame)
        self.name_entry.grid(row=1, column=1)

        ttk.Label(proc_frame, text="Burst Time").grid(row=2, column=0)
        self.bt_entry = ttk.Entry(proc_frame)
        self.bt_entry.grid(row=2, column=1)

        ttk.Label(proc_frame, text="Arrival Time").grid(row=3, column=0)
        self.at_entry = ttk.Entry(proc_frame)
        self.at_entry.grid(row=3, column=1)

        ttk.Label(proc_frame, text="Priority").grid(row=4, column=0)
        self.priority_entry = ttk.Entry(proc_frame)
        self.priority_entry.grid(row=4, column=1)

        ttk.Label(proc_frame, text="Queue Level").grid(row=5, column=0)
        self.ql_entry = ttk.Entry(proc_frame)
        self.ql_entry.grid(row=5, column=1)

        self.algo_choice = ttk.Combobox(proc_frame, values=["FCFS", "SJF", "Priority", "Round Robin", "SRTF", "Multilevel Queue"])
        self.algo_choice.grid(row=6, column=0, columnspan=2)
        self.algo_choice.set("FCFS")

        ttk.Button(proc_frame, text="Add Process", command=self.add_process).grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Button(proc_frame, text="Run Scheduler", command=self.run_scheduler).grid(row=8, column=0, columnspan=2, pady=5)

        # === Memory Management Frame ===
        mem_frame = ttk.LabelFrame(root, text="Memory Management")
        mem_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(mem_frame, text="PID").grid(row=0, column=0)
        self.mem_pid = ttk.Entry(mem_frame)
        self.mem_pid.grid(row=0, column=1)

        ttk.Label(mem_frame, text="Size").grid(row=1, column=0)
        self.mem_size = ttk.Entry(mem_frame)
        self.mem_size.grid(row=1, column=1)

        self.mem_algo = ttk.Combobox(mem_frame, values=["First Fit", "Best Fit", "Worst Fit"])
        self.mem_algo.grid(row=2, column=0, columnspan=2)
        self.mem_algo.set("First Fit")

        ttk.Button(mem_frame, text="Allocate", command=self.allocate_memory).grid(row=3, column=0, columnspan=2)
        ttk.Button(mem_frame, text="Show Table", command=self.show_memory).grid(row=4, column=0, columnspan=2)

        # === File Management Frame ===
        file_frame = ttk.LabelFrame(root, text="File Management")
        file_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

        ttk.Label(file_frame, text="Name").grid(row=0, column=0)
        self.file_name = ttk.Entry(file_frame)
        self.file_name.grid(row=0, column=1)

        ttk.Label(file_frame, text="Size").grid(row=1, column=0)
        self.file_size = ttk.Entry(file_frame)
        self.file_size.grid(row=1, column=1)

        ttk.Button(file_frame, text="Create File", command=self.create_file).grid(row=2, column=0)
        ttk.Button(file_frame, text="Delete File", command=self.delete_file).grid(row=2, column=1)
        ttk.Button(file_frame, text="Show Files", command=self.show_files).grid(row=3, column=0, columnspan=2)

        # === Output Box ===
        self.output_text = scrolledtext.ScrolledText(root, width=60, height=30)
        self.output_text.grid(row=0, column=1, rowspan=5, padx=10, pady=10)

    def add_process(self):
        try:
            p = Process(
                self.pid_entry.get(),
                self.name_entry.get(),
                int(self.bt_entry.get()),
                int(self.at_entry.get()),
                int(self.priority_entry.get()),
                int(self.ql_entry.get())
            )
            self.scheduler.processes.append(p)
            messagebox.showinfo("Success", "Process added")
        except:
            messagebox.showerror("Error", "Invalid input")

    def run_scheduler(self):
        algo = self.algo_choice.get()
        getattr(self.scheduler, algo.lower().replace(" ", "_"))()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, self.scheduler.output)

    def allocate_memory(self):
        pid = self.mem_pid.get()
        try:
            size = int(self.mem_size.get())
            algo = self.mem_algo.get()
            success = self.memory_manager.allocate(pid, size, algo)
            if success:
                messagebox.showinfo("Success", "Memory Allocated")
            else:
                messagebox.showerror("Error", "Allocation Failed")
        except:
            messagebox.showerror("Error", "Enter valid size")

    def show_memory(self):
        table = self.memory_manager.get_memory_table()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Start\tSize\tFree\tPID\n")
        for b in table:
            self.output_text.insert(tk.END, f"{b['Start']}\t{b['Size']}\t{'Yes' if b['Free'] else 'No'}\t{b['PID']}\n")

    def create_file(self):
        try:
            name = self.file_name.get()
            size = int(self.file_size.get())
            if self.file_manager.create_file(name, size):
                messagebox.showinfo("Success", "File Created")
            else:
                messagebox.showerror("Error", "Already Exists")
        except:
            messagebox.showerror("Error", "Invalid input")

    def delete_file(self):
        name = self.file_name.get()
        if self.file_manager.delete_file(name):
            messagebox.showinfo("Deleted", "File Deleted")
        else:
            messagebox.showerror("Error", "File Not Found")

    def show_files(self):
        files = self.file_manager.list_files()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "File Name\tSize\n")
        for name, size in files:
            self.output_text.insert(tk.END, f"{name}\t{size}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualOSManagerGUI(root)
    root.mainloop()