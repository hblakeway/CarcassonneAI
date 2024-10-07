from Carcassonne_Game.GameFeatures import City

def cityConnections(self, PlayingTile, Surroundings, ClosingCities, MeepleUpdate, MeepleKey, Move):
    for i in range(len(PlayingTile.CityOpenings)):
        CityOpenings = PlayingTile.CityOpenings[i]
        AddedMeeples = self.AddMeeple(MeepleUpdate, MeepleKey, "C", i)
        OpeningsQuantity = len(CityOpenings)

        if OpeningsQuantity == 1:
            ClosingCities = cityOneOpening(self, PlayingTile, ClosingCities, CityOpenings, Surroundings, AddedMeeples, Move)
        else:
            ClosingCities = cityMultipleOpenings(self,PlayingTile, ClosingCities, CityOpenings, OpeningsQuantity, Surroundings, AddedMeeples, Move)
        
    return ClosingCities

def cityConnectionIndex(self, Surroundings, CitySide):
    MatchingCityIndex = Surroundings[CitySide].TileCitiesIndex[self.MatchingSide[CitySide]]  # index of connected city
    
    while self.BoardCities[MatchingCityIndex].Pointer != self.BoardCities[MatchingCityIndex].ID:  # update city IDs     
        MatchingCityIndex = self.BoardCities[MatchingCityIndex].Pointer
    return MatchingCityIndex

def cityOneOpening(self, PlayingTile, ClosingCities, CityOpenings, Surroundings, AddedMeeples, Move):
    
    CitySide = CityOpenings[0]  # 0,1,2 or 3

    # treated as new city
    if Surroundings[CitySide] is None:
        NextCityIndex = len(self.BoardCities)  # index is incremented
        self.BoardCities[NextCityIndex] = City(NextCityIndex,1,1,AddedMeeples, Move)  # add new city to board
        PlayingTile.TileCitiesIndex[CitySide] = NextCityIndex  # update tile city index (TCI = [Index1, Index2, Index3, Index4])
                
    # connected to pre-existing city    
    else:
        MatchingCityIndex = cityConnectionIndex(self, Surroundings, CitySide)
        MatchingCity = self.BoardCities[MatchingCityIndex]
        
        # number of city openings decreases by 1
        # all tiles with one city opening have a value of 1
        # update Meeples
        MatchingCity.Update(-1,1,AddedMeeples, Move)
        
        if MatchingCity.Openings == 0:
            ClosingCities.append(MatchingCityIndex)  # update list of closing cities
        
        # added for farms
        PlayingTile.TileCitiesIndex[CitySide] = MatchingCityIndex #Added for farms

    return ClosingCities


def cityMultipleOpenings(self,PlayingTile, ClosingCities, CityOpenings, OpeningsQuantity, Surroundings, AddedMeeples, Move):
    ConnectedCities = []
            
    # iterate for all sides with city opening
    for CitySide in CityOpenings:
        if Surroundings[CitySide] is not None:
            # city opening is connected to city
            MatchingCityIndex = cityConnectionIndex(self, Surroundings, CitySide)
            ConnectedCities.append([MatchingCityIndex,CitySide])
            
            
    # if none of the city openings connect to a pre-existing city
    if ConnectedCities == []:
        # create a new city
        NextCityIndex = len(self.BoardCities)
        self.BoardCities[NextCityIndex] = City(NextCityIndex,PlayingTile.CityValues,OpeningsQuantity,AddedMeeples, Move)
       
        for CitySide in CityOpenings:
            PlayingTile.TileCitiesIndex[CitySide] = NextCityIndex
            
    else: # if one of the openings connects to a city
        
        # keep track of entire city openings
        OpeningsToAdd = OpeningsQuantity - len(ConnectedCities)
        CombinedCityIndex = ConnectedCities[0][0] # Starting with first connected city 
        AlreadyMatched = False

        for MatchingCityIndex, CitySide in ConnectedCities: # Iterate through Connected Cities  

            # City is part of existing City                       
            if CombinedCityIndex == MatchingCityIndex:
                if AlreadyMatched:
                    self.BoardCities[CombinedCityIndex].Update(-1,0,[0,0], Move) 
                else:
                    self.BoardCities[CombinedCityIndex].Update(OpeningsToAdd-1,PlayingTile.CityValues,AddedMeeples, Move)
                    AlreadyMatched = True
            
            # Merging a city 
            else:
                MatchingCity = self.BoardCities[MatchingCityIndex]
                MatchingCity.Pointer = CombinedCityIndex
                self.BoardCities[CombinedCityIndex].Update(MatchingCity.Openings-1,MatchingCity.Value,MatchingCity.Meeples,MatchingCity.tileList)
                # self.BoardCities[CombinedCityIndex].Update(0, 0, [0,0], Move)
 
                # Sets the value as 0 because it is merged 
                MatchingCity.Openings = 0
                MatchingCity.Value = 0
                MatchingCity.Meeples = [0,0]
                MatchingCity.tileList = []
                        
        
        # Updates the tile index for merged city 
        for CitySide in CityOpenings:
            PlayingTile.TileCitiesIndex[CitySide] = CombinedCityIndex
        
        # Mark city as closed 
        if self.BoardCities[CombinedCityIndex].Openings == 0:
            ClosingCities.append(CombinedCityIndex)

    return ClosingCities


def cityClosures(self, ClosingCities):
    # deals with closed cities created from placing latest tile
    #City closure
    for ClosingCityIndex in ClosingCities:
        ClosingCity = self.BoardCities[ClosingCityIndex]
        ClosingCity.ClosedFlag = True
        if ClosingCity.Meeples[0] == 0 and ClosingCity.Meeples[1] == 0:
            pass
        elif ClosingCity.Meeples[0] > ClosingCity.Meeples[1]:
            self.Scores[0] += 2*ClosingCity.Value
            self.FeatureScores[0][0] += 2*ClosingCity.Value
            #print(f'POINTS ADDED - Completed City \nPlayer 1 - Points: +{2*ClosingCity.Value} \n')
        elif ClosingCity.Meeples[0] < ClosingCity.Meeples[1]:
            self.Scores[1] += 2*ClosingCity.Value
            self.FeatureScores[1][0] += 2*ClosingCity.Value
            #print(f'POINTS ADDED - Completed City \nPlayer 2 - Points: +{2*ClosingCity.Value} \n')
        else:
            self.Scores[0] += 2*ClosingCity.Value
            self.FeatureScores[0][0] += 2*ClosingCity.Value
            self.Scores[1] += 2*ClosingCity.Value
            self.FeatureScores[1][0] += 2*ClosingCity.Value
            #print(f'POINTS ADDED - Completed City \nPoints Shared - Points: +{2*ClosingCity.Value} \n')
        ClosingCity.Value = 0
        self.Meeples[0] += ClosingCity.Meeples[0]
        self.Meeples[1] += ClosingCity.Meeples[1]
        
  
   