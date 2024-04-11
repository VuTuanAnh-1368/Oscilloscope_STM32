import tkinter as tk
from tkinter import ttk
import serial
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque

serial_thread = None
serial_port = None
stop_thread = False
data_queue = deque(maxlen=100)  

root = tk.Tk()
root.title("Oscilloscope")

frame_ports = ttk.Labelframe(root, text="Port Settings")
frame_ports.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

def on_port_selected(event):
    selected_port = combo_ports.get()
    combo_ports.set(selected_port)

def on_baud_selected(event):
    selected_baud = combo_baud.get()
    combo_ports.set(selected_baud)

combo_ports = ttk.Combobox(frame_ports, values=["COM1", "COM2", "COM3","COM4", "COM5", "COM6","COM7", "COM8", "COM9"])
combo_ports.pack(side=tk.LEFT, padx=5, pady=5)
combo_ports.set("COM7")
combo_ports.bind("<<ComboboxSelected>>", on_port_selected) 

combo_baud = ttk.Combobox(frame_ports, values=[9600, 115200, 230400])
combo_baud.pack(side=tk.LEFT, padx=5, pady=5)
combo_baud.set("9600")
combo_baud.bind("<<ComboboxSelected>>", on_baud_selected) 

button_connect = ttk.Button(frame_ports, text="Connect")
button_connect.pack(side=tk.LEFT, padx=5, pady=5)

button_disconnect = ttk.Button(frame_ports, text="Disconnect")
button_disconnect.pack(side=tk.LEFT, padx=5, pady=5)

fig = Figure(figsize=(10, 6))
ax = fig.add_subplot(111)
line, = ax.plot([], [], lw=2) 
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0)


initial_time_per_div = 0.02
initial_volts_per_div = 1.0

current_time_per_div = initial_time_per_div
current_volts_per_div = initial_volts_per_div

label_volts_div = ttk.Label(frame_ports, text="Volts/Div:")
label_volts_div.pack(side=tk.LEFT, padx=5, pady=5)
volts_div_entry = ttk.Entry(frame_ports, textvariable=tk.StringVar(value=str(initial_volts_per_div)))
volts_div_entry.pack(side=tk.LEFT, padx=5, pady=5)

label_time_div = ttk.Label(frame_ports, text="Time/Div:")
label_time_div.pack(side=tk.LEFT, padx=5, pady=5)
time_div_entry = ttk.Entry(frame_ports, textvariable=tk.StringVar(value=str(initial_time_per_div)))
time_div_entry.pack(side=tk.LEFT, padx=5, pady=5)


def update_plot():
    global current_time_per_div, current_volts_per_div
    try:
        new_time_per_div = float(time_div_entry.get())
        new_volts_per_div = float(volts_div_entry.get())

        if new_time_per_div != current_time_per_div or new_volts_per_div != current_volts_per_div:
            current_time_per_div = new_time_per_div
            current_volts_per_div = new_volts_per_div
            ax.set_xlim(0, len(data_queue) * current_time_per_div)
            ax.set_ylim(0, max(data_queue) + current_volts_per_div)

        ax.cla()
        ax.grid(True)
        ax.plot(range(len(data_queue)), data_queue, 'b-')
        ax.set_xlim(0, len(data_queue) * current_time_per_div)
        ax.set_ylim(0, 10*current_volts_per_div)

        canvas.draw()

    except ValueError as e:
        print("Error updating plot:", e)

def read_serial_data(ser, data_queue):
    global stop_thread
    while not stop_thread:
        if ser.in_waiting:
            data = ser.readline().decode('utf-8').strip()
            try:
                data_point = float(data) 
                data_queue.append(data_point) 
            except ValueError:
                pass  

def on_connect():
    global serial_thread, serial_port, stop_thread
    if serial_port and serial_port.is_open:
        return 
    port = combo_ports.get()
    baudrate = combo_baud.get()
    try:
        serial_port = serial.Serial(port, baudrate=int(baudrate), timeout=1)
        stop_thread = False
        serial_thread = threading.Thread(target=read_serial_data, args=(serial_port, data_queue))
        serial_thread.start()
        print("Started Serial Thread")
    except serial.SerialException as e:
        print("Serial Exception:", e)

def on_disconnect():
    global serial_port, stop_thread, serial_thread
    if serial_port and serial_port.is_open:
        stop_thread = True
        if serial_thread.is_alive():
            serial_thread.join()
        serial_port.close()
        print("Serial Port Disconnected")

button_connect.config(command=on_connect)
button_disconnect.config(command=on_disconnect)

def refresh_plot():
    update_plot()
    root.after(50, refresh_plot) 

refresh_plot()

root.mainloop()