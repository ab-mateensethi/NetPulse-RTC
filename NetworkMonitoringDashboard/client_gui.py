import base64
import os
import queue
import socket
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from protocol import recv_json, send_json


class MonitoringClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Collaborative Network Monitoring Dashboard")
        self.geometry("980x650")
        self.minsize(900, 580)
        self.sock = None
        self.buffer = b""
        self.inbox = queue.Queue()
        self.connected = False
        self.rooms = ["CPU", "Bandwidth", "Security"]
        self.configure(bg="#f7f7f7")
        self.build_ui()
        self.after(100, self.process_inbox)

    def build_ui(self):
        style = ttk.Style(self)
        style.configure("TButton", padding=6)
        style.configure("TLabel", background="#f7f7f7", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))

        top = ttk.Frame(self, padding=12)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Network Monitoring Dashboard", style="Header.TLabel").grid(row=0, column=0, sticky="w", columnspan=2)
        ttk.Label(top, text="Server").grid(row=1, column=0, sticky="w")
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="5050")
        self.name_var = tk.StringVar(value="Ali")
        ttk.Entry(top, textvariable=self.host_var, width=16).grid(row=1, column=1, padx=4)
        ttk.Entry(top, textvariable=self.port_var, width=7).grid(row=1, column=2, padx=4)
        ttk.Label(top, text="Name").grid(row=1, column=3, padx=(14, 0))
        ttk.Entry(top, textvariable=self.name_var, width=14).grid(row=1, column=4, padx=4)
        self.connect_btn = ttk.Button(top, text="Connect", command=self.connect)
        self.connect_btn.grid(row=1, column=5, padx=8)
        self.status_var = tk.StringVar(value="Offline")
        ttk.Label(top, textvariable=self.status_var).grid(row=1, column=6, sticky="w")

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        left = ttk.Frame(main, padding=8)
        right = ttk.Frame(main, padding=8)
        main.add(left, weight=3)
        main.add(right, weight=1)

        self.log = tk.Text(left, height=20, wrap=tk.WORD, bg="white", fg="#111111", font=("Consolas", 10))
        self.log.pack(fill=tk.BOTH, expand=True)
        self.log.tag_config("alert", foreground="#b42318", font=("Consolas", 10, "bold"))
        self.log.tag_config("emergency", foreground="#ffffff", background="#b42318", font=("Consolas", 10, "bold"))
        self.log.tag_config("private", foreground="#53389e")
        self.log.tag_config("room", foreground="#175cd3")
        self.log.tag_config("system", foreground="#475467")

        send_row = ttk.Frame(left)
        send_row.pack(fill=tk.X, pady=(8, 0))
        self.message_var = tk.StringVar()
        ttk.Entry(send_row, textvariable=self.message_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(send_row, text="Broadcast", command=self.send_broadcast).pack(side=tk.LEFT, padx=4)
        ttk.Button(send_row, text="Alert", command=self.send_alert).pack(side=tk.LEFT, padx=4)
        ttk.Button(send_row, text="Emergency", command=self.send_emergency).pack(side=tk.LEFT, padx=4)

        ttk.Label(right, text="Active Nodes", style="Header.TLabel").pack(anchor="w")
        self.nodes = tk.Listbox(right, height=8, exportselection=False)
        self.nodes.pack(fill=tk.X, pady=(4, 10))
        ttk.Button(right, text="Refresh Nodes", command=lambda: self.send({"type": "nodes_request"})).pack(fill=tk.X)

        room_box = ttk.LabelFrame(right, text="Group Rooms", padding=8)
        room_box.pack(fill=tk.X, pady=10)
        self.room_var = tk.StringVar(value="CPU")
        ttk.Combobox(room_box, values=self.rooms, textvariable=self.room_var, state="readonly").pack(fill=tk.X)
        ttk.Button(room_box, text="Join Room", command=self.join_room).pack(fill=tk.X, pady=(6, 2))
        ttk.Button(room_box, text="Leave Room", command=self.leave_room).pack(fill=tk.X, pady=2)
        ttk.Button(room_box, text="Send Room Message", command=self.room_message).pack(fill=tk.X, pady=2)

        private_box = ttk.LabelFrame(right, text="Private Chat", padding=8)
        private_box.pack(fill=tk.X, pady=10)
        self.private_to_var = tk.StringVar()
        ttk.Entry(private_box, textvariable=self.private_to_var).pack(fill=tk.X)
        ttk.Button(private_box, text="Send Private", command=self.private_message).pack(fill=tk.X, pady=(6, 0))

        file_box = ttk.LabelFrame(right, text="File / Log Sharing", padding=8)
        file_box.pack(fill=tk.X, pady=10)
        ttk.Button(file_box, text="Share File", command=self.share_file).pack(fill=tk.X)
        ttk.Button(file_box, text="Ping Latency", command=lambda: self.send({"type": "ping", "sent_at": time.time()})).pack(fill=tk.X, pady=(6, 0))

    def connect(self):
        if self.connected:
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host_var.get(), int(self.port_var.get())))
            send_json(self.sock, {"type": "hello", "name": self.name_var.get(), "hostname": socket.gethostname()})
            self.connected = True
            self.status_var.set("Online")
            self.connect_btn.configure(state=tk.DISABLED)
            threading.Thread(target=self.listen, daemon=True).start()
        except OSError as exc:
            messagebox.showerror("Connection failed", str(exc))

    def listen(self):
        while self.connected:
            try:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                self.buffer, messages = recv_json(self.buffer, chunk)
                for message in messages:
                    self.inbox.put(message)
            except OSError:
                break
        self.connected = False
        self.inbox.put({"type": "system", "text": "Disconnected from server."})

    def process_inbox(self):
        while not self.inbox.empty():
            self.handle_message(self.inbox.get())
        self.after(100, self.process_inbox)

    def handle_message(self, message):
        msg_type = message.get("type")
        if msg_type == "nodes":
            self.nodes.delete(0, tk.END)
            for node in message.get("nodes", []):
                rooms = ",".join(node.get("rooms", [])) or "-"
                self.nodes.insert(tk.END, f"{node['name']} | {node['ip']} | {node['hostname']} | {rooms}")
        elif msg_type == "event":
            level = message.get("level", "status")
            self.write(f"[{level.upper()}] {message['from']}: {message['text']}", level)
        elif msg_type == "room":
            self.write(f"[ROOM:{message['room']}] {message['from']}: {message['text']}", "room")
        elif msg_type == "private":
            self.write(f"[PRIVATE] {message['from']} -> {message['to']}: {message['text']}", "private")
        elif msg_type == "file":
            self.write(f"[FILE] {message['from']} shared {message['filename']} ({message['size']} bytes)", "alert")
        elif msg_type == "pong":
            latency = (time.time() - float(message.get("sent_at", time.time()))) * 1000
            self.write(f"[METRIC] Round-trip latency: {latency:.1f} ms", "system")
        elif msg_type == "rooms":
            self.rooms = message.get("rooms", self.rooms)
        else:
            self.write(f"[SYSTEM] {message.get('text', message)}", "system")

    def write(self, text, tag=None):
        self.log.insert(tk.END, time.strftime("[%H:%M:%S] ") + text + "\n", tag)
        self.log.see(tk.END)

    def send(self, payload):
        if not self.connected:
            messagebox.showwarning("Offline", "Connect to the server first.")
            return
        send_json(self.sock, payload)

    def current_text(self):
        return self.message_var.get().strip()

    def send_broadcast(self):
        self.send({"type": "broadcast", "text": self.current_text()})
        self.message_var.set("")

    def send_alert(self):
        self.send({"type": "alert", "text": self.current_text()})
        self.message_var.set("")

    def send_emergency(self):
        self.bell()
        self.send({"type": "emergency", "text": self.current_text() or "Critical network threshold breached."})
        self.message_var.set("")

    def join_room(self):
        self.send({"type": "join_room", "room": self.room_var.get()})

    def leave_room(self):
        self.send({"type": "leave_room", "room": self.room_var.get()})

    def room_message(self):
        self.send({"type": "room_message", "room": self.room_var.get(), "text": self.current_text()})
        self.message_var.set("")

    def private_message(self):
        self.send({"type": "private", "to": self.private_to_var.get().strip(), "text": self.current_text()})
        self.message_var.set("")

    def share_file(self):
        path = filedialog.askopenfilename(title="Select log, screenshot, or short video")
        if not path:
            return
        with open(path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("ascii")
        self.send({"type": "file", "filename": os.path.basename(path), "data": encoded})


if __name__ == "__main__":
    MonitoringClientGUI().mainloop()
