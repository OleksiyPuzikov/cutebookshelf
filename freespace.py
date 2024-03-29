"""
Other possible implementations are:

os.popen("df -k dir").split()[-5]

"""

import sys
import os

try:
    os.statvfs

except AttributeError:

    def freespace(path):
        """ freespace(path) -> integer
        Return the number of bytes available to the user on the file system
        pointed to by path."""
        if os.name == "nt":
            return int(str(os.popen4("dir %s /AD" % path)[1].readlines()[-1]).split()[2].replace("\xff", ""))
        else:
            return 0

    def freespace_ex(path):
        return (freespace(path), 0) # I'll follow up with this later...

else:
    import statvfs

    def freespace(path):
        """ freespace(path) -> integer
        Return the number of bytes available to the user on the file system
        pointed to by path."""
        s = os.statvfs(path)
        return s[statvfs.F_BAVAIL] * long(s[statvfs.F_FRSIZE]) # apparently, on MacOS X it's F_FRSIZE

    def freespace_ex(path):
        """ freespace(path) -> (integer, integer)
        Return the number of bytes available to the user on the file system
        pointed to by path, along with total number of bytes over there... """
        s = os.statvfs(path)
        return ( s[statvfs.F_BAVAIL] * long(s[statvfs.F_FRSIZE]), s[statvfs.F_BLOCKS] * long(s[statvfs.F_FRSIZE])) # apparently, on MacOS X it's F_FRSIZE


if __name__=='__main__':
    path = sys.argv[1]
    fs = freespace(path)
    print 'Free space on %s: %i (%iK, %iM, %iG)' % (path, fs, fs/1024, fs/1024/1024, fs/1024/1024/1024) 
