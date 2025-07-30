import tkinter as tk
from tkinter import Canvas
import math, threading, time
import speedtest

# ====== COLORS ======
BG_COLOR = "#0a0a0a"
DL_COLOR = "#00ff44"
UL_COLOR = "#0099ff"
TEXT_COLOR = "#ffffff"
ARC_COLORS = ["#00ff44", "#ffff00", "#ff3333"]  # Green → Yellow → Red

# ====== SPEED TEST THREAD ======
def run_speed_test():
    btn.config(state="disabled")
    result_label.config(text="Testing Download...")
    threading.Thread(target=measure_speed).start()

def measure_speed():
    st = speedtest.Speedtest()
    st.get_best_server()

    download = run_live_test(st.download, update_download_gauge)
    result_label.config(text=f"Download: {download:.2f} Mbps\nTesting Upload...")

    upload = run_live_test(st.upload, update_upload_gauge)
    ping = st.results.ping

    result_label.config(text=f"Download: {download:.2f} Mbps\nUpload: {upload:.2f} Mbps\nPing: {ping:.0f} ms")
    btn.config(state="normal")

def run_live_test(func, update_callback):
    start_time = time.time()
    bytes_tracker = [0]

    def hook(i, total, *args, **kwargs):
        elapsed = time.time() - start_time
        bytes_tracker[0] += 262144
        mbps = (bytes_tracker[0] * 8 / 1_000_000) / elapsed if elapsed > 0 else 0
        update_callback(min(mbps, 200))

    func(callback=hook)
    elapsed = time.time() - start_time
    mbps_final = (bytes_tracker[0] * 8 / 1_000_000) / elapsed if elapsed > 0 else 0
    return mbps_final

# ====== DRAWING INSTRUMENT CLUSTER GAUGE ======
def draw_cluster_gauge(canvas, cx, cy, r, speed_value, color, label):
    canvas.delete(label)

    # Background
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=BG_COLOR, outline="#222222", width=4, tags=label)

    # Color arcs (0–60 = green, 60–120 = yellow, 120–200 = red)
    for idx, (start_val, end_val) in enumerate([(0, 60), (60, 120), (120, 200)]):
        start_angle = 180 - (start_val * 0.9)
        end_angle = 180 - (end_val * 0.9)
        canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=end_angle, extent=start_angle-end_angle,
                          style="arc", outline=ARC_COLORS[idx], width=15, tags=label)

    # Tick marks
    for i in range(0, 201, 20):
        angle = math.radians(180 - i * 0.9)
        x1 = cx + (r-20) * math.cos(angle)
        y1 = cy - (r-20) * math.sin(angle)
        x2 = cx + (r-40) * math.cos(angle)
        y2 = cy - (r-40) * math.sin(angle)
        canvas.create_line(x1, y1, x2, y2, fill="#cccccc", width=2, tags=label)
        if i % 40 == 0:
            tx = cx + (r-60) * math.cos(angle)
            ty = cy - (r-60) * math.sin(angle)
            canvas.create_text(tx, ty, text=str(i), fill="#eeeeee", font=("Arial", 10, "bold"), tags=label)

    # Needle
    angle = math.radians(180 - (speed_value * 0.9))
    x = cx + (r-50) * math.cos(angle)
    y = cy - (r-50) * math.sin(angle)
    canvas.create_line(cx, cy, x, y, fill=color, width=6, tags=label)

    # Needle center hub
    canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill="#ffffff", outline="#666666", tags=label)

    # Speed Text
    canvas.create_text(cx, cy+80, text=f"{speed_value:.1f} Mbps", fill=color,
                       font=("DS-Digital", 16, "bold"), tags=label)

# ====== LIVE UPDATE CALLBACKS ======
def update_download_gauge(speed):
    draw_cluster_gauge(canvas, 220, 300, 150, speed, DL_COLOR, "download")

def update_upload_gauge(speed):
    draw_cluster_gauge(canvas, 480, 300, 150, speed, UL_COLOR, "upload")

# ====== UI SETUP ======
root = tk.Tk()
root.title("Instrument Cluster Speed Test")
root.geometry("750x720")
root.config(bg=BG_COLOR)

canvas = Canvas(root, width=750, height=500, bg=BG_COLOR, highlightthickness=0)
canvas.pack(pady=20)

result_label = tk.Label(root, text="Press Start to Test", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 16))
result_label.pack(pady=10)

btn = tk.Button(root, text="Start Speed Test", command=run_speed_test,
                bg=DL_COLOR, fg=BG_COLOR, font=("Segoe UI", 16, "bold"), width=20, height=2)
btn.pack(pady=20)

draw_cluster_gauge(canvas, 220, 300, 150, 0, DL_COLOR, "download")
draw_cluster_gauge(canvas, 480, 300, 150, 0, UL_COLOR, "upload")

root.mainloop()
