#!/usr/bin/env python

from xml.sax.handler import ContentHandler
import xml.sax
from json import loads
from lxml import etree
from collections import OrderedDict
from bs4 import BeautifulSoup

biblev = '/home/thawes/src/sources/GetBible/BooksOfTheBible/BibleBooks.json'

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
        ret = etree.Element('chapter')
        osisId = "%s.%s" % (self.books[book]['osisId'], chapter)
        ret.attrib['osisID'] = osisId
        print "\tgetting %s" % osisId

        data = ''
        fp = '%s/%s' % (self.version, self._generateFilename(book, chapter))
        with open(fp, 'r') as f:
            data = ''.join(f.readlines())

        soup = BeautifulSoup(data, 'html.parser')

        ## Find verses, and use sax parser to find notes and strongs references.
        span = soup.find_all('span')
        for x in span:
            if x.has_attr('class') and 'verse' in x['class'][0]:
                versenum = x['class'][0].split('-')[1]
                x['osisID'] = '%s.%s.%s' % (
                    self.books[book]['osisId'], chapter, versenum)
                ret.append(self.parseVerse(book, x['osisID'], x))

        ## The notes in the current text are empty. Find the referenced notes and add
        ## them to the notes tags.

        notes = {}
        a_ref = soup.find_all('div')
        for x in a_ref:
            if x.has_attr('id') and 'footnote-' in x['id']:
                fn_num = x['id'].split('-')[1].strip()
                note = x.find_all('li')[0]
                note.span.clear()
                note.i.clear()
                versenum = note.a.text.replace(':', '.')
                note.a.clear()
                fnote = note.text.strip()
                if fnote[0] == '-':
                    fnote = fnote[1:].strip()
                notes.update({'%s.%s' % (osisId, fn_num): fnote})

        for note in ret.iter('note'):
            note.text = notes[note.attrib['osisRef']]

        ## DEBUG Printing
        #print notes
        #print etree.tostring(ret, encoding='unicode', pretty_print=True)
        return ret

    def parseVerse(self, book, osisId, versedata):
        """ Method for parsing verse data. """
        p = BibleHandler(osisId, self.books[book]['strongsRef'])
        return p.parse('%s' % versedata)


    def writeBible(self):
        self.generateOsis()
        f = open("/home/thawes/Documents/%s.xml" % self.version, 'w')
        f.write(etree.tostring(self.osisdoc, pretty_print=True))
        f.close()
        print "done."




class BibleHandler(ContentHandler):
    def __init__(self, osisId, strongsref):
        """ @params storngsref A single letter specifying the specific Strongs
                               dictionary for Strongs references (e.g. H for
                               Hebrew, G for Greek).
        """
        self.osisId = osisId
        self.strongsref = strongsref
        self._result = """<verse osisID="%s">""" % self.osisId
        self.depth = []

    def parse(self, f):
        xml.sax.parseString(f, self)
        self._result += "</verse>"
        edoc = None
        try:
            xdoc = etree.XML(self._result)
            edoc = etree.ElementTree(xdoc)
        except Exception,e:
            print e.message
            print self._result
        return edoc.getroot()

    def characters(self, data):
        if self.depth[-1] != 'a':
            if len(data) > 0 and data[0] == ' ':
                data = ' %s' % data.lstrip()
            if len(data) > 0 and data[-1] == ' ':
                data = '%s ' % data.rstrip()
            self._result += data

    def startElement(self, name, attrs):
        if name == 'a':
            if 'data-strongs-number' in attrs:
                self.depth.append('strongs')
                self._result += """<w lemma="strong:%s%s">""" % (
                    self.strongsref, attrs['data-strongs-number'])
            else:
                self.depth.append(name)
        elif name == 'sup':
            if 'data-identifier' in attrs:
                self.depth.append('note')
                self._result += """<note osisID="%s!%s" """ % (
                    self.osisId, attrs['data-identifier'])
                self._result += """osisRef="%s" """ % self.osisId
                self._result += """placement="foot" """
                self._result += """type="translation">"""
            else:
                self.depth.append(name)
        else:
            self.depth.append(name)

    def endElement(self, name):
        rname = self.depth.pop()
        if rname == 'strongs':
            self._result += "</w>"
        elif rname == 'note':
            self._result += "</note>"

g = BibleParse('web')
g.writeBible()
#c = g.getBook("GEN")
#s = g.getChapter('GEN','1')
