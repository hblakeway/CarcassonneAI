import sys
from dynrules import RuleSet, Rule, LearnSystem


# Goal of the adaptive AI is to adapt to the players strategy
# Example Cases:
# If player is building a city up - make suggestion towards building that 
# If player is build up a road - make suggestion towards building up that road 
# 

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
        If average time to take a move is > 10 seconds, suggest MCST. 
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

    def next_best_feature():
        """
        If there is/isn't a significant strategy or opponent blocking and no where to place, suggest (MCST). 
        """
    

class AdaptiveRuleSet (RuleSet):
    """
    """
   
help_time = Rule(1)
help_time.weight = 5
help_time.code = CarcassonneAdaptive.help_time

# Opponent Focussed 
get_meeple_back = Rule(2)
get_meeple_back.weight = 10 
get_meeple_back.code = CarcassonneAdaptive.get_meeple_back

feature_block = Rule(3)
feature_block.weight = 10 
feature_block.code = CarcassonneAdaptive.feature_block

fields = Rule(7)
fields.weight = 15
fields.code = CarcassonneAdaptive.fields

# Player Foccussed 
enhance_strategy = Rule(5)
enhance_strategy.weight = 15 
enhance_strategy.code = CarcassonneAdaptive.enhance_strategy

next_best_feature = Rule(6)
next_best_feature.weight = 5




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