from MillionSongsApi import Api
import os
import pickle5 as pickle
import pandas
import sys

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def isCompleteListing(song):
    #Return true if all fields are non-Null
    if song['year'] == 0:
        return False
    for elem in song:
        if elem == None:
            return False
    return True


if __name__ == "__main__":
    #Using OS go to the approprpriate directory
    parentDirectory = os.path.dirname(os.getcwd())
    MillionSongDataDirectory = "{}\\MillionSongData".format(parentDirectory)
    #Load the set of all track id
    with open("{}\\allTrackID.pickle".format(MillionSongDataDirectory), "rb") as f:
        trackIDSet = pickle.load(f)
    #Load the trackIDGenrePairs
    with open("{}\\trackIDGenrePairs.pickle".format(MillionSongDataDirectory), "rb") as f:
        trackIDGenrePairs = pickle.load(f)
    #Start the millionsongDataAPI
    print("Done unpickling variables", end="\n")
    blockPrint() #To stop printing outputs
    databaseAPI = Api()
    #Create a pandas dataframe
    savedData = pandas.DataFrame(data=None)
    i = 0 #71500# 715627 might find an error somewhere in this range
    stepSize = 10000 #The amount of info passes from SQL into the code over each sweep of the database
    tracksFound = 0
    hasEnded = False
    totalSongs = 5000
    pickleFile = "allData5000.pickle"
    csvFile = "compiledGenreData_AllAttributes_5000Songs.csv"
    #Loop through all tracks in database until reached a limit of 5000
    # while i < 900:
    while (tracksFound < totalSongs) and (not hasEnded):
        try:
            #Pickle while we're here in case I exit code
            with open(pickleFile, "wb") as f:
                pickle.dump(savedData, f)
            
            currentSongs = databaseAPI.getTracks(stepSize, offset=i)
            #Select the elements from the list of currentSongs
            for j in range(stepSize):
                enablePrint()
                print("On song #{}, found genre of {} songs".format(i+j, tracksFound), end="\r")
                blockPrint()
                currentSong = currentSongs[j]
                if (not currentSong) or (tracksFound > totalSongs):
                    #if currentSong is empty, then it's the end of the database
                    hasEnded = True
                    break #This means that the list is empty
                #There's a space on the front and back of the track_id
                currentSong['track_id'] = currentSong['track_id'].replace(" ","")
                #Checking if trackID is in the set
                currentTrackID = currentSong['track_id']
                if (currentTrackID in trackIDSet) and isCompleteListing(currentSong):
                    tracksFound += 1
                    #For the current song, append the genre information
                    currentGenre = trackIDGenrePairs[currentTrackID]
                    #Add the data to the dataframe
                    currentSong['genre'] = currentGenre
                    savedData = savedData.append(currentSong,ignore_index=True)
        except Exception as e:
            #Print the error
            print("Error: {}, on i = {}".format(e, i))
        finally:
            i += stepSize
    #Pickle the data
    with open(pickleFile, "wb") as f:
        pickle.dump(savedData, f)
    #Save the dataframe as a csv
    savedData.to_csv(csvFile)

            
