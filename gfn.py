import requests
import tkinter as tk
from datetime import datetime
import threading

def fetch_data():
    url = "https://api.printedwaste.com/gfn/queue/cors/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

def format_last_updated(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

def get_color(queue_position):
    if queue_position > 200:
        return "red"
    elif 100 <= queue_position <= 199:
        return "yellow"
    else:
        return "green"

def update_ui():
    data = fetch_data()

    if not data:
        return

    labels = {
        "NP-AMS": "EU Northeast",
        "NP-FRK": "EU Central",
        "NP-PAR": "EU Southwest",
        "NP-LON": "EU West",
        "NP-STH": "EU Northwest",
        "NP-SOF": "EU Southeast",
    }

    aggregated_data = {}
    for server_id, info in data.items():
        for prefix, label in labels.items():
            if server_id.startswith(prefix):
                if label not in aggregated_data:
                    aggregated_data[label] = {
                        "QueuePosition": [],
                        "Last Updated": []
                    }
                aggregated_data[label]["QueuePosition"].append(info.get("QueuePosition"))
                aggregated_data[label]["Last Updated"].append(info.get("Last Updated"))

    for label, values in aggregated_data.items():
        aggregated_data[label] = {
            "QueuePosition": sum(values["QueuePosition"]) // len(values["QueuePosition"]),
            "Last Updated": max(values["Last Updated"])
        }

    sorted_data = sorted(aggregated_data.items(), key=lambda x: x[1]["QueuePosition"])

    seen_widgets = set()

    for label, info in sorted_data:
        queue_position = info["QueuePosition"]
        last_updated = format_last_updated(info["Last Updated"])
        widget_key = label
        seen_widgets.add(widget_key)

        if widget_key not in widget_map:
            bubble = tk.Frame(frame, bg="#2B2B2B", bd=2, relief="groove", highlightbackground="#555555", highlightthickness=1)
            bubble.pack(pady=5, padx=10, fill="x")
            bubble.config(borderwidth=0, highlightbackground="#1E1E1E", relief="flat")
            bubble.grid_propagate(False)

            tk.Label(bubble, text=label, fg=get_color(queue_position), bg="#2B2B2B", font=("Helvetica", 12, "bold"), anchor="w").pack(fill="x", pady=(5, 0))
            tk.Label(bubble, text=f"Queue: {queue_position}", fg="white", bg="#2B2B2B", font=("Helvetica", 10)).pack(anchor="w")
            tk.Label(bubble, text=f"Last Updated: {last_updated}", fg="gray", bg="#2B2B2B", font=("Helvetica", 9)).pack(anchor="w")

            widget_map[widget_key] = bubble

    for widget_key in list(widget_map.keys()):
        if widget_key not in seen_widgets:
            widget_map[widget_key].destroy()
            del widget_map[widget_key]

def periodic_update():
    update_ui()
    frame.after(5000, periodic_update)

root = tk.Tk()
root.title("GFNQueue")
root.configure(bg="#1E1E1E")
root.geometry("400x600")
root.configure(borderwidth=1, highlightbackground="#000000")

header = tk.Label(root, text="GFN EU Servers", bg="#1E1E1E", fg="white", font=("Helvetica", 16, "bold"))
header.pack(pady=10)

frame = tk.Frame(root, bg="#1E1E1E")
frame.pack(fill="both", expand=True, padx=10, pady=10)

widget_map = {}
periodic_update()

root.mainloop()
