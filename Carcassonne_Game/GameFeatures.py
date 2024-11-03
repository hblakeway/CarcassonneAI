"""
Create objects for each of the features in the game:
    - Monastery
    - Cities
    - Farms
    - Roads
"""
class Monastery:
    def __init__(self, ID = None, Owner = None, playTile=None):
        self.tileList = []

        if ID is not None:
            self.ID = ID
            self.Owner = Owner
            self.Value = 1
            self.playTile = playTile
        
        if playTile is not None:
                self.tileList.append(playTile)
    
    def CloneMonastery(self):
        Clone = Monastery()
        Clone.ID = self.ID
        Clone.Owner = self.Owner # 0 for Player 1, 1 for Player 2 
        Clone.Value = self.Value
        Clone.playTile = self.playTile
        Clone.tileList = [tile for tile in self.tileList] 
        return Clone
    
    def Update(self, playTile=None):
        if playTile is not None:
                self.tileList.append(playTile)
    
    def __repr__(self):
        #String = {"ID": self.ID, "Value": self.Value, "Owner": self.Owner, "Tiles": self.tileList}
        String = "\n"+"Monastery ID:"+str(self.ID)+"\n"+"Value:"+str(self.Value)+"\n"+"Owner:"+str(self.Owner)+"\n"+" Tiles:"+str(self.tileList)+"\n"
        return String 

        
    
class City:
    def __init__(self,ID = None, Value=None, Openings=None, Meeples=[0,0], playTile=None):
        self.tileList = []

        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.Openings = Openings
            self.Value = Value
            self.Meeples = Meeples
            self.ClosedFlag = False
            self.playTile = playTile
        
        if playTile is not None:
                self.tileList.append(playTile)
            
        
    def CloneCity(self):
        Clone = City()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.Openings = self.Openings
        Clone.Value = self.Value
        Clone.Meeples = [x for x in self.Meeples]
        Clone.ClosedFlag = self.ClosedFlag
        Clone.playTile = self.playTile
        Clone.tileList = [tile for tile in self.tileList] 
        return Clone
        
    def Update(self, OpeningsChange = 0, ValueAdded = 0, MeeplesAdded = [0,0], playTile=None):

        self.Openings += OpeningsChange
        self.Value += ValueAdded
        self.Meeples[1] += MeeplesAdded[1] # MCST 
        self.Meeples[0] += MeeplesAdded[0] # Player 1
        
        self.tileList.append(playTile)
    
        
    def __repr__(self):
        #String = "City ID"+str(self.ID)+"Pointer"+str(self.Pointer)+"Value"+str(self.Value)+"Openings"+str(self.Openings)+"Meeples" + str(self.Meeples[0])+","+ str(self.Meeples[1])+"Closed?"+str(self.ClosedFlag)+"Tiles"+str(self.tileList)
        # String = {"ID": self.ID, "Meeples": (self.Meeples[0], self.Meeples[1]), "Tiles": self.tileList}
        String = "\n"+"City ID:"+str(self.ID)+"\n"+"Meeples:" + str(self.Meeples[0])+","+ str(self.Meeples[1])+"\n"+"Tiles:"+str(self.tileList)+"\n"
        return String
      

class Farm:
    def __init__(self,ID = None, Meeples=[0,0], playTile=None):
        self.tileList = []

        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.CityIndexes = set()
            self.Meeples = Meeples
            self.playTile = playTile
        
        if playTile is not None:
                self.tileList.append(playTile)
    
    def CloneFarm(self):
        Clone = Farm()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.CityIndexes = set([x for x in self.CityIndexes])
        Clone.Meeples = [x for x in self.Meeples]
        Clone.playTile = self.playTile
        Clone.tileList = [tile for tile in self.tileList] 
        return Clone
    
    def Update(self, NewCityIndexes = [], MeeplesAdded = [0,0], playTile=None):
        for CityIndex in NewCityIndexes:
            self.CityIndexes.add(CityIndex)
        self.Meeples[1] += MeeplesAdded[1]
        self.Meeples[0] += MeeplesAdded[0]

        #if not isinstance(playTile, tuple):
        #    playTile = tuple(playTile)  # Convert to tuple if it's not already

        if playTile is not None:
                self.tileList.append(playTile)
        

        
    def __repr__(self):
        #String = "Farm ID"+str(self.ID)+"Ptr"+str(self.Pointer)+"CI"+str(self.CityIndexes)+"Mps" + str(self.Meeples[0])+","+ str(self.Meeples[1])
        #seen = set()
        #cleaned_tileList = tuple(x for x in self.tileList if not (x in seen or seen.add(x)))
        String = "\n"+"Farm ID:"+str(self.ID)+"\n"+"Meeples:"+str(self.Meeples[0])+","+ str(self.Meeples[1])+"\n"+"Tiles:"+str(self.tileList)+"\n"
        return String
    

    
class Road:
    def __init__(self,ID = None, Value=None, Openings=None, Meeples=[0,0], playTile=None):
        self.tileList = []

        if ID is not None:
            self.ID = ID
            self.Pointer = ID
            self.Openings = Openings
            self.Value = Value
            self.Meeples = Meeples
            self.playTile = playTile
            self.ClosedFlag = False
        
        if playTile is not None:
                self.tileList.append(playTile)
    
    def CloneRoad(self):
        Clone = Road()
        Clone.ID = self.ID
        Clone.Pointer = self.Pointer
        Clone.Openings = self.Openings
        Clone.Value = self.Value
        Clone.ClosedFlag = self.ClosedFlag
        Clone.Meeples = [x for x in self.Meeples]
        Clone.playTile = self.playTile
        Clone.tileList = [tile for tile in self.tileList] 
        return Clone
    
    def Update(self, OpeningsChange = 0, ValueAdded = 0, MeeplesAdded = [0,0], playTile=None):
        self.Openings += OpeningsChange
        self.Value += ValueAdded
        self.Meeples[1] += MeeplesAdded[1]
        self.Meeples[0] += MeeplesAdded[0]
        self.tileList.append(playTile)
        
    def __repr__(self):
        #String = "Road ID"+str(self.ID)+"Ptr"+str(self.Pointer)+"V"+str(self.Value)+"Ops"+str(self.Openings)+"Mps" + str(self.Meeples[0])+","+ str(self.Meeples[1])
        #print(f"Openings = {self.ID, self.Openings, self.ClosedFlag}")
        String = "\n"+"Road ID:"+str(self.ID)+"\n"+"Meeples:"+str(self.Meeples[0])+","+ str(self.Meeples[1])+"\n"+"Tiles:"+str(self.tileList)+"\n"
        return String