#!/usr/bin/env python3

start = False 

def play(status):
    global start
    if(status == "Lobby" and not start):
        start = True
        return "ready"
    return input()