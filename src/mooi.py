'''
Created on Oct 3, 2011

@author: Moises Osorio [WCoder]
'''

import sys
from PyQt4 import QtGui
from MainWindow import MainWindow

def main():
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("Centro de Investigacion y de Estudios Avanzados del Instituto Politecnico Nacional (CINVESTAV-IPN)")
    app.setOrganizationDomain("cs.cinvestav.mx")
    app.setApplicationName("MOOI: Multi-Objective Optimization Interface")
    app.setWindowIcon(QtGui.QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    