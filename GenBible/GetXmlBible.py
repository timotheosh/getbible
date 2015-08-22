#!/usr/bin/env python

from requests import get
from json import loads
from lxml import etree, builder
from collections import OrderedDict
from xml.sax.handler import ContentHandler
from bs4 import BeautifulSoup
import xml.sax

biblev = '/home/thawes/src/sources/GetBible/BooksOfTheBible/BibleBooks.json'


class GetXmlBible:
    """ GetBible program using a Sax Parser
    """
    def __init__(self, version):
        """
        version = version of the bible wanted, ex. web for World English Bible
        """
        self.version = version
        self.osisdoc = etree.Element("osis")

        f = open(biblev,'r')
        self.books = loads(''.join(f.readlines()), object_pairs_hook=OrderedDict)

    def generateOsis(self):
        osisText = etree.Element('osisText')
        osisText.attrib['osisRefWork'] = 'Bible'
        osisText.attrib['osisIDWork'] = self.version
        osisText.attrib['lang'] = 'en'
        for book in self.books.keys():
            print "Retrieving: %s" % self.books[book]['name']
            osisText.append(self.getBook(book))
        self.osisdoc.append(osisText)

    def generateUrl(self, book, chapter):
        return 'http://www.biblestudytools.com/%s/%s/%s.html' % (
            self.version, self.books[book]['name'].lower().replace(' ', '-'), chapter)

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
        ret = etree.Element('chapter')
        osisId = "%s.%s" % (self.books[book]['osisId'], chapter)
        ret.attrib['osisID'] = osisId
        print "\tgetting %s" % osisId

        soup = ''
        data = get(self.generateUrl(book, chapter))
        if data.status_code == 200:
            soup = BeautifulSoup(data.text, 'html.parser')
            span = soup.find_all('span')
            for x in span:
                if x.has_attr('class') and 'verse' in x['class'][0]:
                    self.parseVerse(x)
                    """
                    versenum = x['class'][0].split('-')[1]
                    x['osisID'] = '%s.%s.%s' % (self.books[book]['osisId'], chapter, versenum)
                    verse = etree.Element('verse')
                    verse.attrib['osisID'] = "%s.%s" % (osisId, versenum)
                    verse.text = x.get_text().strip()
                    ret.append(verse)
                    """
        return ret

    def parseVerse(self, versedata):
        """ Method for parsing verse data. """
        print BibleHandler().parse('%s' % versedata)

    def writeBible(self):
        self.generateOsis()
        f = open("/home/thawes/Documents/%s.xml" % self.version, 'w')
        f.write(etree.tostring(self.osisdoc, pretty_print=True))
        f.close()
        print "done."

class BibleHandler(ContentHandler):
    def __init__(self):
        self._charBuffer = []
        self._result = []
        self.depth = []

    def _flushCharBuffer(self):
        s = ''.join(self._charBuffer)
        self._charBuffer = []
        return s

    def parse(self, f):
        xml.sax.parseString(f, self)
        return self._result

    def characters(self, data):
        name = self.depth[-1]
        if name != 'sup' and name != 'a':
            self._charBuffer.append(data)

    def startElement(self, name, attrs):
        if name == 'a':
            if 'class' in attrs and 'strongs' in attrs['class']:
                self.depth.append('strongs')
                print "strongs"
            else:
                self.depth.append(name)
        else:
            self.depth.append(name)

    def endElement(self, name):
        self.depth.pop()
        self._result.append(self._flushCharBuffer())


g = GetXmlBible('nas')
#g.writeBible()
#c = g.getBook("GEN")
s = g.getChapter('GEN','1')
