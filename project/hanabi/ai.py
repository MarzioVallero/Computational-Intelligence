#!/usr/bin/env python3

import itertools

from matplotlib.pyplot import table
import GameData

colors = ["green", "red", "blue", "yellow", "white"]
numbers = [1, 2, 3, 4, 5]
numberFrequency = [3, 2, 2, 2, 1]
start = True

def getLastOptimistCardsOfPlayer(hintMap, playerName):
    optimisticCards = []
    for card in range(5):
        if(hintMap[playerName][card][2] == True):
            optimisticCards.append(card)
    return optimisticCards

# Get dict of tuples indexed by cardIndex containing (value, color, deductionLevel)
def getDeductions(playerName, game_data, hintMap):
    deductions = {}
    combinations = [(i, v, c) for i in range(game_data.handSize) for v in numbers for c in colors]
    for (i, v, c) in combinations:
        if(playerName not in hintMap):
            break
        if (hintMap[playerName][i][0] == None or hintMap[playerName][i][0] == v and
            hintMap[playerName][i][1] == None or hintMap[playerName][i][1] == c and
            isCardPossible(v, c, game_data)):
                if (i not in deductions):
                    deductions[i] = []
                deductions[i].append((v, c, 0))

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

def isCardDiscardable(deductions, game_data):
    # AI can discard a card that can never be played (already played or because of other discards)
    discardable = True
    for deduction in deductions:
        if (isCardEverPlayable(deduction, game_data)):
            discardable = False
    if discardable:
        return True

    # Don't discard necessarily dangerous cards
    dangerous = True
    for deduction in deductions:
        if (not isCardDangerous(deduction, game_data)):
            dangerous = False
    if dangerous:
        return False
    return True

def isLastDiscardableCard(deductions, game_data):
    lastDiscardableCard = True
    for i in range(game_data.handSize):
        if (isCardDiscardable(deductions, game_data)):
            lastDiscardableCard = False
            return lastDiscardableCard
    return lastDiscardableCard

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

def isCardPlayable(cardInfo, game_data):
    # We need certain info to infer in this function
    if (cardInfo[0] != None or cardInfo[1] != None):
        return False
    tableCards = []
    for number in game_data.tableCards[cardInfo[1]]:
        tableCards.append((number, cardInfo[1]))
    # Check if the previous card with respect to the one we're checking has already been played
    isPreviousHere = (cardInfo[0] == 1 or (cardInfo[0]-1, cardInfo[1]) in tableCards)
    # Check if the current card has not yet been played
    isSameNotHere = ((cardInfo[0], cardInfo[1]) in tableCards)
    return isPreviousHere and isSameNotHere

def isCardEverPlayable(cardInfo, game_data):
    tableCards = []
    for number in game_data.tableCards[cardInfo[1]]:
        tableCards.append((number, cardInfo[1]))
    # If the card has already been played once
    if (len(tableCards) >= cardInfo[0]):
        return False
    elif (len(tableCards) < cardInfo[0] - 1):
        # Check whether the cards in between have been discarded
        # e.g. the game pile is a 3 Red, both Red 4s in the discard, and I have a 5 Red in hand
        for i in range(len(tableCards)+1, cardInfo[0]):
            discardedCards = stackToTupleList(game_data.discardPile)
            discarded = len([card for card in discardedCards if (card[0] == i and card[1] == cardInfo[1])])
            if (discarded == numberFrequency[i-1]):
                return False
    return True

def isCardDangerous(cardInfo, game_data):
    if (not isCardEverPlayable(cardInfo, game_data)):
        return False
    if (cardInfo[0] == 5):
        return True
    discardedCards = stackToTupleList(game_data.discardPile)
    discarded = len([card for card in discardedCards if (card[0] == cardInfo[1] and card[1] == cardInfo[1])])
    if (discarded >= numberFrequency[cardInfo[0]-1]):
        return True
    return False

def playerKnowsWhatToPlay(playerName, game_data, hintMap):
    hasOptimistPlayableCard = False
    for card in hintMap[playerName]:
        if (card[2] == True and isCardPlayable((card[0], card[1]), game_data)):
            hasOptimistPlayableCard = True
    return hasOptimistPlayableCard

def findGivableHint(playerName, game_data, hintMap):
    
    return None

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
    lastOptimisticCards = getLastOptimistCardsOfPlayer(hintMap, playerName)
    deductions = getDeductions(playerName, game_data, hintMap)

    # Try to find a definitely playable card
    for i in range(game_data.handSize):
        playable = True
        for deduction in deductions[i]:
            if (not isCardPlayable(deduction, game_data.tableCards)):
                playable = False
                break
        if playable:
            return f"play {i}"

    # If strike tokens < 2, try to play an optimistic card
    if (game_data.usedStormTokens < 2 and len(lastOptimisticCards) > 0):
        # find the most recent optimist card that may be playable and play it
        for card in lastOptimisticCards:
            playable = False
            for deduction in deductions[i]:
                if (isCardPlayable(deduction, game_data.tableCards) and not isLastDiscardableCard(deductions[i], game_data)):
                    playable = True
                    break
            if playable:
                return f"play {i}"

    # If there are hints available, give one
    if (game_data.usedNoteTokens < 8):
        # If someone has a playable card (but with some hint uncertainty), give hint
        for player in game_data.players:
            if(player.name == playerName):
                continue
            if (not playerKnowsWhatToPlay(player.name, game_data, hintMap)):
                action = findGivableHint(player.name, game_data, hintMap)
                if (action != None):
                    return action

    # Discard safe card, if any


    # If 1st play and no playable cards in next player hand, give a hint on 5s or 2s


    # If none of the above, play a random card

    
    return input()