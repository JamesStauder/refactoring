from pyqtgraph.Qt import QtGui
from PyQt4 import QtCore
import pyqtgraph as pg


class ModelGUI(QtGui.QMainWindow):
    def __init__(self, parent):
        self.hdfName = None
        self.plotter = None
        self.parent = parent

        QtGui.QMainWindow.__init__(self, self.parent)

        self.centerWidget = QtGui.QWidget()
        self.setCentralWidget(self.centerWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.centerWidget.setLayout(self.horizontalLayout)

        self.createRightPanel()
        self.createLeftPanel()

        self.horizontalLayout.addWidget(self.leftPanelWidget)
        self.horizontalLayout.addWidget(self.rightPanelWidget)
        self.showMaximized()
        self.show()

    def createRightPanel(self):
        self.rightPanelWidget = QtGui.QWidget()
        self.rightPanelWidget.setMaximumWidth(300)
        self.rightPanelLayout = QtGui.QGridLayout()
        self.rightPanelLayout.setAlignment(QtCore.Qt.AlignTop)
        self.rightPanelLayout.setSpacing(4)

        self.rightPanelWidget.setLayout(self.rightPanelLayout)

        self.timeEndLabel = QtGui.QLabel('time end(yr):')
        self.timeEndLineEdit = QtGui.QLineEdit('20000')
        self.timeStepLabel = QtGui.QLabel('time step(yr):')
        self.timeStepLineEdit = QtGui.QLineEdit('10')
        self.timeCurrent = QtGui.QLabel('Current year: ')

        # Buttons
        self.runButton = QtGui.QPushButton('Run Model')
        self.pauseButton = QtGui.QPushButton('Pause Model')
        self.pauseButton.setEnabled(False)

        self.rightPanelLayout.addWidget(self.timeEndLabel, 0, 0)
        self.rightPanelLayout.addWidget(self.timeEndLineEdit, 0, 1)
        self.rightPanelLayout.addWidget(self.timeStepLabel, 1, 0)
        self.rightPanelLayout.addWidget(self.timeStepLineEdit, 1, 1)
        self.rightPanelLayout.addWidget(self.timeCurrent, 3, 0, 1, 2)
        self.rightPanelLayout.addWidget(self.runButton, 4, 0, 1, 2)
        self.rightPanelLayout.addWidget(self.pauseButton, 5, 0, 1, 2)

    def createLeftPanel(self):
        self.leftPanelWidget = QtGui.QWidget()
        self.leftPanelLayout = QtGui.QVBoxLayout()
        self.leftPanelWidget.setLayout(self.leftPanelLayout)

        self.plot1 = pg.PlotWidget()
        self.plot2 = pg.PlotWidget()
        self.plot3 = pg.PlotWidget()

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setEnabled(False)
        self.sliderLabel = QtGui.QLabel('Year: ')
        self.leftPanelLayout.addWidget(self.plot1)
        self.leftPanelLayout.addWidget(self.plot2)
        self.leftPanelLayout.addWidget(self.plot3)
        self.leftPanelLayout.addWidget(self.slider)
        self.leftPanelLayout.addWidget(self.sliderLabel)

    def runModelEvent(self):
        self.runButton.setEnabled(False)
        self.pauseButton.setEnabled(True)

        self.dr = float(self.spatialResLineEdit.text())




