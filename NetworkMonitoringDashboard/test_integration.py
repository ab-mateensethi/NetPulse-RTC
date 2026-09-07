import base64
import os
import socket
import threading
import time

from protocol import recv_json, send_json
from server import MonitoringServer


class BotClient:
    def __init__(self, name, port):
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = b""
        self.messages = []
        self.sock.connect(("127.0.0.1", port))
        send_json(self.sock, {"type": "hello", "name": name, "hostname": socket.gethostname()})
        self.running = True
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()

    def listen(self):
        while self.running:
            try:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                self.buffer, messages = recv_json(self.buffer, chunk)
                self.messages.extend(messages)
            except OSError:
                break

    def send(self, payload):
        send_json(self.sock, payload)

    def close(self):
        self.running = False
        self.sock.close()

    def saw(self, msg_type, contains):
        return any(m.get("type") == msg_type and contains in str(m) for m in self.messages)


def wait_until(predicate, timeout=3):
    start = time.time()
    while time.time() - start < timeout:
        if predicate():
            return True
        time.sleep(0.05)
    return False


def main():
    port = 5061
    server = MonitoringServer("127.0.0.1", port, upload_dir="test_received")
    threading.Thread(target=server.start, daemon=True).start()
    time.sleep(0.4)

    ali = BotClient("Ali", port)
    ahmed = BotClient("Ahmed", port)
    usman = BotClient("Usman", port)
    clients = [ali, ahmed, usman]

    assert wait_until(lambda: all(c.saw("nodes", "Ali") for c in clients)), "nodes not broadcast"

    ali.send({"type": "alert", "text": "CPU usage crossed 90 percent"})
    assert wait_until(lambda: all(c.saw("event", "CPU usage crossed") for c in clients)), "alert missing"

    ali.send({"type": "join_room", "room": "CPU"})
    ahmed.send({"type": "join_room", "room": "CPU"})
    time.sleep(0.2)
    ali.send({"type": "room_message", "room": "CPU", "text": "CPU room incident opened"})
    assert wait_until(lambda: ahmed.saw("room", "CPU room incident")), "room message missing"

    usman.send({"type": "private", "to": "Ahmed", "text": "Please verify firewall logs"})
    assert wait_until(lambda: ahmed.saw("private", "firewall logs")), "private message missing"

    sample_path = os.path.join("sample_logs", "cpu_fault_log.txt")
    with open(sample_path, "rb") as file_obj:
        data = base64.b64encode(file_obj.read()).decode("ascii")
    ali.send({"type": "file", "filename": "cpu_fault_log.txt", "data": data})
    assert wait_until(lambda: all(c.saw("file", "cpu_fault_log.txt") for c in clients)), "file share missing"

    ali.send({"type": "ping", "sent_at": time.time()})
    assert wait_until(lambda: ali.saw("pong", "sent_at")), "pong missing"

    for client in clients:
        client.close()
    print("Integration test passed: nodes, broadcast alert, rooms, private chat, file sharing, and ping.")


if __name__ == "__main__":
    main()
