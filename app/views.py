"""
Definition of views.
"""
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .statictables import *
from .dynamictables import *
from .CardandDeck import *

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def home2(request, ignore):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def SignUp(request):
    """ Renders sign up page """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            raw_password2 = form.cleaned_data.get('password2')
            user = authenticate(username=username, password1=raw_password, password2=raw_password2)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            else:
                return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'app/signup.html', {'form': form})

# Start Playing - Give Player Choice Which Game Type to Play
def StartGame(request):
    gameTypes = GetGameTypes()
    promptList = ["Which card game would you like to play?"]
    buttonList = []
    for gameType in gameTypes:
        buttonList.append({'value': gameType.gameType,'display_value': gameType.get_gameType_display(), 'callback': 'loadornewgame'})
    return render(request, "app/prompt.html", {'promptList': promptList, 'buttonList': buttonList})

# Ask Player Whether to Load an Existing Game or Start a New Game
def LoadOrNewGame(request, gameType):
    gameTypeObject = GameTypes.objects.filter(gameType=gameType)
    if gameTypeObject.exists():
        gameTypeObject = gameTypeObject.first()
        gameTypeDisplay = gameTypeObject.get_gameType_display()
        promptList = ["Would you like to load a saved game or start a new game?"]
        buttonList = [{'value': gameType, 'display_value': 'Load Game', 'callback': 'loadgame'},
                      {'value': gameType, 'display_value': 'New Game', 'callback': 'newgame'}]
    else:
        promptList = ["Invalid choice. Please choose again."]
        gameTypes = GetGameTypes()
        buttonList = []
        for gameType in gameTypes:
            buttonList.append({'value': gameType.gameType, 'display_value': gameType.get_gameType_display(), 'callback': 'loadornewgame'})
    return render(request, "app/prompt.html", {'promptList': promptList, 'buttonList': buttonList})

# Give Player Choice of Which Game to Load - TODO
def LoadGame(request, gameType):
    if request.user.is_authenticated:
        gameTypeObject = GameTypes.objects.filter(gameType=gameType)
        if gameTypeObject.exists():
            return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('login')

# Begin New Game
def NewGame(request, gameType):
    if request.user.is_authenticated:
        gameTypeObject = GameTypes.objects.filter(gameType=gameType)
        if gameTypeObject.exists():
            # Create a New User Game and Get its Game Number
            gameNumber = CreateUserGame(user=request.user, gameType=gameType)

            # Create Deck and Hands
            deck = CreateNewDeck()
            hands = []
            players = []
            if gameType == 'B':
                # Define Blackjack Players
                players = ['Player', 'Dealer']
            else:
                # Define Poker Players
                players = ['Player', 'Opponent1', 'Opponent2', 'Opponent3']

            # Create Hands for Each Player
            for player in players:
                newPlayer = CreatePlayer(gameNumber, player)
                cards = Hand(2, deck)
                hands.append({'gamePlayer': newPlayer.gamePlayer, 'hand': cards.hd})

            # Save Deck and Hands
            CreatePlayer(gameNumber, "Deck")
            hands.append({'gamePlayer': 'Deck', 'hand': deck.dk})
            SaveHands(gameNumber=gameNumber, hands=hands)

            if gameType == 'B':
                # Begin Playing Blackjack
                return PlayBlackjack(request, gameNumber)
            else:

                # TODO: BEGIN PLAYING POKER - for now return home
                return redirect('home')
        else:
            # Redirect home if invalid game
            return redirect('home')

    else:
        # If not logged in, redirect to login page
        return redirect('login')

# Play Blackjack Game
def PlayBlackjack(request, gameNumber):
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
                              {'value': gameNumber, 'display_value': 'Stay', 'callback': 'hit'}]
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
def HandleDealerTurn(request, gameNumber):
    # Create Deck and Dealer Hand
    dbDeck = GameHands.objects.fitler(gameNumber=gameNumber, gamePlayer="Deck").all()
    deck = Deck()
    for card in dbDeck:
        deck.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

    dbDealerHand = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()
    dealerHand = Hand()
    for card in dbDealerHand:
        dealerHand.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

    # Continue adding cards until dealer has at least 16
    while (ScoreCheck(gameNumber, "Dealer") < 16):
        drawnCard = deck.Draw()
        dealerHand.AddCard(drawnCard)
        GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck", cardSuit=drawnCard['suit'], cardValue=drawnCard['value']).delete()
        GameHands.objects.create(gameNumber=gameNumber, gamePlayer="Dealer", cardSuit=drawnCard['suit'], cardValue=drawnCard['value'])

    # Set appropriate message
    gameMessage = ""
    if (ScoreCheck(gameNumber, "Dealer") > 21):
        gameMessage = "Dealer busted. You win!"
    else:
        gameResult = DetermineBlackjackWinner(gameNumber)
        if gameResult == "Player":
            gameMessage = "You win!"
        elif gameResult == "Dealer":
            gameMessage = "Dealer wins :("
        else:
            gameMessage = "Tie!"

    # Set prompt, button, and card lists for display
    promptList = [gameMessage, "Would you like to return to the homepage or start a new game?"]
    buttonList = [{'value': 'B', 'display_value': 'New Game', 'callback': 'newgame'},
                  {'value': '', 'display_value': 'Home', 'callback': 'home'}]
    dealerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()]
    playerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()]

    # Save game as complete
    SaveUserGame(username=request.user.username, gameType="B", gameStatus="Complete")

    # Render page
    return render(request, "app/prompt.html", {'dealerHand': dealerHand, 'playerHand': playerHand, 'promptList': promptList, 'buttonList': buttonList})

# Handle Blackjack Stay
def HandleStay(request, gameNumber):
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
def HandleHit(request, gameNumber):
    if request.user.is_authenticated:
        # Ensure Game Exists and it's the Player's Turn
        inProgressGame = InProgressGames.objects.filter(gameNumber=gameNumber, gameStatus="PlayerTurn")
        if inProgressGame.exists():
            inProgressGame = inProgressGame.first()

            # Retrieve deck and player hand
            dbDeck = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck").all()
            deck = Deck()
            for card in dbDeck:
                deck.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

            dbPlayerHand = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()
            playerHand = Hand()
            for card in dbPlayerHand:
                playerHand.AddCard({'suit': card.cardSuit, 'value': card.cardValue})

            # Give player new card from the deck
            drawnCard = deck.Draw()
            playerHand.AddCard(drawnCard)
            GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Deck", cardSuit=drawnCard['suit'], cardValue=drawnCard['value']).delete()
            GameHands.objects.create(gameNumber=gameNumber, gamePlayer="Player", cardSuit=drawnCard['suit'], cardValue=drawnCard['value'])

            # Check if player busted
            if BustCheck(gameNumber, "Player"):
                # Handle Bust
                return HandleBust(request, gameNumber)
            else:
                # Player Did Not Bust, Continue
                return PlayBlackjack(request, gameNumber)

        else:
            # Game doesn't exist or is in invalid status
            return redirect('home')
    else:
        # If not logged in, redirect to login page
        return redirect('login')

# Player Bust Screen
def HandleBust(request, gameNumber):
    promptList = ["You busted :(", "Would you like to return to the homepage or start a new game?"]
    buttonList = [{'value': 'B', 'display_value': 'New Game', 'callback': 'newgame'},
                  {'value': 'B', 'display_value': 'Home', 'callback': 'home2'}]
    dealerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Dealer").all()]
    playerHand = [{'suit': GetCardSuitDisplay(card.cardSuit), 'value': GetCardValueDisplay(card.cardValue)} for card in GameHands.objects.filter(gameNumber=gameNumber, gamePlayer="Player").all()]
    return render(request, "app/prompt.html", {'dealerHand': dealerHand, 'playerHand': playerHand, 'promptList': promptList, 'buttonList': buttonList})

# Calculate Score of Specified Player
def ScoreCheck(gameNumber, gamePlayer):
    score = 0
    aces = []
    dbPlayerHand = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer=gamePlayer).all()
    for card in dbPlayerHand:
        if card.cardValue == 0:
            aces.append(card)
        elif card.cardValue > 8:
            score += 10
        else:
            score += (card.cardValue + 1)
        # Automatically Handle Ace Calculation
        for card in aces:
            if (score < (11 - len(aces))):
                score += 11
            else:
                score += 1
    return score

# Determine Blackjack Winner
def DetermineBlackjackWinner(gameNumber):
    playerScore = ScoreCheck(gameNumber, "Player")
    dealerScore = ScoreCheck(gameNumber, "Dealer")
    if playerScore > dealerScore:
        return "Player"
    elif playerScore == dealerScore:
        return "Tie"
    else:
        return "Dealer"

# Returns whether or not a specified player busted
def BustCheck(gameNumber, gamePlayer):
    return (ScoreCheck(gameNumber, gamePlayer) > 21)