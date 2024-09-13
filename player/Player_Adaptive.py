import sys
from dynrules import RuleSet, Rule, LearnSystem

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


# Goal of the adaptive AI is to adapt to the players strategy
# Example Cases:
# If player is building a city up - make suggestion towards building that 
# If player is build up a road - make suggestion towards building up that road 
# 


"""
If player is winning AI could 
- enhance player strategy (player strategy)
- complete player feature (player strategy)
- block player feature (opponent strategy)(if close to completing)
- gain back feature (opponent strategy)

If player is loosing AI could 
- enhance player strategy (player strategy)
- complete player feature (player strategy)
- block player feature (opponent strategy)
- gain back feature (opponent strategy)

If player has strong strategy:
- enhance player strategy (player strategy)
- complete player feature (player strategy)

"""
class CarcassonneAdaptive:
    """
    1. Average Time Strategy 
    2. Opponent Winning Strategy
    3. Player Winning Strategy 
    4. Fields Strategy 
    """

    # 1st check which strategy is possible 

    # Player winning rules 
    def enhance_strategy(availableSpots):
        """
        Check if player has signficant strategy that alligns with tile features 
        """

        "1. Each tile placed should be categorised "
        # Takes available spots


        # Checks if any of those spots are connecting to an unfinished meeple feature 

        # If not check if can create new feature based on majority strategy 



        return
    
    def complete_feature():
        """
        Complete a feature that has a meeple 
        """

        "1. Can the tile complete a feature "

        # Takes available spots

        # Checks if any of those spots are connecting to an unfinished meeple feature

        # Checks if that tile can complete and give that meeple back 
        return

    
    # Opponent Winning rules 
    
    def feature_block():
        """
        If there is a spot that would block opponent feature by placing tile
        """
        # Takes available spots 

        # Checks if any of those would cause block in opponents meeple feature 

        return 

    def gain_feature():
        """
        If field or feature is dominated, check if there is a move to reduce this 
        """
        # Takes available spots 

        # Checks for spot that would score the most points placing meeple on field 

        return 
    

    # Second from the availble stategyies apply rules and with utility weight
    # Adaptive AI chooses rule with most reward 

class AdaptiveRuleSet (RuleSet):
    """
    """
   

# Player Foccussed 
enhance_strategy = Rule(5)
enhance_strategy.weight = 15 
enhance_strategy.code = CarcassonneAdaptive.enhance_strategy

complete_feature = Rule(6)
complete_feature.weight = 5
complete_feature.code = CarcassonneAdaptive.complete_feature

# Opponent Focussed 
feature_block = Rule(3)
feature_block.weight = 10 
feature_block.code = CarcassonneAdaptive.feature_block

gain_feature = Rule(7)
gain_feature.weight = 15
gain_feature.code = CarcassonneAdaptive.gain_feature



def run():
    adaptive = AdaptiveRuleSet(0, 20)
    
    adaptive.add(enhance_strategy)
    # adaptive.add(feature_block)
    # adaptive.add(complete_feature)
    # adaptive.add(gain_feature)


if __name__ == "__main__":
    sys.exit(run())