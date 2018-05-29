import time
import sys
from helperFiles.classes.MainWindow import *
from helperFiles.classes.BlackBox import *

'''
Creator: James Stauder
Creation Date: 1/30/18
Last edit Date: 2/02/18
Purpose: TODO AFTER CLEANUP
'''


'''
Main function
Arguments list:
--help -prints out menu and exits
Purpose:
Return types, values:
Dependencies:
Creator: James Stauder
Date created: 1/31/18
Last edited: 2/02/18
'''


def main(argv):

    if len(argv) > 1:
        if "--help" in argv:
            printMainMenu()
            sys.exit()
        for _ in argv:
            print('hello')
    else:
        app = QApplication(sys.argv)
        mw = MainWindow()
        mw.show()
        datasetDict = createInitialDataSets()

        datasetDict['velocity'].imageItem.mouseClickEvent = mw.mouseClick
        datasetDict['velocity'].imageItem.hoverEvent = mw.mouseMove
        mw.datasetDict = datasetDict
        mw.createIntegrator()

        mw.addToImageItemContainer(datasetDict)

        sys.exit(app.exec_())

'''
Function: printMainMenu:
Argument list: None
Purpose: Print the main menu
Return types, values: None
Dependencies: None
Creator: James Stauder
Date created: 1/31/18
Last edited: 1/31/18
'''


def printMainMenu():
    print("Greenland Ice Sheet modeling tool")
    print("usage: greenland.py [-h]")
    print("optional arguments:")
    print("     --help  show help message and exit")


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


def createInitialDataSets():
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

if __name__ == '__main__':
    main(sys.argv)
