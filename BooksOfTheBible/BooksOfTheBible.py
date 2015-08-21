#!/usr/bin/env python

import json

class BooksOfTheBible:
    """
    Data class containing the books of the Bible and the Chapters
    """
    def __init__(self, input_file):
        ifile = open(input_file,'r')
        rawData = ''.join(ifile.readlines())
        self.data = json.loads(rawData)


    def returnBooks(self):
        return self.data

myfile = '/home/thawes/src/sources/GetBible/BooksOfTheBible/BibleBooks.json'
b = BooksOfTheBible(myfile)
