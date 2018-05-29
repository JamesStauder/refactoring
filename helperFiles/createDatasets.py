import time
from classes.Dataset import *

'''
Function: createInitialDataSets:
Argument list:
Purpose:
Return types, values:
Dependencies:
Creator: James Stauder
Date created: 1/31/18
Last edited: 1/31/18
'''


def createInitialDatasets():
    print "Creating data sets"
    t0 = time.time()

    datasetDict = {}

    dataFile = h5py.File(dataFileName, 'r')
    map['x1'] = len(dataFile['bed'][:][0])
    map['y1'] = len(dataFile['bed'][:])
    map['proj_x1'] = dataFile['x'][:][-1]
    map['proj_y1'] = dataFile['y'][:][-1]

    velocity = Dataset('velocity', greenPlotPen)
    datasetDict['velocity'] = velocity

    smb = Dataset('smb', redPlotPen)
    datasetDict['smb'] = smb

    bed = Dataset('bed', bluePlotPen)
    datasetDict['bed'] = bed

    surface = Dataset('surface', greyPlotPen)
    datasetDict['surface'] = surface

    thickness = Dataset('thickness', orangePlotPen)
    datasetDict['thickness'] = thickness

    t2m = Dataset('t2m', tealPlotPen)
    datasetDict['t2m'] = t2m

    dataFile.close()

    print "Loaded all data sets in ", time.time() - t0, " seconds"
    return datasetDict
