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

class AdaptiveStrategies:

    def adaptive_filtering(Carcassonne):
        # Available Moves for the current tile 

        enhance_feature_tiles = []
        complete_feature_tiles = []
        create_feature_tiles = []
        merge_feature_tiles = []

        availableMoves = Carcassonne.availableMoves()

        for tile in availableMoves:
            
            X = tile.X
            Y = tile.Y
            Rotation = tile.Rotation
            MeepleKey = tile.MeepleInfo
            PlayingTileIndex = tile.TileIndex
            PlayingTile= Tile(PlayingTileIndex)
            
            if PlayingTileIndex == -1:
                Carcassonne.EndGameRoutine()
                return
            
            Surroundings = [None,None,None,None]  # initialization
            SurroundingSpots = [(X-1,Y),(X,Y+1),(X+1,Y),(X,Y-1)]  # left, above, right, below

            # check if there is a tile touching the newly placed tile
            for i in range(4):
                if SurroundingSpots[i] in Carcassonne.Board:
                    Surroundings[i] = Carcassonne.Board[SurroundingSpots[i]]
            
            # rotate tile to rotation specified and place tile on board
            PlayingTile.Rotate(Rotation)
    
            # check if new tile is surrounding a monastery
            if (X,Y) in Carcassonne.MonasteryOpenings:
                for AffectedMonasteryIndex in Carcassonne.MonasteryOpenings[(X,Y)]:
                    AffectedMonastry  = Carcassonne.BoardMonasteries[AffectedMonasteryIndex]
                    if AffectedMonastry.Value == 8 and AffectedMonastry.Owner == 0:
                        complete_feature_tiles.append(['monastery', tile])
                    else:
                        if AffectedMonastry.Owner == 0:
                            enhance_feature_tiles.append(['monastery', tile])

            # New Monastry Logic 
            if MeepleKey is not None: # Monastry is not a feature without a meeple 
                if MeepleKey[0] == "Monastery":
                    if ['monastery', tile] not in create_feature_tiles:
                        create_feature_tiles.append(['monastery', tile])
            
            if PlayingTile.HasCities:
                for i in range(len(PlayingTile.CityOpenings)):
                    CityOpenings = PlayingTile.CityOpenings[i]
                    OpeningsQuantity = len(CityOpenings)

                    if OpeningsQuantity == 1:
                        CitySide = CityOpenings[0]
                        
                        if Surroundings[CitySide] is None: # treated as new city
                            if MeepleKey is not None and MeepleKey[0] == 'C':
                                if ['city', tile] not in create_feature_tiles:
                                    create_feature_tiles.append(['city', tile])
                                    
                        # connected to pre-existing city    
                        else:
                            MatchingCityIndex = Surroundings[CitySide].TileCitiesIndex[Carcassonne.MatchingSide[CitySide]]  # index of connected city
    
                            while Carcassonne.BoardCities[MatchingCityIndex].Pointer != Carcassonne.BoardCities[MatchingCityIndex].ID:  # update city IDs     
                                MatchingCityIndex = Carcassonne.BoardCities[MatchingCityIndex].Pointer

                            MatchingCity = Carcassonne.BoardCities[MatchingCityIndex]

                            if MatchingCity.Meeples[0] == 0 and MatchingCity.Meeples[1] == 0: # Empty city no one has claimed 
                                if MeepleKey is not None and MeepleKey[0] == 'C':
                                    if ['city', tile] not in create_feature_tiles:
                                        create_feature_tiles.append(['city', tile])

                            if (MatchingCity.Meeples[0] >= MatchingCity.Meeples[1]) and MatchingCity.Meeples[0] > 0 and (MatchingCity.Openings - 1 > 0): # Covers enhancing case 1,1
                                if ['city', tile] not in merge_feature_tiles or ['city', tile] not in complete_feature_tiles:
                                    enhance_feature_tiles.append(['city', tile])
                            
                            if (MatchingCity.Meeples[0] >= MatchingCity.Meeples[1]) and MatchingCity.Meeples[0] > 0 and (MatchingCity.Openings - 1 == 0):  # Covers closing case 1,1
                                complete_feature_tiles.append(['city', tile])
                            
                    else:   # Multiple Openings
                        ConnectedCities = [] 
                        # iterate for all sides with city opening
                        for CitySide in CityOpenings:
                            if Surroundings[CitySide] is not None:
                                MatchingCityIndex = Surroundings[CitySide].TileCitiesIndex[Carcassonne.MatchingSide[CitySide]]  # index of connected city
    
                                while Carcassonne.BoardCities[MatchingCityIndex].Pointer != Carcassonne.BoardCities[MatchingCityIndex].ID:  # update city IDs     
                                    MatchingCityIndex = Carcassonne.BoardCities[MatchingCityIndex].Pointer

                                ConnectedCities.append([MatchingCityIndex,CitySide])
                                    
                        # if none of the city openings connect to a pre-existing city
                        if not ConnectedCities:
                            if MeepleKey is not None and MeepleKey[0] == 'C':
                                if ['city', tile] not in create_feature_tiles:
                                    # create a new city
                                    create_feature_tiles.append(['city', tile])  

                        else: # if one of the openings connects to a city
                            # keep track of entire city openings
                            CombinedCityIndex = ConnectedCities[0][0] # Starting with first connected city 

                            for MatchingCityIndex, CitySide in ConnectedCities: # Iterate through Connected Cities, checking if it connected to combinedcity index

                                CombinedCity  = Carcassonne.BoardCities[CombinedCityIndex]

                                # Iterating through connnectedCities. If combined and matching match = this is the same city  
                                if CombinedCityIndex == MatchingCityIndex and CombinedCity.Meeples[0] == 0 and CombinedCity.Meeples[1] == 0: # Case of an unclaimed city 
                                    if MeepleKey is not None and MeepleKey[0] == 'C':
                                        if ['city', tile] not in create_feature_tiles:
                                            create_feature_tiles.append(['city', tile]) 
                                # If the index is the same to the one we are comparing to. And player 1 has a meeple on it 
                                elif CombinedCityIndex == MatchingCityIndex and (CombinedCity.Meeples[0] >= CombinedCity.Meeples[1]) and CombinedCity.Meeples[0] > 0: # Case of a player 1 city
                                    if ['city', tile] not in enhance_feature_tiles:
                                        enhance_feature_tiles.append(['city', tile]) 
                                
                                    if ['city', tile] in enhance_feature_tiles and ['city', tile] in merge_feature_tiles:
                                            enhance_feature_tiles.remove(['city', tile])
                                # Index is different, this connects two cities 
                                else:
                                    MatchingCity = Carcassonne.BoardCities[MatchingCityIndex]
                                    MatchingCity.Pointer = CombinedCityIndex # Changing the pointer to that city 
                                    
                                    # Check owners 
                                    MatchingOwner = None
                                    if MatchingCity.Meeples[0] > MatchingCity.Meeples[1]:
                                        MatchingOwner = 1
                                    elif MatchingCity.Meeples[1] > MatchingCity.Meeples[0]:
                                        MatchingOwner = 2
                                    else:
                                        MatchingOwner = 0
                                    
                                    CombinedOwner = None 
                                    if CombinedCity.Meeples[0] > CombinedCity.Meeples[1]:
                                        CombinedOwner = 1
                                    elif CombinedCity.Meeples[1] > CombinedCity.Meeples[0]:
                                        CombinedOwner = 2
                                    else:
                                        CombinedOwner = 0
                                    
                                    # print(CombinedCity) Player 1
                                    # print(MatchingCity) Player 2
                                    if MatchingOwner == 0 and CombinedOwner == 0: # No one owns these merging cities, can create a new
                                        if MeepleKey is not None and MeepleKey[0] == 'C':
                                            if ['city', tile] not in create_feature_tiles:
                                                create_feature_tiles.append(['city', tile]) 
                                    elif (MatchingOwner == 0 and CombinedOwner == 1) or (MatchingOwner == 1 and CombinedOwner == 0) or (MatchingOwner == 1 and CombinedOwner == 1): # Enhance 
                                        if ['city', tile] not in enhance_feature_tiles:
                                                enhance_feature_tiles.append(['city', tile]) 
                                    elif (MatchingOwner == 1 and CombinedOwner == 2): 
                                        if len(CombinedCity.tileList) > len(MatchingCity.tileList): # Check that Combined is larger 
                                            if (MatchingCity.Meeples[0] + CombinedCity.Meeples[0]) >= (MatchingCity.Meeples[1] + CombinedCity.Meeples[1]): # Check that player 1 meeples will be larger after the merge
                                                if ['city', tile] not in merge_feature_tiles:
                                                    merge_feature_tiles.append(['city', tile])
                                    elif (MatchingOwner == 2 and CombinedOwner == 1):
                                        if len(MatchingCity.tileList) > len(CombinedCity.tileList): # Check that Matching is larger 
                                            if (MatchingCity.Meeples[0] + CombinedCity.Meeples[0]) >= (MatchingCity.Meeples[1] + CombinedCity.Meeples[1]): # Check that player 1 meeples will be larger after the merge
                                                if ['city', tile] not in merge_feature_tiles:
                                                    merge_feature_tiles.append(['city', tile])
                                    
                                    if ['city', tile] in enhance_feature_tiles and ['city', tile] in merge_feature_tiles:
                                        enhance_feature_tiles.remove(['city', tile])

            if PlayingTile.HasRoads:
                for i in range(len(PlayingTile.RoadOpenings)):
                    RoadOpenings = PlayingTile.RoadOpenings[i]      
                    OpeningsQuantity = len(RoadOpenings) 
                    
                    if OpeningsQuantity == 1: 
                        RoadSide = RoadOpenings[0]

                        # Create a new road 
                        if Surroundings[RoadSide] is None:
                            if MeepleKey is not None and MeepleKey[0] == 'R':
                                if ['road', tile] not in create_feature_tiles:
                                    create_feature_tiles.append(['road', tile])
                        else: # Join to existing Road
                            MatchingRoadIndex = Surroundings[RoadSide].TileRoadsIndex[Carcassonne.MatchingSide[RoadSide]]
                            while Carcassonne.BoardRoads[MatchingRoadIndex].Pointer != Carcassonne.BoardRoads[MatchingRoadIndex].ID:                            
                                MatchingRoadIndex = Carcassonne.BoardRoads[MatchingRoadIndex].Pointer

                            MatchingRoad = Carcassonne.BoardRoads[MatchingRoadIndex]

                            if MatchingRoad.Meeples[0] == 0 and MatchingRoad.Meeples[1] == 0: # Empty road no one has claimed 
                                if MeepleKey is not None and MeepleKey[0] == 'R':
                                    if ['road', tile] not in create_feature_tiles:
                                        create_feature_tiles.append(['road', tile])

                            if (MatchingRoad.Meeples[0] >= MatchingRoad.Meeples[1]) and MatchingRoad.Meeples[0] > 0 and (MatchingRoad.Openings - 1 > 0): # Covers enhancing case 1,1
                                enhance_feature_tiles.append(['road', tile])
                            
                            if (MatchingRoad.Meeples[0] >= MatchingRoad.Meeples[1]) and MatchingRoad.Meeples[0] > 0 and (MatchingRoad.Openings - 1 == 0):  # Covers closing case 1,1
                                complete_feature_tiles.append(['road', tile])
                    else:
                        ConnectedRoads = []
    
                        for RoadSide in RoadOpenings:
                            if Surroundings[RoadSide] is not None:
                                MatchingRoadIndex = Surroundings[RoadSide].TileRoadsIndex[Carcassonne.MatchingSide[RoadSide]]
                                while Carcassonne.BoardRoads[MatchingRoadIndex].Pointer != Carcassonne.BoardRoads[MatchingRoadIndex].ID:                            
                                    MatchingRoadIndex = Carcassonne.BoardRoads[MatchingRoadIndex].Pointer
                            
                                ConnectedRoads.append([MatchingRoadIndex,RoadSide])
                        
                        # Create a new road 
                        if not ConnectedRoads:
                            if MeepleKey is not None and MeepleKey[0] == 'R':
                                if ['road', tile] not in create_feature_tiles:
                                    # create a new road
                                    create_feature_tiles.append(['road', tile]) 
                                
                        else: # Connects to a pre existing road 
                            CombinedRoadIndex = ConnectedRoads[0][0] # Current road on the board as reference 
                        
                            for MatchingRoadIndex,RoadSide in ConnectedRoads: # Connected roads are on the board already 
                                CombinedRoad  = Carcassonne.BoardRoads[CombinedRoadIndex] 

                                if CombinedRoadIndex == MatchingRoadIndex and CombinedRoad.Meeples[0] == 0 and CombinedRoad.Meeples[1] == 0: # Case of an unclaimed road:
                                    if MeepleKey is not None and MeepleKey[0] == 'R':
                                        if ['road', tile] not in create_feature_tiles:
                                            create_feature_tiles.append(['road', tile]) 
                                # If the index is the same to the one we are comparing to. And player 1 has a meeple on it 
                                elif CombinedRoadIndex == MatchingRoadIndex and (CombinedRoad.Meeples[0] >= CombinedRoad.Meeples[1]) and CombinedRoad.Meeples[0] > 0: # Case of a player 1 road
                                    if ['road', tile] not in enhance_feature_tiles:
                                        enhance_feature_tiles.append(['road', tile]) 
                                
                                    if ['road', tile] in enhance_feature_tiles and ['road', tile] in merge_feature_tiles:
                                            enhance_feature_tiles.remove(['road', tile])
                                else:
                                    MatchingRoad = Carcassonne.BoardRoads[MatchingRoadIndex]
                                    MatchingRoad.Pointer = CombinedRoadIndex
                                    
                                    # Check owners 
                                    MatchingOwner = None
                                    if MatchingRoad.Meeples[0] > MatchingRoad.Meeples[1]:
                                        MatchingOwner = 1
                                    elif MatchingRoad.Meeples[1] > MatchingRoad.Meeples[0]:
                                        MatchingOwner = 2
                                    else:
                                        MatchingOwner = 0
                                    
                                    CombinedOwner = None 
                                    if CombinedRoad.Meeples[0] > CombinedRoad.Meeples[1]:
                                        CombinedOwner = 1
                                    elif CombinedRoad.Meeples[1] > CombinedRoad.Meeples[0]:
                                        CombinedOwner = 2
                                    else:
                                        CombinedOwner = 0
                                    
                                    if MatchingOwner == 0 and CombinedOwner == 0: # No one owns these merging roads, can create a new
                                        if MeepleKey is not None and MeepleKey[0] == 'R':
                                            if ['road', tile] not in create_feature_tiles:
                                                create_feature_tiles.append(['road', tile]) 
                                    elif (MatchingOwner == 0 and CombinedOwner == 1) or (MatchingOwner == 1 and CombinedOwner == 0) or (MatchingOwner == 1 and CombinedOwner == 1): # Enhance 
                                        if ['road', tile] not in enhance_feature_tiles:
                                                enhance_feature_tiles.append(['road', tile]) 
                                    elif (MatchingOwner == 1 and CombinedOwner == 2): 
                                        if len(CombinedRoad.tileList) > len(MatchingRoad.tileList): # Check that Combined is larger 
                                            if (MatchingRoad.Meeples[0] + CombinedRoad.Meeples[0]) >= (MatchingRoad.Meeples[1] + CombinedRoad.Meeples[1]): # Check that player 1 meeples will be larger after the merge
                                                if ['road', tile] not in merge_feature_tiles:
                                                    merge_feature_tiles.append(['road', tile])
                                    elif (MatchingOwner == 2 and CombinedOwner == 1):
                                        if len(MatchingRoad.tileList) > len(CombinedRoad.tileList): # Check that Matching is larger 
                                            if (MatchingRoad.Meeples[0] + CombinedRoad.Meeples[0]) >= (MatchingRoad.Meeples[1] + CombinedRoad.Meeples[1]): # Check that player 1 meeples will be larger after the merge
                                                if ['road', tile] not in merge_feature_tiles:
                                                    merge_feature_tiles.append(['road', tile])
                                    
                                    if ['road', tile] in enhance_feature_tiles and ['road', tile] in merge_feature_tiles:
                                        enhance_feature_tiles.remove(['road', tile])
                                                
            if PlayingTile.HasFarms:
                for i in range(len(PlayingTile.FarmOpenings)):
                    FarmOpenings = PlayingTile.FarmOpenings[i]
                   
                    OpeningsQuantity = len(FarmOpenings)      
                    if OpeningsQuantity == 1:
                        FarmSide = FarmOpenings[0][0]
                        FarmLine = FarmOpenings[0][1]
                        
                        if Surroundings[FarmSide] is None: # Create a new farm 
                            if MeepleKey is not None and MeepleKey[0] == 'G':
                                if ['farm', tile] not in create_feature_tiles:
                                    create_feature_tiles.append(['farm', tile])
                        else: # Join to existing farm 
                            MatchingFarmIndex = Surroundings[FarmSide].TileFarmsIndex[Carcassonne.MatchingSide[FarmSide]][Carcassonne.MatchingLine[FarmLine]]
                            while Carcassonne.BoardFarms[MatchingFarmIndex].Pointer != Carcassonne.BoardFarms[MatchingFarmIndex].ID:                            
                                MatchingFarmIndex = Carcassonne.BoardFarms[MatchingFarmIndex].Pointer
                            
                            MatchingFarm = Carcassonne.BoardFarms[MatchingFarmIndex]

                            if MatchingFarm.Meeples[0] == 0 and MatchingFarm.Meeples[1] == 0: # Empty farm no one has claimed 
                                if MeepleKey is not None and MeepleKey[0] == 'G':
                                    if ['farm', tile] not in create_feature_tiles:
                                        create_feature_tiles.append(['farm', tile])

                            #if (MatchingFarm.Meeples[0] >= MatchingFarm.Meeples[1]) and MatchingFarm.Meeples[0] > 0: # Covers enhancing case 1,1
                            #    enhance_feature_tiles.append(['farm', tile])
                    else:
                        ConnectedFarms = set()
                        for (FarmSide, FarmLine) in FarmOpenings:
                            if Surroundings[FarmSide] is not None:
                                MatchingFarmIndex = Surroundings[FarmSide].TileFarmsIndex[Carcassonne.MatchingSide[FarmSide]][Carcassonne.MatchingLine[FarmLine]]
                                # Find the root farm with path compression
                                root_farm_index = Carcassonne.find_root(MatchingFarmIndex)
                                ConnectedFarms.add(root_farm_index)

                        if not ConnectedFarms:
                            if MeepleKey is not None and MeepleKey[0] == 'G':
                                if ['farm', tile] not in create_feature_tiles:
                                    # create a new farm
                                    create_feature_tiles.append(['farm', tile])     
                        else:
                            CombinedFarmIndex = min(ConnectedFarms)
                            
                            for MatchingFarmIndex in ConnectedFarms: 
                                CombinedFarm  = Carcassonne.BoardFarms[CombinedFarmIndex]
                                MatchingFarm = Carcassonne.BoardFarms[MatchingFarmIndex]

                                if CombinedFarmIndex != MatchingFarmIndex:
                                    MatchingFarm.Pointer = CombinedFarmIndex

                                # Check owners 
                                MatchingOwner = None
                                if MatchingFarm.Meeples[0] > MatchingFarm.Meeples[1]:
                                    MatchingOwner = 1
                                elif MatchingFarm.Meeples[1] > MatchingFarm.Meeples[0]:
                                    MatchingOwner = 2
                                else:
                                    MatchingOwner = 0
                                
                                CombinedOwner = None 
                                if CombinedFarm.Meeples[0] > CombinedFarm.Meeples[1]:
                                    CombinedOwner = 1
                                elif CombinedFarm.Meeples[1] > CombinedFarm.Meeples[0]:
                                    CombinedOwner = 2
                                else:
                                    CombinedOwner = 0
                                
                                if MatchingOwner == 0 and CombinedOwner == 0: # No one owns these merging farms, can create a new
                                    if MeepleKey is not None and MeepleKey[0] == 'G':
                                        if ['farm', tile] not in create_feature_tiles:
                                            create_feature_tiles.append(['farm', tile]) 
                                #elif (MatchingOwner == 0 and CombinedOwner == 1) or (MatchingOwner == 1 and CombinedOwner == 0) or (MatchingOwner == 1 and CombinedOwner == 1): # Enhance 
                                #    if ['farm', tile] not in enhance_feature_tiles and PlayingTile.HasCities:
                                #            enhance_feature_tiles.append(['farm', tile]) 
                                elif (MatchingOwner == 1 and CombinedOwner == 2) or (MatchingOwner == 2 and CombinedOwner == 1): # Player 1 owns one and Player 2 Owns one 
                                    if (MatchingFarm.Meeples[0] + CombinedFarm.Meeples[0]) >= (MatchingFarm.Meeples[1] + CombinedFarm.Meeples[1]):
                                        if ['farm', tile] not in merge_feature_tiles:
                                            merge_feature_tiles.append(['farm', tile])

                                #if ['farm', tile] in enhance_feature_tiles and ['farm', tile] in merge_feature_tiles:
                                #    enhance_feature_tiles.remove(['farm', tile])
                            

        # print(f"Enhancing List = {enhance_feature_tiles}")
        # print(f"Completing List = {complete_feature_tiles}")
        # print(f"Creating New List = {create_feature_tiles}")
        print(f"Merging List = {merge_feature_tiles}")

        return enhance_feature_tiles,complete_feature_tiles, create_feature_tiles, merge_feature_tiles

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
                return []
            
            # selectedMove = random.choice(options)
            #print(f"It would be good to start a new {meepleDictionary[player_strategy]}.")
            return options
        
        else: # Strategy is False for this move
            return []

# Class to manage rule status
class AdaptiveRules:
    def __init__(self, enhanceFeature=False, enhanceStrategy=False, stealPoints=False, completeFeature=None, enhanceLeast=None, enhanceMost = None):
        
        self.enhanceFeature = enhanceFeature
        self.stealPoints = stealPoints
        self.completeFeature = completeFeature
        self.enhanceLeast = enhanceLeast # Least Points 
        self.enhanceMost = enhanceMost # Most Points
        self.enhanceStrategy = enhanceStrategy # Most common place meeple placed

        self.enhanceFeatureWeight = 5 #Add to existing
        self.completeFeatureWeight = 10 #Complete Existing
        self.enhanceStrategyWeight = 2 #Create new according to player strategy
        self.stealPointsWeight = 10 #Steal points 
        self.enhanceLeastWeight = 1 #Enhance feature with least points
        self.enhanceMostWeight = 1 #Enhance feature with most points

        self.lastMove = 'manual'

        self.lastEnhanceFeature = []
        self.lastEnhanceStrategy = []
        self.lastStealPoints = []
        self.lastCompleteFeature = []
        self.lastEnhanceLeast = []
        self.lastEnhanceMost = []

    def update_weights(self, outcome, move):

        #strategies = ['enhance_feature', 'enhance_strategy', 'steal_points', 'complete_feature', 'enhance_least', 'enhance_most']

        if outcome:
            if self.lastMove == 'enhance_feature':
                self.enhanceFeatureWeight * 2
            elif self.lastMove == 'enhance_strategy':
                self.enhanceStrategyWeight * 1.2
            elif self.lastMove == 'steal_points':
                self.stealPointsWeight * 2
            elif self.lastMove == 'complete_feature':
                self.completeFeatureWeight * 2
            elif self.lastMove == 'enhance_least':
                self.enhanceLeastWeight * 1.2
            elif self.lastMove == 'enhance_most':
                self.enhanceMostWeight * 1.2
            
        else:
            if self.lastMove == 'enhance_feature':
                self.enhanceFeatureWeight -= 0.5
            elif self.lastMove == 'enhance_strategy':
                self.enhanceStrategyWeight -= 3
            elif self.lastMove == 'steal_points':
                self.stealPointsWeight -= 1
            elif self.lastMove == 'complete_feature':
                self.completeFeatureWeight -= 0.5
            elif self.lastMove == 'enhance_least':
                self.enhanceLeastWeight -= 3
            elif self.lastMove == 'enhance_most':
                self.enhanceMostWeight -= 3
            
        print(self.enhanceFeatureWeight,self.enhanceStrategyWeight,self.stealPointsWeight, self.completeFeatureWeight, self.enhanceLeastWeight, self.enhanceMostWeight)
        
    def get_successful_strategy(self, strategies):
    
        weights = {
            'enhance_feature': self.enhanceFeatureWeight,
            'complete_feature': self.completeFeatureWeight,
            'enhance_strategy': self.enhanceStrategyWeight,
            'steal_points': self.stealPointsWeight, 
            'enhance_least': self.enhanceLeastWeight,
            'enhance_most': self.enhanceMostWeight
        }

        best_strategy = None
        highest_weight = -float('inf')  

        for strategy in strategies:
            # Check if the strategy is in the weights dictionary
            if strategy in weights:
                if weights[strategy] > highest_weight:
                    highest_weight = weights[strategy]
                    best_strategy = strategy
        
        return best_strategy

    def adaptive(self, DisplayScreen, Carcassonne, player_strategy):

        enhance_feature_tiles, complete_feature_tiles, create_feature_tiles, merge_feature_tiles = AdaptiveStrategies.adaptive_filtering(Carcassonne)
        
        enhanceStrategyMoves = AdaptiveStrategies.enhance_strategy(Carcassonne, player_strategy)

        # Setting variables to be checked after move is made 
        self.lastEnhanceFeature = enhance_feature_tiles
        self.lastEnhanceStrategy = enhanceStrategyMoves
        self.lastStealPoints = merge_feature_tiles
        self.lastCompleteFeature = complete_feature_tiles

        # Strategic Options 
        lowest_points = []
        highest_points = []
        
        feature_points_index = {0:'city', 1:'road', 2:'monastery', 3: 'city', 4: 'road', 5:'monastery', 6: 'farm'}
        featurePoints = Carcassonne.FeatureScores[0]
        print(f"Current Feature Scores: {featurePoints[:3]}")
        lowest_category = min(featurePoints[:3])
        highest_category = max(featurePoints[:3])

        lowest_index = Carcassonne.FeatureScores[0].index(lowest_category)
        highest_index = Carcassonne.FeatureScores[0].index(highest_category)

        for tileType, enhanceTile in create_feature_tiles:
            if str(tileType) == str(feature_points_index[lowest_index]):
                lowest_points.append([tileType, enhanceTile])
        
        for tileType, enhanceTile in create_feature_tiles:
            if str(tileType) == str(feature_points_index[highest_index]):
                highest_points.append([tileType, enhanceTile])
        
        for entry in enhanceStrategyMoves:
            if entry in lowest_points:
                lowest_points.remove(entry)
            elif entry in highest_points:
                highest_points.remove(entry)
        
        for entry in merge_feature_tiles:
            if entry in lowest_points:
                lowest_points.remove(entry)
            elif entry in highest_points:
                highest_points.remove(entry)
        
        for entry in complete_feature_tiles:
            if entry in lowest_points:
                lowest_points.remove(entry)
            elif entry in highest_points:
                highest_points.remove(entry)

        self.lastEnhanceLeast = lowest_points
        self.lastEnhanceMost = highest_points

        player = Carcassonne.p2
        mctsMoves = player.listAction(Carcassonne)
        player = Carcassonne.p1
        
        adaptiveRules = []

        # print(mctsMoves)

        if enhance_feature_tiles:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(enhance_feature_tiles):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight * self.enhanceFeatureWeight), tile[1], 'enhance_feature', enhanceTile[0]])
        
        if complete_feature_tiles:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(complete_feature_tiles):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight * self.completeFeatureWeight), tile[1], 'complete_feature', enhanceTile[0]])
        
        if enhanceStrategyMoves:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(enhanceStrategyMoves):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight * self.enhanceStrategyWeight), tile[1], 'enhance_strategy', enhanceTile[0]])

        if merge_feature_tiles:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(merge_feature_tiles):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight * self.stealPointsWeight), tile[1], 'steal_points', enhanceTile[0]])
        
        
        if lowest_points:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(lowest_points):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight * self.enhanceLeastWeight), tile[1], 'enhance_least', enhanceTile[0]])
        
        if highest_points:
            for weight, tile in enumerate(mctsMoves):
                for tileType, enhanceTile in enumerate(highest_points):
                    if str(enhanceTile[1]) == str(tile[1]):
                        adaptiveRules.append([int(weight * self.enhanceMostWeight), tile[1], 'enhance_most', enhanceTile[0]])
        
        selectedMove = None
        finalMoveType = None
        finalStrategyType = None

        if adaptiveRules:
            print("Top 10%")
            sorted_list = sorted(adaptiveRules, key=lambda x: x[0], reverse=True)
            calc = max(1, len(sorted_list) // 10)
            for i in sorted_list[:calc]:
                print(i)

            max_weight = max(entry[0] for entry in adaptiveRules) 
            max_weight_entries = [entry for entry in adaptiveRules if entry[0] == max_weight]

            if len(max_weight_entries) > 1:
                # get max 
                strategies = []

                for i in max_weight_entries:
                    weightTile, tileFeatures, strategyType, featureType = i
                    strategies.append(str(strategyType))
                
                featureString = self.get_successful_strategy(strategies)
                # print(featureString)

                for i in max_weight_entries:
                    weightTile, tileFeatures, strategyType, featureType = i
                    if str(strategyType) == featureString:
                        selectedMove = tileFeatures
                        self.lastMove = featureString
                        finalMoveType = featureString
                        finalStrategyType = str(featureType)
                        print("Selected Move =", selectedMove,self.lastMove,finalMoveType,finalStrategyType)
            else:
                selectedMove = max_weight_entries[0][1]
                self.lastMove = max_weight_entries[0][2]
                finalMoveType = max_weight_entries[0][2]
                finalStrategyType = max_weight_entries[0][3]
                print("Selected Move =",selectedMove,self.lastMove,finalMoveType,finalStrategyType)

        
        if selectedMove: # Place tile 
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

            # Place coloured tile 
            
            GAME_X = Grid_Size * math.floor(Grid_Window_Width/(Grid_Size*2)) + X*Grid_Size + Grid_border
            GAME_Y = Grid_Size * math.floor(Grid_Window_Height/(Grid_Size*2)) + (Y*-1)*Grid_Size + Grid_border

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

        


           
    
