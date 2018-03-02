from PyQt4.QtGui import *
from Instructions import *
from FlowIntegrator import *
from Dataset import *
from Marker import *


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
        self.lengthOfFlowline = 300
        self.flowlines = []
        self.flowlineMarkers = []
        self.integratorPerMarker = 7

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

        self.autoCorrectVpt = QtGui.QCheckBox('Auto-correct Marker pos.')
        self.autoCorrectVpt.setTristate(False)
        self.autoCorrectVpt.setCheckState(0)
        self.autoCorrectVpt.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.autoCorrectVpt)

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

        self.velocityWidthButton = QtGui.QPushButton('Velocity Width')
        self.velocityWidthButton.setEnabled(False)
        self.velocityWidthButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.velocityWidthButton)

        self.textOut = QtGui.QTextBrowser()
        self.textOut.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.textOut)

        self.leftSideWidget = QtGui.QWidget()
        self.leftSide = QtGui.QVBoxLayout()
        self.leftSideWidget.setLayout(self.leftSide)

        self.imageIconContainer = QtGui.QStackedWidget()

        self.leftSide.addWidget(self.imageIconContainer)

        self.mainLayout.addWidget(self.leftSideWidget)
        self.mainLayout.addWidget(self.buttonBoxWidget)

        self.buttonBoxWidget.setMaximumWidth(self.maxWidth + 12)

        self.connectButtons()

    '''
    Function: changeMap
    Argument list: index
    Purpose: Changes the map to a different colormap
    Return types, values: None
    Dependencies: None
    Creator: James Stauder
    Date created: 2/25/18
    Last edited: 2/25/18
    '''

    # TODO Make sure markers work with different maps
    def changeMap(self, index):
        vr = self.imageIconContainer.currentWidget().getPlotItem().getViewBox().viewRange()
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

        # Kind of strange way. Possibly able to do this differently
        self.imageIconContainer.setCurrentWidget(self.datasetDict[indexToDatasetDict[index]].plotWidget)

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
                xClickPosition = e.pos().x()
                yClickPosition = e.pos().y()
                dx, dy = colorToProj(xClickPosition, yClickPosition)

                # Create new flowline
                newFlowline = []
                for x in range(0, self.lengthOfFlowline):
                    newFlowline.append(None)
                newFlowline[0] = [dx, dy]

                newFlowline = self.flowIntegrator.integrate(dx, dy, newFlowline, 0)

                # Create a flowline of markers spaced out based on the IntegratorPerMarker
                newFlowlineMarkers = newFlowline[::self.integratorPerMarker]

                for i in range(len(newFlowlineMarkers)):
                    dx = newFlowlineMarkers[i][0]
                    dy = newFlowlineMarkers[i][1]
                    cx, cy = colorCoord(dx, dy)
                    newFlowlineMarkers[i] = Marker(cx, cy, dx, dy, self.imageIconContainer.currentWidget())

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

    # Move marker.
    # TODO: FINISH THIS
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

            self.flowlines[whichFlowlineSelected] = self.flowIntegrator.integrate(self.whichMarkerSelected.dx,
                                                                                  self.whichMarkerSelected.dy,
                                                                                  self.flowlines[whichFlowlineSelected],
                                                                                  indexSelected)

            # Remove every marker past the one we selected
            for i in range(self.selectedMarkerPosition[1] + 1, len(self.flowlineMarkers[0])):
                self.imageIconContainer.currentWidget().removeItem(
                    self.flowlineMarkers[self.selectedMarkerPosition[0]][i])

                # get the flowline position of the new marker
                newPosition = self.flowlines[whichFlowlineSelected][indexSelected + i * self.integratorPerMarker]
                cx, cy = colorCoord(newPosition[0], newPosition[1])
                self.flowlineMarkers[self.selectedMarkerPosition[0]][i] = Marker(cx, cy, newPosition[0], newPosition[1],
                                                                                 self.imageIconContainer.currentWidget())



            '''
            TODO: Markers are now created. Need to display them. Try to utilize displayMarkers function
            So need to add an index to start at in displayMarkers function
            Code below this is old and probably useless but keeping for notekeeping
            
            '''



            whichFlowlineMarkers = self.flowlineMarkers[self.selectedMarkerPosition[0]]

            whichMarker = whichFlowlineMarkers[self.selectedMarkerPosition[1]]

            for i in range(self.selectedMarkerPosition[1] + 1, len(whichFlowlineMarkers)):
                self.imageIconContainer.currentWidget().removeItem(whichFlowline[i])

            whichFlowline = self.flowIntegrator.integrate(dx, dy, whichFlowline, self.selectedMarkerPosition[1],
                                                          self.imageIconContainer.currentWidget())

            for i in range(self.selectedMarkerPosition[1] + 1, self.lengthOfFlowline):
                self.imageIconContainer.currentWidget().addItem(whichFlowline[i].getCross()[0])
                self.imageIconContainer.currentWidget().addItem(whichFlowline[i].getCross()[1])

                xa = [whichFlowline[i - 1].cx, whichFlowline[i].cx]
                ya = [whichFlowline[i - 1].cy, whichFlowline[i].cy]
                whichFlowline[i].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
                whichFlowline[i - 1].setLine(whichFlowline[i].lines[0], 1)

                self.imageIconContainer.currentWidget().addItem(whichFlowline[i].lines[0])

            self.displayMarkerVariables()

            if self.whichMarkerSelected.lines[0] is not None:
                self.whichMarkerSelected.lines[0].setData(
                    [self.whichMarkerSelected.lines[0].getData()[0][0], self.whichMarkerSelected.cx],
                    [self.whichMarkerSelected.lines[0].getData()[1][0], self.whichMarkerSelected.cy])

            if self.whichMarkerSelected.lines[1] is not None:
                self.whichMarkerSelected.lines[1].setData(
                    [self.whichMarkerSelected.cx, self.whichMarkerSelected.lines[1].getData()[0][1]],
                    [self.whichMarkerSelected.cy, self.whichMarkerSelected.lines[1].getData()[1][1]])

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
    Last edited: 3/2/18
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
        midFlowline = self.flowIntegrator.integrate(xProj, yProj, midFlowline, 0)

        # create new Markers that will be displayed on the GUI.
        newFlowlineMarkers = midFlowline[::self.integratorPerMarker]
        for i in range(len(newFlowlineMarkers)):
            dx = newFlowlineMarkers[i][0]
            dy = newFlowlineMarkers[i][1]
            cx, cy = colorCoord(dx, dy)
            newFlowlineMarkers[i] = Marker(cx, cy, dx, dy, self.imageIconContainer.currentWidget())
        self.displayMarkers(newFlowlineMarkers)

        self.flowlines.append(midFlowline)
        self.flowlineMarkers.append(newFlowlineMarkers)

        # Connect the shear margins by the ith index.
        for i in range(len(self.flowlineMarkers[0])):
            xValues = [self.flowlineMarkers[1][i].cx, self.flowlineMarkers[0][i].cx]
            yValues = [self.flowlineMarkers[1][i].cy, self.flowlineMarkers[0][i].cy]

            self.flowlineMarkers[0][i].setLine(pg.PlotDataItem(xValues, yValues, connect='all', pen=skinnyBlackPlotPen),
                                               0)
            self.imageIconContainer.currentWidget().addItem(self.flowlineMarkers[0][i].lines[0])

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
        self.imageIconContainer.currentWidget().addItem(flowline[0].getCross()[0])
        self.imageIconContainer.currentWidget().addItem(flowline[0].getCross()[1])

        for i in range(1, len(flowline)):
            self.imageIconContainer.currentWidget().addItem(flowline[i].getCross()[0])
            self.imageIconContainer.currentWidget().addItem(flowline[i].getCross()[1])

            xValuesOfMarkers = [flowline[i - 1].cx, flowline[i].cx]
            yValuesOfMarkers = [flowline[i - 1].cy, flowline[i].cy]

            # Create lines from each marker
            flowline[i].setLine(
                pg.PlotDataItem(xValuesOfMarkers, yValuesOfMarkers, connect='all', pen=skinnyBlackPlotPen), 0)
            flowline[i - 1].setLine(flowline[i].lines[0], 1)

            self.imageIconContainer.currentWidget().addItem(flowline[i].lines[0])

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

    def showInstructions(self):
        Instructions(self)
