import sys
from player.Player import Player
from collections import Counter as c
import itertools as it
from dynrules import RuleSet, Rule, LearnSystem
from Carcassonne_Game.Tile import Tile, ROTATION_DICT, SIDE_CHANGE_DICT, TILE_PROPERTIES_DICT, AvailableMove
import random
import json
import ast
import re

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
            # print(f"handle features {tiles}")

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
                if characteristics == 'Meeples':
                    player = int(featureList[i][characteristics][0])
                    opponent = int(featureList[i][characteristics][2])

                    if player > opponent:
                        # Player feature 
                        players_features[feature_count] = featureList[i]
                        feature_count += 1
    
    return players_features

def player_features_mon(monList):

    if not monList:
        return {}
    
    players_features = {}
    feature_count = 0
    player_mon = False

    for i in monList:
            for characteristics in monList[i]:
                if characteristics == 'Owner' and monList[i][characteristics] == '0':
                    player_mon = True
                if characteristics == 'Tile' and player_mon == True:
                    players_features[feature_count] = monList[i][characteristics]

    return players_features

def rotate_list(original_list, degrees):
   
   
    if degrees == 0:
        return original_list
    elif degrees == 90:
        return [original_list[-1]] + original_list[:-1]  # Rotate right (clockwise)
    elif degrees == 180:
        return original_list[2:] + original_list[:2] 
    elif degrees == 270:
        return original_list[1:] + [original_list[0]]  # Rotate left (counterclockwise)
    else:
        return original_list  # Return original for unhandled degrees
        
class AdaptiveStrategies:

    """
    If there is a big feature to contribute to, suggest to add there
    Else Return False for Strategy 
    """
    def enhance_feature(Carcassonne, player_strategy):

        city_enhancements = []
        road_enhacements = []
        farm_enhacements = []

        # List of all the player's features 
        cityFeatures = player_features(handle_features(str(Carcassonne.get_city())))
        roadFeatures = player_features(handle_features(str(Carcassonne.get_road())))
        farmFeatures = player_features(handle_features(str(Carcassonne.get_farm())))
        #monFeatures = handle_features_mon(str(Carcassonne.get_mon()))
        #print(player_features_mon(monFeatures))

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()
        
        print(f"Players cities are: {cityFeatures}")
        print(f"Players roads are: {roadFeatures}")
        print(f"Players farms are: {farmFeatures}")
        
        for tile in availableMoves:
    
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            meepleLocation = tile.MeepleInfo
            index = tile.TileIndex
            PlayingTile = Tile(index)

            #Surroundings analysis
            Surroundings = [None,None,None,None]  # initialization
            SurroundingSpots = [(X-1,Y),(X,Y+1),(X+1,Y),(X,Y-1)]  # left, above, right, below

            # left top right bottom
            tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(index)],Rotation)
            
            #print(tile_properties)

            # For each feature tile, get surrounding spots and tile index and tile properties 
            for cities in cityFeatures:
                city_tiles = cityFeatures[cities]['Tiles']
                tuple = ast.literal_eval(city_tiles)
                for components in tuple:
                    city_index = components[0]
                    city_tile = Tile(city_index)
                    city_x = components[1]
                    city_y = components[2]
                    city_rotation = components[3]
                    city_meeple = components[4]
                    # print(city_index,city_x,city_y,city_rotation,city_meeple)

                    #Surroundings analysis
                    CityTileSurroundings = [None,None,None,None]  # initialization
                    CityTileSurroundingSpots = [(X-1,Y),(X,Y+1),(X+1,Y),(X,Y-1)]  # left, above, right, below

                    city_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(city_index)], city_rotation)

                    if (city_x,city_y) in SurroundingSpots and meepleLocation is None:

                        print(f"Assessing available move {tile, tile_properties}")

                        for i in range(4):
                            """
                            # For each tile check surrounding spots line up 
                            # Check coordinates should match 
                            # Check TILES PROPERTY
                            # FEATURE[0] TILE [2]
                            # FEATURE[1] TILE [3]
                            # FEATURE[2] TILE [0]
                            # FEATURE[3] TILE [1]
                            """
                            if tile_properties[i] == 'C' and city_tile_properties[(i + 2) % 4] == 'C':
                                if tile not in city_enhancements:
                                    city_enhancements.append(tile)
        
        print(f"Suggest options are {city_enhancements}")

        return 
        
    def enhance_strategy(Carcassonne, player_strategy):
        """
        suggest to build new feature with that strategy -> given that there are more than 0 meeples
        """

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()

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
    
    def block():
        
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
   


