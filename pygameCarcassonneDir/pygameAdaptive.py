import sys
from player.Player import Player
from collections import Counter as c
import itertools as it
from dynrules import RuleSet, Rule, LearnSystem
from Carcassonne_Game.Tile import Tile, ROTATION_DICT, SIDE_CHANGE_DICT, TILE_PROPERTIES_DICT, AvailableMove
from Carcassonne_Game.Tile_dict import TILE_COMBINE_CITY, TILE_COMBINE_ROAD, TILE_COMBINE_FARM
import random
import json
import ast
import re

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

def shared_features(featureList):

    if not featureList:
        return {}
    
    shared_features = {}
    feature_count = 0

    for i in featureList:
            for characteristics in featureList[i]:
                if characteristics == 'Meeples':
                    player = int(featureList[i][characteristics][0])
                    opponent = int(featureList[i][characteristics][2])

                    if player == opponent:
                        # Player feature 
                        shared_features[feature_count] = featureList[i]
                        feature_count += 1
    
    return shared_features

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

def opponent_features(featureList):

    if not featureList:
        return {}
    
    opponent_features = {}
    feature_count = 0

    for i in featureList:
            for characteristics in featureList[i]:
                if characteristics == 'Meeples':
                    player = int(featureList[i][characteristics][0])
                    opponent = int(featureList[i][characteristics][2])

                    if player < opponent:
                        # Player feature 
                        opponent_features[feature_count] = featureList[i]
                        feature_count += 1
    
    return opponent_features

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

# ADD CONFIG FOR EVERY TILE         
# Returns the tile index where meeple is placed 
"""
      1

0           2

      3

"""
def split_tiles(index, number, rotation):
    # to_check = [6, 11, 18, 19, 23]
    if index == 11:
        if number == 1:
            rotate = {0: 1, 90: 2, 180: 3, 270: 0}
        elif number == 2:
            rotate = {0: 3, 90: 0, 180: 1, 270: 2}
        else:
            return 4

    elif index == 6: 
        if number == 1:
            rotate = {0: 1, 90: 2, 180: 3, 270: 0}
        if number == 2:
            rotate = {0: 2, 90: 3, 180: 0, 270: 1}
        else:
            return 4
    
    else:
        return 4
    
    return rotate[rotation]


class AdaptiveStrategies:

    """
    If there is player feature to contribute to, suggest to add there
    Else Return False for enhacement of player feature 
    """
    def enhance_feature(Carcassonne):

        city_enhancements = []
        road_enhancements = []
        farm_enhancements = []

        # List of all the player's features 
        cityFeatures = player_features(handle_features(str(Carcassonne.get_city())))
        roadFeatures = player_features(handle_features(str(Carcassonne.get_road())))
        farmFeatures = player_features(handle_features(str(Carcassonne.get_farm())))

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()
        
        for tile in availableMoves:
            
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            meepleLocation = tile.MeepleInfo

            #City
            if meepleLocation is None:
                index = tile.TileIndex
                PlayingTile = Tile(index)
                SurroundingSpots = [(X-1,Y),(X,Y+1),(X+1,Y),(X,Y-1)]  # left, above, right, below

                # left top right bottom
                tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(index)],Rotation)

                if PlayingTile.HasCities:
            
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
                                keys = getKeys()

                                if city_opens == 1: # Will definitely have a meeple
                                    CitySide = city_index_list[0]
                                    checkCoord = coordinate_checks[CitySide]
                                    tile_index = index_checks[CitySide]
                                    if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                        if tile not in city_enhancements:
                                            city_enhancements.append(['city', tile])
            
                                elif city_opens == 2 and (city_index == 11 or city_index == 6):  # Account for two cities seperate on one tile, one city has meeple
                                    
                                    meeplePlaced = 0

                                    # Gives back the number where meeple was placed 
                                    if coords in keys:
                                        meeplePlaced = keys[coords][1]
                                    
                                    # Tile Index (Only check the side related to the meeple)
                                    check = split_tiles(city_index, meeplePlaced, city_rotation)
                                    
                                    if check != 4:
                                        checkCoord = coordinate_checks[check]
                                        tile_index = index_checks[check]
                                    
                                        if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                            if tile not in city_enhancements:
                                                city_enhancements.append(['city', tile])

                                else: # 2,3 or 4 opening
                                    for i in city_index_list:
                                        checkCoord = coordinate_checks[i]
                                        tile_index = index_checks[i]
                                        if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                            if tile not in city_enhancements:
                                                city_enhancements.append(['city', tile])
            #Roads
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
                                    road_enhancements.append(['road', tile])
            #Farms
            for farms in farmFeatures:
                farm_tiles = farmFeatures[farms]['Tiles']
                tuple = ast.literal_eval(farm_tiles)
                for components in tuple:
                    print(components)
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
                                    farm_enhancements.append(['farm', tile])
        
    
        all_enhancements = city_enhancements + road_enhancements + farm_enhancements

        if all_enhancements:
            selectedMove = random.choice(all_enhancements)
            print(f"Keep adding to your {selectedMove[0]}")
            return True, selectedMove
        else:
            return False, None
        
    """
    If player can create a new feature based on what they are predominately building
    Else Return False for enhacement of player strategy 
    """
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
            print(f"It would be good to start a new {meepleDictionary[player_strategy]}.")
            return True, selectedMove
        
        else: # Strategy is False for this move
            return False, None
    
    """
    If there is a large opponent feature that you can steal points from 
    Else return False 
    """
    def steal_points(Carcassonne):
        
        combination = []

        # Iterate through self.boardcities, self.boardfarms self.board roads 
        oppcityFeatures = opponent_features(handle_features(str(Carcassonne.get_city())))
        opproadFeatures = opponent_features(handle_features(str(Carcassonne.get_road())))
        oppfarmFeatures = opponent_features(handle_features(str(Carcassonne.get_farm())))

        # List of all the player's features 
        playerCityFeatures = player_features(handle_features(str(Carcassonne.get_city())))
        playerRoadFeatures = player_features(handle_features(str(Carcassonne.get_road())))
        plauyerFarmFeatures = player_features(handle_features(str(Carcassonne.get_farm())))

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()
        
        for tile in availableMoves:
            
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            meepleLocation = tile.MeepleInfo
            index = tile.TileIndex
            PlayingTile = Tile(index)
            tile_coord = (X,Y)

            index_checks = {
                0: (X-1, Y),  
                1: (X, Y+1),  
                2: ((X+1,Y)), 
                3: ((X,Y-1)) 
            }

            side_checks = {
                0: (2),  # For CitySide 0
                1: (3),  # For CitySide 1
                2: (0),  # For CitySide 2
                3: (1)   # For CitySide 3
            }

            # Rotates the tile properties to equal the available rotation
            tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(index)],Rotation)
            keys = getKeys()
            print(keys)

            if meepleLocation is None:  # If we are connecting we wont be able to place meeple 
                if index in TILE_COMBINE_CITY:
                    # Gets the index of the openings 
                    city_openings_index = []
                    for i in range(len(tile_properties)):
                            if tile_properties[i] == 'C':
                                city_openings_index.append(i)
                    
                    # Get opponents features
                    for opp_cities in oppcityFeatures:
                        opponents_city_tuple = ast.literal_eval(oppcityFeatures[opp_cities]['Tiles'])
                        opp_feature_length = len(opponents_city_tuple)

                        for opp_components in opponents_city_tuple:
                            opp_city_index = opp_components[0]
                            opp_city_tile = Tile(opp_city_index)
                            opp_city_x = opp_components[1]
                            opp_city_y = opp_components[2]
                            opp_city_rotation = opp_components[3]
                            opp_city_meeple = opp_components[4]

                            opp_coordinate_checks = {
                                0: (opp_city_x - X),  # For CitySide 0
                                1: (Y - opp_city_y),  # For CitySide 1
                                2: (X - opp_city_x),  # For CitySide 2
                                3: (opp_city_y - Y)   # For CitySide 3
                            }

                            if (opp_city_x, opp_city_y) in keys:
                                oppmeeplePlaced = keys[(opp_city_x, opp_city_y)][1]
                            
                            # Get player features 
                            for player_cities in playerCityFeatures:
                                player_city_tuple = ast.literal_eval(playerCityFeatures[player_cities]['Tiles'])
                                player_feature_length = len(player_city_tuple)
                                
                                for player_components in player_city_tuple:
                                    player_city_index = player_components[0]
                                    player_city_tile = Tile(player_city_index)
                                    player_city_x = player_components[1]
                                    player_city_y = player_components[2]
                                    player_city_rotation = player_components[3]
                                    player_city_meeple = player_components[4]

                                    pla_coordinate_checks = {
                                        0: (player_city_x - X),  # For CitySide 0
                                        1: (Y - player_city_y),  # For CitySide 1
                                        2: (X - player_city_x),  # For CitySide 2
                                        3: (player_city_y - Y)   # For CitySide 3
                                    }

                                    if (player_city_x, player_city_y) in keys:
                                        playermeeplePlaced = keys[(player_city_x, player_city_y)][1]

                                    # Only combine if opponents feature is larger than players
                                    if (opp_feature_length > player_feature_length):

                                        # Check if tile fits index 
                                        for index in city_openings_index:
                                            opp_coords = (opp_city_x, opp_city_y)
                                            if index_checks[index] == opp_coords:
                                                
                                                    
                                                    # Check the remaining indices for player coordinates
                                                    for other_index in city_openings_index:
                                                        player_coords = (player_city_x, player_city_y)
                                                        if other_index != index and index_checks[other_index] == player_coords:

                                                            if opp_city_meeple is not None:
                                                                # Check connected to the right meeple side 
                                                                print(oppmeeplePlaced)
                                                            if player_city_meeple is not None:
                                                                # Check connected to the right meeple side 
                                                                print(playermeeplePlaced)
                                                            
                                                            combination.append(['cities', tile])
                if index in TILE_COMBINE_ROAD: 
                    roads_openings_index = []
                    for i in range(len(tile_properties)):
                            if tile_properties[i] == 'R':
                                roads_openings_index.append(i)

                    for opp_roads in opproadFeatures:
                        opponents_road_tuple = ast.literal_eval(opproadFeatures[opp_roads]['Tiles'])
                        opp_feature_length = len(opponents_road_tuple)

                        for opp_components in opponents_road_tuple:
                            if opp_components[1] is not None:
                                opp_road_x = opp_components[1]
                            else:
                                continue

                            if opp_components[2] is not None:
                                opp_road_y = opp_components[2]
                            else:
                                continue
                            
                            # Get player features 
                            for player_roads in playerRoadFeatures:
                                player_road_tuple = ast.literal_eval(playerRoadFeatures[player_roads]['Tiles'])
                                player_feature_length = len(player_road_tuple)
                                
                                for player_components in player_road_tuple:
                                    player_road_x = player_components[1]
                                    player_road_y = player_components[2]

                                    # Only combine if opponents feature is larger than players
                                    if (opp_feature_length > player_feature_length):
                                        # Check if tile fits index 
                                        for index in roads_openings_index:
                                            if index_checks[index] == (opp_road_x, opp_road_y):
                                                # Check the remaining indices for player coordinates
                                                for other_index in roads_openings_index:
                                                    if other_index != index and index_checks[other_index] == (player_road_x, player_road_y):
                                                        combination.append(['roads', tile])
                     
                if index in TILE_COMBINE_FARM:
                    # Gets the index of the openings 
                    farms_openings_index = []
                    for i in range(len(tile_properties)):
                            if tile_properties[i] == 'G':
                                farms_openings_index.append(i)

                    for opp_farms in oppfarmFeatures:
                        opp_farm_tiles = opproadFeatures[opp_farms]['Tiles']
                        opponents_farm_tuple = ast.literal_eval(opp_farm_tiles)
                        #print(f"farm {opponents_farm_tuple}")

                        for opp_components in opponents_farm_tuple:
                            opp_farm_index = opp_components[0]
                            opp_farm_tile = Tile(opp_farm_index)
                            opp_farm_x = opp_components[1]
                            opp_farm_y = opp_components[2]
                            opp_farm_rotation = opp_components[3]
                            opp_farm_meeple = opp_components[4]
                    

        if combination:
            print(f"All possibilites: {combination}")
            selectedMove = random.choice(combination)
            print(f"This is your opportunity to combine {selectedMove[0]}")
            return True, selectedMove
        else:
            return False, None
    
    

class CarcassonneAdaptive():
    """
    1. Average Time Strategy 
    2. Opponent Winning Strategy
    3. Player Winning Strategy 
    4. Fields Strategy 
    """

    enhance_feature = False, None
    enhance_strategy = False, None
    steal_points = False, None


class AdaptiveRuleSet(RuleSet):
    """
    """
   


