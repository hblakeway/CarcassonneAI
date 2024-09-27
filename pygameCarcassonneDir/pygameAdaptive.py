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

from Carcassonne_Game.Carcassonne import CarcassonneState

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

keys = {}

# Tile Index and Place Meeple is selected on 
def updateKeys(index, numberSelected, xy):
    print("in here")
    keys[xy] = [index, numberSelected]

def getKeys():
    return keys

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


        
# Returns the tile index where meeple is placed 
"""
      1

0           2

      3

"""
def split_tiles(index, number, rotation):
    
    if number == 3 or number == 0:
        # Meeple is placed on a farm for this tile
        return 4
    
    if index == 11:
        if number == 1:
            rotate = {0: 1, 90: 2, 180: 3, 270: 0}
        
        if number == 2:
            rotate = {0: 3, 90: 0, 180: 1, 270: 2}

    elif index == 6: 
        if number == 1:
            rotate = {0: 1, 90: 2, 180: 3, 270: 0}
        
        if number == 2:
            rotate = {0: 2, 90: 3, 180: 0, 270: 1}
    
    else:
        return 4
    
    return rotate[rotation]


        
class AdaptiveStrategies:

    """
    If there is player feature to contribute to, suggest to add there
    Else Return False for enhacement of player feature 
    """
    def enhance_feature(Carcassonne, player_strategy):

        city_enhancements = []
        road_enhancements = []
        farm_enhancements = []

        # List of all the player's features 
        cityFeatures = player_features(handle_features(str(Carcassonne.get_city())))
        roadFeatures = player_features(handle_features(str(Carcassonne.get_road())))
        farmFeatures = player_features(handle_features(str(Carcassonne.get_farm())))
        #monFeatures = handle_features_mon(str(Carcassonne.get_mon()))
        #print(player_features_mon(monFeatures))

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()
        
        for tile in availableMoves:
            
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            meepleLocation = tile.MeepleInfo

            if meepleLocation is None:
                index = tile.TileIndex
                PlayingTile = Tile(index)
                SurroundingSpots = [(X-1,Y),(X,Y+1),(X+1,Y),(X,Y-1)]  # left, above, right, below

                # left top right bottom
                tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(index)],Rotation)

                if PlayingTile.HasCities:
                    for i in range(len(PlayingTile.CityOpenings)):
                        CityOpenings = PlayingTile.CityOpenings[i]
            
                    # For each feature tile, get surrounding spots and tile index and tile properties 
                    for cities in cityFeatures:

                        city_tiles = cityFeatures[cities]['Tiles']
                        tuple = ast.literal_eval(city_tiles)

                        # City components
                        for components in tuple:
                            city_index = components[0]
                            city_tile = Tile(city_index)
                            city_x = components[1]
                            city_y = components[2]
                            city_rotation = components[3]
                            city_meeple = components[4]

                            city_tile_properties = rotate_list(TILE_PROPERTIES_DICT[city_index], city_rotation)
                            city_opens = city_tile_properties.count('C')

                            city_index_list = []
                            for i in range(len(city_tile_properties)):
                                if city_tile_properties[i] == 'C':
                                    city_index_list.append(i)

                            coordinate_checks = {
                                0: (city_x - X),  # For CitySide 0
                                1: (Y - city_y),  # For CitySide 1
                                2: (X - city_x),  # For CitySide 2
                                3: (city_y - Y)   # For CitySide 3
                            }

                            index_checks = {
                                0: (2),  # For CitySide 0
                                1: (3),  # For CitySide 1
                                2: (0),  # For CitySide 2
                                3: (1)   # For CitySide 3
                            }
                            coords = (city_x,city_y)

                            if coords in SurroundingSpots:
                                print(f"Checking {tile}")

                                keys = getKeys()

                                if city_opens == 1: # Will definitely have a meeple
                                    CitySide = city_index_list[0]
                                    checkCoord = coordinate_checks[CitySide]
                                    tile_index = index_checks[CitySide]
                                    if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                        if tile not in city_enhancements:
                                            city_enhancements.append(tile)
            
                                elif city_opens == 2 and (city_index == 11 or city_index == 6):  # Account for two cities seperate on one tile, one city has meeple
                                    
                                    meeplePlaced = 0

                                    # Gives back the number where meeple was placed 
                                    if coords in keys:
                                        meeplePlaced = keys[coords][1]
                                    
                                    # Tile Index (Only check the side related to the meeple)
                                    check = split_tiles(city_index, meeplePlaced, city_rotation)
                                    print(f"Check = {check}")
                                    
                                    if check != 4:
                                        checkCoord = coordinate_checks[check]
                                        tile_index = index_checks[check]
                                        print(f"Coord Check = {checkCoord}")
                                        print(f"Tile Index = {tile_index}")
                                    
                                        if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                            if tile not in city_enhancements:
                                                city_enhancements.append(tile)

                                else: # 2,3 or 4 opening
                                    for i in city_index_list:
                                        checkCoord = coordinate_checks[i]
                                        tile_index = index_checks[i]
                                        if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                            if tile not in city_enhancements:
                                                city_enhancements.append(tile)

            for roads in roadFeatures:
                road_tiles = roadFeatures[roads]['Tiles']
                tuple = ast.literal_eval(road_tiles)
                for components in tuple:
                    road_index = components[0]
                    road_tile = Tile(road_index)
                    road_x = components[1]
                    road_y = components[2]
                    road_rotation = components[3]
                    road_meeple = components[4]

                    road_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(road_index)], road_rotation)

                    if (road_x,road_y) in SurroundingSpots and meepleLocation is None:
                        for i in range(4):
                            if tile_properties[i] == 'R' and road_tile_properties[(i + 2) % 4] == 'R':
                                # Check that tile placement makes roads align

                                if tile not in road_enhancements:
                                    road_enhancements.append(tile)
            
            for farms in farmFeatures:
                farm_tiles = farmFeatures[farms]['Tiles']
                tuple = ast.literal_eval(farm_tiles)
                for components in tuple:
                    farm_index = components[0]
                    farm_x = components[1]
                    farm_y = components[2]
                    farm_rotation = components[3]
                    farm_meeple = components[4]

                    farm_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(farm_index)], farm_rotation)

                    if (farm_x,farm_y) in SurroundingSpots and meepleLocation is None:

                        print(f"Assessing available move {tile, tile_properties}")

                        for i in range(4):
                            if tile_properties[i] == 'G' and farm_tile_properties[(i + 2) % 4] == 'G':
                                # Check that tile placement makes farms align 

                                if tile not in farm_enhancements:
                                    farm_enhancements.append(tile)
        
    
        all_enhancements = city_enhancements + road_enhancements + farm_enhancements

        if all_enhancements:
            print(f"All Suggest options are {all_enhancements}")
            random_suggestion = random.choice(all_enhancements)
            print(f"Suggestion: {random_suggestion}")
            return True, random_suggestion
        else:
            print("No enhancements available.")

        return False, None
        
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
   


