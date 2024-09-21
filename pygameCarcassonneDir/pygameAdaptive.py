import sys
from player.Player import Player
from collections import Counter as c
import itertools as it
from dynrules import RuleSet, Rule, LearnSystem
from Carcassonne_Game.Tile import Tile, ROTATION_DICT, SIDE_CHANGE_DICT, AvailableMove

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


# Player focussed rules 
# Goal of the adaptive AI is to adapt to the players strategy
# Example Cases:
# If player is building a city up - make suggestion towards building that 
# If player is build up a road - make suggestion towards building up that road 

def enhance_strategy(Carcassonne, player_strategy):
    """
    Check if player has a signficant strategy (Meeple on Road/ Meeple on City / Meeple on Monastry / Meple on Field).
    """

    # remaining meeples
    meeples = Carcassonne.Meeples
    p1_meeples = meeples[0]
    print (p1_meeples)

    # Features which the player has placed meeples on 
    meeplePlacements = []
    for i in player_strategy:
        if i[4] is not None:
            meeplePlacements.append(i[4][0])

    print(meeplePlacements)

    # If there is a majority stratgey check if you can place a meeple on the same feature 
    player_strategy = strategy(meeplePlacements)
    if player_strategy is not None and p1_meeples > 0:
        meepleDictionary = {
            "R": "Road",
            "C": "City",
            "G": "Farm",
            "Monastery": "Monastery"
        }
        print(f"Player is building lots of {meepleDictionary[player_strategy]}")

        availableMoves = Carcassonne.availableMoves()

        options = []
        for i in availableMoves:
            MeepleInfo = str(i.MeepleInfo)
            # print(f"Available Move is {i}")
            # print(f"That meeple infor should equal = {MeepleInfo}")
            # print(f"The player strategy is {player_strategy}")

            if player_strategy in MeepleInfo:
                options.append(i)
        
        for i in options:
            print(i)
    else: 
        return False


    return True 

def complete_feature():
    """
    Complete a feature that player has made. 
    """

    "1. Can the tile complete a feature "

    # Checks if any of those spots are connecting to an unfinished meeple feature

    # Checks if that tile can complete and give that meeple back 
    
    return

def grow_feature():
    """
    Grow a feature that player has made. 
    """

    "1. Can the tile complete a feature "

    # Takes available spots

    # Checks if any of those spots are connecting to an unfinished meeple feature

    # Checks if that tile can complete and give that meeple back 
    
    return



class CarcassonneAdaptive():
    """
    1. Average Time Strategy 
    2. Opponent Winning Strategy
    3. Player Winning Strategy 
    4. Fields Strategy 
    """

    # 1st check which strategy is possible 

    
    
    
    

class AdaptiveRuleSet(RuleSet):
    """
    """
   


