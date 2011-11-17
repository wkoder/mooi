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

__VERSION__ = "1.0.0"
__PARETO__ = "pareto"

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
        
        self.plot = PlotWidget()
        self.plot.setMinimumSize(320, 480)
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
        self.solutionSelector.setLayout(QVBoxLayout())
        addSolutionButton = QPushButton("Add")
        addSolutionButton.clicked.connect(self.addImplementation)
        removeSolutionButton = QPushButton("Remove")
        removeSolutionButton.clicked.connect(self.removeImplementation)
        solutionSelectorButtons = QWidget()
        solutionSelectorButtons.setLayout(QHBoxLayout())
        solutionSelectorButtons.layout().addWidget(addSolutionButton)
        solutionSelectorButtons.layout().addWidget(removeSolutionButton)
        self.solutionSelectorWidget = QWidget()
        self.solutionSelectorWidget.setLayout(QVBoxLayout())
        self.solutionSelectorWidget.layout().addWidget(solutionSelectorButtons)
        self.solutionSelectorWidget.layout().addWidget(self.solutionSelector)
        
        exportButton = QPushButton("Export image")
        exportButton.clicked.connect(self.exportImage)
        
        exportAllButton = QPushButton("Export all images")
        exportAllButton.clicked.connect(self.exportAllImages)
        
        refreshButton = QPushButton("Refresh")
        refreshButton.clicked.connect(self.scanAllDirectories)
        
        controlLayout = QVBoxLayout()
        controlLayout.addWidget(radioWidget)
        controlLayout.addWidget(self.generationLabel)
        controlLayout.addWidget(self.generationSlider)
        controlLayout.addWidget(self.solutionSelectorWidget)
        controlLayout.addStretch()
        controlLayout.addWidget(refreshButton)
        controlLayout.addWidget(exportButton)
        controlLayout.addWidget(exportAllButton)
        controlWidget = QWidget()
        controlWidget.setLayout(controlLayout)
        controlDock = QDockWidget("Control", self)
        controlDock.setObjectName("Control")
        controlDock.setWidget(controlWidget)
        controlDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, controlDock)
        
        self.currentSolution = None
        self.implementationDirectories = []

        settings = QSettings()
        self.restoreState(settings.value("UI/State").toByteArray())
        self.restoreGeometry(settings.value("UI/Geometry").toByteArray())
        currentDirs = settings.value("Config/Directories")
        if currentDirs is not None:
            for directory in currentDirs.toList():
                self.implementationDirectories.append(directory.toString())
        
        paretoDirectory = os.path.dirname(__file__) + "/" + __PARETO__
        if not paretoDirectory in self.implementationDirectories and \
            not __PARETO__ in map(self.getImplementationName, self.implementationDirectories):
            self.implementationDirectories.insert(0, paretoDirectory)
        
        QTimer.singleShot(0, self.loadInitialData)

    def shortenName(self, name, maxlen):
        if len(name) <= maxlen:
            return name
        return "..." + name[3 - maxlen:]

    def exportImage(self):
        settings = QSettings()
        filename = settings.value("Config/SaveDirectory").toString()
        filename = QFileDialog.getSaveFileName(self, "Export image as", filename, ("PNG image (*.png)"))
        if filename is None or filename == "":
            return

        settings.setValue("Config/SaveDirectory", QVariant(filename))
        self._exportCurrentImage(filename)
        self.statusBar().showMessage("Image saved!", 5000)
    
    def _exportCurrentImage(self, filename=None):
        generation = self.generationSlider.value()
        self.generationLabel.setText("Generation: %d" % generation)
        self._exportToImage(self.currentSolution, generation, filename)
    
    def exportAllImages(self):
        settings = QSettings()
        directory = settings.value("Config/SaveAllDirectory").toString()
        directory = QFileDialog.getExistingDirectory(self, "Select a directory to export to", directory)
        if directory is None or not os.path.exists(directory):
            return

        settings.setValue("Config/SaveAllDirectory", QVariant(directory))
#        for solutionName in self.solutions.keys():
        for i in xrange(self.solutionWidget.count()):
            solutionName = str(self.solutionWidget.item(i).text())
            filename = directory + "/" + solutionName + ".png"
            self._exportToImage(self.solutions[solutionName], 0, filename)
        self.statusBar().showMessage("Images saved!", 5000)
    
    def _exportToImage(self, solution, generation, filename):
        toPlot = self._getSolutionsToPlot(solution, generation)
        if self.showSolutionsRadio.isChecked():
            self.plot.plotSolution(toPlot, self.currentSolution.functionName, "F1", "F2", "F3", filename)
        else:
            self.plot.plotSolution(toPlot, self.currentSolution.functionName, "x1", "x2", "x3", filename)
                
    def helpAbout(self):
        QMessageBox.about(self, "About Image Changer",
            """<b>Multi-Objective Optimization Interface</b> v%s
            <p>Copyright &copy; 2011 CINVESTAV-IPN
            All rights reserved.
            <p>This application can be used to perform
            simple optimization analysis.
            <p>Python %s - Qt %s - PyQt %s on %s""" % 
            (__VERSION__, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def addImplementation(self):
        directory = None if len(self.implementationDirectories) == 0 else self.implementationDirectories[-1]
        directory = QFileDialog.getExistingDirectory(self, "Select a directory to scan", directory)
        if not os.path.exists(directory) or directory in self.implementationDirectories:
            return
        
        self.implementationDirectories.append(directory)
        self.addSolutionForSelection(self.getImplementationName(directory))
        settings = QSettings()
        settings.setValue("Config/Directories", QVariant(self.implementationDirectories))
        QTimer.singleShot(0, self.scanDirectory)
        
    def removeImplementation(self):
        layout = self.solutionSelector.layout()
        for i in xrange(layout.count()-1, -1, -1):
            if layout.itemAt(i).widget().isChecked():
                layout.removeItem(layout.itemAt(i))
                del self.implementationDirectories[i]
                
        settings = QSettings()
        settings.setValue("Config/Directories", QVariant(self.implementationDirectories))
        
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
        
    def getImplementationName(self, directory):
        directory = str(directory)
        slash = max(directory.rfind("/"), directory.rfind("\\"))
        return directory[slash+1:]
    
    def addSolutionForSelection(self, name):
        solution = QCheckBox(name)
        solution.setChecked(True)
        solution.stateChanged.connect(self._showSolution)
        self.solutionSelector.layout().addWidget(solution)
        self.solutionSelector.layout().update()
            
    def _updateSolutionSelection(self):
        self.clearWidget(self.solutionSelector)
        
        for directory in self.implementationDirectories:
            self.addSolutionForSelection(self.getImplementationName(directory))
        
    def _showSolution(self):
        sol = self.currentSolution
        if sol is None:
            return
        
        if len(sol.variableImplementation) == 0 and self.showVariablesRadio.isEnabled():
            self.showVariablesRadio.setEnabled(False)
            if self.showVariablesRadio.isChecked():
                self.showSolutionsRadio.setChecked(True)
        else:
            self.showVariablesRadio.setEnabled(True)
        
        if len(sol.functionImplementation) == 0 and self.showSolutionsRadio.isEnabled():
            self.showSolutionsRadio.setEnabled(False)
            if self.showSolutionsRadio.isChecked():
                self.showVariablesRadio.setChecked(True)
        else:
            self.showSolutionsRadio.setEnabled(True)
        
#        if self.showSolutionsRadio.isChecked():
#            self.generationSlider.setMaximum(sol.functionImplementation.count())
#        else:
#            self.generationSlider.setMaximum(sol.variableImplementation.count())
        self._exportCurrentImage()
        
    def _getSolutionsToPlot(self, sol, generation):
        solutions = {}
        for i in xrange(0, self.solutionSelector.layout().count()):
            implementationItem = self.solutionSelector.layout().itemAt(i).widget()
            if implementationItem.isChecked():
                solution = None
                name = str(implementationItem.text())
                if self.showSolutionsRadio.isChecked():
                    solution = sol.getFunctionSolution(name)
                else:
                    solution = sol.getVariableSolution(name)
                if solution is not None:
                    rgb = 3*[0]
                    k = i + 1
                    for p in xrange(3):
                        if k & (1 << p) > 0:
                            rgb[p] = 255
                    solutions[name] = [solution.getSolutions()[generation-1], rgb]
            
        return solutions
            
    def isSolutionFile(self, filename):
        if not os.path.exists(filename) or os.path.isdir(filename):
            return False
        
        f = open(filename)
        try:
            tries = 5 # Try 5 times to check if the file is valid
            lastlen = -1
            for line in f:
                points = [float(x) for x in line.split()]
                if lastlen != -1 and len(points) != lastlen:
                    return False
                
                lastlen = len(points)
                tries = tries - 1
                if tries == 0:
                    break
                
            return lastlen >= 2
        except Exception:
            return False
        finally:
            f.close()
            
    def scanDirectory(self):
        if len(self.implementationDirectories) > 0:
            self._scanDirectories([self.implementationDirectories[-1]])
    
    def scanAllDirectories(self):
        self._scanDirectories(self.implementationDirectories)
    
    def _scanDirectories(self, directories):
#        for function in self.solutions.values():
#            if function.functionPareto is None and function.variablePareto is None:
#                del self.solutions[function.functionName]
#            else:
#            function.clear()
                
        for directory in directories:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                continue
            
            implementationName = self.getImplementationName(directory)
            for filename in dircache.listdir(directory):
                filename = str(directory + "/" + filename)
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
                    function.addFunctionSolution(implementationName, filename, generation)
                else:
                    function.addVariableSolution(implementationName, filename, generation)
            
        self.updateUI()
        
    def getFunctionName(self, filename):
        filename = filename[filename.rfind("/")+1:]
        if "." in filename:
            filename = filename[:filename.rfind(".")]
        return filename.lower().replace("_fun", "").replace("_var", "").replace("fun", "").replace("var", "")\
            .replace("front_", "").replace("pareto_", "").replace("pf_", "").replace("_pf", "").replace("_front", "")\
            .replace("_pareto", "").replace("front", "").replace("pareto", "").title()
        
    def isFunctionFile(self, filename):
        return "var" not in filename.lower()
    
    def clearWidget(self, widget):
        layout = widget.layout()
        for i in xrange(layout.count()-1, -1, -1):
            layout.removeItem(layout.itemAt(i))
    
    def _hasNonPareto(self, implementations):
        if len(implementations) > 1:
            return True
        if len(implementations) == 0:
            return False
        return __PARETO__ not in implementations.keys()
    
    def updateUI(self):
        self.statusBar().showMessage("Updating solutions...")
                
        solutions = []
        for solution in self.solutions.values():
            if self._hasNonPareto(solution.functionImplementation) or self._hasNonPareto(solution.variableImplementation):
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
        self.solutions = {}
        self.scanAllDirectories()
        self.statusBar().showMessage("Ready!", 5000)
            
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
