import argparse
import base64
import os
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Set

from protocol import peer_label, recv_json, send_json


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5050
ROOMS = ("CPU", "Bandwidth", "Security")


@dataclass
class ClientInfo:
    sock: socket.socket
    name: str
    hostname: str
    ip: str
    connected_at: float = field(default_factory=time.time)
    rooms: Set[str] = field(default_factory=set)


class MonitoringServer:
    def __init__(self, host: str, port: int, upload_dir: str = "server_received"):
        self.host = host
        self.port = port
        self.upload_dir = upload_dir
        self.clients: Dict[socket.socket, ClientInfo] = {}
        self.lock = threading.RLock()
        self.running = threading.Event()
        os.makedirs(self.upload_dir, exist_ok=True)

    def start(self) -> None:
        self.running.set()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            print(f"[SERVER] Real-time monitoring server listening on {self.host}:{self.port}")
            print("[SERVER] Waiting for clients. Press Ctrl+C to stop.")
            while self.running.is_set():
                try:
                    client_sock, address = server.accept()
                except OSError:
                    break
                threading.Thread(
                    target=self.handle_client,
                    args=(client_sock, address),
                    daemon=True,
                ).start()

    def handle_client(self, sock: socket.socket, address) -> None:
        buffer = b""
        info = None
        try:
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buffer, messages = recv_json(buffer, chunk)
                for message in messages:
                    if message.get("type") == "hello":
                        info = self.register_client(sock, message, address)
                    elif info:
                        self.route_message(sock, message)
        except (ConnectionError, OSError, ValueError) as exc:
            print(f"[SERVER] Client error from {peer_label(sock)}: {exc}")
        finally:
            self.disconnect(sock)

    def register_client(self, sock: socket.socket, message, address) -> ClientInfo:
        name = message.get("name", f"Client-{address[1]}").strip() or f"Client-{address[1]}"
        hostname = message.get("hostname", "unknown")
        info = ClientInfo(sock=sock, name=name, hostname=hostname, ip=address[0])
        with self.lock:
            self.clients[sock] = info
        send_json(sock, {"type": "system", "text": f"Connected to monitoring server as {name}."})
        send_json(sock, {"type": "rooms", "rooms": list(ROOMS)})
        self.broadcast_system(f"{name} joined from {info.ip} ({hostname}).")
        self.broadcast_nodes()
        print(f"[SERVER] {name} connected from {info.ip} ({hostname})")
        return info

    def disconnect(self, sock: socket.socket) -> None:
        with self.lock:
            info = self.clients.pop(sock, None)
        try:
            sock.close()
        except OSError:
            pass
        if info:
            print(f"[SERVER] {info.name} disconnected.")
            self.broadcast_system(f"{info.name} disconnected.")
            self.broadcast_nodes()

    def route_message(self, sock: socket.socket, message) -> None:
        msg_type = message.get("type")
        if msg_type == "broadcast":
            self.broadcast_event(sock, message.get("text", ""), "status")
        elif msg_type == "alert":
            self.broadcast_event(sock, message.get("text", ""), "alert")
        elif msg_type == "emergency":
            self.broadcast_event(sock, message.get("text", ""), "emergency")
        elif msg_type == "join_room":
            self.join_room(sock, message.get("room", ""))
        elif msg_type == "leave_room":
            self.leave_room(sock, message.get("room", ""))
        elif msg_type == "room_message":
            self.room_message(sock, message.get("room", ""), message.get("text", ""))
        elif msg_type == "private":
            self.private_message(sock, message.get("to", ""), message.get("text", ""))
        elif msg_type == "file":
            self.handle_file(sock, message)
        elif msg_type == "nodes_request":
            self.send_nodes(sock)
        elif msg_type == "ping":
            send_json(sock, {"type": "pong", "sent_at": message.get("sent_at", time.time())})

    def broadcast_event(self, sender_sock: socket.socket, text: str, level: str) -> None:
        sender = self.clients.get(sender_sock)
        if not sender or not text.strip():
            return
        payload = {
            "type": "event",
            "level": level,
            "from": sender.name,
            "text": text.strip(),
            "time": time.strftime("%H:%M:%S"),
        }
        self.send_to_all(payload)
        print(f"[{level.upper()}] {sender.name}: {text.strip()}")

    def join_room(self, sock: socket.socket, room: str) -> None:
        room = self.normalize_room(room)
        info = self.clients.get(sock)
        if not info or not room:
            return
        with self.lock:
            info.rooms.add(room)
        send_json(sock, {"type": "system", "text": f"You joined {room} room."})
        self.room_notice(room, f"{info.name} joined {room} room.")

    def leave_room(self, sock: socket.socket, room: str) -> None:
        room = self.normalize_room(room)
        info = self.clients.get(sock)
        if not info or not room:
            return
        with self.lock:
            info.rooms.discard(room)
        send_json(sock, {"type": "system", "text": f"You left {room} room."})
        self.room_notice(room, f"{info.name} left {room} room.")

    def room_message(self, sock: socket.socket, room: str, text: str) -> None:
        room = self.normalize_room(room)
        sender = self.clients.get(sock)
        if not sender or not room or not text.strip():
            return
        payload = {
            "type": "room",
            "room": room,
            "from": sender.name,
            "text": text.strip(),
            "time": time.strftime("%H:%M:%S"),
        }
        with self.lock:
            targets = [c.sock for c in self.clients.values() if room in c.rooms]
        for target in targets:
            self.safe_send(target, payload)
        print(f"[ROOM:{room}] {sender.name}: {text.strip()}")

    def private_message(self, sock: socket.socket, target_name: str, text: str) -> None:
        sender = self.clients.get(sock)
        if not sender or not target_name.strip() or not text.strip():
            return
        target = self.find_by_name(target_name.strip())
        if not target:
            send_json(sock, {"type": "system", "text": f"Private target '{target_name}' is not online."})
            return
        payload = {
            "type": "private",
            "from": sender.name,
            "to": target.name,
            "text": text.strip(),
            "time": time.strftime("%H:%M:%S"),
        }
        self.safe_send(target.sock, payload)
        self.safe_send(sock, payload)
        print(f"[PRIVATE] {sender.name} -> {target.name}: {text.strip()}")

    def handle_file(self, sock: socket.socket, message) -> None:
        sender = self.clients.get(sock)
        if not sender:
            return
        filename = os.path.basename(message.get("filename", "shared_file.bin"))
        file_bytes = base64.b64decode(message.get("data", ""))
        saved_name = f"{int(time.time())}_{sender.name}_{filename}".replace(" ", "_")
        saved_path = os.path.join(self.upload_dir, saved_name)
        with open(saved_path, "wb") as file_obj:
            file_obj.write(file_bytes)
        payload = {
            "type": "file",
            "from": sender.name,
            "filename": filename,
            "size": len(file_bytes),
            "data": message.get("data", ""),
            "time": time.strftime("%H:%M:%S"),
        }
        self.send_to_all(payload)
        print(f"[FILE] {sender.name} shared {filename} ({len(file_bytes)} bytes)")

    def broadcast_system(self, text: str) -> None:
        self.send_to_all({"type": "system", "text": text, "time": time.strftime("%H:%M:%S")})

    def room_notice(self, room: str, text: str) -> None:
        with self.lock:
            targets = [c.sock for c in self.clients.values() if room in c.rooms]
        for target in targets:
            self.safe_send(target, {"type": "system", "text": text, "time": time.strftime("%H:%M:%S")})

    def broadcast_nodes(self) -> None:
        payload = {"type": "nodes", "nodes": self.node_list()}
        self.send_to_all(payload)

    def send_nodes(self, sock: socket.socket) -> None:
        self.safe_send(sock, {"type": "nodes", "nodes": self.node_list()})

    def node_list(self):
        with self.lock:
            return [
                {
                    "name": info.name,
                    "ip": info.ip,
                    "hostname": info.hostname,
                    "rooms": sorted(info.rooms),
                    "online_for": int(time.time() - info.connected_at),
                }
                for info in self.clients.values()
            ]

    def send_to_all(self, payload) -> None:
        with self.lock:
            sockets = list(self.clients.keys())
        for sock in sockets:
            self.safe_send(sock, payload)

    def safe_send(self, sock: socket.socket, payload) -> None:
        try:
            send_json(sock, payload)
        except OSError:
            self.disconnect(sock)

    def find_by_name(self, name: str):
        with self.lock:
            for info in self.clients.values():
                if info.name.lower() == name.lower():
                    return info
        return None

    @staticmethod
    def normalize_room(room: str) -> str:
        for item in ROOMS:
            if item.lower() == room.lower():
                return item
        return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Collaborative Network Monitoring Server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    server = MonitoringServer(args.host, args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")


if __name__ == "__main__":
    main()
