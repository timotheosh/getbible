#!/usr/bin/env python

from xml.sax.handler import ContentHandler
import xml.sax
from json import loads
from lxml import etree
from collections import OrderedDict
from bs4 import BeautifulSoup

biblev = '/home/thawes/src/sources/GetBible/BooksOfTheBible/BibleBooks.json'
datadir = '/home/thawes/src/sources/GetBible/Data'

class BibleParse:
    """ Parsing Bible in html files. """
    def __init__(self, version):
        """ @params version Bible version acronym (e.g. KJV). """
        self.version = version
        self.osisdoc = etree.Element("osis")
        f = open(biblev,'r')
        self.books = loads(''.join(f.readlines()), object_pairs_hook=OrderedDict)


    def _generateFilename(self, book, chapter):
        return '%s_%s.html' % (self.books[book]['name'].replace(' ', '-'), chapter)


    def generateOsis(self):
        osisText = etree.Element('osisText')
        osisText.attrib['osisRefWork'] = 'Bible'
        osisText.attrib['osisIDWork'] = self.version
        osisText.attrib['lang'] = 'en'
        for book in self.books.keys():
            print "Retrieving: %s" % self.books[book]['name']
            osisText.append(self.getBook(book))
        self.osisdoc.append(osisText)


    def getBook(self, bookname):
        osisId = self.books[bookname]['osisId']
        book = etree.Element('div')
        book.attrib['osisID'] = osisId

        i = 0
        while i < int(self.books[bookname]['numChapters']):
            i += 1
            book.append(self.getChapter(bookname, i))
        return book


    def getChapter(self, book, chapter):
        osisId = "%s.%s" % (self.books[book]['osisId'], chapter)
        print "\tgetting %s" % osisId

        data = ''
        fp = '%s/%s/%s' % (datadir, self.version, self._generateFilename(book, chapter))
        with open(fp, 'r') as f:
            data = ''.join(f.readlines())

        soup = BeautifulSoup(data, 'html.parser')
        data = soup.article.div
        p = BibleHandler(osisId)
        ret = p.parse('%s' % data)

        return ret


    def writeBible(self):
        self.generateOsis()
        f = open("/home/thawes/Documents/%s.xml" % self.version, 'w')
        f.write(etree.tostring(self.osisdoc, pretty_print=True))
        f.close()
        print "done."




class BibleHandler(ContentHandler):
    def __init__(self, osisId):
        self.osisId = osisId
        self._result = etree.Element('chapter')
        self._result.attrib['osisID'] = self.osisId
        self._verse = None
        self.depth = []
        self.writeVerse = False

    def parse(self, f):
        xml.sax.parseString(f, self)
        return self._result

    def characters(self, data):
        if self.depth[-1] == 'verseref' and self._verse == None:
            self._verse = etree.Element('verse')
            self._verse.attrib['osisID'] = "%s.%s" % (
                self.osisId, data)
        elif self._verse != None:
            if len(data.strip()) > 0:
                self._verse.text = data
                self._result.append(self._verse)
                self._verse = None
                self.writeVerse = False

    def startElement(self, name, attrs):
        if name == 'a':
            if 'class' in attrs and attrs['class'] == 'verse_ref CLV':
                self.depth.append('verseref')
            else:
                self.depth.append(name)
        else:
            self.depth.append(name)

    def endElement(self, name):
        self.depth.pop()


g = BibleParse('CLV')
DEBUG = False
#DEBUG = True

if not DEBUG:
    g.writeBible()

else:
    #c = g.getBook("GEN")

    ## DEBUG Printing
    s = g.getChapter('GEN','1')
    print etree.tostring(s, encoding='unicode', pretty_print=True)
