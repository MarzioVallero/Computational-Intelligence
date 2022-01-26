#!/usr/bin/env python3

import random

import GameData
from collections import Counter

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

def getFullDeck():
    fullDeck = []
    for _ in range(3):
        fullDeck.append((1, "red"))
        fullDeck.append((1, "yellow"))
        fullDeck.append((1, "green"))
        fullDeck.append((1, "blue"))
        fullDeck.append((1, "white"))
    for _ in range(2):
        fullDeck.append((2, "red"))
        fullDeck.append((2, "yellow"))
        fullDeck.append((2, "green"))
        fullDeck.append((2, "blue"))
        fullDeck.append((2, "white"))
    for _ in range(2):
        fullDeck.append((3, "red"))
        fullDeck.append((3, "yellow"))
        fullDeck.append((3, "green"))
        fullDeck.append((3, "blue"))
        fullDeck.append((3, "white"))
    for _ in range(2):
        fullDeck.append((4, "red"))
        fullDeck.append((4, "yellow"))
        fullDeck.append((4, "green"))
        fullDeck.append((4, "blue"))
        fullDeck.append((4, "white"))
    for _ in range(1):
        fullDeck.append((5, "red"))
        fullDeck.append((5, "yellow"))
        fullDeck.append((5, "green"))
        fullDeck.append((5, "blue"))
        fullDeck.append((5, "white"))
    return fullDeck

def getPossibleCards(game_data):
    tableCards = []
    for color in colors:
        for number in game_data.tableCards[color]:
            tableCards.append((number, color))
    otherPlayerCards = []
    for player in game_data.players:
        otherPlayerCards.append(stackToTupleList(player.hand))
    discardedCards = stackToTupleList(game_data.discardPile)
    tableCards.extend(card for card in otherPlayerCards)
    tableCards.extend(card for card in discardedCards)
    jointList = [item for sublist in tableCards for item in sublist]

    fullDeck = getFullDeck()

    c1 = Counter(jointList)
    c2 = Counter(fullDeck)

    diff = c2 - c1
    rem = list(diff.elements())
    rem = list(set(rem))

    return rem

# Get dict of tuples indexed by cardIndex containing (value, color, deductionLevel)
def getDeductions(playerName, game_data, hintMap):
    deductions = {}
    combinations = [(i, v, c) for i in range(game_data.handSize) for v in numbers for c in colors]
    possibleCards = getPossibleCards(game_data)
    for (i, v, c) in combinations:
        if (i not in deductions):
            deductions[i] = []
        if ((v in hintMap[playerName][i][0]) and (c in hintMap[playerName][i][1]) and isCardPossible(v, c, possibleCards)):
            deductions[i].append((v, c))
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

    if (len(tableCards) == 0 and len(discardedCards) == 0 and data.usedNoteTokens == 0 and data.usedStormTokens == 0):
        return True
    else:
        return False

def isCardDiscardable(deductionsOfSingleCard, game_data):
    # AI can discard a card that can never be played (already played or because of other discards)
    discardable = True
    for deduction in deductionsOfSingleCard:
        if (isCardEverPlayable(deduction, game_data)):
            discardable = False
    if discardable:
        return True

    # Don't discard necessarily dangerous cards
    dangerous = True
    for deduction in deductionsOfSingleCard:
        if (not isCardDangerous(deduction, game_data)):
            dangerous = False
    if dangerous:
        return False
    return True

def isLastDiscardableCard(deductions, cardIndex, game_data):
    lastDiscardableCard = True
    if(cardIndex == game_data.handSize-1):
        return lastDiscardableCard
    for i in range(cardIndex+1, game_data.handSize-1):
        if (isCardDiscardable(deductions[i], game_data)):
            lastDiscardableCard = False
            return lastDiscardableCard
    return lastDiscardableCard

def isCardPossible(value, color, possibleCards):
    if((value, color) in possibleCards):
        return True
    else:
        return False

def isCardPlayable(cardInfo, game_data):
    tableCards = []
    for number in game_data.tableCards[cardInfo[1]]:
        tableCards.append((number, cardInfo[1]))
    # Check if the previous card with respect to the one we're checking has already been played
    isPreviousHere = (cardInfo[0] == 1 or (cardInfo[0]-1, cardInfo[1]) in tableCards)
    # Check if the current card has not yet been played
    isSameNotHere = ((cardInfo[0], cardInfo[1]) not in tableCards)
    #return isPreviousHere and isSameNotHere
    return (len(tableCards) == (cardInfo[0] - 1))

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
        discardedCards = stackToTupleList(game_data.discardPile)
        for i in range(len(tableCards)+1, cardInfo[0]):
            discarded = len([card for card in discardedCards if (card[0] == cardInfo[0] and card[1] == cardInfo[1])])
            if (discarded == numberFrequency[i-1]):
                return False
    return True

def isCardDangerous(cardInfo, game_data):
    if (not isCardEverPlayable(cardInfo, game_data)):
        return False
    discardedCards = stackToTupleList(game_data.discardPile)
    discarded = len([card for card in discardedCards if (card[0] == cardInfo[0] and card[1] == cardInfo[1])])
    if (discarded == (numberFrequency[cardInfo[0] - 1] - 1)):
        return True
    return False

# If player's last hinted card is playable, return True. Else False.
def playerKnowsWhatToPlay(playerName, index, game_data, hintMap):
    if(playerName not in hintMap):
        hintMap[playerName] = []
        for i in range(5):
            hintMap[playerName].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])
    cardIndex = -1
    for card in game_data.players[index].hand:
        cardIndex = cardIndex + 1
        cardTruth = (card.value, card.color)
        if (hintMap[playerName][cardIndex][2] == True and isCardPlayable(cardTruth, game_data)):
            return True
    return False

# Find the first playable card and give a hint on it. If possible, give an optimistic hint
def findGivableHint(playerName, playerIndex, game_data, hintMap):
    # While we have not reached the second hinted card
    isFirstHintedCardOrBefore = True
    hasPlayableCard = False
    for i in range(len(game_data.players[playerIndex].hand)):
        card = game_data.players[playerIndex].hand[i]
        card = (card.value, card.color)
        cardHints = hintMap[playerName][i]
        if (isCardPlayable(card, game_data)):
            hasPlayableCard = True
            # We don't hint the first hinted card
            shouldHint = (len(cardHints[0]) > 1 and len(cardHints[1]) > 1) if isFirstHintedCardOrBefore else (len(cardHints[0]) > 1 or len(cardHints[1]) > 1)

            if shouldHint :
                # Find the type of hint to give, trying to find the most optimist one
                # (if there's a card with the same color, give the number hint)
                hintType = None
                hintContent = None
                sameColor = 0
                sameValue = 0
                # Why not iterate over all cards in hand? "i" vs "len(game_data.players[playerIndex].hand)"
                for cardIndex in range(0, i):
                    c = game_data.players[playerIndex].hand[cardIndex]
                    if(c.color == card[1]):
                        sameColor = sameColor + 1
                    if(c.value == card[0]):
                        sameValue = sameValue + 1
                if (sameColor > 1):
                    hintType = "value" if (len(cardHints[0]) > 1) else "color"
                    hintContent = card[0] if (len(cardHints[0]) > 1) else card[1]
                else:
                    hintType = "color" if (len(cardHints[1]) > 1) else "value"
                    hintContent = card[1] if (len(cardHints[1]) > 1) else card[0]
                print("Give hint type 1")
                return f"hint {hintType} {playerName} {hintContent}"

        # If the card has hints, we switch the condition
        if (len(cardHints[1]) > 1 or len(cardHints[0]) > 1):
            isFirstHintedCardOrBefore = False

    # Give a hint on the last card to avoid discard if possible
    lastCardPos = len(game_data.players[playerIndex].hand) - 1
    lastCardHints = hintMap[playerName][lastCardPos]
    lastCard = game_data.players[playerIndex].hand[lastCardPos]
    lastCard = (lastCard.value, lastCard.color)
    if (isCardDangerous(lastCard, game_data) and len(lastCardHints[1]) > 1 and
        len(lastCardHints[0]) > 1 and not hasPlayableCard):
        hintType = None
        hintContent = None
        # if it's a 5 and the number hint is not given
        if (lastCard[0] == 5 and len(lastCardHints[0]) > 1):
            hintType = "value"
            hintContent = 5
        elif (len(lastCardHints[1]) > 1):
            hintType = "color"
            hintContent = lastCard[1]
        else:
            hintType = "value"
            hintContent = lastCard[0]
        print("Give hint type 2")
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
    # PlayerName doesn't exist
    if (playerIndex == None):
        return discardableIndex

    for i in range(game_data.handSize):
        cardHints = hintMap[playerName][i]
        # If the card is definitely discardable (none of its deductions are playable)
        discardable = True
        for deduction in deductions[i]:
            if (isCardEverPlayable(deduction, game_data)):
                discardable = False
        if discardable:
            return i

        # If the card is unclued and not dangerous
        if (isCardDiscardable(deductions[i], game_data) and len(cardHints[1]) > 1 and
            len(cardHints[0]) > 1 and not uncluedDiscardableCard):
            uncluedDiscardableCard = True
            discardableIndex = i

        # If it's the first discardable card we find, regardless of being already clued
        if (isCardDiscardable(deductions[i], game_data) and discardableIndex == -1):
            discardableIndex = i

    return discardableIndex


def findDiscardIndex(playerName, game_data, hintMap):
    discardIndex = -1

    playerIndex = None
    for i in range(len(game_data.players)):
        if (game_data.players[i].name == playerName):
            playerIndex = i
            break
    # PlayerName doesn't exist
    if (playerIndex == None):
        return -1

    leastHintCount = 0
    # Discard the card of which I know least
    for i in range(game_data.handSize):
        numValueHints = len(hintMap[playerName][i][0])
        numColorHints = len(hintMap[playerName][i][1])
        newHintCount = numValueHints + numColorHints
        if ((newHintCount > leastHintCount) and (numValueHints > 1) and (numColorHints > 1)):
            leastHintCount = newHintCount
            discardIndex = i
    return discardIndex

# If all cards of a given value or color have been played,
# implicitly I know they can't be among my cards
def updateHintMap(game_data, hintMap, playerName):
    for player in game_data.players:  
        if(player.name not in hintMap):
            hintMap[player.name] = []
            for i in range(5):
                hintMap[player.name].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])      
    possibleCards = getPossibleCards(game_data)
    for value in numbers:
        count = sum(map(lambda x : x[0] == value, possibleCards))
        if count == 0:
            for i in range(game_data.handSize):
                if value in hintMap[playerName][i][0]:
                    hintMap[playerName][i][0].remove(value)
    for color in colors:
        count = sum(map(lambda x : x[1] == color, possibleCards))
        if count == 0:
            for i in range(game_data.handSize):
                if color in hintMap[playerName][i][1]:
                    hintMap[playerName][i][1].remove(color)
    return hintMap

def printHintMap(hintMap):
    if(not hintMap):
        return
    print("Hint Map:")
    players = list(hintMap.keys())
    players.sort()
    for player in players:
        print(f"    {player} hints:")
        if(player not in hintMap):
            print("No information")
        else:
            for entry in hintMap[player]:
                print(entry)

def play(playerName, status, game_data, hintMap):
    #printHintMap(hintMap)
    #printGameStats(game_data)

    # A hidden card has an array of deductions, i.e. possible values with deduction levels
    # A hidden card is said to be "optimistic" when it's (one of) the last card(s) that was designated for a hint
    # since the player last played.
    # When there are several possible deductions for a card, we always assume that playing it/ discarding it
    # leads to the worst possible outcome, unless it's an optimist card in which case we trust our partners :)
    # Before playing, each deduction will be assigned a status (IDeductionStatus)
    # (playing a 5) > (playing a playable card) > (happy discard) > (giving a hint) > (discard) > (sad discard) > (sad hint)

    # Get statistics
    lastOptimisticCards = getLastOptimistCardsOfPlayer(hintMap, playerName)
    # deductions contains the list of possible cards for each position 
    # in a player's hand given current public information
    hintMap = updateHintMap(game_data, hintMap, playerName)
    deductions = getDeductions(playerName, game_data, hintMap)
    
    # Try to find a definitely playable card
    for i in range(game_data.handSize):
        playable = True
        # A single deduction is a tuple (value, colour)
        # If all deductions are playable, it means that there's no drawback in playing it
        for deduction in deductions[i]:
            if (not isCardPlayable(deduction, game_data)):
                playable = False
        if playable:
            print("Definitely playable card ")
            return f"play {i}"

    # If storm tokens < 2, try to play an optimistic card
    # Add check on len(lastOptimisticCards)
    # Invert not isLastDiscardable
    # Remove all other optimistic cards before committing play
    if (game_data.usedStormTokens < 2):
        # find the most recent optimist card that may be playable and play it
        for i in lastOptimisticCards:
            # Count positive cases vs all cases
            playable = False
            isLastDiscardable = isLastDiscardableCard(deductions, i, game_data)
            for deduction in deductions[i]:
                if (isCardPlayable(deduction, game_data) and not isLastDiscardable):
                    playable = True
                    break
            if playable:
                print("Optimistic play ")
                return f"play {i}"

    # If there are hints available, give one
    if (game_data.usedNoteTokens < 8):
        # If someone has a playable card (but with some hint uncertainty), give hint
        index = -1
        for player in game_data.players:
            index = index + 1
            if(player.name == playerName):
                continue
            elif (not playerKnowsWhatToPlay(player.name, index, game_data, hintMap)):
                action = findGivableHint(player.name, index, game_data, hintMap)
                if (action != None):
                    return action

    # Discard safe card, if any
    if (game_data.usedNoteTokens > 0):
        discardableIndex = findBestDiscardIndex(playerName, game_data, hintMap, deductions)
        if (discardableIndex != -1):
            print("Discard card type 1")
            return f"discard {discardableIndex}"

    # If 1st play or I got nothing better to do, give a hint on unhinted 5s or 2s
    if (isFirstMove(game_data)):
        index = -1
        for player in game_data.players:
            index = index + 1
            if(player.name == playerName):
                continue
            nextPlayerHand = game_data.players[index].hand
            cardIndex = -1
            for card in nextPlayerHand:
                cardIndex = cardIndex + 1
                if (card.value == 5 and len(hintMap[player.name][cardIndex][0]) > 1):
                    print("First move hint ")
                    return f"hint value {player.name} 5"
                elif (card.value == 5 and len(hintMap[player.name][cardIndex][1]) > 1):
                    print("Give hint type 3")
                    return f"hint color {player.name} {card.color}"
            # If next player has no 5, give a hint on 2s (positive or negative)
            cardIndex = -1
            for card in nextPlayerHand:
                cardIndex = cardIndex + 1
                if (card.value == 2 and len(hintMap[player.name][cardIndex][0]) > 1):
                    print("First move hint ")
                    return f"hint value {player.name} 2"
                elif (card.value == 2 and len(hintMap[player.name][cardIndex][1]) > 1):
                    print("Give hint type 4")
                    return f"hint color {player.name} {card.color}"

    # Add somewhat useful hint (for information completion)

    # Discard a card only based on how little I know about it 
    # (dangerous cards should be always hinted to immediately)
    if (game_data.usedNoteTokens > 0):
        discardableIndex = findDiscardIndex(playerName, game_data, hintMap)
        if (discardableIndex != -1):
            print("Discard card type 2")
            return f"discard {discardableIndex}"

    # If none of the above, do a random action
    # Just avoid getting a 0 score
    print("DESPERATE MOVE")
    randomChoice = random.choice(range(game_data.handSize))
    randomOtherPlayer = random.choice([player for player in game_data.players if player.name != playerName])
    randomType = random.choice(["value", "color"])
    randomHint = randomOtherPlayer.hand[0].value if randomType == "value" else randomOtherPlayer.hand[0].color
    if (game_data.usedNoteTokens < 8):
        return f"hint {randomType} {randomOtherPlayer.name} {randomHint}"
    else:
        return f"discard {randomChoice}"