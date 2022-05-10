"""
Definition of views.
"""
from datetime import datetime
from typing import Union
from django.http.response import HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponseRedirectBase
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .statictables import *
from .dynamictables import *
from .CardandDeck import *
from .Blackjack import *

# Renders Home Page
def home(request: HttpRequest, ignore: str = "") -> HttpResponse:
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

# Renders Contact Page
def contact(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

# Renders About Page
def about(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

# New User Sign Up
def SignUp(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
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
def StartGame(request: HttpRequest) -> HttpResponse:
    promptList = ["Which card game would you like to play?"]
    buttonList = [{'value': gameType.gameType, 'display_value': gameType.get_gameType_display(), 'callback': 'loadornewgame'} for gameType in GetGameTypes()]
    return render(request, "app/prompt.html", {'promptList': promptList, 'buttonList': buttonList})

# Ask Player Whether to Load an Existing Game or Start a New Game
def LoadOrNewGame(request: HttpRequest, gameType: str) -> HttpResponse:
    gameTypeObject = GameTypes.objects.filter(gameType=gameType)
    promptList = ["Would you like to load a saved game or start a new game?"] if gameTypeObject.exists() else ["Invalid choice. Please choose again."]
    buttonList = []
    if gameTypeObject.exists():
        buttonList = [{'value': gameType, 'display_value': 'Load Game', 'callback': 'loadgame'},
                      {'value': gameType, 'display_value': 'New Game', 'callback': 'newgame'}]
    else:
        buttonList = [{'value': gameType.gameType, 'display_value': gameType.get_gameType_display(), 'callback': 'loadornewgame'} for gameType in GetGameTypes()]
    return render(request, "app/prompt.html", {'promptList': promptList, 'buttonList': buttonList})

# Give Player Choice of Which Game to Load
def LoadGame(request: HttpRequest, gameType: str) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        if GameTypes.objects.filter(gameType=gameType).exists():
            # Check if any in progress games exist and if not, return home (for now)
            dbSavedGames = SavedGames.objects.filter(profileName=request.user, gameType=gameType, gameOutcome=False)
            if dbSavedGames.exists():
                callback = 'loadblackjack' if gameType == 'B' else 'loadpoker'
                promptList = ["Which saved game would you like to play?"]
                buttonList = [{'value': inProgressGame.gameNumber, 'display_value': inProgressGame.gameNumber, 'callback': callback} for inProgressGame in dbSavedGames]
                return render(request, "app/prompt.html", {'promptList': promptList, 'buttonList': buttonList})
            else:
                return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('login')

# Load Selected Blackjack Game
def LoadBlackjack(request: HttpRequest, gameNumber: int) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        dbSavedGame = SavedGames.objects.filter(profileName=request.user, gameType='B', gameOutcome=False)
        return PlayBlackjack(request, gameNumber) if dbSavedGame.exists() else redirect('home')
    else:
        return redirect('home')

# Load Selected Poker Game
def LoadPoker(request: HttpRequest, gameNumber: int) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    return redirect('home')

# Begin New Game
def NewGame(request: HttpRequest, gameType: str) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
    if request.user.is_authenticated:
        if GameTypes.objects.filter(gameType=gameType).exists():
            # Create a New User Game and Get its Game Number
            gameNumber = CreateUserGame(user=request.user, gameType=gameType)

            # Create Deck and Hands
            deck = CreateNewDeck()
            players = ['Player', 'Dealer'] if gameType == 'B' else ['Player', 'Opponent1', 'Opponent2', 'Opponent3']
            hands = [{'gamePlayer': CreatePlayer(gameNumber, player).gamePlayer, 'hand': Hand(2, deck).hd} for player in players]
            hands.append({'gamePlayer': 'Deck', 'hand': deck.dk})

            # Save Deck and Hands
            CreatePlayer(gameNumber, "Deck")
            SaveHands(gameNumber=gameNumber, hands=hands)

            # Begin Playing Blackjack or Poker
            # TODO - Poker
            return PlayBlackjack(request, gameNumber) if gameType == 'B' else redirect('home')
        else:
            # Redirect home if invalid game
            return redirect('home')

    else:
        # If not logged in, redirect to login page
        return redirect('login')