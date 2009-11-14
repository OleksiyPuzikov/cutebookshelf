from PyQt4 import QtCore, QtGui

class  MiniSplitterHandle(QtGui.QSplitterHandle):

    def __init__(self, orientation, parent):
        QtGui.QSplitterHandle.__init__(self, orientation, parent)

#        self.setMask(QtGui.QRegion(self.contentsRect()))
#        self.setAttribute(QtCore.Qt.WA_MouseNoMask, True)

        self.setCursor(QtCore.Qt.SplitHCursor) # Qt.SizeBDiagCursor

    def resizeEvent(self, event):

       if (self.orientation() == QtCore.Qt.Horizontal):
           self.setContentsMargins(2, 0, 2, 0)
       else:
           self.setContentsMargins(0, 2, 0, 2)

#       self.setMask(QtGui.QRegion(self.contentsRect()))
#       self.emit(QtCore.SIGNAL("splitterResized()"))

       QtGui.QSplitterHandle.resizeEvent(self, event)


    def paintEvent(self, event):

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.fillRect(event.rect(), QtGui.QColor(64, 64, 64))

        painter.end()


class MiniSplitter(QtGui.QSplitter):

    def createHandle(self):
        return MiniSplitterHandle(self.orientation(), self)

    def __init__(self, orientation, parent):

        QtGui.QSplitter.__init__(self, orientation, parent)
        self.setHandleWidth(1)
        self.setChildrenCollapsible(False)
