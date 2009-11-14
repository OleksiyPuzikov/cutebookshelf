from PyQt4 import QtCore, QtGui
#from PyQt4 import Qt as Qt4
import sys
import math

#from storage import data, header_sizes
import storage

#data = {'id1': {'rating': 5, 'genre': 'drama', 'author': 'John Grisham1', "checked":QtGui.QIcon.On},
#        'id2': {'rating': 4, 'genre': 'drama', 'author': 'John Grisham2', "checked":QtGui.QIcon.Off},
#        'id3': {'rating': 3, 'genre': 'fiction', 'author': 'John Grisham2', "checked":QtGui.QIcon.On},
#        'id4': {'rating': 2, 'genre': 'drama', 'author': 'John Grisham2', "checked":QtGui.QIcon.Off}
#        }
        
header_titles = [ "Name", "Author", "Date", "Size", "Genre", "Rating" ]
        
class GraphDelegate(QtGui.QItemDelegate):
    COLOR  = QtGui.QColor("gray")
    LCOLOR = QtGui.QColor("lightgray")
    SIZE     = 16
    PEN      = QtGui.QPen(COLOR, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
    
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self,parent)

        self.icon_on = QtGui.QIcon()
        self.icon_on.addPixmap(QtGui.QPixmap("pix/check_on.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.icon_on.addPixmap(QtGui.QPixmap("pix/check_off.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        
        self.star_path = QtGui.QPainterPath()
        self.star_path.moveTo(90, 50)
        for i in range(1, 5):
            self.star_path.lineTo(50 + 40 * math.cos(0.8 * i * math.pi), \
                                  50 + 40 * math.sin(0.8 * i * math.pi))
        self.star_path.closeSubpath()
        self.star_path.setFillRule(QtCore.Qt.WindingFill)
        self.factor = self.SIZE/120.0

    def sizeHint(self, option, index):
        size = QtGui.QItemDelegate.sizeHint(self, option, index)
        return QtCore.QSize(size.width(), size.height()+4)

    def paint(self, painter, option, index):
        idata = str(index.model().data(index).toString())
        
        def draw_star():
            painter.save()
            painter.scale(self.factor, self.factor)
            painter.translate(50.0, 50.0)
            painter.rotate(-20)
            painter.translate(-50.0, -50.0)
            painter.drawPath(self.star_path)
            painter.restore()

        def draw_circle():
            painter.save()
            painter.scale(self.factor, self.factor)
            painter.translate(50.0, 25.0*3/2)
            painter.drawEllipse(0, 0, 25, 25)
            painter.restore()

        painter.save()
        if (option.state & QtGui.QStyle.State_Selected):
            painter.fillRect(option.rect, option.palette.highlight().color())

        dt = storage.data.get(idata)

#        print idata, dt, dt['checked']
        
        self.icon_on.paint(painter, option.rect.left(), option.rect.top()+(option.rect.height()-16)/2, 16, 16, QtCore.Qt.AlignCenter, QtGui.QIcon.Normal, dt["checked"])
        
        style = QtGui.QApplication.style()
        align_flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        role = QtGui.QPalette.HighlightedText if (option.state & QtGui.QStyle.State_Selected) else QtGui.QPalette.Text
        brush = option.palette.highlightedText() if (option.state & QtGui.QStyle.State_Selected) else self.COLOR #option.palette.text()
        brush2 = self.LCOLOR
        for x, c in enumerate(header_titles):
            offs = sum(storage.header_sizes[:x])+4 if x>0 else 18
            what = c.lower()
            if what == "rating":
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                y = option.rect.center().y()-self.SIZE/2.0+2
                x = option.rect.left()+sum(storage.header_sizes[:x])
                painter.setPen(self.PEN)
                painter.translate(x, y)
                for x in range(0, 6):
                    if x in range(int(dt[what])):
                        painter.setBrush(brush)
                        draw_star()
                    else:
                        painter.setBrush(brush2)
                        draw_circle()
                    painter.translate(self.SIZE, 0)
            else:                
                woffs = option.rect.width()-storage.header_sizes[x]+20 if x==0 else option.rect.width()-storage.header_sizes[x]+4
                style.drawItemText(painter, option.rect.adjusted(offs, 0, -woffs+offs, 0), align_flags, option.palette, True, dt.get(what,""), role)
        painter.restore()

class NewHeader(QtGui.QHeaderView):
    
    def __init__(self, parent=None):
        QtGui.QHeaderView.__init__(self, QtCore.Qt.Horizontal, parent)
        
        self.setDefaultAlignment(QtCore.Qt.AlignLeft)
        
        self.dosomething = None

        self.model = QtGui.QStandardItemModel(0, len(header_titles)+1)
        
        self.setStretchLastSection(True)

        self.setModel(self.model)
        
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        
        self.resize(100, 20)

        for x, c in enumerate(header_titles):
            self.model.setHeaderData(x, QtCore.Qt.Horizontal, QtCore.QVariant(self.tr(c)))
            self.resizeSection(x, storage.header_sizes[x])
        
        self.model.setHeaderData(x+1, QtCore.Qt.Horizontal, QtCore.QVariant(""))
                
    def sizeHint(self):
        return QtCore.QSize(-1, 20)

    def minimumSizeHint(self):
        return QtCore.QSize(-1, 20)
        
    def mouseReleaseEvent(self, event):
        if self.dosomething:
            self.dosomething()
        event.ignore()

class NewList(QtGui.QListWidget):
    
    StyleSheet = 'QListView { alternate-background-color: rgb(241, 245, 250); border: 0; }'
    
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.setStyleSheet(self.StyleSheet)
        
        self.xx = 0
        self.yy = 0
        
        delegate = GraphDelegate(self)
        self.setItemDelegate(delegate)
        
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setLineWidth(0)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setProperty("showDropIndicator", QtCore.QVariant(False))
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setUniformItemSizes(True)    

    def mousePressEvent(self, event):
        self.xx = event.x()
        QtGui.QListWidget.mousePressEvent(self, event)

class NewListWithHeader(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.layoutV = QtGui.QVBoxLayout(self)
        self.layoutV.setMargin(0)
        self.layoutV.setSpacing(0)

        self.header = NewHeader()

        self.list = NewList()

        self.columnResizeTimerID = None

        self.layoutV.addWidget(self.header)
        self.layoutV.addWidget(self.list)

        self.setLayout(self.layoutV)

        self.connect(self.header, QtCore.SIGNAL("sectionResized(int, int, int)"), self.sectionResized)
#        self.header.dosomething = self.resized2

        self.connect(self.list, QtCore.SIGNAL('itemPressed(QListWidgetItem*)'), self.itemPressed)

        self.setStyleSheet("""QListWidget, QHeaderView { font-size: 11px; }
        QHeaderView { border: 0px; }
        QHeaderView::section { border-left: 0px none; }
   /* QHeaderView::section {
     background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #616161, stop: 0.5 #505050,
                                       stop: 0.6 #434343, stop:1 #656565);
     color: white;
     padding-left: 4px;
     border: 1px solid #6c6c6c;

 } */
 QListView::item { padding: 10px; }
 QListView::item:selected { color: white; background: #999 }
""")


    def itemDoubleClicked(self, item):
        storage.data[str(item.text())]["checked"] = QtGui.QIcon.On if storage.data[str(item.text())]["checked"] == QtGui.QIcon.Off else QtGui.QIcon.Off
        if storage.data[str(item.text())]["checked"] == QtGui.QIcon.Off:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        self.list.update()
        self.list.repaint()

    def itemPressed(self, item):
        if self.list.xx in range(sum(storage.header_sizes[:-2]), sum(storage.header_sizes[:-1])): # rating
            if item.isSelected():
                storage.data[str(item.text())]["rating"] = min(5, (self.list.xx-sum(storage.header_sizes[:-2]))/16+1)
                self.list.repaint(self.list.geometry())
        if self.list.xx in range(0, 16):
            self.itemDoubleClicked(item)

    def sectionResized(self, logicalIndex, oldSize, newSize):

#        if self.columnResizeTimerID == None:
#            self.columnResizeTimerID = self.startTimer(0)

        storage.header_sizes[logicalIndex] = newSize
        self.list.reset()

        # 050 402 35 24 TG mobile

    def timerEvent(self, event):
        if event.timerId() == self.columnResizeTimerID:
            self.killTimer(self.columnResizeTimerID)
            self.columnResizeTimerID = None

            self.update(self.geometry()) # rect.normalized()

        QtGui.QWidget.timerEvent(self, event)


class TestWindow(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self, None)
        
        self.resize(640, 480)
        self.move(10, 50)

        self.layoutV = QtGui.QVBoxLayout(self)
        self.layoutV.setMargin(0)
        self.layoutV.setSpacing(0)

        self.list = NewListWithHeader(self)

        QtGui.QListWidgetItem(self.tr("id1"), self.list.list)
        QtGui.QListWidgetItem(self.tr("id2"), self.list.list)
        QtGui.QListWidgetItem(self.tr("id3"), self.list.list)
        QtGui.QListWidgetItem(self.tr("id4"), self.list.list)

        self.layoutV.addWidget(self.list)

        self.setLayout(self.layoutV)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    view = TestWindow()
    view.show()

    app.exec_()

