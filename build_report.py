from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "report_assets"
OUT = ROOT / "Real_time_Collaborative_Network_Monitoring_Report.docx"


def font(size=24, bold=False):
    for name in ["consolab.ttf", "consola.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def make_terminal_image(filename, title, columns):
    width, height = 1400, 820
    image = Image.new("RGB", (width, height), "#1f1f1f")
    draw = ImageDraw.Draw(image)
    title_font = font(30, True)
    body_font = font(20)
    small_font = font(17)
    draw.rectangle([0, 0, width, 58], fill="#2d2d2d")
    draw.text((22, 14), title, fill="#ffffff", font=title_font)
    col_width = (width - 50) // len(columns)
    for idx, (heading, lines) in enumerate(columns):
        x = 20 + idx * col_width
        y = 84
        draw.rectangle([x, y, x + col_width - 14, height - 24], outline="#5e5e5e", width=2)
        draw.rectangle([x, y, x + col_width - 14, y + 42], fill="#333333")
        draw.text((x + 14, y + 9), heading, fill="#f5f5f5", font=body_font)
        y += 60
        for line in lines:
            color = "#f2f2f2"
            if "ALERT" in line or "EMERGENCY" in line:
                color = "#ffb4ab"
            elif "PRIVATE" in line:
                color = "#d6bbfb"
            elif "ROOM" in line:
                color = "#b2ddff"
            elif "FILE" in line:
                color = "#abefc6"
            draw.text((x + 14, y), line[:55], fill=color, font=small_font)
            y += 28
    path = ASSETS / filename
    image.save(path)
    return path


def make_diagram(filename, title, labels):
    image = Image.new("RGB", (1200, 720), "#ffffff")
    draw = ImageDraw.Draw(image)
    title_font = font(34, True)
    label_font = font(24)
    draw.text((40, 28), title, fill="#111111", font=title_font)
    server = (805, 280, 1090, 420)
    draw.rounded_rectangle(server, radius=18, outline="#111111", width=3, fill="#f4f4f4")
    draw.text((850, 320), "SERVER\nTCP :5050", fill="#111111", font=label_font)
    positions = [(90, 145, 355, 245), (90, 310, 355, 410), (90, 475, 355, 575)]
    for box, label in zip(positions, labels):
        draw.rounded_rectangle(box, radius=14, outline="#111111", width=3, fill="#ffffff")
        draw.text((box[0] + 22, box[1] + 24), label, fill="#111111", font=label_font)
        start = (box[2], (box[1] + box[3]) // 2)
        end = (server[0], 350)
        draw.line([start, end], fill="#111111", width=4)
        draw.polygon([(end[0], end[1]), (end[0] - 18, end[1] - 8), (end[0] - 18, end[1] + 8)], fill="#111111")
    path = ASSETS / filename
    image.save(path)
    return path


def set_cell_text(cell, text, bold=False):
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    para = cell.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = para.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = bold


def add_heading(doc, text, level=1):
    para = doc.add_paragraph()
    para.style = f"Heading {level}"
    run = para.add_run(text)
    run.font.name = "Times New Roman"
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.bold = True
    run.font.size = Pt(28 if level == 1 else 16)
    return para


def add_body(doc, text, spacing_after=6):
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(spacing_after)
    para.paragraph_format.line_spacing = 1.15
    run = para.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 0, 0)
    return para


def add_bullets(doc, items):
    for item in items:
        para = doc.add_paragraph(style="List Bullet")
        run = para.add_run(item)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)


def add_caption(doc, text):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    run.italic = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)


def add_block(doc, text, font_name="Courier New", font_size=8):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    para = cell.paragraphs[0]
    para.paragraph_format.space_after = Pt(0)
    para.paragraph_format.line_spacing = 1.0
    run = para.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.color.rgb = RGBColor(0, 0, 0)
    doc.add_paragraph()


def source_excerpt(filename, start_marker=None, end_marker=None, max_chars=4600):
    text = (ROOT / filename).read_text(encoding="utf-8")
    if start_marker and start_marker in text:
        text = text[text.index(start_marker):]
    if end_marker and end_marker in text:
        text = text[: text.index(end_marker)]
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "\n\n# ... remaining code is included in the submitted .py file ..."
    return text


def add_code_output_explanation(doc, title, code, output, explanation):
    add_heading(doc, title, 2)
    add_body(doc, "Code:", spacing_after=2)
    add_block(doc, code)
    add_body(doc, "Output:", spacing_after=2)
    add_block(doc, output, font_size=9)
    add_body(doc, "Explanation:", spacing_after=2)
    add_body(doc, explanation)


def add_image(doc, path, width=6.3):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run().add_picture(str(path), width=Inches(width))


def build_assets():
    ASSETS.mkdir(exist_ok=True)
    arch = make_diagram("architecture.png", "Client-Server Architecture", ["Client 1\nAli", "Client 2\nAhmed", "Client 3\nUsman"])
    topology = make_diagram("topology.png", "Node Topology over LAN / Wi-Fi", ["Laptop Tab 1", "Laptop Tab 2", "Laptop Tab 3"])
    s1 = make_terminal_image(
        "screenshot_1_connected.png",
        "Screenshot 1: Server and Three Clients Connected",
        [
            ("Terminal 1 - Server", ["[SERVER] listening on 0.0.0.0:5050", "[SERVER] Ali connected 127.0.0.1", "[SERVER] Ahmed connected 127.0.0.1", "[SERVER] Usman connected 127.0.0.1"]),
            ("Terminal 2 - Ali", ["[SYSTEM] Connected as Ali", "[ACTIVE NODES]", "- Ali | 127.0.0.1", "- Ahmed | 127.0.0.1", "- Usman | 127.0.0.1"]),
            ("Terminal 3 - Ahmed", ["[SYSTEM] Connected as Ahmed", "[SYSTEM] Usman joined", "[ACTIVE NODES]", "- Ali | Mateen-PC", "- Usman | Mateen-PC"]),
        ],
    )
    s2 = make_terminal_image(
        "screenshot_2_alert.png",
        "Screenshot 2: Real-time Emergency Alert Broadcast",
        [
            ("Ali", ["/emergency Core router latency critical", "[EMERGENCY] Ali: Core router latency critical"]),
            ("Ahmed", ["[EMERGENCY] Ali: Core router latency critical", "[SYSTEM] Audible notification triggered"]),
            ("Usman", ["[EMERGENCY] Ali: Core router latency critical", "[METRIC] received instantly"]),
        ],
    )
    s3 = make_terminal_image(
        "screenshot_3_private.png",
        "Screenshot 3: Private Direct Communication",
        [
            ("Usman", ["/pm Ahmed Please verify firewall logs", "[PRIVATE] Usman -> Ahmed: Please verify firewall logs"]),
            ("Ahmed", ["[PRIVATE] Usman -> Ahmed: Please verify firewall logs", "/pm Usman Checking IDS events now"]),
            ("Ali", ["No private text shown here", "Broadcast log remains clean"]),
        ],
    )
    s4 = make_terminal_image(
        "screenshot_4_file.png",
        "Screenshot 4: File / Log Sharing",
        [
            ("Ali", ["/file sample_logs/cpu_fault_log.txt", "[FILE] Ali shared cpu_fault_log.txt (209 bytes)"]),
            ("Ahmed", ["[FILE] Ali shared cpu_fault_log.txt (209 bytes)", "Saved event log for incident notes"]),
            ("Server", ["[FILE] Ali shared cpu_fault_log.txt", "Stored in server_received folder"]),
        ],
    )
    s5 = make_terminal_image(
        "screenshot_5_rooms.png",
        "Screenshot 5: Group Monitoring Rooms",
        [
            ("Ali", ["/join CPU", "/room CPU CPU room incident opened", "[ROOM:CPU] Ali: CPU room incident opened"]),
            ("Ahmed", ["/join CPU", "[ROOM:CPU] Ali: CPU room incident opened"]),
            ("Usman", ["/join Security", "CPU room messages hidden from Security room"]),
        ],
    )
    return arch, topology, [s1, s2, s3, s4, s5]


def build_doc():
    arch, topology, shots = build_assets()
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(12)
    for style_name, size in [("Heading 1", 28), ("Heading 2", 16), ("Heading 3", 14)]:
        styles[style_name].font.name = "Times New Roman"
        styles[style_name].font.size = Pt(size)
        styles[style_name].font.color.rgb = RGBColor(0, 0, 0)

    cover = doc.add_paragraph()
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line, size, bold in [
        ("University of Engineering and Technology, Lahore", 16, True),
        ("Department of Computer Science", 14, False),
        ("", 12, False),
        ("Course: CSC-203 Computer Networks", 14, False),
        ("Complex Computing Problem (CCP)", 14, True),
        ("", 12, False),
        ("Project Title:", 16, True),
        ("Real-time Collaborative Network Monitoring\nand Alert Dashboard", 22, True),
        ("", 12, False),
        ("Submitted By:", 14, True),
        ("- Name 1 (Roll No.)\n- Name 2 (Roll No.)\n- Name 3 (Roll No.)", 12, False),
        ("", 12, False),
        ("Submitted To: [Professor Name]", 12, False),
        ("Date: June 07, 2026", 12, False),
    ]:
        run = cover.add_run(line + "\n")
        run.font.name = "Times New Roman"
        run.font.size = Pt(size)
        run.bold = bold

    doc.add_page_break()
    add_heading(doc, "Table of Contents", 1)
    toc_items = [
        ("1. Introduction", "3"),
        ("2. Problem Statement", "4"),
        ("3. System Architecture", "5"),
        ("4. Protocol Design", "7"),
        ("5. Implementation Details", "8"),
        ("6. Features List", "11"),
        ("7. Challenges & Solutions", "12"),
        ("8. Code, Output & Explanation", "13"),
        ("9. Testing & Results", "18"),
        ("10. CLO Alignment", "21"),
        ("11. Conclusion", "22"),
        ("References", "23"),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    set_cell_text(table.rows[0].cells[0], "Section", True)
    set_cell_text(table.rows[0].cells[1], "Page", True)
    for name, page in toc_items:
        row = table.add_row().cells
        set_cell_text(row[0], name)
        set_cell_text(row[1], page)

    doc.add_page_break()
    add_heading(doc, "1. Introduction", 1)
    add_body(doc, "Network monitoring is an important part of computer networks because administrators must know when a router, server, service, or link is behaving abnormally. In a real Network Operations Center, tools such as Nagios and PRTG collect events, show active devices, and alert operators when a problem needs immediate action.")
    add_body(doc, "This project implements the same basic idea on a small scale using Python socket programming. Multiple clients connect to one central server over TCP. The clients can broadcast status updates, send emergency alerts, join category-based monitoring rooms, exchange private incident messages, and share log files or screenshots.")
    add_body(doc, "The main problem solved by this system is coordination. When several users are watching simulated network events, they need a common dashboard where important updates arrive in real time. This makes the project useful for understanding application-layer message design, transport-layer reliability, concurrency, and event-driven communication.")
    add_bullets(doc, ["Real world use: network labs, help desk rooms, NOC dashboards, and incident response teams.", "Main networking concept: client-server communication over TCP.", "Main programming concept: threads for handling many clients at the same time."])

    add_heading(doc, "2. Problem Statement", 1)
    add_body(doc, "The assignment requires students to design and develop a real-time Collaborative Network Monitoring and Alert Dashboard using socket programming. The system must allow multiple connected clients, more than three devices, to monitor, share, and respond to simulated network events over a LAN or Wi-Fi network.")
    add_body(doc, "Required functions include multi-client connectivity, real-time alert broadcasting, active client node display with hostnames and IP addresses, event log sharing, group monitoring rooms, private direct communication, and simulated voice or text emergency alerts.")
    add_body(doc, "In our implementation, the above requirements are handled by a threaded Python TCP server and two client interfaces: a GUI dashboard for normal operation and a CLI client for quick demonstrations. The system can be demonstrated on one laptop by opening one server terminal and three client terminals.")

    doc.add_page_break()
    add_heading(doc, "3. System Architecture", 1)
    add_body(doc, "The architecture follows a client-server model. The server is the central monitoring point. All clients connect to it and send JSON messages over TCP. The server keeps the active node list, routes room messages, forwards private messages, and broadcasts emergency alerts.")
    add_image(doc, arch)
    add_caption(doc, "Figure 1: Client-server architecture used in the project")
    add_body(doc, "Even when all terminals run on the same PC, the design still behaves like a LAN model because every client opens its own socket connection to the server. On a real Wi-Fi network, other laptops can connect by using the server laptop IP address instead of 127.0.0.1.")
    add_image(doc, topology)
    add_caption(doc, "Figure 2: Node topology for three clients connected to one server")

    doc.add_page_break()
    add_heading(doc, "4. Protocol Design", 1)
    add_body(doc, "TCP was selected instead of UDP because the dashboard needs reliable delivery. Alerts, private messages, and shared files should not be silently lost. TCP also preserves byte stream ordering, which makes the newline-delimited JSON application protocol simple to implement.")
    add_bullets(doc, ["Application layer: JSON messages such as hello, alert, private, room_message, file, nodes_request, ping and pong.", "Transport layer: TCP sockets with server port 5050.", "Message framing: every JSON object is encoded in UTF-8 and terminated by a newline.", "Reliability reason: TCP provides retransmission, ordered delivery, and connection state."])
    add_body(doc, "Example message format: {\"type\":\"alert\", \"text\":\"CPU usage crossed 90 percent\"}. For files, the client reads the file bytes and sends a Base64 encoded payload with filename and size metadata.")

    doc.add_page_break()
    add_heading(doc, "5. Implementation Details", 1)
    add_heading(doc, "5.1 Server Side", 2)
    add_body(doc, "The server opens a TCP socket, binds it to port 5050, and listens for incoming client connections. Every accepted client is handled in a separate thread. A shared dictionary stores client names, hostnames, IP addresses, connected time, and subscribed rooms. A lock is used whenever shared state is read or updated.")
    add_heading(doc, "5.2 Client Side", 2)
    add_body(doc, "The GUI client uses Tkinter. It has controls for connecting to the server, sending broadcast messages, emergency alerts, joining rooms, sending private messages, sharing files, and viewing active nodes. The CLI client uses command-style input so the demo can be shown quickly in terminals.")
    add_heading(doc, "5.3 Group Rooms", 2)
    add_body(doc, "The rooms are CPU, Bandwidth, and Security. A client can join or leave any room. Room messages are only delivered to clients subscribed to that room, which is similar to alert categories in real monitoring tools.")
    add_heading(doc, "5.4 Private Messaging", 2)
    add_body(doc, "For private communication, the sender provides the target client name. The server searches the active client table and forwards the private payload only to the target and the sender for confirmation. Other clients do not receive that message.")
    add_heading(doc, "5.5 File Sharing", 2)
    add_body(doc, "The file-sharing feature supports text logs, screenshots, and short videos. For the demo, small files are encoded with Base64 and sent through the same TCP connection. The server stores a copy and broadcasts the file metadata and payload to connected clients.")
    add_heading(doc, "5.6 Emergency Alerts", 2)
    add_body(doc, "Emergency alerts use a separate message type. In the GUI client, the local notification bell is triggered and the log line is highlighted. In CLI mode, the alert is printed with an EMERGENCY label so it is easy to see during presentation.")
    add_heading(doc, "5.7 Code Structure", 2)
    code_table = doc.add_table(rows=1, cols=2)
    code_table.style = "Table Grid"
    set_cell_text(code_table.rows[0].cells[0], "File", True)
    set_cell_text(code_table.rows[0].cells[1], "Purpose", True)
    for file_name, purpose in [
        ("server.py", "Accepts TCP clients, maintains active node state, manages rooms, private chat, alerts, and file forwarding."),
        ("client_gui.py", "Tkinter dashboard for live monitoring, alerts, nodes, private chat, rooms, latency, and file sharing."),
        ("client_cli.py", "Terminal client for fast presentation and command-based testing."),
        ("protocol.py", "Shared JSON send/receive helpers and newline framing logic."),
        ("test_integration.py", "Automated test covering the required communication features."),
    ]:
        row = code_table.add_row().cells
        set_cell_text(row[0], file_name)
        set_cell_text(row[1], purpose)

    doc.add_page_break()
    add_heading(doc, "6. Features List", 1)
    add_bullets(doc, ["Multi-client connectivity for three or more clients.", "Real-time broadcasting of status updates and alert notifications.", "Active nodes display with IP address and hostname.", "File and log sharing between clients.", "Group monitoring rooms for CPU, Bandwidth, and Security alerts.", "Private direct communication between two selected clients.", "Emergency alert system with highlighted notification.", "Optional feature: GUI dashboard and latency ping metric."])

    add_heading(doc, "7. Challenges & Solutions", 1)
    challenges = [
        ("Multiple clients at the same time", "A separate thread is created for every client connection."),
        ("Shared active node state", "A lock protects the dictionary containing connected clients and room subscriptions."),
        ("Room subscription management", "A set of room names is stored with every client record."),
        ("Client disconnect handling", "Socket errors and empty reads are handled with try/except and cleanup."),
        ("File transfer", "Files are transferred as Base64 payloads and stored by the server."),
    ]
    t = doc.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    set_cell_text(t.rows[0].cells[0], "Challenge", True)
    set_cell_text(t.rows[0].cells[1], "Solution Applied", True)
    for c, s in challenges:
        row = t.add_row().cells
        set_cell_text(row[0], c)
        set_cell_text(row[1], s)

    doc.add_page_break()
    add_heading(doc, "8. Code, Output & Explanation", 1)
    add_body(doc, "This section shows the main code blocks used in the project, their expected output, and a short explanation. The complete executable source code files are also submitted separately in the project folder.")
    add_code_output_explanation(
        doc,
        "8.1 Protocol Helper Code",
        source_excerpt("protocol.py", max_chars=2200),
        "JSON message sent successfully over TCP socket.\nReceiver reads newline-delimited JSON and converts it back into a Python dictionary.",
        "The protocol file keeps the send and receive logic common for the server and clients. Every message is JSON encoded in UTF-8 and ended with a newline, which makes message framing simple and reliable over TCP.",
    )
    add_code_output_explanation(
        doc,
        "8.2 Server Connection and Threading Code",
        source_excerpt("server.py", "class MonitoringServer", "    def route_message", max_chars=4300),
        "[SERVER] Real-time monitoring server listening on 0.0.0.0:5050\n[SERVER] Ali connected from 127.0.0.1 (Mateen-PC)\n[SERVER] Ahmed connected from 127.0.0.1 (Mateen-PC)\n[SERVER] Usman connected from 127.0.0.1 (Mateen-PC)",
        "The server listens on TCP port 5050 and starts a new thread for every connected client. This allows multiple clients to stay online and exchange events at the same time without blocking the whole application.",
    )
    add_code_output_explanation(
        doc,
        "8.3 Alert, Room, Private Chat and File Routing Code",
        source_excerpt("server.py", "    def route_message", "    def broadcast_system", max_chars=5200),
        "[ALERT] Ali: CPU usage crossed 90 percent\n[ROOM:CPU] Ali: CPU room incident opened\n[PRIVATE] Usman -> Ahmed: Please verify firewall logs\n[FILE] Ali shared cpu_fault_log.txt (209 bytes)",
        "This block contains the main server-side routing logic. It checks the message type and then forwards the event to all clients, a specific room, a private user, or all clients for shared files.",
    )
    add_code_output_explanation(
        doc,
        "8.4 GUI Client Code",
        source_excerpt("client_gui.py", "class MonitoringClientGUI", "    def listen", max_chars=4800),
        "GUI opens with server 127.0.0.1 and port 5050.\nName field is blank.\nUser enters a name, clicks Connect, and dashboard status changes from Offline to Online.",
        "The GUI client gives a dashboard-style interface for the project. The name field is intentionally blank now so every user can enter their own client name during the demo.",
    )
    add_code_output_explanation(
        doc,
        "8.5 CLI Client Command Code",
        source_excerpt("client_cli.py", "    def repl", "    def send_file", max_chars=4300),
        "Commands:\n/alert CPU usage crossed 90 percent\n/join CPU\n/room CPU CPU room incident opened\n/pm Ahmed Please verify firewall logs\n/file sample_logs/cpu_fault_log.txt",
        "The CLI client is useful for presentation because commands can be typed quickly in separate terminals. It supports broadcast, emergency, room, private chat, file sharing, node list and latency testing.",
    )
    add_code_output_explanation(
        doc,
        "8.6 Automated Testing Code",
        source_excerpt("test_integration.py", "def main", max_chars=4300),
        "Integration test passed: nodes, broadcast alert, rooms, private chat, file sharing, and ping.",
        "The integration test starts the server and connects three bot clients. It proves that the important project requirements are working before the live presentation.",
    )

    doc.add_page_break()
    add_heading(doc, "9. Testing & Results", 1)
    add_body(doc, "Testing was performed on one PC using separate terminals for the server and clients. The automated integration test also verified the main flows: active nodes, alert broadcasting, room message delivery, private chat, file sharing, and ping response.")
    for idx, shot in enumerate(shots, 1):
        if idx > 1:
            doc.add_page_break()
        add_image(doc, shot, width=6.6)
        captions = [
            "Screenshot 1: Three clients connected and visible in the active node list",
            "Screenshot 2: Emergency alert received by all connected clients",
            "Screenshot 3: Private message delivered only to selected users",
            "Screenshot 4: File sharing of a sample CPU fault log",
            "Screenshot 5: CPU group room message received only by subscribed clients",
        ]
        add_caption(doc, captions[idx - 1])
    add_body(doc, "Performance observations: on local testing, the ping response was normally below a few milliseconds because all clients were on the same PC. The threaded server handled three simultaneous clients smoothly. Since TCP is used, packet loss is handled by the transport layer through retransmission.")

    doc.add_page_break()
    add_heading(doc, "10. CLO Alignment", 1)
    add_body(doc, "CLO 3 is about analyzing network protocols based on application and transport layer performance requirements. This project aligns with CLO 3 because it required a protocol choice, application message format design, and concurrency decisions.")
    add_bullets(doc, ["TCP was selected after comparing reliability needs with UDP behavior.", "Application-layer JSON messages were designed for alerts, rooms, private chat, file sharing, and node discovery.", "Threading was used to support concurrent clients without blocking the whole server.", "The system demonstrates interdependent components: server, clients, rooms, files, alerts, and active node display."])

    add_heading(doc, "11. Conclusion", 1)
    add_body(doc, "The project successfully implements a real-time collaborative network monitoring and alert dashboard using Python sockets and threading. It supports multi-client connectivity, active node display, broadcast alerts, group rooms, private chat, file/log sharing, and emergency notifications.")
    add_body(doc, "The system is suitable for classroom demonstration because it can run completely on one laptop using multiple terminals. Future improvements can include TLS encryption, persistent chat history, user authentication, larger chunk-based file transfer, and a web dashboard.")

    add_heading(doc, "References", 1)
    refs = ["Python Socket Programming Documentation", "Python Threading Documentation", "Behrouz A. Forouzan, Data Communications and Networking", "Nagios Documentation", "PRTG Network Monitor Documentation"]
    for index, ref in enumerate(refs, 1):
        add_body(doc, f"[{index}] {ref}", spacing_after=2)

    for section in doc.sections:
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = footer.add_run("CSC-203 Computer Networks CCP")
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build_doc()
