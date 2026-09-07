NetPulse-RTC ⚡ 

Real-Time Collaborative Network Monitoring & Alert Dashboard

NetPulse-RTC is a **Python-based Computer Networking project developed specifically for a client** as a custom project solution. The system was designed to provide a real-time environment where multiple users can connect, monitor simulated network events, communicate with each other and respond to important network alerts.

The project uses **TCP socket programming, JSON-based communication and multithreading** to build a reliable client-server networking system.

What This Project Does 🚀 

NetPulse-RTC connects multiple clients to a central monitoring server and provides a shared dashboard for real-time network communication and incident coordination.

It supports:

- 🔗 Multi-client TCP connectivity
- 📡 Real-time status broadcasting
- 🚨 Alert and emergency notifications
- 🖥️ Active client monitoring with IP addresses and hostnames
- 💬 Private messaging between clients
- 👥 Group monitoring rooms
- 📁 Network log and file sharing
- 📊 GUI monitoring dashboard built with Tkinter
- ⌨️ CLI client for quick demonstrations
- ⚡ Network latency testing using Ping/Pong
- 🧪 Automated integration testing

System Architecture 🏗️ 

The project follows a **Client-Server Architecture**:

```text
                 ┌─────────────────────────┐
                 │    Monitoring Server    │
                 │       TCP : 5050        │
                 └────────────┬────────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
       ┌─────▼─────┐    ┌─────▼─────┐    ┌────▼──────┐
       │ GUI Client│    │ GUI Client│    │ CLI Client│
       └───────────┘    └───────────┘    └───────────┘
````

All connected clients communicate with the central server using **TCP sockets** and newline-delimited **JSON messages**.

Technologies Used 🛠️ 

* 🐍 Python
* 🔌 TCP Socket Programming
* 🧵 Multithreading
* 🖼️ Tkinter
* 📦 JSON
* 📁 Base64 File Transfer
* 🧪 Automated Integration Testing

Main Components 📂 

| Component                        | Purpose                                       |
| -------------------------------- | --------------------------------------------- |
| `server.py`                      | Central TCP monitoring server                 |
| `client_gui.py`                  | GUI-based monitoring dashboard                |
| `client_cli.py`                  | Command-line client                           |
| `protocol.py`                    | Shared JSON communication and message framing |
| `test_integration.py`            | Automated integration testing                 |
| `sample_logs/`                   | Sample network log files                      |
| `server_received/`               | Files received by the server                  |
| `Project Report/`                | Project report resources                      |
| `Computer_Networks_CCP-2026.pdf` | Complete project PDF report                   |

Monitoring Rooms 📡 

The system provides dedicated monitoring rooms for different types of network events:

* 🖥️ **CPU**
* 📶 **Bandwidth**
* 🛡️ **Security**

Clients can join or leave rooms and room messages are delivered to the relevant subscribed clients.

Communication Features 💬 

The system supports several communication methods:

* 📢 Broadcast messages
* ⚠️ Network alerts
* 🚨 Emergency alerts
* 👥 Room-based communication
* 🔒 Private client-to-client messaging
* 📁 File and log sharing
* 🏓 Ping/Pong latency testing

Running the Project ▶️ 

Start the Server

```bash
python server.py
```

Start a GUI Client

```bash
python client_gui.py
```

Start a CLI Client

```bash
python client_cli.py
```

Multiple clients can be connected to the same server simultaneously for demonstration and testing.

Testing 🧪 

The project includes an automated integration test that verifies:

* Active node discovery
* Alert broadcasting
* Monitoring rooms
* Private messaging
* File sharing
* Ping response

Run the test using:

```bash
python test_integration.py
```

Project Report 📄 

A **complete PDF report** is included in this repository:

📘 **`Computer_Networks_CCP-2026.pdf`**

The report provides detailed documentation of the project, including:

* Introduction and problem statement
* System architecture
* Protocol design
* Implementation details
* Project features
* Code explanation
* Testing and results
* Architecture diagrams
* Testing screenshots
* CLO alignment
* Conclusion and references

Project Purpose 🎯 

This project was developed as a **custom Computer Networking solution for a client**, while also demonstrating practical concepts from the **CSC-203 Computer Networks** course.

The project demonstrates:

* Client-server communication
* TCP-based reliable networking
* Application-layer protocol design
* JSON message framing
* Concurrent client handling
* Real-time event communication
* Network file transmission

Future Improvements 🔮 

Possible future improvements include:

* 🔐 TLS-based encrypted communication
* 👤 User authentication
* 💾 Persistent chat and event history
* 📦 Chunk-based file transfer
* 🌐 Web-based monitoring dashboard
* 📈 Advanced network performance analytics

Project Information 👨‍💻 

**Project:** NetPulse-RTC
**Type:** Custom Client Project
**Domain:** Computer Networking
**Language:** Python
**Architecture:** Client-Server
**Protocol:** TCP
**Interface:** GUI + CLI

**NetPulse-RTC** was built to provide a practical, collaborative and real-time network monitoring experience for the client's project requirements ⭐.


