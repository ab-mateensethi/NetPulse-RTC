from client_gui import MonitoringClientGUI


app = MonitoringClientGUI()
app.name_var.set("DemoClient")
app.after(800, app.connect)
app.mainloop()
