#! /usr/bin/python

# . save state for current tree item
# . check if device exist
# + save ** (stars) for books
# + save read state for books
# + bind synchronize button
# + bind empty space
# + import books from
# + move devices settings to settings file

import sys
import os
import glob
import datetime
import stat
import shutil
import inspect
import time

from PyQt4 import QtCore, QtGui

from minisplitter import MiniSplitter
import navbar
from navbar import *

from browser import NewWebView
from list import NewListWithHeader
from grip import BetterGrip

import storage

import sync

from parsers import *
from normalize import *
from animation import *

basepath = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(sys._getframe(0)))) # this is where we come from

product_name = "Cute Bookshelf"

#----------------------------------------------------------------------

#class BookShelfWindow(QtGui.QWidget):
class BookShelfWindow(QtGui.QMainWindow):

    def __init__(self):
#        QtGui.QWidget.__init__(self, None)
        QtGui.QMainWindow.__init__(self, None)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.tr(product_name))

        self.animation = None

        self.move(storage.settings.get("x", 0), storage.settings.get("y", 0))
        self.resize(storage.settings.get("w", 800), storage.settings.get("h", 600))

        if storage.settings.get("maximized", False):
            self.setWindowState(QtCore.Qt.WindowMaximized)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setSpacing(0)

        self.splitter = MiniSplitter(QtCore.Qt.Horizontal, self)

        self.horizontalLayout.addWidget(self.splitter)

        self.tree = navbar.QfNavBar(self.splitter)
        self.tree.setMinimumSize(QtCore.QSize(100, 0))
        self.tree.setMaximumSize(QtCore.QSize(250, 16777215))
        self.tree.setBaseSize(QtCore.QSize(250, 0))

        self.root = storage.settings.get("books_path", "/local1/seq5/books/")
        storage.settings["books_path"] = self.root

        self.groupLibrary = self.tree.addGroupString("LIBRARY")

        for (dirpath, dirnames, filenames) in os.walk(self.root):
            for dirname in dirnames:
                fullpath = os.path.join(dirpath, dirname)
                self.tree.addItemGroupIconName(self.groupLibrary, QtGui.QPixmap("pix/book.png"), self.tr(dirname), self.tr(fullpath), "")

        group = self.tree.addGroupString("DEVICES")
        for i in range(0,5):
            device_name = storage.settings.get("device%d/name" % i, None)
            if device_name != None:
                device_type = storage.settings.get("device%d/type" % i, "default")
                self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/flash.png"), device_name, "devices:/%s" % device_type, str(i))

        group = self.tree.addGroupString("LIB.RUS.EC")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_unknown.png"), "Start", "web:http://lib.rus.ec")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_updates.png"), "What's new", "web:http://lib.rus.ec/new")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_unknown.png"), "Genres", "web:http://lib.rus.ec/g")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_unknown.png"), "Authors", "web:http://lib.rus.ec/a")

        group = self.tree.addGroupString("PROJECT GUTENBERG")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_unknown.png"), "Start", "web:http://www.gutenberg.org/")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_updates.png"), "What's new", "web:http://www.gutenberg.org/browse/recent/last1")

        group = self.tree.addGroupString("FB2 SEARCH")
        self.tree.addItemGroupIconName(group, QtGui.QPixmap("pix/z_unknown.png"), "Start", "web:http://fb2search.com/")

        self.connect(self.tree, QtCore.SIGNAL("onItemSelected(QWidget)"), self.onTreeItemSelected)

        self.rightPane = QtGui.QWidget(self.splitter)

        self.rightPaneLayout = QtGui.QVBoxLayout(self.rightPane)
        self.rightPaneLayout.setMargin(0)
        self.rightPaneLayout.setSpacing(0)

        self.rightStack = QtGui.QStackedWidget(self.rightPane)

        self.page1 = QtGui.QWidget()
        self.page1Layout = QtGui.QVBoxLayout(self.page1)
        self.page1Layout.setMargin(0)
        self.page1Layout.setSpacing(0)

        self.mainList = NewListWithHeader(self.page1)

        self.page1Layout.addWidget(self.mainList)
        self.rightStack.addWidget(self.page1)

        self.page2 = QtGui.QWidget()
        self.page2Layout = QtGui.QVBoxLayout(self.page2)
        self.page2Layout.setMargin(0)
        self.page2Layout.setSpacing(0)

        self.deviceWebView = NewWebView(self.page2)
        self.connect(self.deviceWebView.helper, QtCore.SIGNAL("browserButtonPressed(QString)"), self.onBrowserButton)
        self.connect(self.deviceWebView, QtCore.SIGNAL("titleChanged(QString)"), self.onTitleChanged)

        self.page2Layout.addWidget(self.deviceWebView)
        self.rightStack.addWidget(self.page2)
        
        self.page3 = QtGui.QWidget()
        self.page3Layout = QtGui.QVBoxLayout(self.page3)
        self.page3Layout.setMargin(0)
        self.page3Layout.setSpacing(0)

        self.storeWebView = NewWebView(self.page3)
        self.page3Layout.addWidget(self.storeWebView)
        self.rightStack.addWidget(self.page3)

        self.connect(self.storeWebView, QtCore.SIGNAL("started(QString)"), self.onSomethingStarted)
        self.connect(self.storeWebView, QtCore.SIGNAL("progress(int,QString)"), self.onSomethingProgressing)
        self.connect(self.storeWebView, QtCore.SIGNAL("finished(QString)"), self.onSomethingFinished)

        self.connect(self.storeWebView, QtCore.SIGNAL("downloadCompleted(QString)"), self.onDownloadCompleted)

        self.connect(self.storeWebView, QtCore.SIGNAL("titleChanged(QString)"), self.onTitleChanged)

        self.rightPaneLayout.addWidget(self.rightStack)
        
        self.progressList = QtGui.QListWidget(self.rightPane)
        self.progressList.setMaximumSize(QtCore.QSize(65535, 24))
        self.progressList.setMinimumSize(QtCore.QSize(0, 24))
        self.progressList.setFrameShape(QtGui.QFrame.NoFrame)
        self.progressList.setBackgroundRole(QtGui.QPalette.Button)

        self.progressLayout = QtGui.QHBoxLayout(self.progressList)
        self.progressLayout.setSpacing(0)
        self.progressLayout.setMargin(4)

        self.lblProgress = QtGui.QLabel(self.progressList)
        self.progressBar = QtGui.QProgressBar(self.progressList)
        self.progressBar.resize(300, self.progressBar.height())
        self.progressBar.setMinimumWidth(300)
        self.lblProgress.hide()
        self.progressBar.hide()
        self.grip = QtGui.QSizeGrip(self.progressList)
        
        self.progressLayout.addStretch(1)
        self.progressLayout.addWidget(self.lblProgress, 1, QtCore.Qt.AlignRight)
        self.progressLayout.addSpacing(10)
        self.progressLayout.addWidget(self.progressBar, 0, QtCore.Qt.AlignRight)
        self.progressLayout.addSpacing(10)
        self.progressLayout.addWidget(self.grip, 0, QtCore.Qt.AlignRight)

        self.progressList.setLayout(self.progressLayout)

        self.rightPaneLayout.addWidget(self.progressList)

        self.rightStack.setCurrentIndex(0)

#        self.connect(self.storeWebView, QtCore.SIGNAL("loadProgress(int)"), self.webLoadProgress)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.optionsAction = QtGui.QAction(self.tr("&Options..."),  self)
        self.quitAction = QtGui.QAction(self.tr("&Quit"), self)

        self.quitAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        
        self.connect(self.optionsAction, QtCore.SIGNAL("triggered()"), self.onOptionsAction)
        self.connect(self.quitAction, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("quit()"))

        fileMenu = self.menuBar().addMenu(self.tr("&File"))
        fileMenu.addAction(self.optionsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAction)

        self.centralWidget = QtGui.QWidget(self)
        self.centralWidget.setLayout(self.horizontalLayout)

        self.setCentralWidget(self.centralWidget)

        self.sync = sync.SyncEngine()
        self.connect(self.sync, QtCore.SIGNAL("started(QString)"), self.onSomethingStarted)
        self.connect(self.sync, QtCore.SIGNAL("progress(int,QString)"), self.onSomethingProgressing)
        self.connect(self.sync, QtCore.SIGNAL("finished(QString)"), self.onSomethingFinished)

        self.grip1 = BetterGrip(self.tree)
        self.grip1.coeffy = 0
        self.grip1.resize(13, 13)
        self.tree.grip = self.grip1

        self.firstShow = True

#        self.tree.setCurrentItem(itemBooks)

    def showEvent(self, event):
        if self.firstShow:
            self.firstShow = False

            for i in range(0,5):
                dir_name = storage.settings.get("automergedir%d" % i, None)
                if dir_name != None:
                    self.autoMergeDir(dir_name)

    def autoMergeDir(self, directory):
        filetypes = parsers.keys()
        directory = os.path.expanduser(os.path.expandvars(directory))

        if os.path.isdir(directory):

            for ft in filetypes:

                files = [file for file in glob.glob(str(directory+"/*%s" % ft)) if os.path.isfile(file)]

                for filename in files:
                    self.onDownloadCompleted(self.tr(filename))

    def onTitleChanged(self, url):
        self.setWindowTitle(self.tr("%1 - %2").arg(product_name).arg(url))

    def onBrowserButton(self, button):
        command = str(button)
        if command.startswith("sync/"):
            command = command.replace("sync/", "")
            self.sync.sync(self.root, command)

    def onOptionsAction(self):
        QtGui.QMessageBox.information(self, "Options", "Please edit %s manually" % storage.settingsPath)

    def onDownloadCompleted(self, value):
        tempfilename = str(value)

        filename1 = os.path.split(tempfilename)[-1]

        (bauthor, btitle, bgenre) = parseFile(tempfilename)
        (root, ext) = os.path.splitext(tempfilename)

        bauthor = translit(bauthor) if bauthor != "" else ext[1:]

        root = os.path.normpath(self.root) # always without / at the end

        filename2 = os.path.join(root, bauthor, filename1) # this is probably going to become a configurable string in the future, something like "/$genre/$author/"

        try:
            os.makedirs(os.path.join(root, bauthor))
        except:
            pass

        shutil.copyfile(tempfilename, filename2)
        shutil.os.remove(tempfilename)

        # show where it's going
        it = None
        for item in self.groupLibrary.listItems:
            if str(item.labelText.text()) == bauthor:
                it = item

        if it == None:
            fullpath = os.path.join(self.root, bauthor)
            it = self.tree.addItemGroupIconName(self.groupLibrary, QtGui.QPixmap("pix/book.png"), self.tr(bauthor), self.tr(fullpath))

        self.animateUndoStyle(it)

    def animateUndoStyle(self, lbl):
        if self.animation:
            if self.animation.running():
                self.animation.kill()

        bgcolor = self.tree.colorBackground

        self.animation = FadeSwitch(lbl, bgcolor)
        self.animation.start()

    def onSomethingStarted(self, value):
        self.lblProgress.show()
        self.progressBar.show()
        self.lblProgress.setText(value)

    def onSomethingProgressing(self, progress, value):
        self.lblProgress.setText(value)
        self.progressBar.setValue(progress)

    def onSomethingFinished(self, value):
        self.lblProgress.setText(value)
        self.lblProgress.hide()
        self.progressBar.hide()

    def moveEvent(self, event):
        fg = self.frameGeometry()
        storage.settings["x"] = fg.x()
        storage.settings["y"] = fg.y()

        event.ignore()

    def resizeEvent(self, event):
        storage.settings["w"] = event.size().width()
        storage.settings["h"] = event.size().height()
        storage.settings["maximized"] = self.windowState() == QtCore.Qt.WindowMaximized

        event.ignore()

    def formatByteSize(self, bytes):
        B = 1
        KB = 1024 * B
        MB = 1024 * KB
        GB = 1024 * MB

        if bytes > GB:
            return '%0.3g GB' % (bytes/GB)
        elif bytes > MB:
            return '%0.3g MB' % (bytes/MB)
        elif bytes > KB:
            return '%0.3g KB' % (bytes/KB)
        else:
            return '%0.3g bytes' % bytes

    def onTreeItemSelected(self, item):
        where = str(item.text2)
        try:
            device_number = int(str(item.text3))
        except:
            device_number = -1
        if where.startswith("devices:"):
            if device_number != -1:
                where2 = where.replace("devices:", "")

                where2 = os.path.normpath(os.path.sep.join([basepath, "devices", where2, "index.html"]))

                device_name = storage.settings.get("device%d/name" % device_number, None)
                device_type = storage.settings.get("device%d/type" % device_number, "default")
                device_path = storage.settings.get("device%d/path" % device_number, "~/")
                device_lastsync = storage.settings.get("device%d/lastsync" % device_number, "2009-10-11 12:34")

                now = datetime.datetime.fromtimestamp(time.time())
                last = datetime.datetime.strptime(device_lastsync, '%Y-%m-%d %H:%M')

                import freespace

                device_freespace, device_totalspace = freespace.freespace_ex(device_path)

#                delta = now-last

#                print now, device_lastsync

#                print datetime.datetime.strftime('%Y-%m-%d')

                f = "\n".join(open(where2).readlines())

                f = f.replace("{path}", basepath)
                f = f.replace("{volume}", device_path)
                f = f.replace("{freespace}", self.formatByteSize(device_freespace))
                f = f.replace("{totalspace}", self.formatByteSize(device_totalspace))
                f = f.replace("{lastsync}", device_lastsync)

                self.deviceWebView.setHtml(f)
                self.rightStack.setCurrentIndex(1)

        elif where.startswith("web:"):
            self.rightStack.setCurrentIndex(2)
            where2 = where.replace("web:", "")
            self.storeWebView.load(QtCore.QUrl(where2))

        else:
            self.rightStack.setCurrentIndex(0)
            self.reloadGrid(where)

#    def webLoadProgress(self, progress):
#        print "web load: ", progress

    def reloadGrid(self, directory):
        self.mainList.list.clear()

        files = glob.glob(str(directory+"/*"))

        # import dircache
        # cachedirectory = os.path.sep.join([curpath,directory])
        # files = dircache.listdir( cachedirectory )
        # files = [ os.path.sep.join([cachedirectory, file]) for file in files ]

        files = [file for file in files if os.path.isfile(file)]
        self.setWindowTitle("%s - %s (%d)" % (product_name, directory, len(files)))

        for file in files:

            bauthor = bgenre = btitle = bgenre = ""
            st = os.stat(file)
            bdate = datetime.datetime.fromtimestamp(st[stat.ST_MTIME]).strftime('%Y-%m-%d') # %x %X
            bsize = "%d kb" % ( int(st[stat.ST_SIZE])/1024 )

            (bauthor, btitle, bgenre) = parseFile(file)

            a = storage.data.get(file, {})

            a["name"] = btitle
            a["author"] = bauthor
            a["date"] = self.tr(bdate)
            a["size"] = self.tr(bsize)
            a["genre"] = self.tr(bgenre)
#            a["path"] = self.tr(file)
            a["rating"] = a.get("rating", 0)
            a["checked"] = a.get("checked", QtGui.QIcon.On)

            storage.data[file] = a

            QtGui.QListWidgetItem(self.tr(file), self.mainList.list)

if __name__ == "__main__":
    storage.loadSettings()
    storage.loadData()

    app = QtGui.QApplication(sys.argv)

    window = BookShelfWindow()
    window.show()
    window.raise_()

    app.exec_()

    storage.saveData()
    storage.saveSettings()
