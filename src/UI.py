'''
Created on Oct 3, 2011

@author: Moises Osorio [WCoder]
'''

import sys
import dircache
import platform
import os

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
        self.plot.setAlignment(Qt.AlignCenter)
        self.plot.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.plot)

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Loading initial data...")
        
        self.solutionWidget = QListWidget()
        self.solutionWidget.itemSelectionChanged.connect(self.solutionSelected)
        solutionDock = QDockWidget("Problems", self)
        solutionDock.setObjectName("Problems")
        solutionDock.setWidget(self.solutionWidget)
        solutionDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, solutionDock)
        
        self.showSolutionsRadio = QRadioButton("Functions")
        self.showSolutionsRadio.setChecked(True)
        self.showSolutionsRadio.toggled.connect(self._showSolution)
        self.showVariablesRadio = QRadioButton("Variables")
        
        radioWidget = QWidget()
        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.showSolutionsRadio)
        radioLayout.addWidget(self.showVariablesRadio)
        radioWidget.setLayout(radioLayout)
        
        self.generationLabel = QLabel("Generation: 1")
        self.generationSlider = QSlider(Qt.Horizontal)
        self.generationSlider.setTickPosition(QSlider.TicksBothSides)
        self.generationSlider.setTracking(True)
        self.generationSlider.setMinimum(1)
        self.generationSlider.setMaximum(1)
        self.generationSlider.setTickInterval(1)
        self.generationSlider.valueChanged.connect(self._showSolution)
        
        self.solutionSelector = QWidget()
        solutionSelectorLayout = QVBoxLayout()
        self.solutionSelector.setLayout(solutionSelectorLayout)
        
        self.currentDirLabel = QLabel("No directory to scan")
        self.selectButton = QPushButton("Select")
        self.selectButton.clicked.connect(self.selectCurrentDirectory)
        
        exportButton = QPushButton("Export Image")
        exportButton.clicked.connect(self.exportImage)
        
        refreshButton = QPushButton("Refresh")
        refreshButton.clicked.connect(self.scanDirectory)
        
        controlLayout = QVBoxLayout()
        controlLayout.addWidget(radioWidget)
        controlLayout.addWidget(self.generationLabel)
        controlLayout.addWidget(self.generationSlider)
        controlLayout.addWidget(self.solutionSelector)
        controlLayout.addWidget(refreshButton)
        controlLayout.addWidget(exportButton)
        controlLayout.addStretch()
        controlLayout.addWidget(self.selectButton)
        controlLayout.addWidget(self.currentDirLabel)
        controlWidget = QWidget()
        controlWidget.setLayout(controlLayout)
        controlDock = QDockWidget("Control", self)
        controlDock.setObjectName("Control")
        controlDock.setWidget(controlWidget)
        controlDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, controlDock)
        
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
        
        self.currentSolution = None
        self.currentDir = None

        settings = QSettings()
        self.restoreState(settings.value("UI/State").toByteArray())
        self.restoreGeometry(settings.value("UI/Geometry").toByteArray())
        currentDir = str(settings.value("Config/Directory").toString())
        if currentDir is not None:
            self.currentDir = currentDir
            self.currentDirLabel.setText(currentDir)
        
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
                
    def exportImage(self):
        settings = QSettings()
        filename = settings.value("Config/SaveDirectory").toString()
        filename = QFileDialog.getSaveFileName(self, "Export image as", filename)
        if filename is None or filename == "":
            return

        self.currentDir = filename
        self.currentDirLabel.setText(self.currentDir)
        settings.setValue("Config/SaveDirectory", QVariant(filename))
        self._exportToImage(filename)
        self.statusBar().showMessage("Image saved!", 5000)
                
    def _exportToImage(self, filename=None):
        toPlot = self._getSolutionsToPlot()
        if self.showSolutionsRadio.isChecked():
            self.plot.plotSolution(toPlot[0], toPlot[1:], self.currentSolution.functionName, "F1", "F2", "F3", filename)
        else:
            self.plot.plotSolution(toPlot[0], toPlot[1:], self.currentSolution.functionName, "x1", "x2", "x3", filename)
                
    def helpAbout(self):
        QMessageBox.about(self, "About Image Changer",
            """<b>Multi-Objective Optimization Interface</b> v%s
            <p>Copyright &copy; 2011 CINVESTAV-IPN
            All rights reserved.
            <p>This application can be used to perform
            simple optimization analysis.
            <p>Python %s - Qt %s - PyQt %s on %s""" % 
            (__version__, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def selectCurrentDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select a directory to scan", self.currentDir)
        if os.path.exists(directory):
            self.currentDir = directory
            self.currentDirLabel.setText(self.currentDir)
            settings = QSettings()
            settings.setValue("Config/Directory", QVariant(directory))
            QTimer.singleShot(0, self.scanDirectory)
        
    def solutionSelected(self):
        selection = self.solutionWidget.currentItem()
        if selection is None:
            return
        self.showSolution(selection.text())
        
    def showSolution(self, functionName):
        function = self.solutions[str(functionName)]
        self.currentSolution = function
        self._updateSolutionSelection()
        self._showSolution()
            
    def _updateSolutionSelection(self):
        self.clearWidget(self.solutionSelector)

        pareto = QCheckBox("Pareto")
        pareto.setChecked(True)
        pareto.stateChanged.connect(self._showSolution)
        self.solutionSelector.layout().addWidget(pareto)

        solution = QCheckBox("Solution")
        solution.setChecked(True)
        solution.stateChanged.connect(self._showSolution)
        self.solutionSelector.layout().addWidget(solution)
        
    def _showSolution(self):
        sol = self.currentSolution
        if sol is None:
            return
        
        if sol.variablePareto is None and sol.variableSolution.count() == 0 and self.showVariablesRadio.isEnabled():
            self.showVariablesRadio.setEnabled(False)
            if self.showVariablesRadio.isChecked():
                self.showSolutionsRadio.setChecked(True)
        else:
            self.showVariablesRadio.setEnabled(True)
        
        if sol.functionPareto is None and sol.functionSolution.count() == 0 and self.showSolutionsRadio.isEnabled():
            self.showSolutionsRadio.setEnabled(False)
            if self.showSolutionsRadio.isChecked():
                self.showVariablesRadio.setChecked(True)
        else:
            self.showSolutionsRadio.setEnabled(True)
        
        if self.showSolutionsRadio.isChecked():
            self.generationSlider.setMaximum(sol.functionSolution.count())
        else:
            self.generationSlider.setMaximum(sol.variableSolution.count())
        self._exportToImage()
        
    def _getSolutionsToPlot(self):
        sol = self.currentSolution
        generation = self.generationSlider.value()
        self.generationLabel.setText("Generation: %d" % generation)
        
        solutions = []
        showPareto = self.solutionSelector.layout().itemAt(0).widget().isChecked()
        showSolution = self.solutionSelector.layout().itemAt(1).widget().isChecked()
        if self.showSolutionsRadio.isChecked():
            solutions.append(sol.functionPareto if showPareto else None)
            if showSolution:
                solutions.append(sol.functionSolution.getSolutions()[generation-1])
        else:
            solutions.append(sol.variablePareto if showPareto else None)
            if showSolution:
                solutions.append(sol.variableSolution.getSolutions()[generation-1])
            
        return solutions
            
    def isSolutionFile(self, filename):
        if not os.path.exists(filename) or os.path.isdir(filename):
            return False
        
        f = open(filename)
        try:
            tries = 5 # Try 5 times to check if the file is valid
            for line in f:
                [float(x) for x in line.split()]
                tries = tries - 1
                if tries == 0:
                    break
                
            f.close()
            return True
        except Exception:
            f.close()
            return False
            
    def scanDirectory(self):
        if self.currentDir is None:
            return
        
        for function in self.solutions.values():
            if function.functionPareto is None and function.variablePareto is None:
                del self.solutions[function.functionName]
            else:
                function.clear()
                
        for filename in dircache.listdir(self.currentDir):
            filename = str(self.currentDir + "/" + filename)
#            fileType, _ = mimetypes.guess_type(filename)
#            print fileType, filename
            #if fileType is None or "text" not in fileType or not self.isSolutionFile(filename):
            if not self.isSolutionFile(filename):
                continue
            
            functionName = self.getFunctionName(filename)
            genPos = max(-1, functionName.rfind("."), functionName.rfind("-"), functionName.rfind("_"))
            generation = 1 << 30
            if genPos >= 0:
                try:
                    generation = int(functionName[genPos+1:])
                    functionName = functionName[:genPos]
                except:
                    pass
                
            if functionName in self.solutions:
                function = self.solutions[functionName]
            else:
                function = MOSolution(functionName)
                self.solutions[functionName] = function
                
            if self.isFunctionFile(filename):
                function.addFunctionSolution(filename, generation)
            else:
                function.addVariableSolution(filename, generation)
            
        self.updateUI()
        
    def getFunctionName(self, filename):
        filename = filename[filename.rfind("/")+1:]
        if "." in filename:
            filename = filename[:filename.rfind(".")]
        return filename.lower().replace("_fun", "").replace("_var", "").replace("fun", "").replace("var", "")\
            .replace("front_", "").replace("pareto_", "").replace("front", "").replace("pareto", "").title()
        
    def isFunctionFile(self, filename):
        return "var" not in filename.lower()
    
    def clearWidget(self, widget):
        layout = widget.layout()
        for i in xrange(layout.count()-1, -1, -1):
            layout.removeItem(layout.itemAt(i))
    
    def updateUI(self):
        self.statusBar().showMessage("Updating solutions...")
                
        solutions = []
        for solution in self.solutions.values():
            if solution.functionSolution.count() > 0 or solution.variableSolution.count():
                solutions.append(solution)
            
        solutions.sort(cmp=None, key=lambda sol: sol.functionName.lower())
        self.clearWidget(self.solutionSelector)
        selectedRow = self.solutionWidget.currentRow()
        self.solutionWidget.clear()
        for solution in solutions:
            item = QListWidgetItem()
            item.setText(solution.functionName)
            self.solutionWidget.addItem(item)
            
        if self.solutionWidget.count() > 0:
            self.solutionWidget.setCurrentRow(selectedRow if selectedRow >= 0 and selectedRow < self.solutionWidget.count() else 0)
        self.statusBar().showMessage("Updated!", 5000)

    def loadInitialData(self):
        self.solutions = dict()
        for filename in dircache.listdir(self.dataDir):
            functionName = self.getFunctionName(filename)
            filename = self.dataDir + "/" + filename
            
            if functionName in self.solutions:
                function = self.solutions[functionName]
            else:
                function = MOSolution(functionName)
                self.solutions[functionName] = function
                
            if self.isFunctionFile(filename):
                function.setFunctionPareto(filename)
            else:
                function.setVariablePareto(filename)
        
        self.scanDirectory()
        if self.solutionWidget.count() > 0:
            self.statusBar().showMessage("Ready!", 5000)
        else:
            self.statusBar().showMessage("WARNING: No Pareto front files found.")
            
    def closeEvent(self, event):
        self.statusBar().showMessage("Closing...")
        settings = QSettings()
        settings.setValue("UI/Geometry", self.saveGeometry())
        settings.setValue("UI/State", self.saveState())
        self.plot.clear()
        
def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Centro de Investigacion y de Estudios Avanzados del Instituto Politecnico Nacional (CINVESTAV-IPN)")
    app.setOrganizationDomain("cs.cinvestav.mx")
    app.setApplicationName("MOOI: Multi-Objective Optimization Interface")
    #app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()
