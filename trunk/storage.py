import os.path
from pprint import pprint

try:
   import cPickle as pickle
except:
   import pickle

data = {}
storagePath = os.path.expanduser(os.path.expandvars("~/qbs.storage"))

settings = {}
settingsPath = os.path.expanduser(os.path.expandvars("~/qbs.ini"))

header_sizes = [300, 200, 50, 50, 100, 200, 0]

####################################################################################

def loadData():
    global data

#    try:
    fh = open(storagePath, "rb")
    data = pickle.load(fh)
    fh.close()
#    except:
#        pass

#    import pprint
#    pprint.pprint(data)

def saveData():
    global data

#    import pprint
#    pprint.pprint(data)

    fh = open(storagePath, "w")
    pickle.dump(data, fh)
    fh.close()

####################################################################################

def saveSettings():
    global settings
    global header_sizes

    for x, c in enumerate(header_sizes): # number, value
        settings["col%d" % x] = c

#    print settings

    fout = open(settingsPath, "w")
    pprint(settings, fout)
    fout.close()

def loadSettings():
    global settings
    global header_sizes

    try:
        fin = open(settingsPath, "r")
        settings = eval(fin.read()) # can this be a security threat?
        fin.close()

        for x, c in enumerate(header_sizes): # number, value
            header_sizes[x] = settings.get("col%d" % x, c)
        
    except:
        pass

    return settings

####################################################################################

if __name__ == "__main__":
    print storagePath
