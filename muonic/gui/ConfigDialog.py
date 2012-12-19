
from PyQt4 import QtCore, QtGui

class ConfigDialog(QtGui.QDialog):
    def __init__(self, *args):

        QtGui.QDialog.__init__(self,*args)

        # size of window etc..
        self.setObjectName("Configure")
        self.resize(520, 360)
        self.setModal(True)
        self.setWindowTitle("Channel Configuration")  

        # the 'ok' and 'cancel' buttons
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 300, 300, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        # select the coincidences with Radio Buttons
        # group them in a vertical box, so that they do not
        # collide with the veto radio buttons
        self.vlcoincWid = QtGui.QWidget(self)
        self.vlcoincWid.setGeometry(QtCore.QRect(200, 40, 150, 120))
        self.vlcoincWid.setObjectName("verticalLayoutWidget")
        self.vlcoinc = QtGui.QVBoxLayout(self.vlcoincWid)
        self.vlcoinc.setMargin(0)
        self.vlcoinc.setObjectName("verticalLayout")

        self.coincidenceSingles = QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceSingles.setGeometry(QtCore.QRect(210, 50, 145, 28))
        self.coincidenceSingles.setObjectName("radioButton")
        self.coincidenceSingles.setText("Single")
        self.vlcoinc.addWidget(self.coincidenceSingles)

        self.coincidenceTwofold = QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceTwofold.setGeometry(QtCore.QRect(210, 90, 145, 28))
        self.coincidenceTwofold.setObjectName("radioButton_2")
        self.coincidenceTwofold.setText("Twofold")
        self.vlcoinc.addWidget(self.coincidenceTwofold)

        self.coincidenceThreefold = QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceThreefold.setGeometry(QtCore.QRect(210, 140, 145, 28))
        self.coincidenceThreefold.setObjectName("radioButton_3")
        self.coincidenceThreefold.setText("Threefold")
        self.vlcoinc.addWidget(self.coincidenceThreefold)

        self.coincidenceFourfold= QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceFourfold.setGeometry(QtCore.QRect(210, 180, 145, 28))
        self.coincidenceFourfold.setObjectName("radioButton_4")
        self.coincidenceFourfold.setText("Fourfould")
        self.vlcoinc.addWidget(self.coincidenceFourfold)

        # set Veto with RadioButtons
        self.noveto = QtGui.QRadioButton(self)
        self.noveto.setGeometry(QtCore.QRect(410, 50, 145, 28))
        self.noveto.setObjectName("radioButton_5")
        self.noveto.setText("None")
        self.vetochan1 = QtGui.QRadioButton(self)
        self.vetochan1.setGeometry(QtCore.QRect(410, 90, 145, 28))
        self.vetochan1.setObjectName("radioButton_7")
        self.vetochan1.setText("Chan1")
        self.vetochan2 = QtGui.QRadioButton(self)
        self.vetochan2.setGeometry(QtCore.QRect(410, 140, 145, 28))
        self.vetochan2.setObjectName("radioButton_8")
        self.vetochan2.setText("Chan2")
        self.vetochan3 = QtGui.QRadioButton(self)
        self.vetochan3.setGeometry(QtCore.QRect(410, 180, 145, 28))
        self.vetochan3.setObjectName("radioButton_9")
        self.vetochan3.setText("Chan3")

        # activate Channels with Checkboxes
        self.activateChan0 = QtGui.QCheckBox(self)
        self.activateChan0.setGeometry(QtCore.QRect(20, 40, 119, 28))
        self.activateChan0.setObjectName("checkBox")
        self.activateChan0.setText("Chan0")
        self.activateChan1 = QtGui.QCheckBox(self)
        self.activateChan1.setGeometry(QtCore.QRect(20, 80, 119, 28))
        self.activateChan1.setObjectName("checkBox_2")
        self.activateChan1.setText("Chan1")
        self.activateChan2 = QtGui.QCheckBox(self)
        self.activateChan2.setGeometry(QtCore.QRect(20, 130, 119, 28))
        self.activateChan2.setObjectName("checkBox_3")
        self.activateChan2.setText("Chan2")
        self.activateChan3 = QtGui.QCheckBox(self)
        self.activateChan3.setGeometry(QtCore.QRect(20, 180, 119, 28))
        self.activateChan3.setObjectName("checkBox_4")
        self.activateChan3.setText("Chan3")

        # three labels, one for the radio buttons, and one for the checkboxes, the last one for veto criterion
        self.labelChannel = QtGui.QLabel(self)
        self.labelChannel.setText("Use Channel")
        self.labelChannel.setGeometry(QtCore.QRect(30, 10, 121, 23))
        self.labelChannel.setObjectName("channellabel")

        self.labelCoincidence = QtGui.QLabel(self)
        self.labelCoincidence.setGeometry(QtCore.QRect(210, 10, 121, 23))
        self.labelCoincidence.setObjectName("coincidencelabel")

        self.labelVeto = QtGui.QLabel(self)
        self.labelVeto.setGeometry(QtCore.QRect(410, 10, 121, 23))
        self.labelVeto.setObjectName("vetolabel")

        self.labelCoincidence.setText("Coincidence ")
        self.labelVeto.setText("Use Veto ")
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    Dialog = ConfigDialog()
    sys.exit(app.exec_())

