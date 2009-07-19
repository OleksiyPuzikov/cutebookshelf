import os
import sys
import shutil

from PyQt4 import QtCore, QtGui

lbsDirectionSrcToDest = 0
lbsDirectionDestToSrc = 1
lbsDirectionBidirect = 2

class SyncEngine(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)

    def uniq(self, alist): # Fastest order preserving doublicates removal from arrays.
        set = {}
        return [set.setdefault(e,e) for e in alist if e not in set]

    def get_files(self, root):
        all_files = []
        try:
            elements = os.listdir( root )
            for element in elements:
                path = os.path.join(root,element)
                if os.path.isdir( path ):
                    all_files.extend( self.get_files( path ) )
                elif os.path.isfile( path ):
                    all_files.append( os.path.join(root,element) )
        except:
            pass
        return all_files

    def sync(self, srcd, destd, direction = lbsDirectionSrcToDest, e = []):

        self.emit(QtCore.SIGNAL("started(QString)"), "Synchronizing to %s" % srcd)

        s = self.get_files(srcd)
        d = self.get_files(destd)

        s = [filename.replace(srcd, "") for filename in s]
        d = [filename.replace(destd, "") for filename in d]

#        print s, d

        src = set(s)
        dest = set(d)
    #    excludes = set(e)

        intersect = src.intersection(dest)
        diff_src = src.difference(intersect)
        diff_dest = dest.difference(intersect)

#        print "to delete", len(diff_dest), diff_dest
#        print "to copy", len(diff_src), diff_src

        total_progress = len(diff_dest)+len(diff_src)

        self.emit(QtCore.SIGNAL("started(QString)"), "Synchronizing to %s" % destd)

        # delete files
        for c, f in enumerate(sorted(diff_dest)):
            per = int(round(100.0*c/total_progress))
#            print c, per, f
#            print "rm ", destd+f
            os.remove(destd+f)
            self.emit(QtCore.SIGNAL("progress(int,QString)"), per, f)

        # prepare directory names for deletion and creation
        del_dirs = [os.path.dirname(dir) for dir in sorted(diff_dest)]
        del_dirs = self.uniq(del_dirs)

        cre_dirs = [os.path.dirname(dir) for dir in sorted(diff_src)]
        cre_dirs = self.uniq(cre_dirs)

        # delete empty directories
        for dir in del_dirs:
            if destd+dir != destd:
                if dir not in cre_dirs:
#                    print "rmdir ", destd+dir
                    try:
                        os.removedirs(destd+dir)
                    except:
                        pass

        # create new directories
        for dir in cre_dirs:
#            print "mkdir ", destd+dir
            if not os.path.isdir(destd+dir):
                os.makedirs(destd+dir)

        # copy files
        for c, f in enumerate(sorted(diff_src)):
            per = int(round(100.0*(c+len(diff_dest))/total_progress))
#            print c+len(diff_dest), per, f
#            print "cp %s %s" % (srcd+f, destd+f)
            shutil.copy(srcd+f, destd+f)
            self.emit(QtCore.SIGNAL("progress(int,QString)"),  per, f)

        self.emit(QtCore.SIGNAL("finished(QString)"), "Synchronizing to %s finished" % destd)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    sync = SyncEngine()
    sync.sync("/local1/seq5/books/", "/local1/seq5/books2/")

#    app.exec_()


