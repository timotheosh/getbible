#!/usr/bin/env python

from requests import get
from bs4 import BeautifulSoup
from json import loads
from lxml import etree, builder
from collections import OrderedDict

biblev = '/home/thawes/src/sources/GetBible/BooksOfTheBible/BibleBooks.json'

class GetBible:
    """
    Class for retrieving Bible texts and converting to something
    useful to Sword (http://crosswire.org).
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
                    versenum = x['class'][0].split('-')[1]
                    x['osisID'] = '%s.%s.%s' % (self.books[book]['osisId'], chapter, versenum)
                    verse = etree.Element('verse')
                    verse.attrib['osisID'] = "%s.%s" % (osisId, versenum)
                    verse.text = x.get_text().strip()
                    ret.append(verse)
        return ret

    def writeBible(self):
        self.generateOsis()
        f = open("/home/thawes/Documents/%s.xml" % self.version, 'w')
        f.write(etree.tostring(self.osisdoc, pretty_print=True))
        f.close()
        print "done."

g = GetBible('web')
#g.writeBible()
#c = g.getBook("GEN")
s = g.getChapter('GEN','1')
