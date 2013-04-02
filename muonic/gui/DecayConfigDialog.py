
from PyQt4 import QtCore, QtGui

class DecayConfigDialog(QtGui.QDialog):
    def __init__(self, *args):

        QtGui.QDialog.__init__(self,*args)

        # size of window etc..
        self.setObjectName("Configure")
        self.resize(480, 360)
        self.setModal(True)
        self.setWindowTitle("Channel Configuration")  

        # the 'ok' and 'cancel' buttons
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 300, 300, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        ## select the coincidences with Radio Buttons
        ## group them in a vertical box, so that they do not
        ## collide with the veto radio buttons
        #self.vlcoincWid = QtGui.QWidget(self)
        #self.vlcoincWid.setGeometry(QtCore.QRect(200, 40, 150, 120))
        #self.vlcoincWid.setObjectName("verticalLayoutWidget")
        #self.vlcoinc = QtGui.QVBoxLayout(self.vlcoincWid)
        #self.vlcoinc.setMargin(0)
        #self.vlcoinc.setObjectName("verticalLayout")

        #self.coincidenceSingles = QtGui.QRadioButton(self.vlcoincWid)
        #self.coincidenceSingles.setGeometry(QtCore.QRect(210, 50, 145, 28))
        #self.coincidenceSingles.setObjectName("radioButton")
        #self.coincidenceSingles.setText("Single")
        #self.vlcoinc.addWidget(self.coincidenceSingles)

        #self.coincidenceTwofold = QtGui.QRadioButton(self.vlcoincWid)
        #self.coincidenceTwofold.setGeometry(QtCore.QRect(210, 90, 145, 28))
        #self.coincidenceTwofold.setObjectName("radioButton_2")
        #self.coincidenceTwofold.setText("Twofold")
        #self.vlcoinc.addWidget(self.coincidenceTwofold)

        #self.coincidenceThreefold = QtGui.QRadioButton(self.vlcoincWid)
        #self.coincidenceThreefold.setGeometry(QtCore.QRect(210, 140, 145, 28))
        #self.coincidenceThreefold.setObjectName("radioButton_3")
        #self.coincidenceThreefold.setText("Threefold")
        #self.vlcoinc.addWidget(self.coincidenceThreefold)

        #self.coincidenceFourfold= QtGui.QRadioButton(self.vlcoincWid)
        #self.coincidenceFourfold.setGeometry(QtCore.QRect(210, 180, 145, 28))
        #self.coincidenceFourfold.setObjectName("radioButton_4")
        #self.coincidenceFourfold.setText("Fourfould")
        #self.vlcoinc.addWidget(self.coincidenceFourfold)

        ## set Veto with RadioButtons
        #self.noveto = QtGui.QRadioButton(self)
        #self.noveto.setGeometry(QtCore.QRect(410, 50, 145, 28))
        #self.noveto.setObjectName("radioButton_5")
        #self.noveto.setText("None")
        #self.vetochan1 = QtGui.QRadioButton(self)
        #self.vetochan1.setGeometry(QtCore.QRect(410, 90, 145, 28))
        #self.vetochan1.setObjectName("radioButton_7")
        #self.vetochan1.setText("Chan1")
        #self.vetochan2 = QtGui.QRadioButton(self)
        #self.vetochan2.setGeometry(QtCore.QRect(410, 140, 145, 28))
        #self.vetochan2.setObjectName("radioButton_8")
        #self.vetochan2.setText("Chan2")
        #self.vetochan3 = QtGui.QRadioButton(self)
        #self.vetochan3.setGeometry(QtCore.QRect(410, 180, 145, 28))
        #self.vetochan3.setObjectName("radioButton_9")
        #self.vetochan3.setText("Chan3")

        # activate Channels with Checkboxes
        self.singlegroupBox = QtGui.QGroupBox("Single Pulse")
        self.singlegroupBox.setCheckable(False)


        self.singleChan0 = QtGui.QRadioButton(self)
        self.singleChan0.setGeometry(QtCore.QRect(20, 40, 119, 28))
        self.singleChan0.setObjectName("singlecheckBox")
        self.singleChan0.setText("Chan0")
        self.singleChan1 = QtGui.QRadioButton(self)
        self.singleChan1.setGeometry(QtCore.QRect(20, 80, 119, 28))
        self.singleChan1.setObjectName("singlecheckBox_2")
        self.singleChan1.setText("Chan1")
        self.singleChan2 = QtGui.QRadioButton(self)
        self.singleChan2.setGeometry(QtCore.QRect(20, 130, 119, 28))
        self.singleChan2.setObjectName("singlecheckBox_3")
        self.singleChan2.setText("Chan2")
        self.singleChan3 = QtGui.QRadioButton(self)
        self.singleChan3.setGeometry(QtCore.QRect(20, 180, 119, 28))
        self.singleChan3.setObjectName("singlecheckBox_4")
        self.singleChan3.setText("Chan3")

        self.singlevbox = QtGui.QVBoxLayout()
        self.singlevbox.addWidget(self.singleChan0)
        self.singlevbox.addWidget(self.singleChan1)
        self.singlevbox.addWidget(self.singleChan2)
        self.singlevbox.addWidget(self.singleChan3)
        self.singlevbox.addStretch(1)
        self.singlegroupBox.setLayout(self.singlevbox)




        #self.labelsingleChannel = QtGui.QLabel(self)
        #self.labelsingleChannel.setText("Single Pulse")
        #self.labelsingleChannel.setGeometry(QtCore.QRect(30, 10, 121, 23))
        #self.labelsingleChannel.setObjectName("singlechannellabel")




        # activate Channels with Checkboxes
        self.doublegroupBox = QtGui.QGroupBox("Double Pulse")
        self.doublegroupBox.setCheckable(False)
        self.doubleChan0 = QtGui.QRadioButton(self)
        self.doubleChan0.setGeometry(QtCore.QRect(180, 40, 119, 28))
        self.doubleChan0.setObjectName("doublecheckBox")
        self.doubleChan0.setText("Chan0")
        self.doubleChan1 = QtGui.QRadioButton(self)
        self.doubleChan1.setGeometry(QtCore.QRect(180, 80, 119, 28))
        self.doubleChan1.setObjectName("doublecheckBox_2")
        self.doubleChan1.setText("Chan1")
        self.doubleChan2 = QtGui.QRadioButton(self)
        self.doubleChan2.setGeometry(QtCore.QRect(180, 130, 119, 28))
        self.doubleChan2.setObjectName("doublecheckBox_3")
        self.doubleChan2.setText("Chan2")
        self.doubleChan3 = QtGui.QRadioButton(self)
        self.doubleChan3.setGeometry(QtCore.QRect(180, 180, 119, 28))
        self.doubleChan3.setObjectName("doublecheckBox_4")
        self.doubleChan3.setText("Chan3")

        self.doublevbox = QtGui.QVBoxLayout()
        self.doublevbox.addWidget(self.doubleChan0)
        self.doublevbox.addWidget(self.doubleChan1)
        self.doublevbox.addWidget(self.doubleChan2)
        self.doublevbox.addWidget(self.doubleChan3)
        self.doublevbox.addStretch(1)
        self.doublegroupBox.setLayout(self.doublevbox)
        #self.labeldoubleChannel = QtGui.QLabel(self)
        #self.labeldoubleChannel.setText("Double Pulse")
        #self.labeldoubleChannel.setGeometry(QtCore.QRect(180, 10, 121, 23))
        #self.labeldoubleChannel.setObjectName("doublechannellabel")

        # activate Channels with Checkboxes
        self.vetogroupBox = QtGui.QGroupBox("Veto Pulse")
        self.vetogroupBox.setCheckable(False)
        self.vetoChan0 = QtGui.QRadioButton(self)
        self.vetoChan0.setGeometry(QtCore.QRect(300, 40, 119, 28))
        self.vetoChan0.setObjectName("vetocheckBox")
        self.vetoChan0.setText("Chan0")
        self.vetoChan1 = QtGui.QRadioButton(self)
        self.vetoChan1.setGeometry(QtCore.QRect(300, 80, 119, 28))
        self.vetoChan1.setObjectName("vetocheckBox_2")
        self.vetoChan1.setText("Chan1")
        self.vetoChan2 = QtGui.QRadioButton(self)
        self.vetoChan2.setGeometry(QtCore.QRect(300, 130, 119, 28))
        self.vetoChan2.setObjectName("vetocheckBox_3")
        self.vetoChan2.setText("Chan2")
        self.vetoChan3 = QtGui.QRadioButton(self)
        self.vetoChan3.setGeometry(QtCore.QRect(300, 180, 119, 28))
        self.vetoChan3.setObjectName("vetocheckBox_4")
        self.vetoChan3.setText("Chan3")

        self.vetovbox = QtGui.QVBoxLayout()
        self.vetovbox.addWidget(self.vetoChan0)
        self.vetovbox.addWidget(self.vetoChan1)
        self.vetovbox.addWidget(self.vetoChan2)
        self.vetovbox.addWidget(self.vetoChan3)
        self.vetovbox.addStretch(1)
        self.vetogroupBox.setLayout(self.vetovbox)
        #self.labelvetoChannel = QtGui.QLabel(self)
        #self.labelvetoChannel.setText("Veto Pulse")
        #self.labelvetoChannel.setGeometry(QtCore.QRect(300, 10, 121, 23))
        #self.labelvetoChannel.setObjectName("vetochannellabel")
        # three labels, one for the radio buttons, and one for the checkboxes, the last one for veto criterion

        #self.labelCoincidence = QtGui.QLabel(self)
        #self.labelCoincidence.setGeometry(QtCore.QRect(210, 10, 121, 23))
        #self.labelCoincidence.setObjectName("coincidencelabel")

        #self.labelVeto = QtGui.QLabel(self)
        #self.labelVeto.setGeometry(QtCore.QRect(410, 10, 121, 23))
        #self.labelVeto.setObjectName("vetolabel")

        #self.labelCoincidence.setText("Coincidence ")
        #self.labelVeto.setText("Use Veto ")

        grid = QtGui.QGridLayout()
        grid.addWidget(self.singlegroupBox, 0, 0)
        grid.addWidget(self.doublegroupBox, 1, 0)
        grid.addWidget(self.vetogroupBox, 0, 1)
        self.setLayout(grid)


        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    Dialog = DecayConfigDialog()
    sys.exit(app.exec_())

