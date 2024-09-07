import sys
from dynrules import RuleSet, Rule, LearnSystem

class CarcassonneAdaptive:
    """
    1. Average Time Strategy 
    2. Opponent Winning Strategy
    3. Player Winning Strategy 
    4. Fields Strategy 
    """

    # For player that is taking a long time to make decisions -> can probably cover in main game loop
    def help_time():
        """
        If average time to take a move is > 10 seconds, suggest MCST
        """
        
        return 
    
    # Opponent Winning rules 
    def get_meeple_back():
        """
        Check if tile can finish any features to give points and get meeples back
        """

        return 
    
    def feature_block():
        """
        If there is a spot that would block opponent feature by placing tile
        """

    def feature_latch():
        """
        Place a tile strategically near an opponents feature to steal points 
        """
    
    def fields():
        """
        If fields is in opponents favour, check if there is a way to gain the field back
        """
        return 
    
    # Player winning rules 
    def enhance_strategy():
        """
        Check if player has signficant strategy that alligns with tile features 
        """

        return 
    
    def build_features():
        """
        Suggest to add to city/road/field already building
        """
        return

    
    def next_best_feature():
        """
        If there is/isn't a significant strategy and no where to place, suggest (MCST). 
        """
    

class AdaptiveRuleSet (RuleSet):
    """
    """
   
help_time = Rule(1)
help_time.weight = 5
help_time.code = " "

# Opponent Focussed 
get_meeple_back = Rule(2)
get_meeple_back.weight = 10 

feature_block = Rule(3)
feature_block.weight = 10 

feature_latch = Rule(4)
feature_latch.weight = 10 

# Player Foccussed 
enhance_strategy = Rule(5)
enhance_strategy.weight = 15 

build_features = Rule(6)
build_features.weight = 15 

next_best_feature = Rule(7)
next_best_feature.weight = 15 

fields = Rule(8)
fields.weight = 15


def run():
    adaptive = AdaptiveRuleSet(0, 20)
    adaptive.add(help_time)
    # adaptive.add(get_meeple_back)
    # adaptive.add(feature_block)
    # adaptive.add(feature_latch)
    # adaptive.add(enhance_strategy)
    # adaptive.add(build_features)
    # adaptive.add(next_best_feature)
    # adaptive.add(fields)


if __name__ == "__main__":
    sys.exit(run())