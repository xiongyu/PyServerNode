#encoding: utf-8

import sys
sys.path.append("./server")
sys.path.append("./common")

import serverapp
import sys

app = serverapp.CServerApplication(sys.argv)
app.Listen(12349, "0.0.0.0")
app.Exec()
print("Bye!~")
