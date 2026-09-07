import argparse
import os
import subprocess
import sys
import time


ROOT = os.path.dirname(os.path.abspath(__file__))


def launch(title: str, command: str):
    full = f'title {title} & cd /d "{ROOT}" & {command}'
    return subprocess.Popen(["cmd.exe", "/k", full])


def main() -> None:
    parser = argparse.ArgumentParser(description="Open demo terminals for presentation day")
    parser.add_argument("--mode", choices=["cli", "gui"], default="cli")
    args = parser.parse_args()
    python = sys.executable
    processes = [launch("Monitoring Server", f'"{python}" server.py')]
    time.sleep(1.5)
    if args.mode == "gui":
        for name in ["Ali", "Ahmed", "Usman"]:
            processes.append(launch(f"Client {name}", f'"{python}" client_gui.py'))
    else:
        for name in ["Ali", "Ahmed", "Usman"]:
            processes.append(launch(f"Client {name}", f'"{python}" client_cli.py --name {name}'))
    print("Demo terminals opened. Close each terminal after the presentation.")


if __name__ == "__main__":
    main()
