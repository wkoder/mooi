#   This file is part of Gnupylot.
#
#    Gnupylot is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Gnupylot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Gnupylot; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
Created on 16/gen/2010

@author: Lorenzo Rovigatti
'''

from PyQt4 import QtCore, QtGui

try:
    import Gnuplot.termdefs as termdefs
except ImportError:
    import src.Gnuplot.termdefs as termdefs

TERMS_CONFIG = {
                'png' : {
                         'filter' : 'png files(*.png)',
                         'selectedFilter' : '*.png'
                         },
                'postscript' : {
                                'filter' : 'PostScript files(*.ps);;Encapsulated PostScript files(*.eps)',
                                'selectedFilter' : '*.ps'
                                },
                }

class ExportPlot(QtGui.QDialog):
    def __init__(self, terminal):
        QtGui.QDialog.__init__(self)
        self.terminal = terminal
        try:
            self.opts = termdefs.terminal_opts[terminal]
        except KeyError:
            self.critical("Terminal '" + terminal + "' doesn't exist in termdefs.py")
        
#        try:
#            self.filewidget = ChooseFileWidget(self, TERMS_CONFIG[terminal]['filter'], 
#                                               TERMS_CONFIG[terminal]['selectedFilter'],
#                                               "Choose destination file")
#        except KeyError:
#            self.critical("Terminal '" + terminal + "' not yet implemented")
        
        self.setWindowTitle("Export plot as " + terminal)
        self.formlayout = QtGui.QFormLayout(self)
#        self.formlayout.addRow("&File", self.filewidget)
        
        self.populateForm()
        self.addButtons()

        self.setFixedSize(self.sizeHint())
        
    def populateForm(self):
        """
        Populate the dialog with the widgets that will let the user choose the various
        options accessible for the right terminal.
        """
        self.optWidgets = []
        for opt in self.opts:
            if opt.__class__.__name__ == 'KeywordOrBooleanArg':
                self.optWidgets.append(QtGui.QComboBox(self))
                self.optWidgets[-1].setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed))
                self.optWidgets[-1].addItems(opt.options)
                # let's forward the currentText method of this combobox so we can use a unified
                # way to access selected data
                self.optWidgets[-1].text = self.optWidgets[-1].currentText 
                if opt.default != None:
                    self.optWidgets[-1].setCurrentIndex(self.optWidgets[-1].findText(opt.default))
            elif opt.__class__.__name__ == 'BareStringArg' or opt.__class__.__name__ == 'StringArg':
                self.optWidgets.append(QtGui.QLineEdit(self))
                if opt.default != None: self.optWidgets[-1].setText(opt.default)
            else:
                self.critical("Terminal argument '" + opt.__class__.__name__ + "' not supported")
                
            if opt.argname != None:
                self.formlayout.addRow(opt.argname, self.optWidgets[-1])
            else: self.formlayout.addRow('', self.optWidgets[-1])

    def addButtons(self):
        okbutton = QtGui.QPushButton("Export", self)
        okbutton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        self.connect(okbutton, QtCore.SIGNAL("clicked()"), self.export)
        cancelbutton = QtGui.QPushButton("Cancel", self)
        cancelbutton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        self.connect(cancelbutton, QtCore.SIGNAL("clicked()"), self.reject)
        
        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        hbox.addWidget(okbutton)
        hbox.addWidget(cancelbutton)
        self.formlayout.addRow(hbox)
        
    def getKeyw(self):
        """
        Returns a dictionary that can be used as the **keyw argument in the Gnuplot.hardcopy method.
        """
        keyw = {}
        keyw['filename'] = self.filewidget.getFilename()
        keyw['terminal'] = self.terminal
        for opt in self.optWidgets:
            text = str(opt.text())
            # if opt has an associated label use its text as the key for
            # the current argument
            label = self.formlayout.labelForField(opt)
            if label == None: keyw[text] = '1'
            else: keyw[str(label.text()).strip()] = text
            
        return keyw
            
        
    def export(self):
        filename = self.filewidget.getFilename()
        if len(filename) == 0:
            QtGui.QMessageBox.warning(self, "Empty filename", "Please select the output file for your plot")
            return
        
        self.accept()
        
    def critical(self, msg):
        QtGui.QMessageBox.critical(self, "Error", msg)
        self.reject()
        return
