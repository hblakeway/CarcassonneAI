import sys
from player.Player import Player
from collections import Counter as c
import itertools as it
from dynrules import RuleSet, Rule, LearnSystem
from Carcassonne_Game.Tile import Tile, ROTATION_DICT, SIDE_CHANGE_DICT, AvailableMove
import random
import json

from Carcassonne_Game.Carcassonne import (
    CarcassonneState,  
)

from pygameCarcassonneDir.pygameFunctions import (
    playMove,
    getAImove,
    drawGrid,
    diplayGameBoard,
    printScores,
    printTilesLeft,
    Counter,
    playerStrategy,
    opponentStrategy
)

"""
Checks Majority strategy pattern for a player 
 """
def strategy(strategy_list):
    # Count the occurrences of each element in the list
    count = c(strategy_list)
        
    # Find the most common element and its count
    highest = count.most_common(1)
        
    # Return the most common element or None if the list is empty
    if highest:
        return highest[0][0]
    else:
        return None
    
def handle_features_mon(featureList):
    
    featureList = featureList.strip("{}")
    
    if not featureList:
        return 
    
    entries = featureList.split("\n, ") 
    
    features = {}

    for entry in entries:
        if entry:  
            new_feature = {}
            id = int(entry.split("ID:")[1].split("Value:")[0].strip())
            value = entry.split("Value:")[1].split("Owner:")[0].strip()
            owner = entry.split("Owner:")[1].split("Tiles:")[0].strip()
            tiles = entry.split("Tiles:")[1].strip()

            new_feature['ID'] = id
            new_feature['Value'] = value
            new_feature['Owner'] = owner
            new_feature['Tiles'] = tiles
            
            features[id] = new_feature

    return features

def handle_features(featureList):
    
    featureList = featureList.strip("{}")
    
    if not featureList:
        return 
    
    entries = featureList.split("\n, ") 
    
    features = {}

    for entry in entries:
        if entry:  
            new_feature = {}
            id = int(entry.split("ID:")[1].split("Meeples:")[0].strip())
            meeples = entry.split("Meeples:")[1].split("Tiles:")[0].strip()
            tiles = entry.split("Tiles:")[1].strip()

            new_feature['ID'] = id
            new_feature['Meeples'] = meeples
            new_feature['Tiles'] = tiles
            
            features[id] = new_feature

    return features

def player_features(featureList):


    if not featureList:
        return {}
    
    players_features = {}
    feature_count = 0

    for i in featureList:
            for characteristics in featureList[i]:
                if characteristics == 'ID':
                    id = featureList[i][characteristics]
                if characteristics == 'Meeples':
                    
                    player = int(featureList[i][characteristics][0])
                    opponent = int(featureList[i][characteristics][2])

                    print(player, opponent)
                    if player > opponent:
                        # Player feature 
                        players_features[feature_count] = featureList[i]
                        feature_count += 1
    
    return players_features
        
class AdaptiveStrategies:

    """
    If there is a big feature to contribute to, suggest to add there
    If not check majority strategy and suggest to build new feature with that strategy -> given that there are more than 0 meeples
    Else Return False for Strategy 
    """
    def enhance_strategy(Carcassonne, player_strategy):

        # Get all features
        cityFeatures = handle_features(str(Carcassonne.get_city()))
        print(cityFeatures)
        roadFeatures = handle_features(str(Carcassonne.get_road()))
        farmFeatures = handle_features(str(Carcassonne.get_farm()))
        monFeatures = handle_features_mon(str(Carcassonne.get_mon()))
        
        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()

        # Get players features
        print("players cities")
        print(player_features(cityFeatures))

        # Check if any of the moves would add to players features 

        # remaining meeples
        meeples = Carcassonne.Meeples
        p1_meeples = meeples[0]

        # Features which the player has placed meeples on 
        meeplePlacements = []
        for i in player_strategy:
            if i[4] is not None:
                meeplePlacements.append(i[4][0])

        # If there is a majority stratgey check if you can place a meeple on the same feature 
        player_strategy = strategy(meeplePlacements)
        if player_strategy is not None and p1_meeples > 0:
            meepleDictionary = {
                "R": "Road",
                "C": "City",
                "G": "Farm",
                "Monastery": "Monastery"
            }

            options = []
            for i in availableMoves:
                MeepleInfo = str(i.MeepleInfo)

                if player_strategy in MeepleInfo:
                    options.append(i)
            
            if not options:
                return False, None
            
            selectedMove = random.choice(options)
            print(f"You have a strong {meepleDictionary[player_strategy]} strategy. Keep going on it.")
            return True, selectedMove
        
        else: # Strategy is False for this move
            return False, None
    

    def complete_feature():
        """
        Complete a feature that player has made. 
        """

        "1. Can the tile complete a feature "

        # Checks if any of those spots are connecting to an unfinished meeple feature

        # Checks if that tile can complete and give that meeple back 
        
        return

    def steal_points():
        
        return



class CarcassonneAdaptive():
    """
    1. Average Time Strategy 
    2. Opponent Winning Strategy
    3. Player Winning Strategy 
    4. Fields Strategy 
    """

class AdaptiveRuleSet(RuleSet):
    """
    """
   


