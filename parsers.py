import zipfile
import pyPdf
from xml.etree import cElementTree as ElementTree
import os

def fb2parser_int(xmldoc):
    namespace = "{http://www.gribuser.ru/xml/fictionbook/2.0}"

    di = {}
    descr = xmldoc.getchildren()[0].getchildren()[0]
    for child in descr.getchildren():
        t = child.tag.replace(namespace, "")
        if t == "author":
            for c in child.getchildren():
                tt = c.tag.replace(namespace, "")
                di[tt] = c.text
        else:
            di[t] = child.text

#    aList = ti.getElementsByTagName("author")
#    bauthor = ', '.join([getnText(aut.getElementsByTagName("last-name")[0].childNodes)+" "+getnText(aut.getElementsByTagName("first-name")[0].childNodes) for aut in aList])
    bauthor = ', '.join([ di.get("last-name", "unknown"), di.get("first-name", "unknown") ]) # only last author is listed!!!
    btitle = di.get("book-title", "unknown")
    bgenre = di.get("genre", "unknown")

    return (bauthor, btitle, bgenre)

def fb2parser(file):
    tree = ElementTree.parse(file)
    return fb2parser_int(tree)

def fb2zipparser(file):
    zf = zipfile.ZipFile(file)
    for fname in zf.namelist():
        if fname.endswith(".fb2"):
            data = zf.read(fname)
            tree = ElementTree.fromstring(data)
    return fb2parser_int(tree)

def epubparser(file):
    tree = None

    dc_namespace = "{http://purl.org/dc/elements/1.1/}"

    zf = zipfile.ZipFile(file)

    container = ElementTree.fromstring(zf.read("META-INF/container.xml"))
    rootfile = container.find("{urn:oasis:names:tc:opendocument:xmlns:container}rootfiles/{urn:oasis:names:tc:opendocument:xmlns:container}rootfile").get("full-path")

    data = zf.read(rootfile)
    tree = ElementTree.fromstring(data)

    if tree:
        e = tree.find('{http://www.idpf.org/2007/opf}metadata')
        if e:
            di = {}
            for child in e:
                di[child.tag.replace(dc_namespace, "")] = child.text

            bauthor = di.get("creator", "unknown")
            btitle = di.get("title", "unknown")
            bgenre = di.get("subject", "unknown")

            return (bauthor, btitle, bgenre)
        else:
            return defaultparser(file)
    else:
        return defaultparser(file)

def pdfparser(filename):
    p = pyPdf.PdfFileReader(file(filename, "rb"))
    try:
        di = p.documentInfo
    except:
        return ("", os.path.basename(filename), "")
    if di.title != None:
        return (str(di.author), str(di.title), "")
    else:
        return ("", os.path.basename(filename), "")

def defaultparser(file):
    return ("", os.path.basename(file), "")

parsers = { ".fb2.zip" : fb2zipparser, ".fb2" : fb2parser, ".pdf" : pdfparser, ".epub" : epubparser }

def parseFile(file):

    bauthor = btitle = bgenre = ""

    resparser = defaultparser
    for ext in parsers:
        if file.endswith(ext):
            resparser = parsers[ext]
    try:
        (bauthor, btitle, bgenre) = resparser(file)
    except:
        (bauthor, btitle, bgenre) = defaultparser(file)

    return (bauthor, btitle, bgenre)


