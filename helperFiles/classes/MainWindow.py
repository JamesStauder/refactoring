from PyQt4.QtGui import *
import math

from Instructions import *
from FlowIntegrator import *
from Dataset import *
from Marker import *
from ModelGUI import *
from ..caching.cachingFunctions import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Greenland")
        self.setMinimumHeight(1000)
        self.setMinimumWidth(1200)

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QtGui.QHBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

        # index of current map
        self.currentMap = 0

        # marker selected variables
        self.isMarkerSelected = False
        self.whichMarkerSelected = None
        self.selectedMarkerPosition = None
        self.whichIndexOfFlowlineSelected = None

        # Flowline information
        self.flowlineDistance = 100000
        self.lengthOfFlowline = 1
        self.flowlines = []
        self.flowlineMarkers = []
        self.integratorPerMarker = 10

        '''
        Side widget with button
        '''
        self.maxWidth = 300

        self.buttonBoxWidget = QtGui.QWidget()
        self.buttonBox = QtGui.QVBoxLayout()
        self.buttonBoxWidget.setLayout(self.buttonBox)

        self.mapList = QtGui.QComboBox()
        self.maps = ['Velocity', 'Bed', 'Surface', 'SMB', 'Thickness', 't2m']
        self.mapList.addItems(self.maps)
        self.mapList.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.mapList)

        self.spatialResolutionWidget = QtGui.QWidget()
        self.spatialResolutionLayout = QtGui.QHBoxLayout()
        self.spatialResolutionWidget.setLayout(self.spatialResolutionLayout)
        self.spatialResolutionLabel = QtGui.QLabel('Spatial Resolution(m)')
        self.spatialResolutionLineEdit = QtGui.QLineEdit('1000')
        self.spatialResolutionLayout.addWidget(self.spatialResolutionLabel)
        self.spatialResolutionLayout.addWidget(self.spatialResolutionLineEdit)
        self.buttonBox.addWidget(self.spatialResolutionWidget)

        self.distanceWidget = QtGui.QWidget()
        self.distanceLayout = QtGui.QHBoxLayout()
        self.distanceWidget.setLayout(self.distanceLayout)
        self.distanceLabel = QtGui.QLabel('distance(km)')
        self.distanceLineEdit = QtGui.QLineEdit('100')
        self.spatialResolutionLayout.addWidget(self.distanceLabel)
        self.spatialResolutionLayout.addWidget(self.distanceLineEdit)
        self.buttonBox.addWidget(self.distanceWidget)

        self.profileWidget = QtGui.QWidget()
        self.profileLayout = QtGui.QHBoxLayout()
        self.profileWidget.setLayout(self.profileLayout)
        self.profileLabel = QtGui.QLabel('output file name')
        self.profileLineEdit = QtGui.QLineEdit('myProfile.h5')
        self.profileLayout.addWidget(self.profileLabel)
        self.profileLayout.addWidget(self.profileLineEdit)
        self.buttonBox.addWidget(self.profileWidget)

        self.instructionButton = QtGui.QPushButton('Instructions')
        self.instructionButton.setEnabled(True)
        self.instructionButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.instructionButton)

        self.plotPathButton = QtGui.QPushButton('Plot Path')
        self.plotPathButton.setEnabled(False)
        self.plotPathButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.plotPathButton)

        self.runModelButton = QtGui.QPushButton('Run Model')
        self.runModelButton.setEnabled(False)
        self.runModelButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.runModelButton)

        self.generateMeshButton = QtGui.QPushButton('Generate Mesh')
        self.generateMeshButton.setEnabled(False)
        self.generateMeshButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.generateMeshButton)

        self.velocityWidthButton = QtGui.QPushButton('Create Profile')
        self.velocityWidthButton.setEnabled(False)
        self.velocityWidthButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.velocityWidthButton)

        self.textOut = QtGui.QTextBrowser()
        self.textOut.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.textOut)

        self.leftSideWidget = QtGui.QWidget()
        self.leftSide = QtGui.QVBoxLayout()
        self.leftSideWidget.setLayout(self.leftSide)

        self.imageItemContainer = QtGui.QStackedWidget()

        self.leftSide.addWidget(self.imageItemContainer)

        self.mainLayout.addWidget(self.leftSideWidget)
        self.mainLayout.addWidget(self.buttonBoxWidget)

        self.buttonBoxWidget.setMaximumWidth(self.maxWidth + 12)

        self.connectButtons()

    '''
    Function: addToImageItemContainer
    Argument list: datasetDict
    Purpose: add the different dataset widgets to the imageItemContainer
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 2/25/18
    Last edited: 3/5/18
    '''

    def addToImageItemContainer(self, datasetDict):
        self.imageItemContainer.addWidget(datasetDict['velocity'].plotWidget)
        self.imageItemContainer.setCurrentWidget(datasetDict['velocity'].plotWidget)

        self.imageItemContainer.addWidget(datasetDict['bed'].plotWidget)
        self.imageItemContainer.addWidget(datasetDict['surface'].plotWidget)
        self.imageItemContainer.addWidget(datasetDict['thickness'].plotWidget)
        self.imageItemContainer.addWidget(datasetDict['t2m'].plotWidget)
        self.imageItemContainer.addWidget(datasetDict['smb'].plotWidget)

        for key in datasetDict:
            datasetDict[key].pathPlotItem.clear()

    '''
    Function: changeMap
    Argument list: index
    Purpose: Changes the map to a different colormap
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 2/25/18
    Last edited: 3/5/18
    '''

    # TODO mouseMove does not work when changing maps
    def changeMap(self, index):
        vr = self.imageItemContainer.currentWidget().getPlotItem().getViewBox().viewRange()
        indexToDatasetDict = {
            0: 'velocity',
            1: 'bed',
            2: 'surface',
            3: 'smb',
            4: 'thickness',
            5: 't2m'}
        if index != self.currentMap:
            oldMap = self.currentMap
            self.currentMap = index

        self.imageItemContainer.setCurrentWidget(self.datasetDict[indexToDatasetDict[self.currentMap]].plotWidget)
        self.datasetDict[indexToDatasetDict[self.currentMap]].imageItem.hoverEvent = self.mouseMove
        self.datasetDict[indexToDatasetDict[self.currentMap]].imageItem.mouseClickEvent = self.mouseClick

        self.datasetDict[indexToDatasetDict[self.currentMap]].plotWidget.getPlotItem().getViewBox().setRange(
            xRange=vr[0],
            yRange=vr[1],
            padding=0.0)
        for line in self.flowlineMarkers:
            for marker in line:
                marker.plotWidget = self.datasetDict[indexToDatasetDict[self.currentMap]]
                self.datasetDict[indexToDatasetDict[oldMap]].plotWidget.removeItem(marker.cross[0])
                self.datasetDict[indexToDatasetDict[oldMap]].plotWidget.removeItem(marker.cross[1])
                self.datasetDict[indexToDatasetDict[self.currentMap]].plotWidget.addItem(marker.cross[0])
                self.datasetDict[indexToDatasetDict[self.currentMap]].plotWidget.addItem(marker.cross[1])

                if marker.lines[0]:
                    self.datasetDict[indexToDatasetDict[self.currentMap]].plotWidget.addItem(marker.lines[0])

    '''
     Function: mouseClick
     Argument list: None
     Purpose: Either select a marker or create new flowline
     Return types, values: None
     Dependencies: None
     Creator: James Stauder
     Date created: 2/25/18
     Last edited: 3/5/18
     '''

    def mouseClick(self, e):

        # If no marker is selected
        if self.isMarkerSelected is False:

            # Check to see if click selects a marker. If so memoize the marker and the flowline Position
            for i in range(len(self.flowlineMarkers)):
                for j in range(len(self.flowlineMarkers[i])):
                    if self.flowlineMarkers[i][j].checkClicked(e.pos()):
                        self.isMarkerSelected = True
                        self.whichMarkerSelected = self.flowlineMarkers[i][j]
                        self.selectedMarkerPosition = [i, j]

                        self.displayMarkerVariables()
                        tempX, tempY = self.whichMarkerSelected.dx, self.whichMarkerSelected.dy
                        for k in range(len(self.flowlines[i])):
                            if self.flowlines[i][k] == [tempX, tempY]:
                                self.whichIndexOfFlowlineSelected = [i, k]
                        break

            # If no marker selected previously or currently create new flowline. Also cannot create more
            # then 2 flowlines.
            if (len(self.flowlines) < 2) and self.isMarkerSelected is False:
                self.spatialResolutionLineEdit.setReadOnly(True)
                self.distanceLineEdit.setReadOnly(True)
                self.flowlineDistance = int(self.distanceLineEdit.text()) * 1000
                self.lengthOfFlowline = int(self.flowlineDistance / float(self.spatialResolutionLineEdit.text()))
                self.integratorPerMarker = int(math.ceil(10000 / (float(self.spatialResolutionLineEdit.text()))))
                xClickPosition = e.pos().x()
                yClickPosition = e.pos().y()
                dx, dy = colorToProj(xClickPosition, yClickPosition)

                # Create new flowline
                newFlowline = []
                for x in range(0, self.lengthOfFlowline):
                    newFlowline.append(None)
                newFlowline[0] = [dx, dy]

                newFlowline = self.flowIntegrator.integrate(dx, dy, newFlowline, 0,
                                                            float(self.spatialResolutionLineEdit.text()))

                # Create a flowline of markers spaced out based on the IntegratorPerMarker
                newFlowlineMarkers = newFlowline[::self.integratorPerMarker]

                for i in range(len(newFlowlineMarkers)):
                    dx = newFlowlineMarkers[i][0]
                    dy = newFlowlineMarkers[i][1]
                    cx, cy = colorCoord(dx, dy)
                    newFlowlineMarkers[i] = Marker(cx, cy, dx, dy, self.imageItemContainer.currentWidget())

                self.displayMarkers(newFlowlineMarkers)

                self.flowlines.append(newFlowline)
                self.flowlineMarkers.append(newFlowlineMarkers)

                if len(self.flowlines) == 2:
                    self.velocityWidthButton.setEnabled(True)

        # Release the marker that was previously held
        else:
            self.isMarkerSelected = False
            self.whichMarkerSelected = None
            self.textOut.clear()

    '''
    Function: mouseMove
    Argument list: None
    Purpose: This function is used to move the marker that is selected and create a new integration path. 
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 2/25/18
    Last edited: 3/9/18
    TODO: This can be a bit confusing to read. The code is kind of wordy. We could possibly redraw flowline with the 
    display Markers function but that would require some changes to the Markers function to take an index.
    '''

    def mouseMove(self, e):
        if self.isMarkerSelected:

            # change the x , y values of the marker at the selected index
            xPositionOfCursor = e.pos().x()
            yPositionOfCursor = e.pos().y()
            self.whichMarkerSelected.cx = xPositionOfCursor
            self.whichMarkerSelected.cy = yPositionOfCursor
            self.whichMarkerSelected.updateCross()

            # change the x, y values of the flowline at the selected index
            whichFlowlineSelected = self.whichIndexOfFlowlineSelected[0]
            indexSelected = self.whichIndexOfFlowlineSelected[1]
            self.flowlines[whichFlowlineSelected][indexSelected] = [self.whichMarkerSelected.dx,
                                                                    self.whichMarkerSelected.dy]

            self.flowlines[whichFlowlineSelected] = self.flowIntegrator.integrate(
                self.whichMarkerSelected.dx, self.whichMarkerSelected.dy,
                self.flowlines[whichFlowlineSelected], indexSelected,
                float(self.spatialResolutionLineEdit.text()))

            # Remove every marker past the one we selected
            for i in range(self.selectedMarkerPosition[1] + 1, len(self.flowlineMarkers[0])):
                self.imageItemContainer.currentWidget().removeItem(
                    self.flowlineMarkers[self.selectedMarkerPosition[0]][i])

                # get the flowline position of the new marker
                newPosition = self.flowlines[whichFlowlineSelected][i * self.integratorPerMarker]
                cx, cy = colorCoord(newPosition[0], newPosition[1])

                # Create new marker with new data
                self.flowlineMarkers[self.selectedMarkerPosition[0]][i] = Marker(
                    cx, cy, newPosition[0], newPosition[1],
                    self.imageItemContainer.currentWidget())
            # This section redraws the new markers
            for i in range(self.selectedMarkerPosition[1] + 1, len(self.flowlineMarkers[0])):
                self.imageItemContainer.currentWidget().addItem(
                    self.flowlineMarkers[self.selectedMarkerPosition[0]][i].getCross()[0])
                self.imageItemContainer.currentWidget().addItem(
                    self.flowlineMarkers[self.selectedMarkerPosition[0]][i].getCross()[1])

                xa = [self.flowlineMarkers[self.selectedMarkerPosition[0]][i - 1].cx,
                      self.flowlineMarkers[self.selectedMarkerPosition[0]][i].cx]
                ya = [self.flowlineMarkers[self.selectedMarkerPosition[0]][i - 1].cy,
                      self.flowlineMarkers[self.selectedMarkerPosition[0]][i].cy]
                self.flowlineMarkers[self.selectedMarkerPosition[0]][i].setLine(
                    pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
                self.flowlineMarkers[self.selectedMarkerPosition[0]][i - 1].setLine(
                    self.flowlineMarkers[self.selectedMarkerPosition[0]][i].lines[0], 1)

                self.imageItemContainer.currentWidget().addItem(
                    self.flowlineMarkers[self.selectedMarkerPosition[0]][i].lines[0])

            self.displayMarkerVariables()

            # Connect lines between marker selected and previous marker
            if self.whichMarkerSelected.lines[0] is not None:
                self.whichMarkerSelected.lines[0].setData(
                    [self.whichMarkerSelected.lines[0].getData()[0][0], self.whichMarkerSelected.cx],
                    [self.whichMarkerSelected.lines[0].getData()[1][0], self.whichMarkerSelected.cy])

    '''
    Function: calcVelocityWidth
    Argument list: None
    Purpose: Calculates velocity width by connecting the ith marker of each shear margin. This displays lines between
    each displayed marker as well. This will also average both the x and y coordinates of the shear margins(index 0)
    and integrate a flowline starting from that center point. 
    Return types, values: None
    Dependencies: Two selected shear margins. This is susceptible to user errors
    Creator: James Stauder
    Date created: 2/25/18
    Last edited: 3/9/18
    '''

    def calcVelocityWidth(self):

        # Get center point at terminus between two shear margins
        x1, y1 = self.flowlineMarkers[0][0].cx, self.flowlineMarkers[0][0].cy
        x2, y2 = self.flowlineMarkers[1][0].cx, self.flowlineMarkers[1][0].cy
        xMid = (x1 + x2) / 2
        yMid = (y1 + y2) / 2
        xProj, yProj = colorToProj(xMid, yMid)

        # Create mid flowline
        midFlowline = []
        for i in range(self.lengthOfFlowline):
            midFlowline.append(None)
        midFlowline[0] = [xProj, yProj]
        midFlowline = self.flowIntegrator.integrate(
            xProj, yProj, midFlowline, 0,
            float(self.spatialResolutionLineEdit.text()))

        # create new Markers that will be displayed on the GUI.
        newFlowlineMarkers = midFlowline[::self.integratorPerMarker]
        for i in range(len(newFlowlineMarkers)):
            dx = newFlowlineMarkers[i][0]
            dy = newFlowlineMarkers[i][1]
            cx, cy = colorCoord(dx, dy)
            newFlowlineMarkers[i] = Marker(cx, cy, dx, dy, self.imageItemContainer.currentWidget())
        self.displayMarkers(newFlowlineMarkers)

        self.flowlines.append(midFlowline)
        self.flowlineMarkers.append(newFlowlineMarkers)

        # Connect the shear margins by the ith index.
        for i in range(len(self.flowlineMarkers[0])):
            xValues = [self.flowlineMarkers[1][i].cx, self.flowlineMarkers[0][i].cx]
            yValues = [self.flowlineMarkers[1][i].cy, self.flowlineMarkers[0][i].cy]

            self.flowlineMarkers[0][i].setLine(pg.PlotDataItem(xValues, yValues, connect='all', pen=skinnyBlackPlotPen),
                                               0)
            self.imageItemContainer.currentWidget().addItem(self.flowlineMarkers[0][i].lines[0])
        self.runModelButton.setEnabled(True)

        interpolateFlowlineDataAverage(self.datasetDict, self.flowlines, self.flowlineDistance,
                                       float(self.spatialResolutionLineEdit.text()), self.profileLineEdit.text())
        interpolateFlowlineData(self.datasetDict, self.flowlines, self.flowlineDistance,
                                float(self.spatialResolutionLineEdit.text()), self.profileLineEdit.text())

    '''
    Function: displayMarkers
    Argument list: flowline 
    Purpose: Takes a flowline of markers and displays them on the gui
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 3/2/18
    Last edited: 3/2/18
    '''

    def displayMarkers(self, flowline):

        # Add first marker. This needs to be peeled because the for loop
        # connects the markers backwards
        self.imageItemContainer.currentWidget().addItem(flowline[0].getCross()[0])
        self.imageItemContainer.currentWidget().addItem(flowline[0].getCross()[1])

        for i in range(1, len(flowline)):
            self.imageItemContainer.currentWidget().addItem(flowline[i].getCross()[0])
            self.imageItemContainer.currentWidget().addItem(flowline[i].getCross()[1])

            xValuesOfMarkers = [flowline[i - 1].cx, flowline[i].cx]
            yValuesOfMarkers = [flowline[i - 1].cy, flowline[i].cy]

            # Create lines from each marker
            flowline[i].setLine(
                pg.PlotDataItem(xValuesOfMarkers, yValuesOfMarkers, connect='all', pen=skinnyBlackPlotPen), 0)
            flowline[i - 1].setLine(flowline[i].lines[0], 1)

            self.imageItemContainer.currentWidget().addItem(flowline[i].lines[0])

    '''
    Function: displayMarkerVariables
    Argument list: None
    Purpose: Displays the marker variables of the marker selected
    Return types, values: None
    Dependencies: Marker to be selected
    Creator: James Stauder
    Date created: 2/25/18
    Last edited: 2/25/18
    '''

    def displayMarkerVariables(self):
        self.textOut.clear()
        selectedMarkerX = self.whichMarkerSelected.dx
        selectedMarkerY = self.whichMarkerSelected.dy

        for x in self.maps:
            stringOut = str(self.datasetDict[x.lower()].getInterpolatedValue(selectedMarkerX, selectedMarkerY))
            self.textOut.append(x + ": " + stringOut[2:-2])

    '''
    Function: createIntegrator
    Argument list: Nones
    Purpose: Create integrator class. This will allow us to integrate up the ice flow
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 2/5/18
    Last edited: 2/5/18
    '''

    # TODO: Does this have to be tied to mw? Can this be changed in some way?
    def createIntegrator(self):
        vx = Dataset('VX', tealPlotPen)
        vy = Dataset('VY', tealPlotPen)
        self.flowIntegrator = FlowIntegrator(vx, vy)

    def runModel(self):
        m = ModelGUI(self)

    '''
    Function: connectButtons
    Argument list: None
    Purpose: connect the buttons of the gui to various functions
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 2/5/18
    Last edited: 2/5/18
    '''

    def connectButtons(self):
        self.mapList.currentIndexChanged.connect(self.changeMap)
        self.instructionButton.clicked.connect(self.showInstructions)
        self.velocityWidthButton.clicked.connect(self.calcVelocityWidth)
        self.runModelButton.clicked.connect(self.runModel)

    def showInstructions(self):
        Instructions(self)
