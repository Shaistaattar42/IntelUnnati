import tkinter as tk
from tkinter import ttk
import time
import psutil

def read_power():
    battery = psutil.sensors_battery()
    if battery:
        return battery.power_plugged, battery.percent
    return None, None

def read_cpu_performance(percentage):
    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage should be between 0 and 100")
    cpu_percent = percentage
    cpu_freq = psutil.cpu_freq()
    cpu_power = None
    if cpu_freq is not None:
        cpu_power = cpu_percent / 100.0 * cpu_freq.current / 1000.0
    return cpu_percent, cpu_freq.current / 1000.0 if cpu_freq else None, cpu_power

def calculate_tdp():
    cpu_tdp_watts = 35
    memory_tdp_watts = 8
    nic_tdp_watts = 5
    total_tdp_watts = cpu_tdp_watts + memory_tdp_watts + nic_tdp_watts
    return total_tdp_watts

def read_memory():
    mem = psutil.virtual_memory()
    used_memory = mem.used / (1024 ** 3)
    available_memory = mem.available / (1024 ** 3)
    return used_memory, available_memory

def get_memory_usage():
    memory = psutil.virtual_memory()
    total_memory = memory.total
    used_memory = memory.used
    remaining_memory = total_memory - used_memory
    return total_memory, used_memory, remaining_memory

def bytes_to_gb(bytes):
    return bytes / (1024**3)

def read_nic_info():
    nic_info = psutil.net_if_addrs()
    nic_details = {}
    for interface, addrs in nic_info.items():
        nic_details[interface] = []
        for addr in addrs:
            nic_details[interface].append({
                'family': addr.family.name,
                'address': addr.address,
                'netmask': addr.netmask,
                'broadcast': addr.broadcast
            })
    return nic_details

def read_iris_graphics():
    gpu_info = {
        'gpu_load': 45.6,
        'gpu_memory_total': 2048 * 1024 * 1024,
        'gpu_memory_used': 1024 * 1024 * 1024,
    }
    gpu_load = gpu_info['gpu_load']
    gpu_memory_total = gpu_info['gpu_memory_total']
    gpu_memory_used = gpu_info['gpu_memory_used']
    return gpu_load, bytes_to_gb(gpu_memory_total), bytes_to_gb(gpu_memory_used)

def read_network_traffic():
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv

def start_stopwatch():
    global stopwatch_running, start_time
    stopwatch_running = True
    start_time = time.time()
    update_stopwatch()

def stop_stopwatch():
    global stopwatch_running
    stopwatch_running = False

def update_stopwatch():
    if stopwatch_running:
        elapsed_time = time.time() - start_time
        elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        stopwatch_label.config(text=f"Elapsed Time: {elapsed_time_str}")
        root.after(1000, update_stopwatch)

def start_monitoring():
    global monitoring
    monitoring = True
    update_gui()

def stop_monitoring():
    global monitoring
    monitoring = False

def update_gui():
    if monitoring:
        power_plugged, battery_percent = read_power()
        if power_plugged is not None:
            power_status = "Plugged In" if power_plugged else "On Battery"
            power_label.config(text=f"Power Status: {power_status}, Battery: {battery_percent}%")
        else:
            power_label.config(text="Failed to retrieve power information.")

        try:
            percentage = float(cpu_percentage_entry.get())
            if percentage < 0 or percentage > 100:
                cpu_label.config(text="Error: Percentage should be between 0 and 100")
            else:
                cpu_percent, cpu_frequency, cpu_power = read_cpu_performance(percentage)
                cpu_label.config(text=f"Desired CPU Usage: {percentage}%\nCPU Frequency: {cpu_frequency:.2f} GHz\nEstimated CPU Power Consumption: {cpu_power:.2f} Watts")
        except ValueError:
            cpu_label.config(text="Error: Please enter a valid percentage.")

        total_memory, used_memory, remaining_memory = get_memory_usage()
        total_memory_gb = bytes_to_gb(total_memory)
        used_memory_gb = bytes_to_gb(used_memory)
        remaining_memory_gb = bytes_to_gb(remaining_memory)
        memory_label.config(text=f"Total Memory: {total_memory_gb:.2f} GB\nUsed Memory: {used_memory_gb:.2f} GB\nRemaining Memory: {remaining_memory_gb:.2f} GB")

        gpu_load, gpu_memory_total, gpu_memory_used = read_iris_graphics()
        gpu_label.config(text=f"Iris Graphics Load: {gpu_load:.2f}%\nIris Graphics Total Memory: {gpu_memory_total:.2f} GB\nIris Graphics Used Memory: {gpu_memory_used:.2f} GB")

        curr_sent, curr_recv = read_network_traffic()
        sent_bytes = curr_sent - prev_sent[0]
        recv_bytes = curr_recv - prev_recv[0]
        prev_sent[0], prev_recv[0] = curr_sent, curr_recv
        sent_gb = bytes_to_gb(sent_bytes)
        recv_gb = bytes_to_gb(recv_bytes)
        network_label.config(text=f"Network Traffic: Sent = {sent_gb:.6f} GB, Received = {recv_gb:.6f} GB")

        nic_details = read_nic_info()
        nic_info_text_left = ""
        nic_info_text_right = ""

        for interface, addrs in nic_details.items():
            nic_info_text = f"Interface: {interface}\n"
            for addr in addrs:
                nic_info_text += f"  {addr['family']} Address: {addr['address']}\n"
                if addr['netmask']:
                    nic_info_text += f"  Netmask: {addr['netmask']}\n"
                if addr['broadcast']:
                    nic_info_text += f"  Broadcast: {addr['broadcast']}\n"
            nic_info_text += "\n"
            if len(nic_info_text_left.splitlines()) <= len(nic_info_text_right.splitlines()):
                nic_info_text_left += nic_info_text
            else:
                nic_info_text_right += nic_info_text

        nic_label_left.config(text=nic_info_text_left)
        nic_label_right.config(text=nic_info_text_right)

        center_frame_contents()

        root.after(2000, update_gui)

def center_frame_contents():
    second_frame.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()

    second_frame_width = second_frame.winfo_width()
    second_frame_height = second_frame.winfo_height()

    x = max(0, (width - second_frame_width) // 2)
    y = max(0, (height - second_frame_height) // 2)

    canvas.coords(second_frame_canvas, x, y)

# Initialize variables
prev_sent = [0]
prev_recv = [0]
stopwatch_running = False
monitoring = False

# Create the main window
root = tk.Tk()
root.title("System Telemetry")

# Layout setup
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

second_frame = tk.Frame(canvas)
second_frame_canvas = canvas.create_window((0, 0), window=second_frame, anchor="nw")

font_size = 12

cpu_percentage_label = ttk.Label(second_frame, text="Desired CPU Utilization Percentage (0-100):", font=("Arial", font_size))
cpu_percentage_label.pack()

cpu_percentage_entry = ttk.Entry(second_frame, font=("Arial", font_size))
cpu_percentage_entry.pack()

power_label = ttk.Label(second_frame, text="", font=("Arial", font_size))
power_label.pack()

cpu_label = ttk.Label(second_frame, text="", font=("Arial", font_size))
cpu_label.pack()

memory_label = ttk.Label(second_frame, text="", font=("Arial", font_size))
memory_label.pack()

gpu_label = ttk.Label(second_frame, text="", font=("Arial", font_size))
gpu_label.pack()

network_label = ttk.Label(second_frame, text="", font=("Arial", font_size))
network_label.pack()

nic_frame = tk.Frame(second_frame)
nic_frame.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

nic_label_left = ttk.Label(nic_frame, text="", font=("Arial", font_size))
nic_label_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

nic_label_right = ttk.Label(nic_frame, text="", font=("Arial", font_size))
nic_label_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, pady=10)

button_style = {"font": ("Arial", font_size), "bg": "black", "fg": "white", "padx": 10, "pady": 10}

start_button = tk.Button(button_frame, text="Start Calculating", **button_style, command=lambda: [start_monitoring(), start_stopwatch()])
start_button.pack(side="left", padx=5)

stop_button = tk.Button(button_frame, text="Stop Calculating", **button_style, command=lambda: [stop_monitoring(), stop_stopwatch()])
stop_button.pack(side="right", padx=5)

stopwatch_frame = tk.Frame(button_frame)
stopwatch_frame.pack(fill=tk.X, pady=10)

stopwatch_label = ttk.Label(stopwatch_frame, text="00:00:00", font=("Arial", 12))
stopwatch_label.pack(side="left", padx=(600, 5))

center_frame_contents()

root.mainloop()
