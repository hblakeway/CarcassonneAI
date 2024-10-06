from Carcassonne_Game.Tile import Tile, TILE_PROPERTIES_DICT
from Carcassonne_Game.Tile_dict import TILE_COMBINE_CITY, TILE_COMBINE_ROAD, TILE_COMBINE_FARM
from pygameCarcassonneDir.pygameSettings import MEEPLE_SIZE, WHITE
from pygameCarcassonneDir.pygameFunctions import meepleCoordinatesAI
import ast
from collections import Counter as c
import pygame
import math

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

X_DEPTH = 10
Y_DEPTH = 20
WIDTH = HEIGHT = 104  # image scaled x2

XSHIFT = YSHIFT = MEEPLE_SIZE//2

MEEPLE_LOCATION_DICT_AI = {
    (0,1): [X_DEPTH - XSHIFT, HEIGHT//2 - YSHIFT],
    (0,2): [WIDTH//4 -XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (1,1): [WIDTH//2 - XSHIFT, Y_DEPTH - YSHIFT],
    (1,2): [WIDTH//4- XSHIFT, Y_DEPTH-YSHIFT],
    (2,1): [WIDTH - X_DEPTH - XSHIFT, HEIGHT//2 - YSHIFT],
    (2,2): [3*(WIDTH//4) - XSHIFT, Y_DEPTH-YSHIFT],
    (3,0): [3*(WIDTH//4) - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (3,1): [WIDTH//2 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (3,2): [WIDTH//4 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (0,4): [WIDTH//2 - XSHIFT, HEIGHT//2- YSHIFT],
    # exceptions
    0: [3*(WIDTH//4),Y_DEPTH - YSHIFT]
    }

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
                        #print(f"FeatureList[i] = {featureList[i]}")
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
                    #print(f"player mon = {monList[i][characteristics]}")
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
      
def check_tiles(coord, rotation):
   
    if coord in coord_rotation:
        #print(f"Original: {coord}, Rotation: {rotation}, Final: {coord_rotation[coord][rotation]}")
        return coord_rotation[coord][rotation]
    else:
        #print(0,0)
        return (0,0)

def clean(original):

    clean_tuple = []

    for item in original:
        # If the item is a tuple and has length 2, keep only the first element
        if isinstance(item, tuple) and len(item) == 2:
            clean_tuple.append(item[0])
        else:
            clean_tuple.append(item)

    return clean_tuple

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
                clean_tuple = clean(mon_tuple)
                
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
                        #f"Cities: {cities}")
                        city_tiles = cityFeatures[cities]['Tiles']
                        city_tuple = ast.literal_eval(city_tiles)
                        clean_tuple = []
                        clean_tuple = clean(city_tuple)

                        # Individual tiles that make up the city feature 
                        for item, components in enumerate(clean_tuple):
                            #print(f"City component {item}")
                            if len(components) != 5:
                                continue

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
                                #print("This tile has available spots around one of my already cities")
                                keys = getKeys()
                                meeplePlaced = 0
                                check = (0,0)
                                #print(city_index, city_rotation)
                                # Check if city feature tile we are checking has a meeple on it
                                if (city_x, city_y) in keys:
                                    #print("I may have a meeple")
                                    meeplePlaced = keys[(city_x, city_y)][1]
                                    check = check_tiles(meeplePlaced, city_rotation) # Getting true coordinate of where the meeple is placed on the city feature

                                if check != (0,0) and (index == 6 or index == 11):
                                    #print("I have a meeple on a split city. Need to be specific")
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
                        clean_tuple = []
                        clean_tuple = clean(road_tuple)
                        

                        # Individual tiles that make up the road feature 
                        for item, components in enumerate(clean_tuple):
                            #print(f"Road item {item}")
                            #print(f"Road components {components}")
                            if len(components) != 5:
                                continue

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
                        clean_tuple = []
                        clean_tuple = clean(farm_tuple)
                        

                        # Individual tiles that make up the road feature 
                        for item, components in enumerate(clean_tuple):
                            #f"Farm component {item}")
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
        #print(all_enhancements)

        if all_enhancements:
            # selectedMove = random.choice(all_enhancements) # CHECK WHICH ONE IS HIGHEST IN MCTS 
            # print(f"Keep adding to your {selectedMove[0]}")
            #print(selectedMove[1])
            return all_enhancements
        else:
            return False
        
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
                "R": "road",
                "C": "city",
                "G": "farm",
                "Monastery": "monastery"
            }

            options = []
            for i in availableMoves:
                MeepleInfo = str(i.MeepleInfo)

                if player_strategy in MeepleInfo:
                    options.append([meepleDictionary[player_strategy], i])
            
            if not options:
                return False
            
            # selectedMove = random.choice(options)
            #print(f"It would be good to start a new {meepleDictionary[player_strategy]}.")
            return options
        
        else: # Strategy is False for this move
            return False
    
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
                        opponents_city_tuple = ast.literal_eval(oppcityFeatures[opp_cities]['Tiles'])
                        opp_feature_length = len(opponents_city_tuple)
                        clean_tuple = []
                        clean_tuple = clean(opponents_city_tuple)
                    
                        for item, opp_components in enumerate(clean_tuple):
                            #f"opp_component {opp_components}")
                            if len(opp_components) != 5:
                                print(f"Skipping invalid tuple {item}.")
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
                                clean_tuple = []
                                clean_tuple = clean(player_city_tuple)
                                
                                for item, player_components in enumerate(clean_tuple):
                                    if len(player_components) != 5:
                                        print(f"Skipping invalid tuple {item}.")
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
                        #print(f"opp_roads {opp_roads}")
                        opponents_road_tuple = ast.literal_eval(opproadFeatures[opp_roads]['Tiles'])
                        #print(f"opponents_road_tuple {opponents_road_tuple}")
                        opp_feature_length = len(opponents_road_tuple)
                        clean_tuple = []
                        clean_tuple = clean(opponents_road_tuple)
                    
                        for item, opp_components in enumerate(clean_tuple):
                            #print(f"opp_component {item}")
                            if len(opp_components) != 5:
                                print(f"Skipping invalid tuple {opp_components}.")
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
                                clean_tuple = []
                                clean_tuple = clean(player_road_tuple)
                                
                                for item, player_components in enumerate(clean_tuple):
                                    #f"player_component {item}")
                                    if len(player_components) != 5:
                                        print(f"Skipping invalid tuple {item}.")
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
                     
                if index in TILE_COMBINE_FARM: # If available tile is a farm connecting tile 
                    # Gets the index of the openings 
                    farms_openings_index = []
                    for i in range(len(tile_properties)):
                            if tile_properties[i] == 'G':
                                farms_openings_index.append(i)

                    for opp_farms in oppfarmFeatures:
                        opp_farm_tiles = opproadFeatures[opp_farms]['Tiles']
                        opponents_farm_tuple = ast.literal_eval(opp_farm_tiles)
                        clean_tuple = []
                        clean_tuple = clean(opponents_farm_tuple)
                        #print(f"farm {opponents_farm_tuple}")

                        for item, opp_components in enumerate(clean_tuple):
                            if len(opp_components) != 5:
                                continue

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
            #print(f"All possibilites: {combination}")
            #selectedMove = random.choice(combination)
            #print(f"This is your opportunity to combine {selectedMove[0]}")
            return combination
        else:
            return False


# Class to manage rule status
class AdaptiveRules:
    def __init__(self, enhanceFeature=False, enhanceStrategy=False, stealPoints=False):
        self.enhanceFeature = enhanceFeature
        self.enhanceStrategy = enhanceStrategy
        self.stealPoints = stealPoints
        self.enhanceFeatureWeight = 6
        self.enhanceStrategyWeight = 3
        self.stealPointsWeight = 9
        self.lastMove = 'manual'
    
    def update_weights(self, outcome):
        if outcome:
            if self.lastMove == 'enhance_feature':
                self.enhanceFeatureWeight += 1
            elif self.lastMove == 'enhance_strategy':
                self.enhanceStrategyWeight += 1
            elif self.lastMove == 'steal_points':
                self.stealPointsWeight += 1
        else:
            if self.lastMove == 'enhance_feature':
                self.enhanceFeatureWeight -= 1
            elif self.lastMove == 'enhance_strategy':
                self.enhanceStrategyWeight -= 1
            elif self.lastMove == 'steal_points':
                self.stealPointsWeight -= 1
        print(self.enhanceFeatureWeight,self.enhanceStrategyWeight,self.stealPointsWeight)
        
    
    def get_successful_strategy(self):
    
        weights = {
            'enhance_feature': self.enhanceFeatureWeight,
            'enhance_strategy': self.enhanceStrategyWeight,
            'steal_points': self.stealPointsWeight
        }
        
        string = max(weights, key=weights.get) 
        
        return string

    def adaptive(self, DisplayScreen, Carcassonne, player_strategy):

        # Enhance feature moves 
        enhanceFeatureMoves = AdaptiveStrategies.enhance_feature(Carcassonne)
        #print(f"Enhance Features = {enhanceFeatureMoves}")

        # Enhance strategy moves 
        enhanceStrategyMoves = AdaptiveStrategies.enhance_strategy(Carcassonne, player_strategy)
        #print(f"Enhance Strategy = {enhanceStrategyMoves}")
        
        # Steal Point moves 
        enhanceStealPointMoves = AdaptiveStrategies.steal_points(Carcassonne)
        #print(f"Steal Points = {enhanceStealPointMoves}")

        player = Carcassonne.p2
        mctsMoves = player.listAction(Carcassonne)
        player = Carcassonne.p1
        # print(mctsMoves)

        adaptiveRules = []
        if enhanceFeatureMoves:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(enhanceFeatureMoves):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight + self.enhanceFeatureWeight), tile[1], 'enhance_feature', enhanceTile[0]])
        
        if enhanceStrategyMoves:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(enhanceStrategyMoves):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight + self.enhanceStrategyWeight), tile[1], 'enhance_strategy', enhanceTile[0]])

        if enhanceStealPointMoves:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(enhanceStealPointMoves):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight + self.stealPointsWeight), tile[1], 'steal_points', enhanceTile[0]])
        
        #print(adaptiveRules)
        selectedMove = None
        finalMoveType = None
        finalStrategyType = None
        if adaptiveRules:
            max_weight = max(entry[0] for entry in adaptiveRules) 
            max_weight_entries = [entry for entry in adaptiveRules if entry[0] == max_weight]

            if len(max_weight_entries) > 1:
                # get max 
                featureString = self.get_successful_strategy()
                for i in max_weight_entries:
                    weightTile, tileFeatures, strategyType, featureType = i
                    if str(strategyType) == featureString:
                        selectedMove = tileFeatures
                        self.lastMove = featureString
                        finalMoveType = featureString
                        finalStrategyType = str(featureType)
            else:
                selectedMove = max_weight_entries[0][1]
                self.lastMove = max_weight_entries[0][2]
                finalMoveType = max_weight_entries[0][2]
                finalStrategyType = max_weight_entries[0][3]
        
        if selectedMove:
            # Get attributes needed to display on the GUI
            # play move on board
            Grid_Window_Width = DisplayScreen.Grid_Window_Width
            Grid_Window_Height = DisplayScreen.Grid_Window_Height
            Grid_Size = DisplayScreen.Grid_Size
            Grid_border = DisplayScreen.Grid_border
            Meeple_Size = DisplayScreen.Meeple_Size
            GAME_DISPLAY = DisplayScreen.pygameDisplay

            DisplayTileIndex = selectedMove.TileIndex
            X,Y = selectedMove.X, selectedMove.Y
            Rotation = selectedMove.Rotation
            MeepleKey = selectedMove.MeepleInfo

            currentTile = Tile(DisplayTileIndex)

            if not(MeepleKey is None):
                feature = MeepleKey[0]
                playerSymbol = MeepleKey[1]

            # reverse orientation
            Y=Y*-1
            
            GAME_X = Grid_Size * math.floor(Grid_Window_Width/(Grid_Size*2)) + X*Grid_Size + Grid_border
            GAME_Y = Grid_Size * math.floor(Grid_Window_Height/(Grid_Size*2)) + Y*Grid_Size + Grid_border

            # Tile = DisplayTileIndex
            # load image
            image = pygame.image.load('images/' + str(DisplayTileIndex) + '.png')
            
            if not(MeepleKey is None):
                # add meeple info if one is played
                MeepleLocation = currentTile.AvailableMeepleLocs[MeepleKey]
                currentTile.Meeple = [MeepleKey[0], MeepleLocation, playerSymbol]
                #   meeple image
                meepleColour = "blue" 
                meepleImage = pygame.image.load('meeple_images/' + meepleColour + '.png')
                meepleImage = pygame.transform.scale(meepleImage, (Meeple_Size, Meeple_Size))
                X,Y = meepleCoordinatesAI(MeepleLocation, feature, MEEPLE_LOCATION_DICT_AI, DisplayTileIndex)
                image.blit(meepleImage, (X,Y))

            # Make image bigger 
            size = Grid_Size + 60
                    
            # add image      
            image = pygame.transform.scale(image, (size,size))
            image = pygame.transform.rotate(image, Rotation)
            
            # draw suggestion place rectangle
            rect_coordinates = (GAME_X,GAME_Y, Grid_Size, Grid_Size) # White spot size
            rect_surf = pygame.Surface(pygame.Rect(rect_coordinates).size)
            rect_surf.set_alpha(150)
            pygame.draw.rect(rect_surf, WHITE, rect_surf.get_rect())

            # Draw on screen
            image_coordinate  = (1070, 540)

            return(selectedMove, image, image_coordinate, rect_surf, rect_coordinates, finalMoveType, finalStrategyType )
        else:
            return(None, None, None, None, None, None, None)

        


           
    
