"""
{
    0:
    1:
    2:
    3:
    4:
    5:
    6:
    7:
    8:
    9:
    10:
    11:
    12:
    13:
    14:
    15:
    16:
    17:
    18:
    19:
    20:
    21:
    22:
    23:
    }
"""

TILE_DESC_DICT = {
    0:"City Centre (Double)",
    1:"City + Small Farm to South",
    2:"City + Small Farm to South (Double)",
    3:"City + Road Entrance",
    4:"City + Road Entrance (Double)",
    5:"Diagonal City Wall + Farm",
    6:"Two Adjacent City Walls",
    7:"Diagonal City Wall + Farm (Double)",
    8:"Diagonal City Wall + Farm + Road",
    9:"Diagonal City Wall + Farm + Road (Double)",
    10:"City with Farms Either Side",
    11:"Opposite Facing City Walls",
    12:"Opposite Facing City Walls (Double)",
    13:"One City Wall",
    14:"One City Wall + Diagonal Road 1",
    15:"Monastery + Road",
    16:"One City Wall + Straight Road",
    17:"One City Wall + Diagonal Road 2",
    18:"One City Wall + Road Junction",
    19:"3-way Junction",
    20:"Monastery",
    21:"Diagonal Road",
    22:"Straight Road",
    23:"4-way Junction"
    }

# number of times tile appears in a deck
TILE_COUNT_DICT={
    0:1,
    1:3,
    2:1,
    3:1,
    4:2,
    5:3,
    6:2,
    7:2,
    8:2,
    9:3,
    10:1,
    11:3,
    12:2,
    13:5,
    14:3,
    15:2,
    16:4,
    17:3,
    18:3,
    19:4,
    20:4,
    21:9,
    22:8,
    23:1
    }



# list of tile types with following properties
HAS_MONASTERY = [15,20] # has a monastery
HAS_CITY = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18]
HAS_ROAD = [3,4,8,9,14,15,16,17,18,19,21,22,23]
HAS_NOT_FARM = [0]

# number of rotations available for each tile (4 available if not listed)
NO_ROTATIONS = [0,20,23]
ONE_ROTATION = [10,11,12,22]

# double city value
IS_DOUBLE = [0,2,4,7,9,12]

# city openings
CITY_OPENINGS_DICT={
    0: [[0,1,2,3]],
    1: [[0,1,2]],
    2: [[0,1,2]],
    3: [[0,1,2]],
    4: [[0,1,2]],
    5: [[1,2]],
    6: [[1],[2]],
    7: [[1,2]],
    8: [[1,2]],
    9: [[1,2]],
    10: [[0,2]],
    11: [[1],[3]],
    12: [[0,2]],
    13: [[1]],
    14: [[1]],
    16: [[1]],
    17: [[1]],
    18: [[1]]
    }

# locations of farms on tiles
FARM_OPENINGS_DICT={
    1:[[(3,1)]],
    2:[[(3,1)]],
    3:[[(3,0)],[(3,2)]],
    4:[[(3,0)],[(3,2)]],
    5:[[(0,1),(3,1)]],
    6:[[(0,1),(3,1)]],
    7:[[(0,1),(3,1)]],
    8:[[(0,0),(3,2)],[(0,2),(3,0)]],
    9:[[(0,0),(3,2)],[(0,2),(3,0)]],
    10:[[(1,1)],[(3,1)]],
    11:[[(0,1),(2,1)]],
    12:[[(1,1)],[(3,1)]],
    13:[[(0,1),(2,1),(3,1)]],
    14:[[(0,0),(3,2)],[(0,2),(2,1),(3,0)]],
    15:[[(0,1),(1,1),(2,1),(3,0),(3,2)]],
    16:[[(0,0),(2,2),(3,1)],[(0,2),(2,0)]],
    17:[[(0,1),(2,0),(3,2)],[(2,2),(3,0)]],
    18:[[(0,0),(3,2)],[(0,2),(2,0)],[(2,2),(3,0)]],
    19:[[(0,0),(3,2)],[(0,2),(1,1),(2,0)],[(2,2),(3,0)]],
    20:[[(0,1),(1,1),(2,1),(3,1)]],
    21:[[(0,0),(3,2)],[(0,2),(1,1),(2,1),(3,0)]],
    22:[[(0,0),(2,2),(3,1)],[(0,2),(1,1),(2,0)]],
    23:[[(0,0),(3,2)],[(0,2),(1,0)],[(1,2),(2,0)],[(2,2),(3,0)]]
    }

# locations of roads on tiles
ROAD_OPENINGS_DICT={
    3:[[3]],
    4:[[3]],
    8:[[0,3]],
    9:[[0,3]],
    14:[[0,3]],
    15:[[3]],
    16:[[0,2]],
    17:[[2,3]],
    18:[[0],[2],[3]],
    19:[[0],[2],[3]],
    21:[[0,3]],
    22:[[0,2]],
    23:[[0],[1],[2],[3]]  
    }

# description of tile edges
TILE_PROPERTIES_DICT={
    0:["C","C","C","C"],
    1:["C","C","C","G"],
    2:["C","C","C","G"],
    3:["C","C","C","R"],
    4:["C","C","C","R"],
    5:["G","C","C","G"],
    6:["G","C","C","G"],
    7:["G","C","C","G"],
    8:["R","C","C","R"],
    9:["R","C","C","R"],
    10:["C","G","C","G"],
    11:["G","C","G","C"],
    12:["C","G","C","G"],
    13:["G","C","G","G"],
    14:["R","C","G","R"], # bottom left top right
    15:["G","G","G","R"],
    16:["R","C","R","G"],
    17:["G","C","R","R"],
    18:["R","C","R","R"],
    19:["R","G","R","R"],
    20:["G","G","G","G"],
    21:["R","G","G","R"],
    22:["R","G","R","G"],
    23:["R","R","R","R"]
    }



# list of city sides connected to farm
FARM_CITY_INDEX_DICT = {
    1:[[1]],
    2:[[1]],
    3:[[1],[1]],
    4:[[1],[1]],
    5:[[1]],
    6:[[1,2]],
    7:[[1]],
    8:[[],[1]],
    9:[[],[1]],
    10:[[0],[0]],
    11:[[1,3]],
    12:[[0],[0]],
    13:[[1]],
    14:[[],[1]],
    15:[[]],
    16:[[],[1]],
    17:[[1],[]],
    18:[[],[1],[]],
    19:[[],[],[]],
    20:[[]],
    21:[[],[]],
    22:[[],[]],
    23:[[],[],[],[]]
    }

# possible location of meeples for each tile
MEEPLE_LOC_DICT={
    0:{("C",0):(0,1)},
    1:{("C",0):(0,1),("G",0):(3,1)},
    2:{("C",0):(0,1),("G",0):(3,1)},
    3:{("C",0):(0,1),("R",0):(3,1),("G",0):(3,0),("G",1):(3,2)},
    4:{("C",0):(0,1),("R",0):(3,1),("G",0):(3,0),("G",1):(3,2)},
    5:{("C",0):(1,1),("G",0):(3,1)},
    6:{("C",0):(1,1),("C",1):(2,1),("G",0):(3,1)},
    7:{("C",0):(1,1),("G",0):(3,1)},
    8:{("C",0):(1,1),("R",0):(0,1),("G",0):(3,2),("G",1):(0,2)},
    9:{("C",0):(1,1),("R",0):(0,1),("G",0):(3,2),("G",1):(0,2)},
    10:{("C",0):(0,1),("G",0):(1,1),("G",1):(3,1)},
    11:{("C",0):(1,1),("C",1):(3,1),("G",0):(0,1)},
    12:{("C",0):(0,1),("G",0):(1,1),("G",1):(3,1)},
    13:{("C",0):(1,1),("G",0):(3,1)},
    14:{("C",0):(1,1),("R",0):(0,1),("G",0):(3,2),("G",1):(2,1)},
    15:{("R",0):(3,1),("Monastery",0):(0,4),("G",0):(0,2)},
    16:{("C",0):(1,1),("R",0):(0,1),("G",0):(3,1),("G",1):(0,2)},
    17:{("C",0):(1,1),("R",0):(2,1),("G",0):(0,1),("G",1):(2,2)},
    18:{("C",0):(1,1),("R",0):(0,1),("R",1):(2,1),("R",2):(3,1),("G",0):(3,2),("G",1):(0,2),("G",2):(2,2)},
    19:{("R",0):(0,1),("R",1):(2,1),("R",2):(3,1),("G",0):(3,2),("G",1):(0,2),("G",2):(2,2)},
    20:{("Monastery",0):(0,4),("G",0):(0,2)},
    21:{("R",0):(0,1),("G",0):(3,2),("G",1):(2,1)},
    22:{("R",0):(0,1),("G",0):(3,2),("G",1):(0,2)},
    23:{("R",0):(0,1),("R",1):(1,1),("R",2):(2,1),("R",3):(3,1),("G",0):(3,2),("G",1):(0,2),("G",2):(1,2),("G",3):(2,2)}
    }

TILE_INDEX_LIST = [0, 1, 1, 1, 2, 3, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 
                   10, 11, 11, 11, 12, 12, 13, 13, 13, 13, 13, 14, 14, 14, 15, 
                   15, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 19, 20, 
                   20, 20, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 
                   22, 22, 22, 22, 22, 23]


# Tiles that could combine features potentially 
TILE_COMBINE_CITY = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 12]

TILE_COMBINE_ROAD = [8, 9, 14, 16, 17, 21, 22]

TILE_COMBINE_FARM = [5, 6, 7, 11, 13, 14, 15, 17, 18, 19, 20, 21, 22]