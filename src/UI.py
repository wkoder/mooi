'''
Created on Oct 3, 2011

@author: Moises Osorio [WCoder]
'''
from Analyzer import Analyzer
from MetricsPanel import MetricsPanel
from PlotWidget import PlotWidget
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import os
import platform
import sys
import tempfile

__VERSION__ = "1.0.0"
__WEBSITE__ = "http://mooi.wkoder.com"
__AUTHOR__ = "Moises Osorio"

class MainWindow(QMainWindow):
    
    __PREF_GEOM__ = "UI/Geometry"
    __PREF_STATE__ = "UI/State"
    __PREF_DIR__ = "Config/Directories"
    __PREF_SAVE__ = "Config/SaveDirectory"
    
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
        
        self.functionWidget = QListWidget()
        self.functionWidget.itemSelectionChanged.connect(self.solutionSelected)
        rightDock = QDockWidget("Functions", self)
        rightDock.setObjectName("Functions")
        rightDock.setWidget(self.functionWidget)
        rightDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, rightDock)
        
        self.showSolutionsRadio = QRadioButton("Functions")
        self.showSolutionsRadio.setChecked(True)
        self.showSolutionsRadio.toggled.connect(self._showSolution)
        self.showVariablesRadio = QRadioButton("Variables")
        
        radioWidget = QWidget()
        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.showSolutionsRadio)
        radioLayout.addWidget(self.showVariablesRadio)
        radioWidget.setLayout(radioLayout)
        
        self.generationLabel = QLabel("Run: 1")
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
        removeSolutionButton = QPushButton("Remove unselected")
        removeSolutionButton.clicked.connect(self.removeResult)
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
        
        computeMetricsButton = QPushButton("Compute metrics")
        computeMetricsButton.clicked.connect(self.computeMetricsAsync)
        
        refreshButton = QPushButton("Refresh")
        refreshButton.clicked.connect(self.updateUI)
        
        controlLayout = QVBoxLayout()
        controlLayout.addWidget(radioWidget)
        controlLayout.addWidget(self.generationLabel)
        controlLayout.addWidget(self.generationSlider)
        controlLayout.addWidget(self.solutionSelectorWidget)
        controlLayout.addStretch()
        controlLayout.addWidget(computeMetricsButton)
        controlLayout.addWidget(refreshButton)
        controlLayout.addWidget(exportButton)
        controlLayout.addWidget(exportAllButton)
        controlWidget = QWidget()
        controlWidget.setLayout(controlLayout)
        leftDock = QDockWidget("Control", self)
        leftDock.setObjectName("Control")
        leftDock.setWidget(controlWidget)
        leftDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, leftDock)
        
        self.metrics = MetricsPanel()
        bottomDock = QDockWidget("Metrics", self)
        bottomDock.setObjectName("Metrics")
        bottomDock.setWidget(self.metrics)
        bottomDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottomDock)
        
        exitAction = QAction('&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        
        copyAction = QAction("&Copy",  self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.setStatusTip('Copy metrics')
        copyAction.triggered.connect(self.metrics.copyMetrics)
        
        aboutAction = QAction("&About",  self)
        aboutAction.setStatusTip('About MOOI')
        aboutAction.triggered.connect(self.helpAbout)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(copyAction)
        fileMenu.addAction(aboutAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        
        self.currentSolution = None

        settings = QSettings()
        self.restoreState(settings.value(MainWindow.__PREF_STATE__).toByteArray())
        self.restoreGeometry(settings.value(MainWindow.__PREF_GEOM__).toByteArray())

        self.analyzer = Analyzer()
        paretoDirectory = os.path.dirname(__file__) + "/../resources/" + Analyzer.__PARETO__
        self.analyzer.setPareto(paretoDirectory)
        currentDirs = settings.value(MainWindow.__PREF_DIR__)
        if currentDirs is not None:
            self.analyzer.setResultDirectories([directory.toString() for directory in currentDirs.toList()])
            
        self._updateSolutionSelection()
        QTimer.singleShot(0, self.loadInitialData)
        
    def exportImage(self):
        settings = QSettings()
        filename = settings.value(MainWindow.__PREF_SAVE__)
        if filename is None:
            filename = os.path.dirname(__file__)
        else:
            filename = os.path.abspath(os.path.join(str(filename.toString()), os.path.pardir)) + "/"
        filename += "%s_%s.png" % (self.currentSolution.functionName, "fun" if self.isFunctionSpaceSelected() else "var")
        
        filename = QFileDialog.getSaveFileName(self, "Export image as", filename, ("PNG image (*.png)"))
        if filename is None or filename == "":
            return

        settings.setValue(MainWindow.__PREF_SAVE__, QVariant(filename))
        self._exportCurrentImage(filename)
        self.statusBar().showMessage("Image saved!", 5000)
    
    def isFunctionSpaceSelected(self):
        return self.showSolutionsRadio.isChecked()
    
    def _exportCurrentImage(self, filename=None):
        generation = self.generationSlider.value()
        self.generationLabel.setText("Run: %d" % generation)
        
        tmp = filename is None
        if tmp:
            prefix = "mooi_%s_" % self.currentSolution.functionName
            filename = tempfile.mkstemp(prefix=prefix, suffix=".png", text=False)[1]
        self.analyzer.exportToImage(self.currentSolution, generation, self.isFunctionSpaceSelected(), \
                                    self._getSelectedResultNames(), filename)
        if tmp:
            self.plot.setPlotPixmap(filename)
            try:
                os.remove(filename)
            except:
                print >> sys.stderr, "Couldn't delete temporal file: %s" % filename
    
    def _getSelectedResultNames(self):
        resultNames = []
        for i in xrange(self.analyzer.nResults):
            implementationItem = self.solutionSelector.layout().itemAt(i).widget()
            if implementationItem.isChecked():
                resultNames.append(str(implementationItem.text()))
        return resultNames
    
    def exportAllImages(self):
        settings = QSettings()
        directory = settings.value("Config/SaveAllDirectory").toString()
        directory = QFileDialog.getExistingDirectory(self, "Select a directory to export to", directory)
        if directory is None or not os.path.exists(directory):
            return

        self.analyzer.exportAllImages(directory, self._getSelectedResultNames())
        settings.setValue("Config/SaveAllDirectory", QVariant(directory))
        self.statusBar().showMessage("Images saved!", 5000)
    
    def computeMetricsAsync(self):
        self.statusBar().showMessage("Computing metrics...")
        QTimer.singleShot(0, self.computeMetrics)
        
    def computeMetrics(self):
        self._computeMetrics(self.currentSolution.functionName)
        self.statusBar().showMessage("Metrics computed!", 5000)
        
    def _computeMetrics(self, functionName):
        pareto = self.analyzer.getFunctionPareto(functionName)
        solutions = self.analyzer.getFunctionResults(functionName, self._getSelectedResultNames())
        self.metrics.updateMetrics(pareto, solutions)
        
    def helpAbout(self):
        QMessageBox.about(self, "About Image Changer",
            """<b>Multi-Objective Optimization Interface</b> v%s
            <p>Copyright &copy; 2011-2012 %s All rights reserved.
            <p>This application can be used to perform simple optimization analysis.
            <p><a href='%s'>%s</a>
            <p>Python %s - Qt %s - PyQt %s on %s""" % 
            (__VERSION__, __AUTHOR__, __WEBSITE__, __WEBSITE__, platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def addImplementation(self):
        if self.analyzer.nResults == 0:
            directory = ""
        else:
            directory = os.path.abspath(os.path.join(str(self.analyzer.resultDirectories[-1]), os.path.pardir))
        directory = QFileDialog.getExistingDirectory(self, "Select a directory to scan", directory, QFileDialog.ShowDirsOnly)
        if not os.path.exists(directory) or directory in self.analyzer.resultDirectories:
            return
        
        self.analyzer.addResultDirectory(directory)
        self.addSolutionForSelection(self.analyzer.getResultName(directory))

        settings = QSettings()
        settings.setValue(MainWindow.__PREF_DIR__, QVariant(self.analyzer.resultDirectories))
        
    def removeResult(self):
        layout = self.solutionSelector.layout()
        for i in xrange(layout.count()-1, -1, -1):
            item = layout.itemAt(i)
            if not item.widget().isChecked():# and self.analyzer.resultNames[i] != Analyzer.__PARETO__:
                item.widget().setVisible(False)
                layout.removeItem(item)
                self.analyzer.removeResultDirectory(self.analyzer.resultDirectories[i])
        layout.update()
                
        settings = QSettings()
        settings.setValue(MainWindow.__PREF_DIR__, QVariant(self.analyzer.resultDirectories))
        
    def solutionSelected(self):
        selection = self.functionWidget.currentItem()
        if selection is None:
            return
        self.showSolution(str(selection.text()))
        
    def showSolution(self, functionName):
        self.currentSolution = self.analyzer.getResultsForFunction(functionName)
        self.metrics.clear()
        self._showSolution()
        
    def addSolutionForSelection(self, name):
        solution = QCheckBox(name)
        solution.setChecked(True)
        solution.stateChanged.connect(self._showSolution)
        self.solutionSelector.layout().addWidget(solution)
        self.solutionSelector.layout().update()
            
    def _updateSolutionSelection(self):
        self.clearWidget(self.solutionSelector)
        
        for directory in self.analyzer.resultDirectories:
            self.addSolutionForSelection(self.analyzer.getResultName(directory))
        
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
        
        if self.showSolutionsRadio.isChecked():
            self.generationSlider.setMaximum(max([sol.getFunctionSolution(impl).count() for impl in sol.functionImplementation]))
        else:
            self.generationSlider.setMaximum(max([sol.getVariableSolution(impl).count() for impl in sol.variableImplementation]))
        self._exportCurrentImage()
      
    def clearWidget(self, widget):
        layout = widget.layout()
        for i in xrange(layout.count()-1, -1, -1):
            layout.removeItem(layout.itemAt(i))
    
    def updateUI(self):
        self.statusBar().showMessage("Updating solutions...")
                
        selectedRow = self.functionWidget.currentRow()
        self.functionWidget.clear()
        names = [] + self.analyzer.getFunctionNames()
        names.sort()
        for name in names:
            item = QListWidgetItem()
            item.setText(name)
            self.functionWidget.addItem(item)
            
        if self.functionWidget.count() > 0:
            self.functionWidget.setCurrentRow(selectedRow if selectedRow >= 0 and selectedRow < self.functionWidget.count() else 0)
        self.statusBar().showMessage("Updated!", 5000)

    def loadInitialData(self):
        self.updateUI()
        self.statusBar().showMessage("Ready!", 5000)
            
    def closeEvent(self, event):
        self.statusBar().showMessage("Closing...")
        settings = QSettings()
        settings.setValue(MainWindow.__PREF_GEOM__, self.saveGeometry())
        settings.setValue(MainWindow.__PREF_STATE__, self.saveState())
        self.plot.clear()
        
def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Centro de Investigacion y de Estudios Avanzados del Instituto Politecnico Nacional (CINVESTAV-IPN)")
    app.setOrganizationDomain("cs.cinvestav.mx")
    app.setApplicationName("MOOI: Multi-Objective Optimization Interface")
    app.setWindowIcon(QIcon(os.path.dirname(__file__) + "/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()
