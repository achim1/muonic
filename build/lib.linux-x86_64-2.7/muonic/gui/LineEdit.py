from PyQt4 import QtGui
from PyQt4 import QtCore

class LineEdit(QtGui.QLineEdit):

    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)
        self.history=[]
        self.hist_pointer = 0
        
    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key()==QtCore.Qt.Key_Down:
                self.emit(QtCore.SIGNAL("keyDownPressed"))
                if self.hist_pointer < len(self.history)-1:
                    self.hist_pointer += 1
                    self.setText(self.history[self.hist_pointer])
                elif self.hist_pointer == len(self.history)-1:
                    self.setText('')
                    self.hist_pointer += 1
                return True
            if event.key()==QtCore.Qt.Key_Up:
                self.emit(QtCore.SIGNAL("keyUpPressed"))
                if self.hist_pointer > 0:
                    self.hist_pointer -= 1
                    self.setText(self.history[self.hist_pointer])
                return True
            else:
                return QtGui.QLineEdit.event(self, event)
        return QtGui.QLineEdit.event(self, event)

    def add_hist_item(self,item):
        self.history.append(item)
        self.hist_pointer = len(self.history)

# vim: ai ts=4 sts=4 et sw=4
