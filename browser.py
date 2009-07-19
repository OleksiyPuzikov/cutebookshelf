import os
import sys
import tempfile

from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

import storage
#from parsers import *

class Helper(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)

    @QtCore.pyqtSignature("QString")
    def onDoSomething(self, what):
#        print "onDoSomething", what
        self.emit(QtCore.SIGNAL("browserButtonPressed(QString)"), what)

class NewWebView(QtWebKit.QWebView):

    def __init__(self, parent = None):
        QtWebKit.QWebView.__init__(self, parent)

        self.manager = QtNetwork.QNetworkAccessManager()

        self.helper = Helper()

        useProxy = storage.settings.get("useproxy", True)
        if useProxy:

            self.proxy = QtNetwork.QNetworkProxy()
            self.proxy.setHostName(storage.settings.get("proxy_address", ""))
            self.proxy.setPort(storage.settings.get("proxy_port", 0))
            self.proxy.setType(QtNetwork.QNetworkProxy.HttpProxy)
            self.manager.setProxy(self.proxy)

        self.page().setNetworkAccessManager(self.manager)

        self.page().setForwardUnsupportedContent(True)

        self.connect(self.page(), QtCore.SIGNAL("downloadRequested(const QNetworkRequest &)"), self.handleRequest)
        self.connect(self.page(), QtCore.SIGNAL("unsupportedContent(QNetworkReply *)"), self.handleUnsupported)
        
        self.connect(self.page(), QtCore.SIGNAL("loadProgress(int)"), self.setProgress)
        self.connect(self.page(), QtCore.SIGNAL("loadStarted()"), self.onLoadStarted)
        self.connect(self.page(), QtCore.SIGNAL("urlChanged(QUrl&)"), self.onUrlChanged)
        self.connect(self.page(), QtCore.SIGNAL("loadFinished(bool)"), self.onLoadFinished)

        self.connect(self.page().mainFrame(), QtCore.SIGNAL("initialLayoutCompleted()"), self.initialLayoutCompleted)

    def initialLayoutCompleted(self):
        self.page().mainFrame().addToJavaScriptWindowObject("qhelper", self.helper)

    def onUrlChanged(self, url):
        self.emit(QtCore.SIGNAL("started(QString)"), self.url().toString())

    def onLoadStarted(self):
        try:
            self.emit(QtCore.SIGNAL("started(QString)"), self.url().toString())
        except:
            pass

    def onLoadFinished(self, status):
        try:
            self.emit(QtCore.SIGNAL("finished(QString)"), self.url().toString())
        except:
            pass

    def handleUnsupported(self, reply):
#        print "handleUnsupported"
#        print reply.url()
#        print str(reply.url().path()).split("/")[-1]

        request = QtNetwork.QNetworkRequest(reply.url())

        self.reply = self.manager.get(request)
        self.connect(self.reply, QtCore.SIGNAL("finished()"), self.downloadFinished)
        self.connect(self.reply, QtCore.SIGNAL("loadProgress(int)"), self.setProgress)

    def handleRequest(self, request):
#        print request.url()
        self.reply = self.manager.get(request)

        self.connect(self.reply, QtCore.SIGNAL("finished()"), self.downloadFinished)
        self.connect(self.reply, QtCore.SIGNAL("loadProgress(int)"), self.setProgress)

    def setProgress(self, progress):
#        print progress
        try:
            self.emit(QtCore.SIGNAL("progress(int,QString)"), progress, self.url().toString())
        except:
            pass

    def downloadFinished(self):
#        print "download finished"
#        print self.reply.url()
#        print str(self.reply.url().path()).split("/")[-1]
        filename1 = str(self.reply.url().path()).split("/")[-1]

        tempfilename = os.path.join(tempfile.gettempdir(), filename1)

        f = open(tempfilename, "w")
        f.write(self.reply.readAll())
        f.close()

        self.reply.deleteLater()

        self.emit(QtCore.SIGNAL("downloadCompleted(QString)"), self.tr(tempfilename))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    view = NewWebView()

    where2 = "/local1/seq5/devices/lbook/index.html"

    f = open(where2).readlines()
    ht = "\n".join(f)

    view.setHtml(ht)

#    view.setHtml("""<h1>dfkljdfdj</h1>
#
#    <button onclick="javascript:qhelper.onDoSomething('wonderful value');">Test!</button>
#
#    """)
    view.show()

    app.exec_()

