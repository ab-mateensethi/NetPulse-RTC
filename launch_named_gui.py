import sys

from client_gui import MonitoringClientGUI


name = sys.argv[1] if len(sys.argv) > 1 else "Client"

app = MonitoringClientGUI()
app.name_var.set(name)
app.after(900, app.connect)
app.mainloop()
