import os
import sys
from subprocess import Popen, CREATE_NEW_CONSOLE

Popen(['python', 'server.py', f"{sys.argv[1]}"])
for client in range(int(sys.argv[1])):
    Popen(['python', 'client.py', '127.0.0.1', '1024', f"Player{client}"], creationflags=CREATE_NEW_CONSOLE)