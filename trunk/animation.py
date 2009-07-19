from PyQt4 import QtCore, QtGui

class Animation:
    def __init__(self, duration=500):
        self.timeLine = QtCore.QTimeLine(duration)
        self.timeLine.setFrameRange(0, 100)
        QtCore.QObject.connect(self.timeLine, QtCore.SIGNAL('frameChanged(int)'), self.animate)
        QtCore.QObject.connect(self.timeLine, QtCore.SIGNAL('finished()'), self.finalize)

    def animate(self, frame):
        pass

    def finalize(self):
        pass

    def running(self):
        return self.timeLine.state() == QtCore.QTimeLine.Running

    def start(self):
        self.timeLine.start()

    def kill(self):
        self.timeLine.stop()
        self.finalize()

class FadeSwitch(Animation):
    def __init__(self, label, bgcolor):
        Animation.__init__(self, duration=600)
        self.timeLine.setUpdateInterval(50)

        self.label = label

        self.sColor = QtGui.QColor(255, 255, 0)
        self.dColor = bgcolor

        self.r0 = self.sColor.red()
        self.g0 = self.sColor.green()
        self.b0 = self.sColor.blue()

        self.r1 = self.dColor.red()
        self.g1 = self.dColor.green()
        self.b1 = self.dColor.blue()

        self.label.setStyleSheet("background-color: %s;" % self.sColor.name())
        self.label.update()

    def animate(self, value):

        gg = self.g0+(self.g1-self.g0)*value/100
        bb = self.b0+(self.b1-self.b0)*value/100
        rr = self.r0+(self.r1-self.r0)*value/100

        c = QtGui.QColor(rr, gg, bb)

        self.label.setStyleSheet("background-color: %s;" % c.name())
        self.label.update()


    def finalize(self):
        self.label.setStyleSheet("background-color: transparent;")
        self.label.update()
