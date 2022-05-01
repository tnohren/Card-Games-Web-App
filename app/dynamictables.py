from .models import *

"""
    SAVED/COMPLETE/INPROGRESS GAME FUNCTIONS
"""
def CreateUserGame(user, gameType):
    # Create New Game in SavedGames Table
    game = SavedGames.objects.create(profileName=user, gameType=gameType, gameOutcome=False)
    game.save()

    # Use gameNumber of New SavedGame to add to InProgressGames Table
    inProgressGame = InProgressGames.objects.create(gameNumber=game.gameNumber, gameStatus="Begin")
    inProgressGame.save()

    # Return Newly Created Game Number
    return game.gameNumber

def SaveUserGame(username, gameType, gameNumber, gameStatus=""):
    # Set Outcome in Main Table
    savedGame = SavedGames.objects.filter(profileName=username, gameType=gameType, gameNumber=gameNumber).first()
    savedGame.gameOutcome = (gameStatus == "Complete")
    savedGame.save()
    if gameStatus == "Complete":
        # Create New Complete Game
        completeGame = CompleteGames.objects.create(gameNumber=gameNumber)
        completeGame.save()

        # Remove Old In Progress Game
        InProgressGames.objects.filter(gameNumber=gameNumber).delete()
    else:
        # Update Status of In Progress Game
        inProgressGame = InProgressGames.objects.filter(gameNumber=gameNumber).first()
        inProgressGame.gameStatus = gameStatus
        inProgressGame.save()

def RetrieveUserGames(username, gameType, complete):
    # Retrieve List of All User Games of Specified Type and Outcome
    return [game.gameNumber for game in SavedGames.objects.filter(profileName=username, gameType=gameType, gameOutcome=complete).all()]

def RetrieveInProgressGameStatus(gameNumber):
    inProgressGame = InProgressGames.objects.filter(gameNumber=gameNumber).first()
    return inProgressGame.gameStatus

"""
    PLAYER FUNCTIONS
"""
def CreatePlayer(gameNumber, playerName):
    player = GamePlayer.objects.create(gameNumber=gameNumber, gamePlayer=playerName)
    player.save()
    return player

def RetrievePlayers(gameNumber):
    return [player.gamePlayer for player in GamePlayer.objects.filter(gameNumber=gameNumber).all()]

"""
    HAND/CARD FUNCTIONS
"""
def SaveHands(gameNumber, hands):
    # Remove Prior Saved Hands
    GameHands.objects.filter(gameNumber=gameNumber).delete()

    # Save Current Hands
    for hand in hands:
        for card in hand['hand']:
            GameHands.objects.create(gameNumber=gameNumber, gamePlayer=hand['gamePlayer'], cardSuit = card['suit'], cardValue = card['value'])

def RetrieveHands(gameNumber):
    players = RetrievePlayers(gameNumber)
    hands = []
    for player in players:
        savedHands = GameHands.objects.filter(gameNumber=gameNumber, gamePlayer=player).all()
        temp = []
        for hand in savedHands:
            temp.append({'suit': hand.cardSuit, 'value': hand.cardValue})
        hands.append({'gamePlayer': player, 'hand': temp})
    return hands