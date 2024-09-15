import sys
from player.Player import Player
from collections import Counter as c
from dynrules import RuleSet, Rule, LearnSystem

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

def leastPlayerStrategy():
    """

    """


# Player focussed rules 
# Goal of the adaptive AI is to adapt to the players strategy
# Example Cases:
# If player is building a city up - make suggestion towards building that 
# If player is build up a road - make suggestion towards building up that road 

def enhance_strategy(player_strategy):
    """
    Check if player has a signficant strategy (Meeple on Road/ Meeple on City / Meeple on Monastry / Meple on Field).
    """

    # Have current tile 

    # Have all the available spots
    # var = CarcassonneState.availableMoves

    meeplePlacements = []
    for i in player_strategy:
        if i[4] is not None:
            meeplePlacements.append(i[4][0])

    print(meeplePlacements)

    # If there is a majority stratgey check if you can place a meeple on the same feature 
    player_strategy = strategy(meeplePlacements)
    if player_strategy is not None:
        meepleDictionary = {
            "R": "roads",
            "C": "cities",
            "G": "farms",
            "Monastery": "monastries"
        }
        print(f"Player is building lots of {meepleDictionary[player_strategy]}")

    # If not rule is false 

    return

def complete_feature():
    """
    Complete a feature that player has made. 
    """

    "1. Can the tile complete a feature "

    # Takes available spots

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
   


