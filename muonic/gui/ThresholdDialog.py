#! /usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore


class ThresholdDialog(QtGui.QDialog):

    def __init__(self,thr0,thr1,thr2,thr3, *args):

        QtGui.QDialog.__init__(self,*args)

        dimension = QtCore.QSize()

        #self.resize(260, 260)
        self.resize(dimension)     
        self.setModal(True)

        self.v_box = QtGui.QVBoxLayout()

        self.ch0_input = QtGui.QLineEdit()
        self.ch1_input = QtGui.QLineEdit()
        self.ch2_input = QtGui.QLineEdit()
        self.ch3_input = QtGui.QLineEdit()
        self.label0 = QtGui.QLabel("Chan0: %s" %thr0)
        self.label1 = QtGui.QLabel("Chan1: %s" %thr1)
        self.label2 = QtGui.QLabel("Chan2: %s" %thr2)
        self.label3 = QtGui.QLabel("Chan3: %s" %thr3)

        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.label0)
        self.v_box.addWidget(self.ch0_input)
        self.v_box.addWidget(self.label1)
        self.v_box.addWidget(self.ch1_input)
        self.v_box.addWidget(self.label2)
        self.v_box.addWidget(self.ch2_input)
        self.v_box.addWidget(self.label3)
        self.v_box.addWidget(self.ch3_input)
        self.v_box.addWidget(self.button_box)

        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )

        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('rejected()'),
                              self.reject)

        windowtitle = QtCore.QString("Threshold Settings")
        
        self.setWindowTitle(windowtitle)
        self.adjustSize()
        self.show()

if __name__ == "__main__":

    # self test section

    import sys
    app = QtGui.QApplication(sys.argv)
    tdialog = ThresholdDialog("100","100","100","100")
    sys.exit(app.exec_())

