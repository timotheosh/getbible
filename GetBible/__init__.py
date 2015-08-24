#!/usr/bin/env python

from requests import get
from json import loads
from os import system
from collections import OrderedDict

biblev = '/home/thawes/src/sources/GetBible/BooksOfTheBible/BibleBooks.json'


class GetBible:
    """ Class for downloading a Bible from the web."""

    def __init__(self, version):
        """
        version = version of the bible wanted, ex. web for World English Bible
        """
        self.version = version

        f = open(biblev,'r')

        self.books = loads(''.join(f.readlines()), object_pairs_hook=OrderedDict)

    def _generateUrl(self, book, chapter):
        return 'http://www.biblestudytools.com/%s/%s/%s.html' % (
            self.version, self.books[book]['name'].lower().replace(' ', '-'), chapter)

    def _generateStudybibleInfoUrl(self, book, chapter):
        import urllib
        refpath = urllib.quote('%s %s' % (self.books[book]['name'], chapter))
        return 'http://studybible.info/%s/%s' % (self.version, refpath)


    def _generateFilename(self, book, chapter):
        return '%s_%s.html' % (self.books[book]['name'].replace(' ', '-'), chapter)

    def getBible(self):
        for book in self.books.keys():
            print "Retrieving: %s" % self.books[book]['name']
            self._getBook(book)

    def _getBook(self, bookname):
        i = 0
        while i < int(self.books[bookname]['numChapters']):
            i += 1
            self._getChapter(bookname, i)


    def _getChapter(self, book, chapter):
        print "Retrieving %s %s" % (book, chapter)
        fp = '%s/%s' % (self.version, self._generateFilename(book, chapter))
        # data = get(self._generateUrl(book, chapter))
        data = get(self._generateStudybibleInfoUrl(book, chapter))
        if data.status_code == 200:
            system('mkdir -p %s' % self.version)
            f = open(fp, 'w')
            f.write(data.text.encode('utf8'))
            f.close()
        else:
            print "ERROR STATUS %s: %s %s" % (data.status_code, book, chapter)

g = GetBible('ASV_Strongs')
g.getBible()
