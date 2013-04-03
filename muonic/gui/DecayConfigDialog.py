
from PyQt4 import QtCore, QtGui

class DecayConfigDialog(QtGui.QDialog):
    
    
    
    def __init__(self, *args):

        QtGui.QDialog.__init__(self,*args)

        # size of window etc..
        self.setObjectName("Configure")
        self.resize(480, 360)
        self.setModal(True)
        self.setWindowTitle("Muon Decay Configuration")  

        # the 'ok' and 'cancel' buttons
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(80, 300, 300, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        grid = QtGui.QGridLayout()
        grid.addWidget(self.createGroupBox(label="Single Pulse",objectname = "singlecheckbox",leftoffset=20,checkitem=1), 0, 0)
        grid.addWidget(self.createGroupBox(label="Double Pulse",objectname = "doublecheckbox",leftoffset=180,checkitem=2), 1, 0)
        grid.addWidget(self.createGroupBox(label="Veto Pulse",objectname = "vetocheckbox",leftoffset=300,checkitem=3), 0, 1)
        self.strict = QtGui.QCheckBox(self)
        self.strict.setChecked(False)
        self.strict.setGeometry(QtCore.QRect(20, 300, 119, 28))
        self.strict.setText("Do strictly what I say!")
        grid.addWidget(self.strict)
        self.setLayout(grid)


        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()


    def createGroupBox(self,label="Single Pulse",objectname="singlecheckbox",leftoffset=20,checkitem=None):

        # activate Channels with Checkboxes
        groupBox = QtGui.QGroupBox(label)
        groupBox.setCheckable(False)


        Chan0 = QtGui.QRadioButton(self)
        Chan0.setGeometry(QtCore.QRect(leftoffset, 40, 119, 28))
        Chan0.setObjectName(objectname + "_0")
        Chan0.setText("Chan0")
        Chan1 = QtGui.QRadioButton(self)
        Chan1.setGeometry(QtCore.QRect(leftoffset, 80, 119, 28))
        Chan1.setObjectName(objectname + "_1")
        Chan1.setText("Chan1")
        Chan2 = QtGui.QRadioButton(self)
        Chan2.setGeometry(QtCore.QRect(leftoffset, 130, 119, 28))
        Chan2.setObjectName(objectname + "_2")
        Chan2.setText("Chan2")
        Chan3 = QtGui.QRadioButton(self)
        Chan3.setGeometry(QtCore.QRect(leftoffset, 180, 119, 28))
        Chan3.setObjectName(objectname + "_3")
        Chan3.setText("Chan3")
        for channel in enumerate([Chan0,Chan1,Chan2,Chan3]):
            if checkitem == channel[0]:
                channel[1].setChecked(True)

                    

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(Chan0)
        vbox.addWidget(Chan1)
        vbox.addWidget(Chan2)
        vbox.addWidget(Chan3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        return groupBox


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    Dialog = DecayConfigDialog()
    sys.exit(app.exec_())

