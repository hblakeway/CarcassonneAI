import sys
from player.Player import Player
from collections import Counter as c
import itertools as it
from dynrules import RuleSet, Rule, LearnSystem
from Carcassonne_Game.Tile import Tile, ROTATION_DICT, SIDE_CHANGE_DICT, TILE_PROPERTIES_DICT, AvailableMove
from Carcassonne_Game.Tile_dict import TILE_COMBINE_CITY, TILE_COMBINE_ROAD, TILE_COMBINE_FARM, features_specific
import random
import json
import ast
import re
from Carcassonne_Game.Tile_dict import MEEPLE_LOC_DICT

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

coord_rotation = {
    (0,1): {0: (0,1), 90: (1,1), 180: (2,1), 270: (3,1)}, # Side 0
    (1,1): {0: (1,1), 90: (2,1), 180: (3,1), 270: (0,1)}, # Side 0
    (2,1): {0: (2,1), 90: (3,1), 180: (0,1), 270: (1,1)}, # Side 0
    (3,1): {0: (3,1), 90: (0,1), 180: (1,1), 270: (2,1)}, # Side 0

    (3,2): {0: (3,2), 90: (0,2), 180: (1,2), 270: (2,2)}, # SW Corner
    (0,2): {0: (0,2), 90: (1,2), 180: (2,2), 270: (3,2)}, # NW Corner 
    (1,2): {0: (1,2), 90: (2,2), 180: (3,2), 270: (0,2)}, # NE Corner
    (2,2): {0: (2,2), 90: (3,2), 180: (0,2), 270: (1,2)}, # SE Corner 

    (0,4): {0: (0,4), 90: (0,4), 180: (0,4), 270: (0,4)} # Middle 
}

corner_cords = [(3,2), (0,2), (1,2), (2,2)]

# Tile Index and Place Meeple is selected on 
def updateKeys(index, meepleCoord, xy, rotation):
    if meepleCoord == 0:
        meepleCoord = (0,0)
    keys[xy] = [index, meepleCoord, rotation]

def getKeys():
    return keys

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
                        print(f"FeatureList[i] = {featureList[i]}")
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
                if characteristics == 'Tiles' and player_mon == True:
                    print(f"player mon = {monList[i][characteristics]}")
                    players_features[feature_count] = monList[i][characteristics]
                    feature_count += 1
                    player_mon = False

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

def rotate_dictionary(index, rotation):
    # Check if the specified key exists
    if index not in features_specific:
        raise KeyError(f"Index {index} not found in the dictionary.")
    
    values = features_specific[index]

    if rotation == 0:
        rotated_values = values
    elif rotation == 90:
        rotated_values = [
            values[0],                # Keep first value
            values[3],                # Move last value to second
            values[1],                # Move second value to third
            values[2]                 # Move third value to last
        ]
    elif rotation == 180:
        rotated_values = [
            values[2],                # Move third to first
            values[1],                # Keep second
            values[0],                # Move first to third
            values[3]                 # Keep last
        ]
    elif rotation == 270:
        rotated_values = [
            values[1],                # Move second to first
            values[2],                # Move third to second
            values[3],                # Move last to third
            values[0]                 # Keep first as last
        ]
    else:
        return features_specific  # Return original for unhandled cases


    return rotated_values
      
def check_tiles(coord, rotation):
   
    if coord in coord_rotation:
        print(f"Original: {coord}, Rotation: {rotation}, Final: {coord_rotation[coord][rotation]}")
        return coord_rotation[coord][rotation]
    else:
        print(0,0)
        return (0,0)

def get_meeple():

    return

class AdaptiveStrategies:

    """
    If there is player feature to contribute to, suggest to add there
    Else Return False for enhacement of player feature 
    """
    def enhance_feature(Carcassonne):

        city_enhancements = []
        road_enhancements = []
        farm_enhancements = []
        monastery_enhacements = []

        # List of all the player's features 
        cityFeatures = player_features(handle_features(str(Carcassonne.get_city())))
        roadFeatures = player_features(handle_features(str(Carcassonne.get_road())))
        farmFeatures = player_features(handle_features(str(Carcassonne.get_farm())))
        monasteryFeatures = player_features_mon(handle_features_mon(str(Carcassonne.get_mon())))
        print(monasteryFeatures)

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()
        
        for tile in availableMoves:
            
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            meepleLocation = tile.MeepleInfo
            index = tile.TileIndex
            PlayingTile = Tile(index)
            tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(index)],Rotation)

            # Check monastery 
            for mon in monasteryFeatures:
                mon_tiles = monasteryFeatures[mon]
                mon_tuple = ast.literal_eval(mon_tiles)
                clean_tuple = []
                for item in mon_tuple:
                    # If the item is a tuple and has length 2, keep only the first element
                    if isinstance(item, tuple) and len(item) == 2:
                        clean_tuple.append(item[0])
                    else:
                        clean_tuple.append(item)

                for index, item in enumerate(clean_tuple):
                    if isinstance(item, tuple) and len(item) == 5:
                        mon_x = item[1]
                        mon_y = item[2]

                        if isinstance(item[4], tuple) and item[4][0] == 'Monastery':
                            CompleteSurroundingSpots = [(mon_x-1,mon_y),(mon_x,mon_y+1),(mon_x+1,mon_y),(mon_x,mon_y-1),(mon_x-1,mon_y-1),(mon_x+1,mon_y+1),(mon_x+1,mon_y-1),(mon_x-1,mon_y+1)]

                            if (X,Y) in CompleteSurroundingSpots:
                                if tile not in monastery_enhacements:
                                    monastery_enhacements.append(['monastery', tile])

            if meepleLocation is None: # Don't want to look at available moves that have meeples 
                
                if PlayingTile.HasCities: # Check if it can connect to any cities 
                    for cities in cityFeatures:
                        print(f"Cities: {cities}")
                        city_tiles = cityFeatures[cities]['Tiles']
                        city_tuple = ast.literal_eval(city_tiles)

                        # Individual tiles that make up the city feature 
                        for components in city_tuple:
                            print(f"City component {components}")
                            city_index = components[0]
                            city_x = components[1]
                            city_y = components[2]
                            city_rotation = components[3]

                            city_tile_properties = rotate_list(TILE_PROPERTIES_DICT[city_index], city_rotation)
                            SurroundingSpots = [(city_x-1,city_y),(city_x,city_y+1),(city_x+1,city_y),(city_x,city_y-1)]  # left, above, right, below

                            city_index_list = [] # city index position on the city feature tile 
                            for i in range(len(city_tile_properties)):
                                if city_tile_properties[i] == 'C':
                                    city_index_list.append(i)

                            coordinate_checks = {
                                0: (X - city_x),  
                                1: (city_y - Y),  
                                2: (city_x - X),  
                                3: (Y - city_y)   
                            }

                            index_checks = {
                                (0,1): 2,  # For CitySide 0
                                (1,1): 3,  # For CitySide 1
                                (2,1): 0,  # For CitySide 2
                                (3,1): 1   # For CitySide 3
                            }

                            if (X,Y) in SurroundingSpots: # if the available move is a surrounding tile of this city feature 
                                print("This tile has available spots around one of my already cities")
                                keys = getKeys()
                                meeplePlaced = 0
                                check = (0,0)
                                print(city_index, city_rotation)
                                # Check if city feature tile we are checking has a meeple on it
                                if (city_x, city_y) in keys:
                                    print("I may have a meeple")
                                    meeplePlaced = keys[(city_x, city_y)][1]
                                    check = check_tiles(meeplePlaced, city_rotation) # Getting true coordinate of where the meeple is placed on the city feature

                                if check != (0,0) and (index == 6 or index == 11):
                                    print("I have a meeple on a split city. Need to be specific")
                                    tile_index = index_checks[check] # I want to check this side on the available tile 
                                    checkCoord = coordinate_checks[tile_index] # Checking if on that index on the available tile is a 'C'

                                    if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                        if tile not in city_enhancements:
                                            city_enhancements.append(['city', tile])
                                else:
                                    for i in city_index_list:
                                        tile_index = (i + 2) % 4
                                        checkCoord = coordinate_checks[tile_index]
                                        
                                        if checkCoord == 1 and tile_properties[tile_index] == 'C':
                                            if tile not in city_enhancements:
                                                city_enhancements.append(['city', tile])
                    
                if PlayingTile.HasRoads: # Check if it can connect to any roads 
                    for roads in roadFeatures:
                        road_tiles = roadFeatures[roads]['Tiles']
                        road_tuple = ast.literal_eval(road_tiles)

                        # Individual tiles that make up the road feature 
                        for components in road_tuple:
                            print(f"Road component {components}")
                            road_index = components[0]
                            road_x = components[1]
                            road_y = components[2]
                            road_rotation = components[3]

                            road_tile_properties = rotate_list(TILE_PROPERTIES_DICT[road_index], road_rotation)
                            SurroundingSpots = [(road_x-1,road_y),(road_x,road_y+1),(road_x+1,road_y),(road_x,road_y-1)]  # left, above, right, below

                            road_index_list = [] # road index position on the road feature tile 
                            for i in range(len(road_tile_properties)):
                                if road_tile_properties[i] == 'R':
                                    road_index_list.append(i)

                            coordinate_checks = {
                                0: (X - road_x),  
                                1: (road_y - Y),  
                                2: (road_x - X),  
                                3: (Y - road_y)   
                            }

                            index_checks = {
                                (0,1): 2,  # For Road 0
                                (1,1): 3,  # For Road 1
                                (2,1): 0,  # For Road 2
                                (3,1): 1   # For Road 3
                            }

                            if (X,Y) in SurroundingSpots: # if the available move is a surrounding tile of this city feature 
                                
                                keys = getKeys()
                                meeplePlaced = 0
                                check = (0,0)
                               
                                # Check if road feature tile we are checking has a meeple on it
                                if (road_x, road_y) in keys:
                                    meeplePlaced = keys[(road_x, road_y)][1]
                                    check = check_tiles(meeplePlaced, road_rotation) # Getting true coordinate of where the meeple is placed on the road feature

                                if check != (0,0) and (index == 18 or index == 19 or index == 23):
                                    tile_index = index_checks[check] # I want to check this side on the available tile 
                                    checkCoord = coordinate_checks[tile_index] # Checking if on that index on the available tile is a 'C'

                                    if checkCoord == 1 and tile_properties[tile_index] == 'R':
                                        if tile not in road_enhancements:
                                            road_enhancements.append(['road', tile])
                                else:
                                    for i in road_index_list:
                                        tile_index = (i + 2) % 4
                                        checkCoord = coordinate_checks[tile_index]
                                        
                                        if checkCoord == 1 and tile_properties[tile_index] == 'R':
                                            if tile not in road_enhancements:
                                                road_enhancements.append(['road', tile])
                    
                if PlayingTile.HasFarms: # Check if it can connect to any farms 
                    for farms in farmFeatures:
                        farm_tiles = farmFeatures[farms]['Tiles']
                        farm_tuple = ast.literal_eval(farm_tiles)

                        # Individual tiles that make up the road feature 
                        for components in farm_tuple:
                            print(f"Farm component {components}")
                            farm_index = components[0]
                            farm_x = components[1]
                            farm_y = components[2]
                            farm_rotation = components[3]

                            farm_tile_properties = rotate_list(TILE_PROPERTIES_DICT[farm_index], farm_rotation)
                            SurroundingSpots = [(farm_x-1,farm_y),(farm_x,farm_y+1),(farm_x+1,farm_y),(farm_x,farm_y-1)]  # left, above, right, below

                            farm_index_list = [] # road index position on the road feature tile 
                            for i in range(len(farm_tile_properties)):
                                if farm_tile_properties[i] == 'G':
                                    farm_index_list.append(i)

                            coordinate_checks = {
                                0: (X - farm_x),  
                                1: (farm_y - Y),  
                                2: (farm_x - X),  
                                3: (Y - farm_y)   
                            }

                            index_checks = {
                                (0,1): [2],  # For Road 0
                                (0,2): [2,1],
                                (1,1): [3],  # For Road 1
                                (1,2): [0,3],
                                (2,1): [0],  # For Road 2
                                (2,2): [0,1],
                                (3,1): [1],   # For Road 3
                                (3,2): [1,2]
                            }

                            if (X,Y) in SurroundingSpots: # if the available move is a surrounding tile of this city feature 
                                
                                keys = getKeys()
                                meeplePlaced = 0
                                check = (0,0)
                               
                                # Check if road feature tile we are checking has a meeple on it
                                if (farm_x, farm_y) in keys:
                                    meeplePlaced = keys[(farm_x, farm_y)][1]
                                    check = check_tiles(meeplePlaced, farm_rotation) # Getting true coordinate of where the meeple is placed on the road feature

                                split_farms = [3, 4, 8, 9, 10, 12, 14, 16, 17, 18, 19, 21, 22, 23]
                                if check != (0,0) and (index in split_farms):
                                    tile_index = index_checks[check] # I want to check this side on the available tile 
                                    count = 0
                                    for sides in tile_index:
                                        checkCoord = coordinate_checks[sides] # Checking if on that index on the available tile is a 'C'
                                        if checkCoord == 1 and tile_properties[sides] == 'G':
                                            count += 1

                                    if count == len(tile_index) and tile not in farm_enhancements:
                                        farm_enhancements.append(['farm', tile])
                                else:
                                    for i in farm_index_list:
                                        tile_index = (i + 2) % 4
                                        checkCoord = coordinate_checks[tile_index]
                                        
                                        if checkCoord == 1 and tile_properties[tile_index] == 'G':
                                            if tile not in farm_enhancements:
                                                farm_enhancements.append(['farm', tile])

        all_enhancements = city_enhancements + road_enhancements + farm_enhancements + monastery_enhacements
        print(all_enhancements)

        if all_enhancements:
            selectedMove = random.choice(all_enhancements)
            print(f"Keep adding to your {selectedMove[0]}")
            print(selectedMove[1])
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
        keys = getKeys()
        
        combination = []

        # Iterate through self.boardcities, self.boardfarms self.board roads 
        oppcityFeatures = opponent_features(handle_features(str(Carcassonne.get_city())))
        opproadFeatures = opponent_features(handle_features(str(Carcassonne.get_road())))
        oppfarmFeatures = opponent_features(handle_features(str(Carcassonne.get_farm())))

        # List of all the player's features 
        playerCityFeatures = player_features(handle_features(str(Carcassonne.get_city())))
        playerRoadFeatures = player_features(handle_features(str(Carcassonne.get_road())))
        playerFarmFeatures = player_features(handle_features(str(Carcassonne.get_farm())))

        # Available Moves for the current tile 
        availableMoves = Carcassonne.availableMoves()
        
        for tile in availableMoves:
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            meepleLocation = tile.MeepleInfo
            index = tile.TileIndex

            SurroundingSpots = [(X-1,Y),(X,Y+1),(X+1,Y),(X,Y-1)]

            index_checks = {
                0: (X-1, Y),  
                1: (X, Y+1),  
                2: ((X+1,Y)), 
                3: ((X,Y-1)) 
            }

            tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(index)],Rotation)  # Rotates the tile properties to equal the available rotation

            if meepleLocation is None:  # If we are connecting we wont be able to place meeple 

                if index in TILE_COMBINE_CITY: # If available tile is a city connecting tile 

                    city_openings_index = []
                    for i in range(len(tile_properties)):
                            if tile_properties[i] == 'C':
                                city_openings_index.append(i)
                    
                    # Get opponents features
                    for opp_cities in oppcityFeatures:
                        print(f"opp_cities {opp_cities}")
                        opponents_city_tuple = ast.literal_eval(oppcityFeatures[opp_cities]['Tiles'])
                        print(f"opponents_city_tuple {opponents_city_tuple}")
                        opp_feature_length = len(opponents_city_tuple)
                    
                        for opp_components in opponents_city_tuple:
                            print(f"opp_component {opp_components}")
                            if not len(opp_components) == 5:
                                print(f"Skipping invalid tuple {opp_components}. Components must be of length 4. Length = {len(opp_components)}")
                                for i in range(len(opp_components)):
                                    print(opp_components[i])
                                continue  
                            opp_city_index = opp_components[0]
                            opp_city_x = opp_components[1]
                            opp_city_y = opp_components[2]
                            opp_city_rotation = opp_components[3]

                            opp_coordinate_checks = {
                                0: (X - opp_city_x),  # For CitySide 0
                                1: (opp_city_y - Y),  # For CitySide 1
                                2: (opp_city_x - X),  # For CitySide 2
                                3: (Y - opp_city_y)   # For CitySide 3
                            }
                            
                            opp_index_checks = {
                                (0,1): 2,  # For CitySide 0
                                (1,1): 3,  # For CitySide 1
                                (2,1): 0,  # For CitySide 2
                                (3,1): 1   # For CitySide 3
                            }

                            opponentMeeplePlaced = 0

                            if (opp_city_x, opp_city_y) in keys:
                                opponentMeeplePlaced = keys[(opp_city_x, opp_city_y)][1]
                            
                            opp_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(opp_city_index)],opp_city_rotation)

                            opp_index_list = [] # city index position on the city feature tile 
                            for i in range(len(opp_tile_properties)):
                                if opp_tile_properties[i] == 'C':
                                    opp_index_list.append(i)

                            # Get player features 
                            for player_cities in playerCityFeatures:
                                player_city_tuple = ast.literal_eval(playerCityFeatures[player_cities]['Tiles'])
                                player_feature_length = len(player_city_tuple)
                                
                                for player_components in player_city_tuple:
                                    if not len(player_components) == 5:
                                        print(f"Skipping invalid tuple {player_components}. Components must be of length 4. Length = {len(player_components)}")
                                        continue  
                                    player_city_index = player_components[0]
                                    player_city_x = player_components[1]
                                    player_city_y = player_components[2]
                                    player_city_rotation = player_components[3]

                                    player_coordinate_checks = {
                                        0: (X - player_city_x),  # For CitySide 0
                                        1: (player_city_y - Y),  # For CitySide 1
                                        2: (player_city_x - X),  # For CitySide 2
                                        3: (Y - player_city_y)   # For CitySide 3
                                    }
                                    
                                    player_index_checks = {
                                        (0,1): 2,  # For CitySide 0
                                        (1,1): 3,  # For CitySide 1
                                        (2,1): 0,  # For CitySide 2
                                        (3,1): 1   # For CitySide 3
                                    }

                                    playermeeplePlaced = 0

                                    if (player_city_x, player_city_y) in keys:
                                        playermeeplePlaced = keys[(player_city_x, player_city_y)][1]
                                    
                                    player_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(player_city_index)],player_city_rotation)

                                    player_index_list = [] # city index position on the city feature tile 
                                    for i in range(len(player_tile_properties)):
                                        if player_tile_properties[i] == 'C':
                                            player_index_list.append(i)

                                    # Only combine if opponents feature is larger than players
                                    if (opp_feature_length > player_feature_length): # These two features are eligible. Now we need to check if the tile fits 
                                        opp_coords = (opp_city_x, opp_city_y)
                                        player_coords = (player_city_x, player_city_y)

                                        if (opp_coords in SurroundingSpots) and (player_coords in SurroundingSpots):
                                            # Tile connects two tiles. 
                                            # Check that there isn't a meeple on a seperate side 
                                            # Check that it is conneted via cities 

                                            opp_check = (0,0)
                                            player_check = (0,0)
                                           
                                            opp_check = check_tiles(opponentMeeplePlaced, opp_city_rotation) # Getting true coordinate of where the meeple is placed on the city feature
                                            player_check = check_tiles(playermeeplePlaced, player_city_rotation)

                                            if opp_check != (0,0) and (opp_city_index == 6 or opp_city_index == 11): # Have to check which side meeple is on because there is a meeple on the tile

                                                opp_tile_index = opp_index_checks[opp_check]
                                                opp_checkCoord = opp_coordinate_checks[opp_tile_index]

                                                if opp_checkCoord == 1 and tile_properties[opp_tile_index] == 'C': # If this lines up with meeple space check the player  
                                                    # The tile matches to opponent tile city opening  

                                                    if player_check != (0,0) and (player_city_index == 6 or player_city_index == 11):
                                                        player_tile_index = player_index_checks[opp_check]
                                                        player_checkCoord = player_coordinate_checks[player_tile_index]

                                                        if player_checkCoord == 1 and tile_properties[player_tile_index] == 'C':
                                                            if tile not in combination:
                                                                combination.append(['city', tile])
                                                    else: # Player city index is not 6 or 11 
                                                        for i in player_index_list:
                                                            player_tile_index = (i + 2) % 4
                                                            player_checkCoord = player_coordinate_checks[player_tile_index]

                                                            if player_checkCoord == 1 and tile_properties[player_tile_index] == 'C':
                                                                if tile not in combination:
                                                                    combination.append(['city', tile])

                                            else: # Opponents city index is not 6 or 11 
                                                for i in opp_index_list:
                                                    opp_tile_index = (i + 2) % 4
                                                    opp_checkCoord = opp_coordinate_checks[opp_tile_index]
                                                    if opp_checkCoord == 1 and tile_properties[opp_tile_index] == 'C':

                                                        if player_check != (0,0) and (player_city_index == 6 or player_city_index == 11):
                                                            player_tile_index = player_index_checks[opp_check]
                                                            player_checkCoord = player_coordinate_checks[player_tile_index]

                                                            if player_checkCoord == 1 and tile_properties[player_tile_index] == 'C':
                                                                if tile not in combination:
                                                                    combination.append(['city', tile])
                                                        else: # Opponents city index is not 6 or 11 
                                                            for i in player_index_list:
                                                                player_tile_index = (i + 2) % 4
                                                                player_checkCoord = player_coordinate_checks[player_tile_index]

                                                                if player_checkCoord == 1 and tile_properties[player_tile_index] == 'C':
                                                                    if tile not in combination:
                                                                        combination.append(['city', tile])
                
                if index in TILE_COMBINE_ROAD: # If available tile is a road connecting tile 

                    road_openings_index = []
                    for i in range(len(tile_properties)):
                            if tile_properties[i] == 'R':
                                road_openings_index.append(i)
                    
                    # Get opponents features
                    for opp_roads in opproadFeatures:
                        print(f"opp_roads {opp_roads}")
                        opponents_road_tuple = ast.literal_eval(opproadFeatures[opp_roads]['Tiles'])
                        print(f"opponents_road_tuple {opponents_road_tuple}")
                        opp_feature_length = len(opponents_road_tuple)
                    
                        for opp_components in opponents_road_tuple:
                            print(f"opp_component {opp_components}")
                            if not len(opp_components) == 5:
                                print(f"Skipping invalid tuple {opp_components}. Components must be of length 4. Length = {len(opp_components)}")
                                for i in range(len(opp_components)):
                                    print(opp_components[i])
                                continue  
                            opp_road_index = opp_components[0]
                            opp_road_x = opp_components[1]
                            opp_road_y = opp_components[2]
                            opp_road_rotation = opp_components[3]

                            opp_coordinate_checks = {
                                0: (X - opp_road_x),  
                                1: (opp_road_y - Y),  
                                2: (opp_road_x - X),  
                                3: (Y - opp_road_y)  
                            }
                            
                            opp_index_checks = {
                                (0,1): 2,  
                                (1,1): 3, 
                                (2,1): 0,  
                                (3,1): 1   
                            }

                            opponentMeeplePlaced = 0

                            if (opp_road_x, opp_road_y) in keys:
                                opponentMeeplePlaced = keys[(opp_road_x, opp_road_y)][1]
                            
                            opp_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(opp_road_index)],opp_road_rotation)

                            opp_index_list = [] # road index position on the road feature tile 

                            for i in range(len(opp_tile_properties)):
                                if opp_tile_properties[i] == 'R':
                                    opp_index_list.append(i)

                            # Get player features 
                            for player_road in playerRoadFeatures:
                                player_road_tuple = ast.literal_eval(playerRoadFeatures[player_road]['Tiles'])
                                player_feature_length = len(player_road_tuple)
                                
                                for player_components in player_road_tuple:
                                    print(f"player_component {player_components}")
                                    if not len(player_components) == 5:
                                        print(f"Skipping invalid tuple {player_components}. Components must be of length 4. Length = {len(player_components)}")
                                        continue  
                                    player_road_index = player_components[0]
                                    player_road_x = player_components[1]
                                    player_road_y = player_components[2]
                                    player_road_rotation = player_components[3]

                                    player_coordinate_checks = {
                                        0: (X - player_road_x),  
                                        1: (player_road_y - Y),  
                                        2: (player_road_x - X),  
                                        3: (Y - player_road_y)   
                                    }
                                    
                                    player_index_checks = {
                                        (0,1): 2,  
                                        (1,1): 3,  
                                        (2,1): 0,  
                                        (3,1): 1  
                                    }

                                    playermeeplePlaced = 0

                                    if (player_road_x, player_road_y) in keys:
                                        playermeeplePlaced = keys[(player_road_x, player_road_y)][1]
                                    
                                    player_tile_properties = rotate_list(TILE_PROPERTIES_DICT[int(player_road_index)],player_road_rotation)

                                    player_index_list = [] # road index position on the road feature tile 

                                    for i in range(len(player_tile_properties)):
                                        if player_tile_properties[i] == 'R':
                                            player_index_list.append(i)

                                    # Only combine if opponents feature is larger than players
                                    if (opp_feature_length > player_feature_length): # These two features are eligible. Now we need to check if the tile fits 
                                        opp_coords = (opp_road_x, opp_road_y)
                                        player_coords = (player_road_x, player_road_y)

                                        if (opp_coords in SurroundingSpots) and (player_coords in SurroundingSpots):
                                            # Tile connects two tiles. 
                                            # Check that there isn't a meeple on a seperate side 
                                            # Check that it is conneted via cities 

                                            opp_check = (0,0)
                                            player_check = (0,0)
                                           
                                            opp_check = check_tiles(opponentMeeplePlaced, opp_road_rotation) # Getting true coordinate of where the meeple is placed on the city feature
                                            player_check = check_tiles(playermeeplePlaced, player_road_rotation)

                                            if opp_check != (0,0) and (opp_road_index == 18 or opp_road_index == 19 or opp_road_index == 23): # Have to check which side meeple is on because there is a meeple on the tile

                                                opp_tile_index = opp_index_checks[opp_check]
                                                opp_checkCoord = opp_coordinate_checks[opp_tile_index]

                                                if opp_checkCoord == 1 and tile_properties[opp_tile_index] == 'R': # If this lines up with meeple space check the player  
                                                    # The tile matches to opponent tile city opening  

                                                    if player_check != (0,0) and (opp_road_index == 18 or opp_road_index == 19 or opp_road_index == 23):
                                                        player_tile_index = player_index_checks[opp_check]
                                                        player_checkCoord = player_coordinate_checks[player_tile_index]

                                                        if player_checkCoord == 1 and tile_properties[player_tile_index] == 'R':
                                                            if tile not in combination:
                                                                combination.append(['road', tile])
                                                    else: # Player road index is not 18 or 19 or 23
                                                        for i in player_index_list:
                                                            player_tile_index = (i + 2) % 4
                                                            player_checkCoord = player_coordinate_checks[player_tile_index]

                                                            if player_checkCoord == 1 and tile_properties[player_tile_index] == 'R':
                                                                if tile not in combination:
                                                                    combination.append(['road', tile])

                                            else: # Opponents city index is not 6 or 11 
                                                for i in opp_index_list:
                                                    opp_tile_index = (i + 2) % 4
                                                    opp_checkCoord = opp_coordinate_checks[opp_tile_index]

                                                    if opp_checkCoord == 1 and tile_properties[opp_tile_index] == 'R':

                                                        if player_check != (0,0) and (player_road_index == 18 or player_road_index == 19 or player_road_index == 23):
                                                            player_tile_index = player_index_checks[opp_check]
                                                            player_checkCoord = player_coordinate_checks[player_tile_index]

                                                            if player_checkCoord == 1 and tile_properties[player_tile_index] == 'R':
                                                                if tile not in combination:
                                                                    combination.append(['road', tile])
                                                        else: # Opponents city index is not 6 or 11 
                                                            for i in player_index_list:
                                                                player_tile_index = (i + 2) % 4
                                                                player_checkCoord = player_coordinate_checks[player_tile_index]

                                                                if player_checkCoord == 1 and tile_properties[player_tile_index] == 'R':
                                                                    if tile not in combination:
                                                                        combination.append(['road', tile])
                     
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

                            # If tile connected two is in two farm features
                            # and a merging tile can be placed 
                            # Then suggest
                    

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
   


