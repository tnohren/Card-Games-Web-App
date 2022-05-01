import random
import itertools

# To Store Current Game Deck While Playing
class Deck:
    def __init__(self):
        self.dk = []

    def __len__(self):
        return len(self.dk)

    def Shuffle(self):
        random.shuffle(self.dk)

    def Draw(self):
        return self.dk.pop(-1)

    def AddCard(self, newCard):
        self.dk.append(newCard)

# To Store Current Game Hands While Playing
class Hand:
    def __init__(self, numberOfCards = 0, deck = []):
        self.hd = []
        for i in range(numberOfCards):
            self.AddCard(deck.Draw())

    def __len__(self):
        return len(self.hd)

    def AddCard(self, newCard):
        self.hd.append(newCard)