#!/usr/bin/env python3

import itertools
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

# Find the first playable card and give a hint on it. If possible, give an optimistic hint
def findGivableHint(playerName, playerIndex, game_data, hintMap, deductions):
    # While we have not reached the second hinted card
    isFirstHintedCardOrBefore = True
    hasPlayableCard = False
    for i in range(5):
        card = hintMap[playerName][i]
        if (isCardPlayable(card, game_data)):
            hasPlayableCard = True
            # We don't hint the first hinted card
            shouldHint = (card[1] == None and card[0] == None) if isFirstHintedCardOrBefore else (card[1] == None or card[0] == None)

            if shouldHint :
                # Find the type of hint to give, trying to find the most optimist one
                # (if there's a card with the same color, give the number hint)
                hintType = None
                hintContent = None
                cardTruthValues = game_data.player[playerIndex].hand[i]
                sameColor = 0
                for c in hintMap[playerName]:
                    if(c[1] == card[1]):
                        sameColor = sameColor + 1
                if (sameColor > 1):
                    hintType = "value" if (card[0] == None) else "color"
                    hintContent = cardTruthValues.value if (card[0] == None) else cardTruthValues.color
                else:
                    hintType = "color" if (card[1] == None) else "value"
                    hintContent = cardTruthValues.color if (card[1] == None) else cardTruthValues.value
                return f"hint {hintType} {playerName} {hintContent}"

        # If the card has hints, we switch the condition
        if (card[1] == None or card[0] == None):
            isFirstHintedCardOrBefore = False

    # Give a hint on the last card to avoid discard if possible
    lastCardPos = len(game_data.player[playerIndex].hand) - 1
    lastCard = hintMap[playerName][lastCardPos]
    lastCardTruthValues = game_data.player[playerIndex].hand[lastCardPos]
    if (isCardDangerous(lastCard, game_data) and lastCard[1] == None and
        lastCard[0] == None and not hasPlayableCard):
        hintType = None
        hintContent = None
        cardTruthValues = game_data.player[playerIndex].hand[i]
        # if it's a 5 and the number hint is not given
        if (lastCard[0] == 5 or lastCard[0] == None):
            hintType = "value"
            hintContent = lastCardTruthValues.value
        else:
            hintType = "color"
            hintContent = lastCardTruthValues.color
        return f"hint {hintType} {playerName} {hintContent}"

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
        index = -1
        for player in game_data.players:
            index = index + 1
            if(player.name == playerName):
                continue
            if (not playerKnowsWhatToPlay(player.name, game_data, hintMap)):
                action = findGivableHint(player.name, index, game_data, hintMap, deductions)
                if (action != None):
                    return action

    # Discard safe card, if any
    


    # If 1st play and no playable cards in next player hand, give a hint on 5s or 2s


    # If none of the above, play a random card

    
    return input()