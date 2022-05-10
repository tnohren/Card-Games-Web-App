import random

# To Store Current Game Deck While Playing
class Deck:
    def __init__(self) -> None:
        self.dk = []

    def __len__(self) -> int:
        return len(self.dk)

    def Shuffle(self) -> None:
        random.shuffle(self.dk)

    def Draw(self):
        return self.dk.pop(-1)

    def AddCard(self, newCard) -> None:
        self.dk.append(newCard)

# To Store Current Game Hands While Playing
class Hand:
    def __init__(self, numberOfCards = 0, deck = []) -> None:
        self.hd = []
        for i in range(numberOfCards):
            self.AddCard(deck.Draw())

    def __len__(self) -> int:
        return len(self.hd)

    def AddCard(self, newCard) -> None:
        self.hd.append(newCard)