from datetime import datetime
from typing import Union
from django.http.response import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, authenticate
from .models import *
from .statictables import *
from .dynamictables import *
from .CardandDeck import *

# Play Blackjack Game
def PlayBlackjack(request: HttpRequest, gameNumber: int) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        # Make Sure Game Exists
        inProgressGame = InProgressGames.objects.filter(gameNumber=gameNumber)
        if inProgressGame.exists():
            inProgressGame = inProgressGame.first()
            # If the game is just beginning, then it is the player's turn
            if inProgressGame.gameStatus == "Begin":
                inProgressGame.gameStatus = "PlayerTurn"
                inProgressGame.save()

            # Start Player's Turn
            if inProgressGame.gameStatus == "PlayerTurn":
                promptList = ["Would you like to hit or stay?"]
                buttonList = [{'value': gameNumber, 'display_value': 'Hit', 'callback': 'hit'},
                              {'value': gameNumber, 'display_value': 'Stay', 'callback': 'stay'}]
                dealerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()]
                playerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()]
                return render(request, "app/prompt.html", {'dealerHand': dealerHand, 'playerHand': playerHand, 'promptList': promptList, 'buttonList': buttonList}) 

            # Start Dealer's Turn
            elif inProgressGame.gameStatus == "DealerTurn":
                return HandleDealerTurn(request, gameNumber)

            else:
                return redirect('home')
        else:
            return redirect('home')
    else:
        # If not logged in, redirect to login page
        return redirect('login')

# Handle Dealer Turn
def HandleDealerTurn(request: HttpRequest, gameNumber: int) -> HttpResponse:
    # Create Deck
    dbDeck = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck").all()
    deck = Deck()
    for card in dbDeck: deck.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

    # Create Dealer Hand
    dbDealerHand = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()
    dealerHand = Hand()
    for card in dbDealerHand: dealerHand.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

    # Continue adding cards until dealer has at least 16
    while (BlackjackScoreCheck(gameNumber, "Dealer") < 16):
        drawnCard = deck.Draw()
        dealerHand.AddCard(drawnCard)
        GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck", cardSuit=drawnCard['suit'], cardValue=drawnCard['value']).delete()
        GameHands.objects.create(gameNumber=gameNumber, gamePlayer="Dealer", cardSuit=drawnCard['suit'], cardValue=drawnCard['value'])

    # Set appropriate message
    gameMessage = ""
    if (BlackjackScoreCheck(gameNumber, "Dealer") > 21):
        gameMessage = "Dealer busted. You win!"
    else:
        gameResult = DetermineBlackjackWinner(gameNumber)
        gameMessage = "You win!" if gameResult == "Player" else ("Dealer wins :(" if gameResult == "Dealer" else "Tie!")

    # Set prompt, button, and card lists for display
    promptList = [gameMessage, "Would you like to return to the homepage or start a new game?"]
    buttonList = [{'value': 'B', 'display_value': 'New Game', 'callback': 'newgame'},
                  {'value': 'B', 'display_value': 'Home', 'callback': 'home2'}]
    dealerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()]
    playerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()]

    # Save game as complete
    SaveUserGame(user=request.user, gameType="B", gameNumber=gameNumber, gameStatus="Complete")

    # Render page
    return render(request, "app/prompt.html", {'dealerHand': dealerHand, 'playerHand': playerHand, 'promptList': promptList, 'buttonList': buttonList})

# Handle Blackjack Stay
def HandleStay(request: HttpRequest, gameNumber: int) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        # Ensure Game Exists and it's the Player's Turn
        inProgressGame = InProgressGames.objects.filter(gameNumber=gameNumber, gameStatus="PlayerTurn")
        if inProgressGame.exists():
            inProgressGame = inProgressGame.first()

            # Player chose to stay, so set to dealer's turn
            inProgressGame.gameStatus = "DealerTurn"
            inProgressGame.save()

            # Next Game Cycle
            return PlayBlackjack(request, gameNumber)
        else:
            # Game doesn't exist or is in an invalid status
            return redirect('home')
    else:
        # If not logged in, redirect to login page
        return redirect('login')

# Handle Blackjack Hit
def HandleHit(request: HttpRequest, gameNumber: int) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        # Ensure Game Exists and it's the Player's Turn
        if InProgressGames.objects.filter(gameNumber=gameNumber, gameStatus="PlayerTurn").exists():
            # Create Deck
            dbDeck = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck").all()
            deck = Deck()
            for card in dbDeck: deck.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

            # Create Player Hand
            dbPlayerHand = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()
            playerHand = Hand()
            for card in dbPlayerHand: playerHand.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

            # Give player new card from the deck
            drawnCard = deck.Draw()
            playerHand.AddCard(drawnCard)
            GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck", cardSuit=drawnCard['suit'], cardValue=drawnCard['value']).delete()
            GameHands.objects.create(gameNumber=gameNumber, gamePlayer="Player", cardSuit=drawnCard['suit'], cardValue=drawnCard['value'])

            # Determine if Player Busted and Handle Next Part of Game Flow
            return HandleBust(request, gameNumber) if BustCheck(gameNumber, "Player") else PlayBlackjack(request, gameNumber)
        else:
            # Game doesn't exist or is in invalid status
            return redirect('home')
    else:
        # If not logged in, redirect to login page
        return redirect('login')

# Player Bust Screen
def HandleBust(request: HttpRequest, gameNumber: int) -> HttpResponse:
    promptList = ["You busted :(", "Would you like to return to the homepage or start a new game?"]
    buttonList = [{'value': 'B', 'display_value': 'New Game', 'callback': 'newgame'},
                  {'value': 'B', 'display_value': 'Home', 'callback': 'home2'}]
    dealerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()]
    playerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()]
    return render(request, "app/prompt.html", {'dealerHand': dealerHand, 'playerHand': playerHand, 'promptList': promptList, 'buttonList': buttonList})

# Calculate Score of Specified Player
def BlackjackScoreCheck(gameNumber: int, gamePlayer: str) -> int:
    score = 0
    aces = []
    for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer=gamePlayer).all():
        if card.cardValue == 0: aces.append(card) # Handle aces separately
        else: score = (score + 10) if card.cardValue > 8 else (score + card.cardValue + 1) # K, Q, J, 10 all worth 10. Otherwise, worth face value

    # Automatically Handle Ace Calculation
    for card in aces: score = (score + 11) if (score < (11 - len(aces))) else (score + 1)

    # Return Score
    return score

# Determine Blackjack Winner
def DetermineBlackjackWinner(gameNumber: int) -> str:
    playerScore = BlackjackScoreCheck(gameNumber, "Player")
    dealerScore = BlackjackScoreCheck(gameNumber, "Dealer")
    return "Player" if playerScore > dealerScore else ("Tie" if playerScore == dealerScore else "Dealer")

# Returns whether or not a specified player busted
def BustCheck(gameNumber: int, gamePlayer: str) -> bool:
    return (BlackjackScoreCheck(gameNumber, gamePlayer) > 21)