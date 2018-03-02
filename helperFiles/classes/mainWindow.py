import sys
from PyQt4.QtGui import *
from pyqtgraph.Qt import QtGui
from Instructions import *
from FlowlinePath import *
from FlowIntegrator import *
from Dataset import *
from Marker import *


class mainWindow(QMainWindow):
    def __init__(self, parent=None):

        super(mainWindow, self).__init__(parent)
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

        self.flowlines = []
        self.flowlineMarkers = []

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
        self.imageIconContainer.setCurrentWidget(self.datasetDict[indexToDatasetDict[index]].plotWidget)

    def mouseClick(self, e):

        ##If no marker is selected
        if self.isMarkerSelected == False:

            ##Check to see if a marker is selected
            for flowline in self.flowlineMarkers:
                for marker in flowline:
                    if (marker.checkClicked(e.pos())):
                        self.isMarkerSelected = True
                        self.whichMarkerSelected = marker
                        self.displayMarkerVariables()

            for i in range(len(self.flowlineMarkers)):
                for j in range(len(self.flowlineMarkers[i])):
                    if (self.flowlineMarkers[i][j].checkClicked(e.pos())):
                        self.isMarkerSelected = True
                        self.whichMarkerSelected = self.flowlineMarkers[i][j]
                        self.selectedMarkerPosition = [i, j]
                        self.displayMarkerVariables()

            ##If no marker selected previously or currently create new flowline            
            if (len(self.flowlines) < 2) and self.isMarkerSelected == False:
                xClickPosition = e.pos().x()
                yClickPosition = e.pos().y()

                newFlowline = []
                self.lengthOfFlowline = 300
                for x in range(0, self.lengthOfFlowline):
                    newFlowline.append(None)

                dx, dy = colorToProj(xClickPosition, yClickPosition)
                

                newFlowline[0] = [dx,dy]
                
                '''
                newFlowline[0] = Marker(xClickPosition, yClickPosition, dx, dy, self.imageIconContainer.currentWidget())
                self.imageIconContainer.currentWidget().addItem(newFlowline[0].getCross()[0])
                self.imageIconContainer.currentWidget().addItem(newFlowline[0].getCross()[1])
                '''
                
                newFlowline = self.flowIntegrator.integrate(dx, dy, newFlowline, 0)
                self.IntegratorPerMarker = 7
                
                
                
                newFlowlineMarkers = newFlowline[::self.IntegratorPerMarker]
                

                
                for i in range(len(newFlowlineMarkers)):
                    dx = newFlowlineMarkers[i][0]
                    dy = newFlowlineMarkers[i][1]
                    cx, cy = colorCoord(dx,dy)
                    newFlowlineMarkers[i] = Marker(cx,cy,dx,dy, self.imageIconContainer.currentWidget())
                    
                self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[0].getCross()[0])
                self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[0].getCross()[1])
                
                for i in range(1, len(newFlowlineMarkers)):
                    self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[i].getCross()[0])
                    self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[i].getCross()[1])
                    xa = [newFlowlineMarkers[i - 1].cx, newFlowlineMarkers[i].cx]
                    ya = [newFlowlineMarkers[i - 1].cy, newFlowlineMarkers[i].cy]
                    newFlowlineMarkers[i].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
                    newFlowlineMarkers[i - 1].setLine(newFlowlineMarkers[i].lines[0], 1)
                    self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[i].lines[0])

                self.flowlines.append(newFlowline)
                self.flowlineMarkers.append(newFlowlineMarkers)

                if len(self.flowlines) == 2:
                    self.velocityWidthButton.setEnabled(True)

        ##Release the marker that was previously held
        else:
            self.isMarkerSelected = False
            self.whichMarkerSelected = None
            self.textOut.clear()

    ##Move marker. Need to finish
    def mouseMove(self, e):
        if self.isMarkerSelected:

            xPosition = e.pos().x()
            yPosition = e.pos().y()
            self.whichMarkerSelected.cx = xPosition
            self.whichMarkerSelected.cy = yPosition
            self.whichMarkerSelected.updateCross()

            whichFlowline = self.flowlineMarkers[self.selectedMarkerPosition[0]]
            whichMarker = whichFlowline[self.selectedMarkerPosition[1]]

            dx, dy = colorToProj(self.whichMarkerSelected.cx, self.whichMarkerSelected.cy)

            for i in range(self.selectedMarkerPosition[1] + 1, self.lengthOfFlowline):
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

    def showInstructions(self):
        Instructions(self)

    def calcVelocityWidth(self):
        x1, y1 = self.flowlineMarkers[0][0].cx, self.flowlineMarkers[0][0].cy
        x2, y2 = self.flowlineMarkers[1][0].cx, self.flowlineMarkers[1][0].cy

        # print(x1, y1, x2, y2)
        # print(self.flowlines[0][0].dx, self.flowlines[0][0].dy,self.flowlines[1][0].dx, self.flowlines[1][0].dy )
        xMid = (x1 + x2) / 2
        yMid = (y1 + y2) / 2
        xProj, yProj = colorToProj(xMid, yMid)

        # print(xMid, yMid, xProj, yProj)

        midFlowline = []
        for i in range(self.lengthOfFlowline):
            midFlowline.append(None)
            
        midFlowline[0] = [xProj, yProj]

        midFlowline = self.flowIntegrator.integrate(xProj, yProj, midFlowline, 0)
               
               

        newFlowlineMarkers = midFlowline[::self.IntegratorPerMarker]
       
        for i in range(len(newFlowlineMarkers)):
            dx = newFlowlineMarkers[i][0]
            dy = newFlowlineMarkers[i][1]
            cx, cy = colorCoord(dx,dy)
            newFlowlineMarkers[i] = Marker(cx,cy,dx,dy, self.imageIconContainer.currentWidget())
                    
        self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[0].getCross()[0])
        self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[0].getCross()[1])
                
        for i in range(1, len(newFlowlineMarkers)):
            self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[i].getCross()[0])
            self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[i].getCross()[1])
            xa = [newFlowlineMarkers[i - 1].cx, newFlowlineMarkers[i].cx]
            ya = [newFlowlineMarkers[i - 1].cy, newFlowlineMarkers[i].cy]
            newFlowlineMarkers[i].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
            newFlowlineMarkers[i - 1].setLine(newFlowlineMarkers[i].lines[0], 1)
            self.imageIconContainer.currentWidget().addItem(newFlowlineMarkers[i].lines[0])

        self.flowlines.append(midFlowline)
        self.flowlineMarkers.append(newFlowlineMarkers)

        for i in range(len(self.flowlineMarkers[0])):
            xValues = [self.flowlineMarkers[1][i].cx, self.flowlineMarkers[0][i].cx]
            yValues = [self.flowlineMarkers[1][i].cy, self.flowlineMarkers[0][i].cy]
            
            self.flowlineMarkers[0][i].setLine(pg.PlotDataItem(xValues,yValues,connect='all', pen=skinnyBlackPlotPen), 0)
            self.imageIconContainer.currentWidget().addItem(self.flowlineMarkers[0][i].lines[0])


    def displayMarkerVariables(self):
        self.textOut.clear()
        selectedMarkerX = self.whichMarkerSelected.dx
        selectedMarkerY = self.whichMarkerSelected.dy

        for x in self.maps:
            stringOut = str(self.datasetDict[x.lower()].getInterpolatedValue(selectedMarkerX, selectedMarkerY))
            self.textOut.append(x + ": " + stringOut[2:-2])

    def createIntegrator(self):
        vx = Dataset('VX', tealPlotPen)
        vy = Dataset('VY', tealPlotPen)
        self.flowIntegrator = FlowIntegrator(vx, vy)

    def connectButtons(self):
        self.mapList.currentIndexChanged.connect(self.changeMap)
        self.instructionButton.clicked.connect(self.showInstructions)
        self.velocityWidthButton.clicked.connect(self.calcVelocityWidth)
