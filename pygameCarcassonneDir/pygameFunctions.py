# file imports
from Carcassonne_Game.Tile import Tile, ROTATION_DICT, SIDE_CHANGE_DICT, AvailableMove
from pygameCarcassonneDir.pygameSettings import GRID, GRID_SIZE, GRID_WINDOW_HEIGHT, GRID_WINDOW_WIDTH, MEEPLE_SIZE, BLACK, WHITE, LIGHTGREEN, BROWN
from pygameCarcassonneDir.pygameSettings import FONT_MEEPLE_IMAGE, FONT_MEEPLE_MENU, RED, BLUE, DARK_GREEN
from pygameCarcassonneDir.pygameLabel import Label

# packages
import pygame
import math

X_DEPTH = 10
Y_DEPTH = 20
WIDTH = HEIGHT = 104  # image scaled x2

XSHIFT = YSHIFT = MEEPLE_SIZE//2

"""
MEEPLE_LOCATION_DICT = {
    (0,1): [X_DEPTH, HEIGHT//2 - YSHIFT],
    (0,2): [WIDTH//4, HEIGHT - Y_DEPTH],
    (1,1): [WIDTH//2 - XSHIFT, Y_DEPTH - YSHIFT],
    (1,2): [WIDTH//4, Y_DEPTH],
    (2,1): [WIDTH - X_DEPTH - XSHIFT, HEIGHT//2 - YSHIFT],
    (2,2): [3*(WIDTH//4), Y_DEPTH],
    (3,0): [WIDTH//4 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (3,1): [WIDTH//2 - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (3,2): [3*(WIDTH//4) - XSHIFT, HEIGHT - Y_DEPTH - YSHIFT],
    (0,4): [WIDTH//2, HEIGHT//2]
    }
"""

# reverse ?
MEEPLE_LOCATION_DICT = {
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

# pygame functions

class Counter:
    def __init__(self, initial_count=0):
        self.count = initial_count

    def add(self, value = 1):
        self.count += value

    def get(self):
        return self.count

class playerStrategy:
    """
        PlayingTileIndex = Move[0]
        X,Y = Move[1], Move[2]
        Rotation = Move[3]
        MeepleKey = Move[4]
    """
    def __init__(self, player_strategy=None, features=None):
        demo = False 

        if demo:
            player_strategy = [(6, 0, 1, 180, ('C', 0)), (2, 2, 1, 180, ('C', 0)), (20, 0, -1, 0, ('Monastery', 0)), (21, 1, 0, 0, ('R', 0)),
                               (1, 3, 2, 270, ('G', 0)), (16, 1, -1, 90, ('C', 0)), (1, 2, -1, 180, None), (21, 1, -2, 180, ('G', 1)),
                               (14, 2, -2, 0, None), (10, 3, -1, 0, None), (21, -2, 0, 180, None), (22, -3, 1, 0, ('R', 0)), (5, 4, -1, 270, None),
                               (3, -4, 1, 270, None), (19, 2, 4, 0, ('R', 2)), (21, 3, 0, 180, None), (13, 0, -2, 180, ('C', 0)), (23, 5, 4, 0, None),
                               (18, 4, 1, 90, None), (0, 0, -3, 0, None), (19, -1, -2, 90, None), (22, 2, -3, 90, None), (22, 2, -4, 90, None), 
                               (8, 0, -4, 0, None), (7, 1, -3, 180, None), (17, -4, 0, 0, None), (13, -4, 4, 180, ('C', 0)), (9, 3, 4, 90, None),
                               (7, 1, -4, 270, None), (20, 1, 3, 0, ('Monastery', 0))]
            
            if features is None:
                features = []

            self.playerStrategy = player_strategy
            self.playerFeatures = features
        
        else:
            if player_strategy is None:
                player_strategy = []
            
            if features is None:
                features = []

            self.playerStrategy = player_strategy
            self.playerFeatures = features
        
        print(f"Init Player Strat = {player_strategy}")

    def add(self, move=None):
        if move is None:
            move = []
        self.playerStrategy.append(move)

        self.playingTileIndex = move[0]
        self.coordinateX = move[1]
        self.coordinateY = move[2]
        self.rotation = move[3]
        self.meepleKey = move[4]

    def get(self):
        return self.playerStrategy

    def get_playing_tile_index(self):
        return self.playingTileIndex
    
    def get_coordx(self):
        return self.coordinateX
    
    def get_coordy(self):
        return self.coordinateY
    
    def get_rotation(self):
        return self.rotation
    
    def get_meeple_key(self):
        return self.meepleKey


class opponentStrategy:
    def __init__(self, opponent_strategy=None):
        if opponent_strategy is None:
            opponent_strategy = []
        self.opponentStrategy = opponent_strategy

    def add(self, move=None):
        if move is None:
            move = []
        self.opponentStrategy.append(move)
        
        self.playingTileIndex = move[0]
        self.coordinateX = move[1]
        self.coordinateY = move[2]
        self.rotation = move[3]
        self.meepleKey = move[4]

    def get(self):
        return self.playerStrategy

    def get_playing_tile_index(self):
        return self.playingTileIndex
    
    def get_coordx(self):
        return self.coordinateX
    
    def get_coordy(self):
        return self.coordinateY
    
    def get_rotation(self):
        return self.rotation
    
    def get_meeple_key(self):
        return self.meepleKey

    
def get_clicked_X(mouse_pos, displayScreen):
    Grid = displayScreen.Grid
    Grid_Size = displayScreen.Grid_Size
    Grid_border = displayScreen.Grid_border
    # column coordinate
    x = mouse_pos[0]
    max_X = math.floor(Grid[0]/2)
    min_X = -max_X#+displayScreen.Grid_border
    
    for i in range(min_X, max_X+2):
        if Grid_border < x < ((i-min_X)*Grid_Size) + Grid_border:
            return i-1
    return 1000
    

def get_clicked_Y(mouse_pos, displayScreen):
    Grid = displayScreen.Grid
    Grid_Size = displayScreen.Grid_Size
    Grid_border = displayScreen.Grid_border
    # row coordinate
    y = mouse_pos[1]
    max_Y = math.floor(Grid[1]/2) #+ displayScreen.Grid_border
    min_Y = -max_Y #+ displayScreen.Grid_border
    
    for i in range(min_Y, max_Y+2):
        if Grid_border < y < ((i-min_Y) * Grid_Size) + Grid_border:
            return -(i-1)
    return 1000

    
def drawGrid(DisplayScreen):
    # display constants
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_border = DisplayScreen.Grid_border
    Grid_Size = DisplayScreen.Grid_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay
    
    # add game mat
    gameMat = pygame.image.load('pygame_images/game_mat.jpg')
    gameMat = pygame.transform.scale(gameMat, (Grid_Window_Width, Grid_Window_Height))
    GAME_DISPLAY.blit(gameMat, (Grid_border, Grid_border))
    
    # for loop for each grid sqaure
    for x in range(0, Grid_Window_Width, Grid_Size):
        for y in range(0, Grid_Window_Height, Grid_Size):
            rect = pygame.Rect(x+Grid_border, y+Grid_border, Grid_Size, Grid_Size)
            pygame.draw.rect(GAME_DISPLAY, WHITE, rect, 1)
    
   

def placeColourTile(x, y, DisplayScreen, COLOUR):
    # display constants
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_border = DisplayScreen.Grid_border
    Grid_Size = DisplayScreen.Grid_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay
    
    # reverse orientation
    y = y*-1
    
    X = Grid_Size * math.floor(Grid_Window_Width/(Grid_Size*2)) + x*Grid_Size + Grid_border
    Y = Grid_Size * math.floor(Grid_Window_Height/(Grid_Size*2)) + y*Grid_Size + Grid_border
    
    # draw rectangle
    rect = (X,Y, Grid_Size, Grid_Size)
    rect_surf = pygame.Surface(pygame.Rect(rect).size)
    rect_surf.set_alpha(150)
    pygame.draw.rect(rect_surf, COLOUR, rect_surf.get_rect())
    GAME_DISPLAY.blit(rect_surf, rect)
    

def placeTile(Tile, Rotation, x, y, DisplayScreen):
    # display constants
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_Size = DisplayScreen.Grid_Size
    Grid_border = DisplayScreen.Grid_border
    Meeple_Size = DisplayScreen.Meeple_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay
    
    TileIndex = Tile.TileIndex
    # reverse orientation
    y=y*-1
    
    GAME_X = Grid_Size * math.floor(Grid_Window_Width/(Grid_Size*2)) + x*Grid_Size + Grid_border
    GAME_Y = Grid_Size * math.floor(Grid_Window_Height/(Grid_Size*2)) + y*Grid_Size + Grid_border
    
    # load image
    image = pygame.image.load('images/' + str(TileIndex) + '.png')
    
    # load meeple
    TileMeeple = Tile.Meeple
    if not(TileMeeple is None):
        #print(TileMeeple)
        Feature, Location = TileMeeple[0], TileMeeple[1]
        playerSymbol = TileMeeple[2]
        # meeple image
        meepleColour = "blue" if playerSymbol == 1 else "red"
        meepleImage = pygame.image.load('meeple_images/' + meepleColour + '.png')
        meepleImage = pygame.transform.scale(meepleImage, (Meeple_Size, Meeple_Size))
        X,Y = meepleCoordinates(Location, Feature, MEEPLE_LOCATION_DICT, TileIndex)
        image.blit(meepleImage, (X,Y))
    # add image        
    image = pygame.transform.scale(image, (Grid_Size,Grid_Size))
    image = pygame.transform.rotate(image, Rotation)
    GAME_DISPLAY.blit(image, (GAME_X, GAME_Y))


def meepleCoordinates(Location, Feature, DICT, TileIndex):
    """
    Get meeple coordinates from Meeple Tile Location
    """
    coords = DICT[Location]
    
    # exceptions 
    if TileIndex in [8,9]:
        if Location == (0,2):
            coords = DICT[(3,0)]
            
    elif TileIndex == 14:
        if Location == (2,1):
            coords = DICT[(3,0)]
            
    elif TileIndex == 16:
        if Location == (0,2):
            coords = DICT[0]
            
    elif TileIndex == 17:
        if Location == (2,2):
            coords = DICT[(3,0)]
            
    elif TileIndex in [18,19]:
        if Location == (0,2):
            coords = DICT[(2,2)]
        if Location == (2,2):
            coords = DICT[(3,0)]
            
    elif TileIndex == 22:
        if Location == (0,1):
            coords = DICT[(0,4)]
        if Location == (0,2):
            coords = DICT[(1,1)]
            
    elif TileIndex == 23:
        if Location == (0,2):
            coords = DICT[(1,2)]
        if Location == (1,2):
            coords = DICT[(2,2)]
        if Location == (2,2):
            coords = DICT[(3,0)]
        
    X,Y = coords[0],coords[1]
    return X,Y


def diplayGameBoard(Carcassonne, displayScreen):
    """
    Display all current tiles on the game board        
    """    
    tiles = Carcassonne.Board  # stored in a dictionary
    tile_coorindates = list(tiles.keys())
    
    for X,Y in tile_coorindates:
        tile = tiles[X,Y]
        # reverse rotation
        rotation = 360-tile.Rotation
        # place tile on board
        placeTile(tile, rotation, X, Y, displayScreen)


def playMove(NextTile, player, Carcassonne, TileIndex, isStartOfGame = False, ManualMove=None):
    
    # check if there is a possible move
    if len(Carcassonne.availableMoves()) == 0:
        print("No Moves Available - Tile Discarded From Game")
        Carcassonne.move([None, TileIndex])
        return player  # turn not over
    
    # get move
    if player.isAIPlayer:
        selectedMove = player.chooseAction(Carcassonne)
    else:
        selectedMove = ManualMove
    
    # play move on board
    #print(f'(pygame) Selected Move: {selectedMove}')
    #print(f'(pygame) Selected Move[0]: {selectedMove[0]}')
    meepleLoc = Carcassonne.move(selectedMove)
    # switch player
    if player == Carcassonne.p1:
        return Carcassonne.p2, selectedMove, meepleLoc
    
    return Carcassonne.p1, selectedMove, meepleLoc

def printTilesLeft(Carcassonne, displayScreen):
    # attributes
    Grid_Window_Width = displayScreen.Total_Grid_Width
    Menu_Width = displayScreen.Menu_Width
    GAME_DISPLAY = displayScreen.pygameDisplay
    
    # rectangular surface
    rect = (0,0, 300, 40)
    label = pygame.Surface(pygame.Rect(rect).size)
    label.set_alpha(165)
    pygame.draw.rect(label, BROWN, label.get_rect(), 10)
    width = (label.get_rect().size)[0]
    height = (label.get_rect().size)[1]
    
    # number of tiles left
    tilesLeft = Carcassonne.TotalTiles
    text = "Tiles Left: " + str(tilesLeft)
    tilesLeftLabel = Label(text, font_size = 25, background = None, foreground = WHITE)
    text_width = (tilesLeftLabel.text_surface.get_rect().size)[0]
    text_height = (tilesLeftLabel.text_surface.get_rect().size)[1]
    # attach to rectangle
    label.blit(tilesLeftLabel.text_surface, ((width - text_width)/2, (height - text_height)/2))
    # attach rectangle to screen
    GAME_DISPLAY.blit(label, (Grid_Window_Width + (Menu_Width - width)/2, 250))
    
    
def printScores(Carcassonne, displayScreen):
    # attributes
    Grid_Window_Width = displayScreen.Total_Grid_Width
    Grid_Window_Height = displayScreen.Total_Grid_Height
    Menu_Width = displayScreen.Menu_Width
    GAME_DISPLAY = displayScreen.pygameDisplay
    
    color1 = color2 = WHITE
    
    # highlight current player
    if Carcassonne.playerSymbol == 1:
        color1 = DARK_GREEN
    else:
        color2 = DARK_GREEN
        
    # latest scores
    scores = Carcassonne.Scores
    p1_score = scores[0]
    p2_score = scores[1]
    
    # names 
    name_p1 = Carcassonne.p1.name
    name_p2 = Carcassonne.p2.name
    
    # meeple count
    meeples = Carcassonne.Meeples
    p1_meeples = meeples[0]
    p2_meeples = meeples[1]
    
    # score labels
    p1_Label = Label("Player 1:", font_size = 30, background = None, foreground = color1)
    p2_Label = Label("Player 2:", font_size = 30, background = None, foreground = color2)
    
    p1_Name_Label = Label(" Name: " + name_p1, font_size = 25, background = None, foreground = WHITE)
    p2_Name_Label = Label(" Name: " + name_p2, font_size = 25, background = None, foreground = WHITE)
    
    p1_Score_Label = Label(" Score: " + str(Carcassonne.Scores[2]), font_size = 25, background = None, foreground = WHITE)
    p2_Score_Label = Label(" Score: " + str(Carcassonne.Scores[3]), font_size = 25, background = None, foreground = WHITE)
    
    p1_Meeples_Label = Label(" Meeples: " + str(p1_meeples), font_size = 25, background = None, foreground = WHITE)
    p2_Meeples_Label = Label(" Meeples: " + str(p2_meeples), font_size = 25, background = None, foreground = WHITE)
    
    label1_x = [(p1_Label.text_surface.get_rect().size)[0],  (p1_Name_Label.text_surface.get_rect().size)[0], 
               (p1_Score_Label.text_surface.get_rect().size)[0], (p1_Meeples_Label.text_surface.get_rect().size)[0]]
    label1_y = [(p1_Label.text_surface.get_rect().size)[1],  (p1_Name_Label.text_surface.get_rect().size)[1],
               (p1_Score_Label.text_surface.get_rect().size)[1], (p1_Meeples_Label.text_surface.get_rect().size)[1]]
    
    # dimension of text
    text_width1 = max(label1_x) 
    text_width2 = max(label1_x) 
    text_height = sum(label1_y) + 10*5
   
    # surfaces to add text to
    rect1 = (0,0, text_width1 + 20, text_height)
    label1 = pygame.Surface(pygame.Rect(rect1).size)
    label1.set_alpha(165)
    pygame.draw.rect(label1, BLUE, label1.get_rect(), 10)
    
    rect2 = (0,0, text_width2 + 20, text_height)
    label2 = pygame.Surface(pygame.Rect(rect2).size)
    label2.set_alpha(165)
    pygame.draw.rect(label2, RED, label2.get_rect(), 10)
    
    width = (label1.get_rect().size)[0]
    
    # attach to rectangle
    label1.blit(p1_Label.text_surface, ((width - text_width1)/2, 13))
    label1.blit(p1_Name_Label.text_surface, ((width - text_width1)/2, 40))
    label1.blit(p1_Score_Label.text_surface, ((width - text_width1)/2, 65))
    label1.blit(p1_Meeples_Label.text_surface, ((width - text_width1)/2, 90))
    
    label2.blit(p2_Label.text_surface, ((width - text_width2)/2, 13))
    label2.blit(p2_Name_Label.text_surface, ((width - text_width2)/2, 40))
    label2.blit(p2_Score_Label.text_surface, ((width - text_width2)/2, 65))
    label2.blit(p2_Meeples_Label.text_surface, ((width - text_width2)/2, 90))
    
    total_width = 2*width
    
    GAME_DISPLAY.blit(label1, (Grid_Window_Width + (Menu_Width - total_width)/2, Grid_Window_Height-125 ))
    GAME_DISPLAY.blit(label2, (Grid_Window_Width + width + (Menu_Width - total_width)/2, Grid_Window_Height-125))

def getAImove(DisplayScreen, player, Carcassonne, TileIndex):
    
    # check if there is a possible move
    if len(Carcassonne.availableMoves()) == 0:
        print("AI has no move reccomendations")
        return player  # turn not over
    
    # Return if AI
    if player == Carcassonne.p2:
        return player
   
     # get move
    player = Carcassonne.p2
    selectedMove = player.chooseAction(Carcassonne)
    player = Carcassonne.p1
  
    # play move on board
    Grid_Window_Width = DisplayScreen.Grid_Window_Width
    Grid_Window_Height = DisplayScreen.Grid_Window_Height
    Grid_Size = DisplayScreen.Grid_Size
    Grid_border = DisplayScreen.Grid_border
    Meeple_Size = DisplayScreen.Meeple_Size
    GAME_DISPLAY = DisplayScreen.pygameDisplay

    DisplayTileIndex = selectedMove[0]
    X,Y = selectedMove[1], selectedMove[2]
    Rotation = selectedMove[3]
    MeepleKey = selectedMove[4]

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

    return(selectedMove, image, image_coordinate, rect_surf, rect_coordinates)

def meepleCoordinatesAI(Location, Feature, DICT, TileIndex):
        """
        Get meeple coordinates from Meeple Tile Location
        """
        coords = DICT[Location]
        
        # exceptions 
        if TileIndex in [8,9]:
            if Location == (0,2):
                coords = DICT[(3,0)]
                
        elif TileIndex == 14:
            if Location == (2,1):
                coords = DICT[(3,0)]
                
        elif TileIndex == 16:
            if Location == (0,2):
                coords = DICT[0]
                
        elif TileIndex == 17:
            if Location == (2,2):
                coords = DICT[(3,0)]
                
        elif TileIndex in [18,19]:
            if Location == (0,2):
                coords = DICT[(2,2)]
            if Location == (2,2):
                coords = DICT[(3,0)]
                
        elif TileIndex == 22:
            if Location == (0,1):
                coords = DICT[(0,4)]
            if Location == (0,2):
                coords = DICT[(1,1)]
                
        elif TileIndex == 23:
            if Location == (0,2):
                coords = DICT[(1,2)]
            if Location == (1,2):
                coords = DICT[(2,2)]
            if Location == (2,2):
                coords = DICT[(3,0)]
            
        X,Y = coords[0],coords[1]
        return X,Y

def placeColourTileAI(x, y, DisplayScreen, COLOUR):
        # display constants
        Grid_Window_Width = DisplayScreen.Grid_Window_Width
        Grid_Window_Height = DisplayScreen.Grid_Window_Height
        Grid_border = DisplayScreen.Grid_border
        Grid_Size = DisplayScreen.Grid_Size
        GAME_DISPLAY = DisplayScreen.pygameDisplay
        
        # reverse orientation
        y = y*-1
        
        X = Grid_Size * math.floor(Grid_Window_Width/(Grid_Size*2)) + x*Grid_Size + Grid_border
        Y = Grid_Size * math.floor(Grid_Window_Height/(Grid_Size*2)) + y*Grid_Size + Grid_border
        
        # draw rectangle
        rect = (X,Y, Grid_Size, Grid_Size)
        rect_surf = pygame.Surface(pygame.Rect(rect).size)
        rect_surf.set_alpha(150)
        pygame.draw.rect(rect_surf, COLOUR, rect_surf.get_rect())
        GAME_DISPLAY.blit(rect_surf, rect)


