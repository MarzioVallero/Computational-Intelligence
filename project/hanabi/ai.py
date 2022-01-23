#!/usr/bin/env python3

import random
import GameData

colors = ["green", "red", "blue", "yellow", "white"]
numbers = [1, 2, 3, 4, 5]
numberFrequency = [3, 2, 2, 2, 1]
start = True

def printGameStats(data):
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

def getLastOptimistCardsOfPlayer(hintMap, playerName):
    optimisticCards = []
    if(playerName not in hintMap):
        return optimisticCards
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
            hintMap[playerName] = [[None, None, False], [None, None, False], [None, None, False], [None, None, False], [None, None, False]]
        if ((hintMap[playerName][i][0] == None or hintMap[playerName][i][0] == v) and
            (hintMap[playerName][i][1] == None or hintMap[playerName][i][1] == c) and
            isCardPossible(v, c, game_data)):
                if (i not in deductions):
                    deductions[i] = []
                deductions[i].append((v, c, 0))
    return deductions

def stackToTupleList(stack):
    tupleList = []
    for card in stack:
        tupleList.append((card.value, card.color))
    return tupleList

def isFirstMove(data):
    tableCards = []
    for color in colors:
        for number in data.tableCards[color]:
            tableCards.append((number, color))
    discardedCards = stackToTupleList(data.discardPile)

    print(tableCards, discardedCards)

    if (len(tableCards) == 0 and len(discardedCards) == 0 and data.usedNoteTokens == 0 and data.usedStormTokens == 0):
        return True
    else:
        return False

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

def isLastDiscardableCard(deductions, cardIndex, game_data):
    lastDiscardableCard = True
    for i in range(cardIndex, game_data.handSize):
        if (isCardDiscardable(deductions[i], game_data)):
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
    if (cardInfo[0] == None or cardInfo[1] == None):
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
    # Is a card dangerous if I know nothing about it?
    if (cardInfo[0] == None and cardInfo[1] == None):
        return False
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
    if(playerName not in hintMap):
        hintMap[playerName] = [[None, None, False], [None, None, False], [None, None, False], [None, None, False], [None, None, False]]
        return hasOptimistPlayableCard
    for card in hintMap[playerName]:
        if (card[2] == True or isCardPlayable((card[0], card[1]), game_data)):
            hasOptimistPlayableCard = True
    return hasOptimistPlayableCard

# Find the first playable card and give a hint on it. If possible, give an optimistic hint
def findGivableHint(playerName, playerIndex, game_data, hintMap, deductions):
    # While we have not reached the second hinted card
    isFirstHintedCardOrBefore = True
    hasPlayableCard = False
    for i in range(len(game_data.players[playerIndex].hand)):
        cardTruthValues = game_data.players[playerIndex].hand[i]
        card = (cardTruthValues.value, cardTruthValues.color)
        cardHints = hintMap[playerName][i]
        if (isCardPlayable(card, game_data)):
            hasPlayableCard = True
            # We don't hint the first hinted card
            shouldHint = (cardHints[1] == None and cardHints[0] == None) if isFirstHintedCardOrBefore else (cardHints[1] == None or cardHints[0] == None)

            if shouldHint :
                # Find the type of hint to give, trying to find the most optimist one
                # (if there's a card with the same color, give the number hint)
                hintType = None
                hintContent = None
                sameColor = 0
                for c in game_data.players[playerIndex].hand:
                    if(c[1] == card[1]):
                        sameColor = sameColor + 1
                if (sameColor > 1):
                    hintType = "value" if (cardHints[0] == None) else "color"
                    hintContent = cardTruthValues.value if (cardHints[0] == None) else cardTruthValues.color
                else:
                    hintType = "color" if (cardHints[1] == None) else "value"
                    hintContent = cardTruthValues.color if (cardHints[1] == None) else cardTruthValues.value
                return f"hint {hintType} {playerName} {hintContent}"

        # If the card has hints, we switch the condition
        if (cardHints[1] == None or cardHints[0] == None):
            isFirstHintedCardOrBefore = False

    # Give a hint on the last card to avoid discard if possible
    lastCardPos = len(game_data.players[playerIndex].hand) - 1
    lastCardHints = hintMap[playerName][lastCardPos]
    lastCardTruthValues = game_data.players[playerIndex].hand[lastCardPos]
    lastCard = (lastCardTruthValues.value, lastCardTruthValues.color)
    if (lastCardHints[1] == None and lastCardHints[0] == None and isCardDangerous(lastCard, game_data) and not hasPlayableCard):
        hintType = None
        hintContent = None
        cardTruthValues = game_data.players[playerIndex].hand[i]
        # if it's a 5 and the number hint is not given
        if (lastCard[0] == 5 and lastCardHints[0] == None):
            hintType = "value"
            hintContent = lastCardTruthValues.value
        else:
            hintType = "color"
            hintContent = lastCardTruthValues.color
        return f"hint {hintType} {playerName} {hintContent}"

    return None

def findBestDiscardIndex(playerName, game_data, hintMap, deductions):
    uncluedDiscardableCard = False
    discardableIndex = -1

    playerIndex = None
    for i in range(len(game_data.players)):
        if (game_data.players[i].name == playerName):
            playerIndex = i
            break
    if (playerIndex != None):
        return discardableIndex

    for i in range(len(game_data.players[playerIndex].hand)):
        card = hintMap[playerName][i]
        # If the card is definitely discardable (never playable)
        discardable = True
        for deduction in deductions[i]:
            if (isCardEverPlayable((deduction[0], deduction[1]), game_data)):
                discardable = False
        if discardable:
            discardableIndex = i
            break

        # If the card is unclued and not dangerous
        if (isCardDiscardable(deductions, game_data) and card[1] == None and
            card[0] == None and not uncluedDiscardableCard):
            uncluedDiscardableCard = True
            discardableIndex = i

        # If it's the first discardable card we find, regardless of being already clued
        if (isCardDiscardable(deductions, game_data) and discardableIndex == -1):
            discardableIndex = i

    return discardableIndex

def play(playerName, status, game_data, hintMap):
    print(playerName, status, hintMap)
    printGameStats(game_data)

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
            if (not isCardPlayable(deduction, game_data)):
                playable = False
                break
        if playable:
            return f"play {i}"

    # If strike tokens < 2, try to play an optimistic card
    if (game_data.usedStormTokens < 2 and len(lastOptimisticCards) > 0):
        # find the most recent optimist card that may be playable and play it
        for i in lastOptimisticCards:
            playable = False
            isLastDiscardable = isLastDiscardableCard(deductions, i, game_data)
            for deduction in deductions[i]:
                if (isCardPlayable(deduction, game_data) and not isLastDiscardable):
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
    if (game_data.usedNoteTokens > 0):
        discardableIndex = findBestDiscardIndex(playerName, game_data, hintMap, deductions)
        if (discardableIndex > -1):
            return f"discard {discardableIndex}"

    # If 1st play and no playable cards in next player hand, give a hint on 5s or 2s
    if (isFirstMove(game_data)):
        index = -1
        for player in game_data.players:
            index = index + 1
            if(player.name == playerName):
                continue
            nextPlayerHand = game_data.players[index].hand
            cIndex = -1
            for card in nextPlayerHand:
                cIndex = cIndex + 1
                if (card.value == 5):
                    return f"hint value {game_data.players[index].name} 5"
            # If next player has no 5, give a hint on 2s (positive or negative)
            cIndex = -1
            for card in nextPlayerHand:
                cIndex = cIndex + 1
                if (card.value == 2):
                    return f"hint value {game_data.players[index].name} 2"

    # If none of the above, play a random card
    print("DESPERATE MOVE")
    randomChoice = random.choice(range(5))
    return f"play {randomChoice}"