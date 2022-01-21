#!/usr/bin/env python3

import itertools

from matplotlib.pyplot import table
import GameData

colors = ["green", "red", "blue", "yellow", "white"]
numbers = [1, 2, 3, 4, 5]
start = True

def getLastOptimistCardOfPlayer(hintMap, playerName):
    optimisticCards = []
    for card in range(5):
        if(hintMap[playerName][card][2] == True):
            optimisticCards.append(card)
    return optimisticCards

# Get dict of tuples with (cardIndex, value, color, deductionLevel)
def getDeductions(playerName, game_data, hintMap):
    deductions = []
    combinations = [(i, v, c) for i in range(5) for v in numbers for c in colors]
    for (i, v, c) in combinations:
        if(playerName not in hintMap):
            break
        if (hintMap[playerName][i][0] == None or hintMap[playerName][i][0] == v and
            hintMap[playerName][i][1] == None or hintMap[playerName][i][1] == c and
            isCardPossible(v, c, game_data)):
                deductions.append(i, v, c, 0)

def stackToTupleList(stack):
    tupleList = []
    for card in stack:
        tupleList.append((card.value, card.color))
    return tupleList

# TO REMOVE
def test(data):
    tableCards = []
    for color in colors:
        for number in data.tableCards[color]:
            tableCards.append((number, color))
    otherPlayerCards = []
    for player in data.players:
        otherPlayerCards.append(stackToTupleList(player.hand))
    discardedCards = stackToTupleList(data.discardPile)
    tableCards.extend(card for card in otherPlayerCards if card not in tableCards)
    tableCards.extend(card for card in discardedCards if card not in tableCards)
    return tableCards

def isCardPossible(value, color, data):
    tableCards = []
    for color in colors:
        for number in data.tableCards[color]:
            tableCards.append((number, color))
    otherPlayerCards = []
    for player in data.players:
        otherPlayerCards.append(stackToTupleList(player.hand))
    discardedCards = stackToTupleList(data.discardPile)
    tableCards.extend(card for card in otherPlayerCards if card not in tableCards)
    tableCards.extend(card for card in discardedCards if card not in tableCards)
    jointList = tableCards

    if((value, color) not in jointList):
        return True
    else:
        return False

def isCardPlayable(card, game_data):
    tableCards = game_data.tableCards

def isCardDangerous(card, game_data):
    return

def play(playerName, status, game_data, hintMap, deductionStatus):
    print(playerName, status, test(game_data), hintMap, deductionStatus)

    # A hidden card has an array of deductions, i.e. possible values with deduction levels
    # A hidden card is said to be "optimistic" when it's (one of) the last card(s) that was designated for a hint
    # since the player last played.
    # When there are several possible deductions for a card, we always assume that playing it/ discarding it
    # leads to the worst possible outcome, unless it's an optimist card in which case we trust our partners :)
    # Before playing, each deduction will be assigned a status (IDeductionStatus)
    # (playing a 5) > (playing a playable card) > (happy discard) > (giving a hint) > (discard) > (sad discard)

    # Get statistics
    lastOptimisticCards = getLastOptimistCardOfPlayer(hintMap, playerName)
    deductions = getDeductions(playerName, game_data, hintMap)

    # If I have a playable card, play it
    

    # If strike tokens < 2, try to play an optimistic card


    # If there are hints available, give one


    # Discard safe card, if any


    # If 1st play and no playable cards in next player hand, give a hint on 5s or 2s


    # If none of the above, play a random card

    
    return input()