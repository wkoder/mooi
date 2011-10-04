'''
Created on Oct 3, 2011

@author: Moises Osorio [WCoder]
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PlotWidget import PlotWidget
__version__ = "1.0.0"

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.mirroredvertically = False
        self.mirroredhorizontally = False
        self.resize(640, 480)
        
        self.plot = PlotWidget()
        self.plot.setMinimumSize(640, 480)
        self.plot.setMaximumSize(640, 480)
        self.plot.setAlignment(Qt.AlignCenter)
        self.plot.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.plot)
        
#        logDockWidget = QDockWidget("Log", self)
#        logDockWidget.setObjectName("LogDockWidget")
#        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
#        self.listWidget = QListWidget()
#        logDockWidget.setWidget(self.listWidget)
        
#        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidget)
        self.printer = None
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)
        
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
        self.recentFiles = settings.value("RecentFiles").toStringList()
        self.restoreGeometry(settings.value("Geometry").toByteArray())
        self.restoreState(settings.value("MainWindow/State").toByteArray())
        self.setWindowTitle("MOOI: Multi-Objective Optimization Interface")

        QTimer.singleShot(0, self.loadInitialFile)

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

    def loadInitialFile(self):
        self.plot.plotFile("data/Deb1fun.dat")
        