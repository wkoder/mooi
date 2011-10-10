'''
Created on Oct 3, 2011

@author: Moises Osorio [WCoder]
'''

import sys
import dircache

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport

from PlotWidget import PlotWidget

from MOSolution import MOSolution

__version__ = "1.0.0"

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("MOOI: Multi-Objective Optimization Interface")
        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.mirroredvertically = False
        self.mirroredhorizontally = False
        self.resize(840, 480)
        self.dataDir = "data"
        
        self.plot = PlotWidget()
        self.plot.setMinimumSize(640, 480)
        self.plot.setMaximumSize(640, 480)
        self.plot.setAlignment(Qt.AlignCenter)
        self.plot.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.plot)
        self.printer = None
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Loading initial data...")
        
        self.pfWidget = QListWidget()
        self.pfWidget.itemSelectionChanged.connect(self.solutionSelected)
        pfDockWidget = QDockWidget("Pareto Fronts", self)
        pfDockWidget.setObjectName("ParetoFronts")
        pfDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        pfDockWidget.setWidget(self.pfWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, pfDockWidget)
        
#        fileNewAction = self.createAction("&New...", self.fileNew, QKeySequence.New, "filenew", "Create an image file")
#        mirrorGroup = QActionGroup(self)
#        editUnMirrorAction = self.createAction("&Unmirror", self.editUnMirror, "Ctrl+U", "editunmirror", "Unmirror the image", True, "toggled(bool)")
#        mirrorGroup.addAction(editUnMirrorAction)
#        editUnMirrorAction.setChecked(True)
        
#        editMenu = self.menuBar().addMenu("&Edit")
#        self.addActions(editMenu, (editInvertAction, editZoomAction))

#        mirrorMenu = editMenu.addMenu(QIcon(":/editmirror.png"), "&Mirror")
#        self.addActions(mirrorMenu, (editUnMirrorAction))
        
#        fileToolbar = self.addToolBar("File")
#        fileToolbar.setObjectName("FileToolBar")
#        self.addActions(fileToolbar, (fileNewAction, fileQuitAction))
        
        settings = QSettings()
        self.restoreGeometry(settings.value("UI/Geometry").toByteArray())
        self.restoreState(settings.value("UI/State").toByteArray())
        
        QTimer.singleShot(0, self.loadInitialData)

    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
                
    def solutionSelected(self):
        selection = self.pfWidget.currentItem()
        if selection is None:
            return
        self.showSolution(selection.text())
        
    def showSolution(self, functionName):
        function = self.solutionMap[str(functionName)]
        self.plot.plotFile(function.functionSolution if function.functionSolution is not None else function.variableSolution)
                
    def getFunctionName(self, filename):
        return filename.replace("_", "").replace("fun", "").replace("var", "").replace(".dat", "").replace("front", "").replace("pareto", "")
        
    def isFunctionFile(self, filename):
        return "var" not in filename

    def loadInitialData(self):
        self.solutionMap = dict()
        self.solutions = []
        for filename in dircache.listdir(self.dataDir):
            functionName = self.getFunctionName(filename)
            filename = self.dataDir + "/" + filename
            
            if functionName in self.solutionMap:
                function = self.solutionMap[functionName]
            else:
                function = MOSolution(functionName)
                self.solutionMap[functionName] = function
                self.solutions.append(function)
                
            if self.isFunctionFile(filename):
                function.functionSolution = filename
            else:
                function.variableSolution = filename
                
        self.solutions.sort()
        for solution in self.solutions:
            item = QListWidgetItem()
            item.setText(solution.functionName)
            self.pfWidget.addItem(item)
        
        if len(self.solutions) > 0:
            self.pfWidget.setCurrentItem(self.pfWidget.item(0))
            self.statusBar().showMessage("Ready!", 5000)
        else:
            self.statusBar().showMessage("Warning: No pareto front files found.")
            
    def closeEvent(self, event):
        self.statusBar().showMessage("Closing...")
        settings = QSettings()
        settings.setValue("UI/Geometry", self.saveGeometry())
        settings.setValue("UI/State", self.saveState())
        self.plot.removeTemporalFiles()
        
def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Centro de Investigacion y de Estudios Avanzados del Instituto Politecnico Nacional (CINVESTAV-IPN)")
    app.setOrganizationDomain("cs.cinvestav.mx")
    app.setApplicationName("MOOI: Multi-Objective Optimization Interface")
    #app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()
