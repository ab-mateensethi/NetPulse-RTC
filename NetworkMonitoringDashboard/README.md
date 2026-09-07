# Real-time Collaborative Network Monitoring and Alert Dashboard

This project is a Python socket programming implementation for CSC-203 Computer Networks CCP.

## Run

Open terminals in this folder.

Terminal 1:

```powershell
python server.py
```

Terminal 2:

```powershell
python client_gui.py
```

Terminal 3 and 4:

```powershell
python client_cli.py --name Ahmed
python client_cli.py --name Usman
```

You can also open demo terminals automatically:

```powershell
python demo_script.py --mode cli
```

## CLI Commands

- `/alert CPU usage crossed 90%`
- `/emergency Core router is down`
- `/join CPU`
- `/room CPU CPU node 192.168.1.10 needs checking`
- `/pm Ahmed Please verify bandwidth graph`
- `/file sample_logs/cpu_fault_log.txt`
- `/nodes`
- `/ping`

## Features

- Multi-client TCP connectivity
- Threaded server
- Real-time broadcast and emergency alerts
- Active node display with IP and hostname
- Group rooms: CPU, Bandwidth, Security
- Private direct messages
- File/log sharing
- GUI client and CLI client
