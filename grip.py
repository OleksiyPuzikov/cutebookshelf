import sys

from PyQt4 import QtGui, QtCore

class BetterGrip(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setCursor(QtCore.Qt.SplitHCursor) # Qt.SizeBDiagCursor

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
    
        self.px = self.py = 0

        self.coeffx = 1
        self.coeffy = 1

        self.resize(15, 15)
        self.adjustPosition()

    def adjustPosition(self):
        self.move(self.parent().width()-self.width()-1, self.parent().height()-self.height()-1)

    def paintEvent(self, event):

        painter = QtGui.QPainter()
        painter.begin(self)

        opt = QtGui.QStyleOptionSizeGrip()
        opt.init(self)
        opt.rect = event.rect()
        opt.corner = QtCore.Qt.BottomRightCorner

#        self.style().drawControl(QtGui.QStyle.CE_SizeGrip, opt, painter)

        x, y, w, h = opt.rect.getRect()

#        if self.coeffx == self.coeffy:

#        self.style().drawControl(QtGui.QStyle.CE_SizeGrip, opt, painter)


#            sw = min(h, w)
#            if h > w:
#                painter.translate(0, h - w)
#            else:
#                painter.translate(w - h, 0)
#
#            sx = x
#            sy = y
#            s = sw / 3
#
#            for i in range(0, 4):
#                painter.setPen(QtGui.QPen(opt.palette.dark().color(), 1))
#                painter.drawLine(sx - 1, sw, sw, sy - 1)
#                painter.setPen(QtGui.QPen(opt.palette.light().color(), 1))
#                painter.drawLine(sx, sw, sw, sy)
#                painter.setPen(QtGui.QPen(opt.palette.light().color(), 1))
#                painter.drawLine(sx + 1, sw, sw, sy + 1)
#                sx += s
#                sy += s

#        else:
        sy = y
        sw = min(h, w)
        s = sw / 4
        sx = x+s

        for i in range(0, 3):
            painter.setPen(QtGui.QPen(opt.palette.dark().color(), 1))
            painter.drawLine(sx - 1, sy, sx - 1, sw-4)
            painter.setPen(QtGui.QPen(opt.palette.light().color(), 1))
            painter.drawLine(sx, sy, sx, sw-4)
            sx += s

        painter.end()

    def mousePressEvent(self, e):
    
        self.px = e.globalPos().x()
        self.py = e.globalPos().y()
        
    def mouseMoveEvent(self, e):
    
        if e.buttons() != QtCore.Qt.LeftButton:
            return

        tlw = self.parent()

        np = e.globalPos()

        valx = (self.px -  np.x())*self.coeffx
        valy = (self.py -  np.y())*self.coeffy

        self.px = e.globalPos().x()
        self.py = e.globalPos().y()

        tlw.resize(tlw.width()-valx, tlw.height()-valy)

#        tlw.parent().refresh()
        tlw.parent().setSizes([tlw.width(), 0])

        self.adjustPosition()

class QermitWindow(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self, None)

        self.widget1 = QtGui.QWidget(self)
        self.widget1.setGeometry(QtCore.QRect(70, 110, 201, 24))
        self.widget1.setStyleSheet("background-color: rgb(84, 255, 175)")

        self.widget2 = QtGui.QWidget(self)
        self.widget2.setGeometry(QtCore.QRect(310, 110, 191, 24))
        self.widget2.setStyleSheet("background-color: rgb(189, 184, 255)")

        self.resize(800, 600)

        self.grip1 = BetterGrip(self.widget1)
        self.grip1.coeffy = 0
        self.grip1.resize(24, 24)
        self.grip1.adjustPosition()
        
        self.grip2 = BetterGrip(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = QermitWindow()
    window.show()

    app.exec_()