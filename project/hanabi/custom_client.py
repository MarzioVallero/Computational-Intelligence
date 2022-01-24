#!/usr/bin/env python3

from sys import argv, stdout
from threading import Thread, Semaphore

import GameData
import socket
from constants import *
import os
import ai

if len(argv) < 4:
    print("You need the player name to start the game.")
    #exit(-1)
    playerName = "Test" # For debug
    ip = HOST
    port = PORT
else:
    playerName = argv[3]
    ip = argv[1]
    port = int(argv[2])

run = True
statuses = ["Lobby", "Game", "GameHint"]
status = statuses[0]
hintMap = {}
socketManager = Semaphore(0)
inputManger = Semaphore(0)

def manageInput():
    global run
    global status
    global hintMap
    playerName = argv[3]

    while run:
        inputManger.acquire()
        print("Input manager alive")
        s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
        data = s.recv(DATASIZE)
        data = GameData.GameData.deserialize(data)

        if type(data) is GameData.ServerGameStateData and data.currentPlayer == playerName:
            command = ai.play(playerName, status, data, hintMap)
            print(f"AI chosen command: {command}")
            a = input()
        else:
            socketManager.release()
            continue

        # Choose data to send
        if command == "exit":
            run = False
            os._exit(0)
        elif command == "ready" and status == statuses[0]:
            s.send(GameData.ClientPlayerStartRequest(playerName).serialize())
            socketManager.release()
        elif command == "show" and status == statuses[1]:
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
            socketManager.release()
        elif command.split(" ")[0] == "discard" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                s.send(GameData.ClientPlayerDiscardCardRequest(playerName, cardOrder).serialize())
                socketManager.release()
            except:
                print("Maybe you wanted to type 'discard <num>'?")
                inputManger.release()
                continue
        elif command.split(" ")[0] == "play" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                s.send(GameData.ClientPlayerPlayCardRequest(playerName, cardOrder).serialize())
                socketManager.release()
            except:
                print("Maybe you wanted to type 'play <num>'?")
                inputManger.release()
                continue
        elif command.split(" ")[0] == "hint" and status == statuses[1]:
            try:
                destination = command.split(" ")[2]
                t = command.split(" ")[1].lower()
                if t != "colour" and t != "color" and t != "value":
                    print("Error: type can be 'color' or 'value'")
                    inputManger.release()
                    continue
                value = command.split(" ")[3].lower()
                if t == "value":
                    value = int(value)
                    if int(value) > 5 or int(value) < 1:
                        print("Error: card values can range from 1 to 5")
                        inputManger.release()
                        continue
                else:
                    if value not in ["green", "red", "blue", "yellow", "white"]:
                        print("Error: card color can only be green, red, blue, yellow or white")
                        inputManger.release()
                        continue
                s.send(GameData.ClientHintData(playerName, destination, t, value).serialize())
                socketManager.release()
            except:
                print("Maybe you wanted to type 'hint <type> <destinatary> <value>'?")
                inputManger.release()
                continue
        elif command == "":
            print("[" + playerName + " - " + status + "]: ", end="")
            inputManger.release()
        else:
            print("Unknown command: " + command)
            inputManger.release()
            continue
        stdout.flush()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    request = GameData.ClientPlayerAddData(playerName)
    s.connect((HOST, PORT))
    s.send(request.serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)
    if type(data) is GameData.ServerPlayerConnectionOk:
        print("Connection accepted by the server. Welcome " + playerName)
    print("[" + playerName + " - " + status + "]: ", end="")
    Thread(target=manageInput).start()
    s.send(GameData.ClientPlayerStartRequest(playerName).serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)
    if type(data) is GameData.ServerPlayerStartRequestAccepted:
        print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
        data = s.recv(DATASIZE)
        data = GameData.GameData.deserialize(data)
    if type(data) is GameData.ServerStartGameData:
        print("Game start!")
        s.send(GameData.ClientPlayerReadyData(playerName).serialize())
        status = statuses[1]
    print("[" + playerName + " - " + status + "]: ", end="")
    inputManger.release()
    socketManager.acquire()
    while run:
        print("socket manager alive")
        dataOk = False
        data = s.recv(DATASIZE)
        if not data:
            continue
        data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerPlayerStartRequestAccepted:
            dataOk = True
            print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerStartGameData:
            dataOk = True
            print("Game start!")
            s.send(GameData.ClientPlayerReadyData(playerName).serialize())
            status = statuses[1]
        if type(data) is GameData.ServerGameStateData:
            dataOk = True
            print("Current player: " + data.currentPlayer)
            print("Player hands: ")
            for p in data.players:
                print(p.toClientString())
            print("Table cards: ")
            for pos in data.tableCards:
                print(pos + ": [ ")
                for c in data.tableCards[pos]:
                    print(c.toClientString() + " ")
                print("]")
            print("Discard pile: ")
            for c in data.discardPile:
                print("\t" + c.toClientString())            
            print("Note tokens used: " + str(data.usedNoteTokens) + "/8")
            print("Storm tokens used: " + str(data.usedStormTokens) + "/3")
            inputManger.release()
            socketManager.acquire()
        if type(data) is GameData.ServerActionInvalid:
            dataOk = True
            print("Invalid action performed. Reason:")
            print(data.message)
        # This is used to manage discard commands, why there is no report for which card has been discarded????
        if type(data) is GameData.ServerActionValid:
            dataOk = True
            print(f"{data.lastPlayer} discarded card number {data.cardHandIndex}")
            print("Current player: " + data.player)
            if data.lastPlayer not in hintMap:
                hintMap[data.lastPlayer] = []
                for i in range(5):
                    hintMap[data.lastPlayer].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])
            hintMap[data.lastPlayer][data.cardHandIndex] = [[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False]
            inputManger.release()
            socketManager.acquire()
        if type(data) is GameData.ServerPlayerMoveOk:
            dataOk = True
            print("Nice move!")
            print("Current player: " + data.player)
            if data.lastPlayer not in hintMap:
                hintMap[data.lastPlayer] = []
                for i in range(5):
                    hintMap[data.lastPlayer].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])
            hintMap[data.lastPlayer][data.cardHandIndex] = [[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False]
            inputManger.release()
            socketManager.acquire()
        if type(data) is GameData.ServerPlayerThunderStrike:
            dataOk = True
            print("OH NO! The Gods are unhappy with you!")
            if data.lastPlayer not in hintMap:
                hintMap[data.lastPlayer] = []
                for i in range(5):
                    hintMap[data.lastPlayer].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])
            hintMap[data.lastPlayer][data.cardHandIndex] = [[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False]
            inputManger.release()
            socketManager.acquire()
        if type(data) is GameData.ServerHintData:
            dataOk = True
            print("Hint type: " + data.type)
            print("Player " + data.destination + " cards with value " + str(data.value) + " are:")
            for i in data.positions:
                print("\t" + str(i))
            # Update the hintMap
            if data.destination not in hintMap:
                # first all possible values, then all possible colours, then lastHinted
                hintMap[data.destination] = []
                for i in range(5):
                    hintMap[data.destination].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])
            for i in range(5):
                if i in data.positions:
                    hintMap[data.destination][i][2] = True
                    if data.type == "value":
                        hintMap[data.destination][i][0] = [data.value]
                    elif data.type == "color" or data.type == "colour":
                        hintMap[data.destination][i][1] = [data.value]
                else:
                    hintMap[data.destination][i][2] = False
                    if (data.type == "value") and (data.value in hintMap[data.destination][i][0]):
                        hintMap[data.destination][i][0].remove(data.value)
                    elif (data.type == "color" or data.type == "colour") and (data.value in hintMap[data.destination][i][1]):
                        hintMap[data.destination][i][1].remove(data.value)
            inputManger.release()
            socketManager.acquire()
        if type(data) is GameData.ServerInvalidDataReceived:
            dataOk = True
            print(data.data)
        if type(data) is GameData.ServerGameOver:
            dataOk = True
            print(data.message)
            print(data.score)
            print(data.scoreMessage)
            stdout.flush()
            #run = False
            print("Ready for a new game!")
        if not dataOk:
            print("Unknown or unimplemented data type: " +  str(type(data)))
        print("[" + playerName + " - " + status + "]: ", end="")
        stdout.flush()