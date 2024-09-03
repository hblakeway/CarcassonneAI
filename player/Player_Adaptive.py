import sys
from dynrules import RuleSet, Rule, LearnSystem

class CarcassonneAdaptive:
    """
    1. Average Time Strategy 
    2. Opponent Winning Strategy
    3. Player Winning Strategy 
    4. Fields Strategy 
    """

    # For player that is taking a long time to make decisions
    def help_time():
        """
        If average time to take a move is > 10 seconds, suggest MCST
        """
        
        return 
    
    # Opponent Winning rules 
    def get_meeple_back():
        """
        Check if tile can finish any features to give  points and get meeples back
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
    
    # Fields points
    def fields():
        """
        If fields is in opponents favour, check if there is a way to gain the field back
        """
        return 
    
    help_time = Rule(1)

    get_meeple_back = Rule(2)

    feature_block = Rule(3)

    feature_latch = Rule(4)

    enhance_strategy = Rule(5)

    build_features = Rule(6)

    next_best_feature = Rule(7)

    fields = Rule(8)


class AdaptiveRuleSet (RuleSet):
    """
    """

def run():
    adaptive = CarcassonneAdaptive()


if __name__ == "__main__":
    sys.exit(run())