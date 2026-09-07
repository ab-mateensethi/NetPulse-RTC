import json
import socket
from typing import Any, Dict


ENCODING = "utf-8"


def send_json(sock: socket.socket, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode(ENCODING) + b"\n"
    sock.sendall(data)


def recv_json(buffer: bytes, chunk: bytes):
    buffer += chunk
    messages = []
    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)
        if line.strip():
            messages.append(json.loads(line.decode(ENCODING)))
    return buffer, messages


def peer_label(sock: socket.socket) -> str:
    try:
        host, port = sock.getpeername()
        return f"{host}:{port}"
    except OSError:
        return "disconnected"
