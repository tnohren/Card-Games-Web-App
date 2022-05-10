import itertools
from .models import *
from .CardandDeck import *

"""
    CARDS FUNCTIONS
"""
# Returns All Available Cards
# Also Ensures Proper # of Cards Exist
def GetCardsList():
    cards = Cards.objects.all()
    print(cards)
    if len(cards) != 52:
        for val, st in itertools.product(range(0,13), range(0,4)):
            newCard = Cards(suit=st, value=val)
            newCard.save()
        cards = Cards.objects.all()
    return cards

def CreateNewDeck() -> Deck:
    deck = Deck()
    for card in GetCardsList():
        deck.AddCard({'suit': card.suit, 'value': card.value})
    deck.Shuffle()
    return deck

def GetCardSuitDisplay(cardSuit: int) -> str:
    return Cards.objects.filter(suit=cardSuit).first().get_suit_display()

def GetCardValueDisplay(cardValue: int) -> str:
    return Cards.objects.filter(value=cardValue).first().get_value_display()

"""
    GAMETYPES FUNCTIONS
"""
# Returns All Available GameTypes
# Also Ensures Proper GameTypes Exist
def GetGameTypes():
    gameTypes = GameTypes.objects.all()
    if len(gameTypes) != 2:
        for gameType in ['B', 'P']:
            newGameType = GameTypes(gameType=gameType)
            newGameType.save()
        gameTypes = GameTypes.objects.all()
    return gameTypes
