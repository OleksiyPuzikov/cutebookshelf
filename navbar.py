#! /usr/bin/python

import sys
from PyQt4 import QtCore, QtGui
#import QfNavBar

class QfClickableLabel(QtGui.QLabel):
    def __init__(self, title = "", parent=None):
        QtGui.QLabel.__init__(self, parent)

    def mouseReleaseEvent (self, event):
    	QtGui.QLabel.mouseReleaseEvent(self, event)

    	event.setAccepted(True)

        self.emit(QtCore.SIGNAL("clicked()"))

class QfNavBarItem(QtGui.QWidget):

    def __init__(self, icon = None, text = "", text2 = "", text3 = "", parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.isSelected = False

        self.layout = QtGui.QHBoxLayout()

        self.labelIcon = QtGui.QLabel()
        self.labelIcon.setPixmap(icon)

        self.labelText = QtGui.QLabel()
        self.labelText.setText(text)

        self.text2 = text2
        self.text3 = text3

        self.labelText.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        self.labelIcon.setFixedWidth(18)

        font = self.labelText.font()
        font.setPixelSize(10)
        self.labelText.setFont(font)

        self.layout.addWidget(self.labelIcon)
        self.layout.addWidget(self.labelText)

        self.layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(self.layout)

    def select(self, sel):
        self.isSelected = sel
        if sel:
#            print self, "selected"
            self.emit(QtCore.SIGNAL("selected(QWidget)"), self)
            self.update()

    def mouseReleaseEvent(self, event):
        QtGui.QWidget.mouseReleaseEvent(self, event)

    	if event.button() == QtCore.Qt.LeftButton:
            self.select(not self.isSelected)

    def insertSpacing (self, index, size):
        self.layout.insertSpacing(index, size)

    def setTextColor(self, color):
        palette = self.labelText.palette()
        palette.setColor(QtGui.QPalette.WindowText, color)
        self.labelText.setPalette(palette)


class QfNavBarGroup(QtGui.QWidget):
    def __init__(self, title = "", parent=None):
        QtGui.QWidget.__init__(self, None)

        self.layout = QtGui.QVBoxLayout()
        self.labelTitle = QfClickableLabel()
        self.labelTitle.setText(title)

        self.isExpanded = True

        self.listItems = []

        self.layout.addWidget(self.labelTitle)

        font = self.labelTitle.font()
        font.setBold(True)
        font.setPixelSize(10)
        self.labelTitle.setFont(font)
        self.labelTitle.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.connect(self.labelTitle, QtCore.SIGNAL("clicked()"), self.onTitleClicked)

    def addItem(self, item):
        item.insertSpacing(0, 10)
        self.listItems.append(item)
        self.layout.addWidget(item)
        self.connect(item, QtCore.SIGNAL("selected(QWidget)"), self.onItemSelected)

    def addItemIconName(self, icon, text, text2=None, text3=None):
        item = QfNavBarItem(icon, text, text2, text3)
        self.addItem(item)
        return item
    
    def containsItem (self, item) :
        return (item in self.listItems)
    
    def setTitle (self, title) :
        self.labelTitle.setText(title)
    
    def setTitleColor (self, color) :
        palette = self.labelTitle.palette()
        palette.setColor(QtGui.QPalette.WindowText, color)
        self.labelTitle.setPalette(palette)

    def expand (self, expand) :
        if self.isExpanded == expand:
            return

        if expand:
            for item in self.listItems:
                self.layout.addWidget(item)
                item.show()
            
        else:
            for item in self.listItems:
                self.layout.removeWidget(item)
                item.hide()
        
        self.isExpanded = expand

#        emit expanded(this)
    
    def onItemSelected(self, who):
        self.emit(QtCore.SIGNAL("selected2(QWidget, QWidget)"), self, who)

    def onTitleClicked(self) :
        self.expand(not self.isExpanded)

        

class QfNavBar(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.resize(200, 300)

        self.layout = QtGui.QVBoxLayout()
        self.itemSelected = None
        self.groupSelected = None

        self.colorBackground = QtGui.QColor(0xdf, 0xe4, 0xea)
        self.colorSelection = QtGui.QColor(0xa6, 0xa6, 0xa6)

        self.layout.addStretch(2)
        self.setLayout(self.layout)

    def addGroupGroup(self, group):
    	group.setTitleColor(QtGui.QColor(0x65, 0x71, 0x80))

        self.connect(group, QtCore.SIGNAL("selected2(QWidget, QWidget)"), self.onItemSelected)

    	self.layout.insertWidget(self.layout.count()-1, group)

    def addGroupString(self, name):
        group = QfNavBarGroup(name)
        self.addGroupGroup(group)
        return group

    def containsGroup(self, group):
        for i in range(0, self.layout.count()):
            if self.layout.itemAt(i).widget() == group:
                return True

        return False

    def addItemGroupItem(self, group, item):
        return group.addItem(item)

    def addItemNameGroupName(self, group, text):
        return group.addItemName(text)

    def addItemGroupIconName(self, group, icon, text, text2=None, text3=None):
        return group.addItemIconName(icon, text, text2, text3)


    def paintEvent(self, event):
        QtGui.QWidget.paintEvent(self, event)

        if (event.rect().x() > 0) or (event.rect().y() > 0):
            self.update()

        p = QtGui.QPainter()
        p.begin(self)

        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.fillRect(event.rect(), self.colorBackground)

        if (self.groupSelected != None) and self.groupSelected.isExpanded and (self.itemSelected != None) :
            pos = self.groupSelected.pos() + self.itemSelected.pos()
            width = self.geometry().width()

            r = self.colorSelection.red()
            g = self.colorSelection.green()
            b = self.colorSelection.blue()

            p.fillRect(0, pos.y() - 1, width, 1, QtGui.QColor(r - 0x26, g - 0x26, b - 0x26))

            linearGrad = QtGui.QLinearGradient(QtCore.QPointF(0, pos.y()), QtCore.QPointF(0, pos.y() + self.itemSelected.height()))
            linearGrad.setColorAt(0, self.colorSelection)
            linearGrad.setColorAt(1, QtGui.QColor(r - 0x3b, g - 0x3b, b - 0x3b))
            p.fillRect(0, pos.y(), width, self.itemSelected.height(), linearGrad)

        p.end()


    def onItemSelected(self, group, item):
        if (self.itemSelected != None) and (self.itemSelected != item):
            self.itemSelected.setFont(item.font())
            self.itemSelected.setTextColor(QtCore.Qt.black)
            self.itemSelected.select(False)

        self.itemSelected = item
        self.groupSelected = group

        if self.itemSelected != None:

            font = self.itemSelected.font()
            font.setPixelSize(9)
            font.setBold(True)
            self.itemSelected.setFont(font)
            self.itemSelected.setTextColor(QtCore.Qt.white)

            self.update()

            self.emit(QtCore.SIGNAL("onItemSelected(QWidget)"), self.itemSelected)

    def onGroupExpanded(self, group) :
    	self.update()


if __name__ == "__main__":

    def onItemSelected(item):
        print item

    a = QtGui.QApplication(sys.argv)
    navbar = QfNavBar()
    group = navbar.addGroupString("APPLICATIONS PYTHON")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_allApps.png"), "All Applications")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_updates.png"), "Updates")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_upToDate.png"), "Up To Date")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_unknown.png"), "Unknown")

    group = navbar.addGroupString("BY KIND")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_apps.png"), "Applications")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_plugins.png"), "Plugins")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_widgets.png"), "Widgets")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_prefApp.png"), "Preference Panes")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_systemUpdates.png"), "System Updates")

    group = navbar.addGroupString("VENDORS")
    navbar.addItemGroupIconName(group, QtGui.QPixmap("pix/z_apple.png"), "Apple")
    navbar.resize(152, 165)

    a.connect(navbar, QtCore.SIGNAL("onItemSelected(QWidget)"), onItemSelected)

    navbar.show()
    a.exec_()
