import argparse
import base64
import os
import socket
import threading
import time

from protocol import recv_json, send_json


class CLIClient:
    def __init__(self, host: str, port: int, name: str):
        self.host = host
        self.port = port
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = b""
        self.running = True

    def connect(self) -> None:
        self.sock.connect((self.host, self.port))
        send_json(
            self.sock,
            {"type": "hello", "name": self.name, "hostname": socket.gethostname()},
        )
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self) -> None:
        while self.running:
            try:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                self.buffer, messages = recv_json(self.buffer, chunk)
                for message in messages:
                    self.print_message(message)
            except OSError:
                break
        self.running = False

    def print_message(self, message) -> None:
        msg_type = message.get("type")
        if msg_type == "nodes":
            print("\n[ACTIVE NODES]")
            for node in message.get("nodes", []):
                rooms = ", ".join(node.get("rooms", [])) or "no rooms"
                print(f" - {node['name']} | {node['ip']} | {node['hostname']} | {rooms}")
        elif msg_type == "event":
            print(f"[{message.get('level', 'status').upper()}] {message['from']}: {message['text']}")
        elif msg_type == "room":
            print(f"[ROOM:{message['room']}] {message['from']}: {message['text']}")
        elif msg_type == "private":
            print(f"[PRIVATE] {message['from']} -> {message['to']}: {message['text']}")
        elif msg_type == "file":
            print(f"[FILE] {message['from']} shared {message['filename']} ({message['size']} bytes)")
        elif msg_type == "pong":
            latency = (time.time() - float(message.get("sent_at", time.time()))) * 1000
            print(f"[METRIC] Round-trip latency: {latency:.1f} ms")
        else:
            print(f"[SYSTEM] {message.get('text', message)}")

    def repl(self) -> None:
        print("Commands: /alert text | /emergency text | /join room | /leave room | /room room text")
        print("          /pm name text | /file path | /nodes | /ping | /quit")
        while self.running:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                continue
            if line == "/quit":
                break
            self.handle_command(line)
        self.running = False
        self.sock.close()

    def handle_command(self, line: str) -> None:
        if line.startswith("/alert "):
            send_json(self.sock, {"type": "alert", "text": line[7:]})
        elif line.startswith("/emergency "):
            send_json(self.sock, {"type": "emergency", "text": line[11:]})
        elif line.startswith("/join "):
            send_json(self.sock, {"type": "join_room", "room": line[6:]})
        elif line.startswith("/leave "):
            send_json(self.sock, {"type": "leave_room", "room": line[7:]})
        elif line.startswith("/room "):
            _, room, text = line.split(" ", 2)
            send_json(self.sock, {"type": "room_message", "room": room, "text": text})
        elif line.startswith("/pm "):
            _, target, text = line.split(" ", 2)
            send_json(self.sock, {"type": "private", "to": target, "text": text})
        elif line.startswith("/file "):
            self.send_file(line[6:].strip('"'))
        elif line == "/nodes":
            send_json(self.sock, {"type": "nodes_request"})
        elif line == "/ping":
            send_json(self.sock, {"type": "ping", "sent_at": time.time()})
        else:
            send_json(self.sock, {"type": "broadcast", "text": line})

    def send_file(self, path: str) -> None:
        if not os.path.exists(path):
            print(f"[ERROR] File not found: {path}")
            return
        with open(path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("ascii")
        send_json(
            self.sock,
            {"type": "file", "filename": os.path.basename(path), "data": encoded},
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI client for network monitoring dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    client = CLIClient(args.host, args.port, args.name)
    client.connect()
    client.repl()


if __name__ == "__main__":
    main()
