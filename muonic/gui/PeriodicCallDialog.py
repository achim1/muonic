#! /usr/bin/env python


from PyQt4 import QtGui
from PyQt4 import QtCore

class PeriodicCallDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self,*args)
        self.setModal(True)
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QLineEdit()
        self.time_box = QtGui.QSpinBox()
        self.time_box.setMaximum(600)
        self.time_box.setMinimum(1)
        self.time_box.setSingleStep(1)
        self.command_label = QtGui.QLabel("Command")
        self.interval_label = QtGui.QLabel("Interval")
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.command_label)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.interval_label)
        self.v_box.addWidget(self.time_box)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('rejected()'),
                              self.reject)
        windowtitle = QtCore.QString("PeridicCall")
 
        self.setWindowTitle(windowtitle)
        self.show()

if __name__ == "__main__":

    # self test section

    import sys
    app = QtGui.QApplication(sys.argv)
    tdialog = PeriodicCallDialog()
    sys.exit(app.exec_())

    
# vim: ai ts=4 sts=4 et sw=4
