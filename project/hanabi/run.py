import os
import sys
from subprocess import Popen, CREATE_NEW_CONSOLE

playerNames = ['Mars', 'Marty', 'Rick', 'Vale', 'Ose', 'Alex']

Popen(['python', 'server.py', f"{sys.argv[1]}"])
for client in range(int(sys.argv[1])):
    Popen(['python', 'custom_client.py', '127.0.0.1', '1024', f"{playerNames[client]}"], creationflags=CREATE_NEW_CONSOLE)