from Carcassonne_Game.GameFeatures import City

def cityConnectionIndex(self, Surroundings, CitySide):
    MatchingCityIndex = Surroundings[CitySide].TileCitiesIndex[self.MatchingSide[CitySide]]  # index of connected city
    
    while self.BoardCities[MatchingCityIndex].Pointer != self.BoardCities[MatchingCityIndex].ID:  # update city IDs     
        MatchingCityIndex = self.BoardCities[MatchingCityIndex].Pointer
    return MatchingCityIndex

def cityConnections(self, PlayingTile, Surroundings, ClosingCities, MeepleUpdate, MeepleKey, Move):
    # for each side of the tile with disconnected cities, eg. tile with opposite cites and farm in-between (Tile11)
    for i in range(len(PlayingTile.CityOpenings)):
        CityOpenings = PlayingTile.CityOpenings[i]
        AddedMeeples = self.AddMeeple(MeepleUpdate, MeepleKey, "C", i)
        OpeningsQuantity = len(CityOpenings)
        if OpeningsQuantity == 1:
            ClosingCities = cityOneOpening(self, PlayingTile, ClosingCities, CityOpenings, Surroundings, AddedMeeples, Move)
        else:
            ClosingCities = cityMultipleOpenings(self,PlayingTile, ClosingCities, CityOpenings, OpeningsQuantity, Surroundings, AddedMeeples, Move)
        
    return ClosingCities

def removeCity(self, cityIndex):
    """ Remove the city from BoardCities and handle re-indexing if necessary. """
    if cityIndex in self.BoardCities:
        del self.BoardCities[cityIndex] 

def cityOneOpening(self, PlayingTile, ClosingCities, CityOpenings, Surroundings, AddedMeeples, Move):
    
    CitySide = CityOpenings[0]  # 0,1,2 or 3

    # treated as new city
    if Surroundings[CitySide] is None:
        NextCityIndex = len(self.BoardCities)  # index is incremented
        self.BoardCities[NextCityIndex] = City(NextCityIndex,1,1,AddedMeeples, Move)  # add new city to board
        self.BoardCities[NextCityIndex].Update(1,1,AddedMeeples, Move)
        PlayingTile.TileCitiesIndex[CitySide] = NextCityIndex  # update tile city index (TCI = [Index1, Index2, Index3, Index4])

        print(f"New City part {self.BoardCities[NextCityIndex].Openings}")
        # check if city is closed
        if self.BoardCities[NextCityIndex].Openings == 0:
            ClosingCities.append(NextCityIndex)  # update list of closing cities
                
    # connected to pre-existing city    
    else:
        MatchingCityIndex = cityConnectionIndex(self, Surroundings, CitySide)
        MatchingCity = self.BoardCities[MatchingCityIndex]
        
        # number of city openings decreases by 1
        # all tiles with one city opening have a value of 1
        # update Meeples
        MatchingCity.Update(-1,1,AddedMeeples, Move)
        
        print(f"Pre Existing City part {MatchingCity.Openings}")
        # check if city is closed
        if MatchingCity.Openings == 0:
            ClosingCities.append(MatchingCityIndex)  # update list of closing cities
        
        # added for farms
        PlayingTile.TileCitiesIndex[CitySide] = MatchingCityIndex #Added for farms

    return ClosingCities


def cityMultipleOpenings(self,PlayingTile, ClosingCities, CityOpenings, OpeningsQuantity, Surroundings, AddedMeeples, Move):
    ConnectedCities = []
            
    # iterate for all sides with city opening
    for CitySide in CityOpenings:
        
        #if PlayingTile.Rotation % 180 == 90:  # 90 or 270 degress
        #    CitySide = (CitySide+2) % 4

        if Surroundings[CitySide] is not None:
            # city opening is connected to city
            MatchingCityIndex = cityConnectionIndex(self, Surroundings, CitySide)
            ConnectedCities.append([MatchingCityIndex,CitySide])
            
            
    # if none of the city openings connect to a pre-existing city
    if ConnectedCities == []:
        # create a new city
        NextCityIndex = len(self.BoardCities)
        self.BoardCities[NextCityIndex] = City(NextCityIndex,PlayingTile.CityValues,OpeningsQuantity,AddedMeeples, Move)
        self.BoardCities[NextCityIndex].Update(PlayingTile.CityValues,OpeningsQuantity,AddedMeeples, Move)
        for CitySide in CityOpenings:
            PlayingTile.TileCitiesIndex[CitySide] = NextCityIndex
            
    # if one of the openings connects to a city
    else:
        # keep track of entire city openings
        OpeningsToAdd = OpeningsQuantity - len(ConnectedCities)
        CombinedCityIndex = ConnectedCities[0][0]
                
        AlreadyMatched = False
        for MatchingCityIndex,CitySide in ConnectedCities:                            
            # openings part of the same city
            if CombinedCityIndex == MatchingCityIndex:
                if AlreadyMatched:
                    self.BoardCities[CombinedCityIndex].Update(-1,0,[0,0], Move) 
                else:
                    self.BoardCities[CombinedCityIndex].Update(OpeningsToAdd-1,PlayingTile.CityValues,AddedMeeples,Move)
                    AlreadyMatched = True
                    
            # openings part of different cities
            else:
                MatchingCity = self.BoardCities[MatchingCityIndex]
                MatchingCity.Pointer = CombinedCityIndex
                self.BoardCities[CombinedCityIndex].Update(MatchingCity.Openings-1,MatchingCity.Value,MatchingCity.Meeples,MatchingCity.tileList)
                MatchingCity.Openings = 0
                MatchingCity.Value = 0
                MatchingCity.Meeples = [0,0]
                MatchingCity.tileList = []
                        
        # update Tile City Index
        for CitySide in CityOpenings:
            PlayingTile.TileCitiesIndex[CitySide] = CombinedCityIndex
        # update list of closing cities
        print(f"Combined {self.BoardCities[CombinedCityIndex].Openings}")
        if self.BoardCities[CombinedCityIndex].Openings == 0:
            ClosingCities.append(CombinedCityIndex)

    return ClosingCities


def cityClosures(self, ClosingCities):
    # deals with closed cities created from placing latest tile
    #City closure
    for ClosingCityIndex in ClosingCities:
        ClosingCity = self.BoardCities[ClosingCityIndex]
        ClosingCity.ClosedFlag = True
        print(f"Before removal {self.BoardCities}")
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
        
        removeCity(ClosingCityIndex)
        print(f"After removal {self.BoardCities}")