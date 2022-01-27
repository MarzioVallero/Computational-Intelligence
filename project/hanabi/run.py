import os
import sys
from subprocess import Popen, CREATE_NEW_CONSOLE

playerNames = ['Mars', 'Marty', 'Rick', 'Vale', 'Ose', 'Alex']

try:
    os.remove("game.log")
    os.remove("results.dat")
except OSError:
    pass

Popen(['python', 'server.py', f"{sys.argv[1]}"])
for client in range(int(sys.argv[1])):
    Popen(['python', 'ai_client.py', '127.0.0.1', '1024', f"{playerNames[client]}"], creationflags=CREATE_NEW_CONSOLE)