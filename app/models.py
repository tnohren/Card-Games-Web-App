"""
Definition of models.
"""
from django.db import models
from django.contrib.auth.models import User

# Holds All Available Game Types
class GameTypes(models.Model):
    gameTypes = (('P', 'Poker'), ('B', 'Blackjack'))
    gameType = models.CharField(max_length = 1, choices = gameTypes, primary_key = True)

# Holds All Available Cards
class Cards(models.Model):
    cardSuits = ((0, 'Clubs'), (1, 'Spades'), (2, 'Diamonds'), (3, 'Hearts'))
    cardValues = ((0, 'Ace'), (1, '2'), (2, '3'), (3, '4'), (4, '5'), (5, '6'), (6, '7'), (7, '8'), (8, '9'), (9, '10'), (10, 'Jack'), (11, 'Queen'), (12, 'King'))
    suit = models.IntegerField(choices = cardSuits)
    value = models.IntegerField(choices = cardValues)
    class Meta:
        unique_together = (("suit", "value"),)
         
# Holds All Games for a Profile
class SavedGames(models.Model):
    # profileName = models.ForeignKey(Profiles, on_delete = models.CASCADE)
    profileName = models.ForeignKey(User, on_delete = models.CASCADE)
    gameTypes = (('P', 'Poker'), ('B', 'Blackjack'))
    gameType = models.CharField(max_length = 1, choices = gameTypes)
    gameNumber = models.BigAutoField(primary_key = True)
    gameOutcome = models.BooleanField(default = False)

# Holds All Completed Games for a Profile
class CompleteGames(models.Model):
    gameNumber = models.IntegerField(primary_key=True)

# Holds All In Progress Games for a Profile
class InProgressGames(models.Model):
    gameNumber = models.IntegerField(primary_key=True)
    gameStatus = models.CharField(max_length = 10)

# Holds All Players in a Game
class GamePlayer(models.Model):
    gameNumber = models.IntegerField()
    gamePlayer = models.CharField(max_length = 10)
    class Meta:
        unique_together = (("gameNumber", "gamePlayer"),)

# Holds All Hands in a Game
class GameHands(models.Model):
    cardSuits = ((0, 'Clubs'), (1, 'Spades'), (2, 'Diamonds'), (3, 'Hearts'))
    cardValues = ((0, 'Ace'), (1, '2'), (2, '3'), (3, '4'), (4, '5'), (5, '6'), (6, '7'), (7, '8'), (8, '9'), (9, '10'), (10, 'Jack'), (11, 'Queen'), (12, 'King'))
    gameNumber = models.IntegerField()
    gamePlayer = models.CharField(max_length = 10)
    cardSuit = models.IntegerField(choices=cardSuits)
    cardValue = models.IntegerField(choices=cardValues)
    class Meta:
        unique_together = (("gameNumber", "gamePlayer", "cardSuit", "cardValue"),)