# -*- coding: utf-8 -*-
#

import os
from .parseUsfm import parseString
from .books import silNames

class DummyFile(object):
    def close(self):
        pass
    def write(self, str):
        pass

class TokenStream(object):
    def __init__(self, array):
        self.tokens = array
        self.i = 0

    def copy(self):
        t = TokenStream(self.tokens)
        t.i = self.i
        return t

    def next(self, n=1):
        self.i = self.i + n
        return self.tokens[self.i -1]

    def previous(self, n=1):
        self.i = self.i - n
        return self.tokens[self.i -1]

    def peek(self):
        return self.tokens[self.i -1]

    def atEnd(self):
        return self.i == len(self.tokens) - 1

    def moveTo(self, p):
        self.i = p

    def position(self):
        return self.i

class ReaderPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = '001'    # Current Book
        self.cc = '001'    # Current Chapter
        self.cv = '001'    # Currrent Verse
        self.indentFlag = False
        self.inSpanFlag = False
        self.inParaFlag = False
        self.tokenStream = None

    def renderStream(self, ts):
        self.tokenStream = ts
        while not self.tokenStream.atEnd():
            self.tokenStream.next().renderOn(self)
        self.close()

    def close(self):
        self.writeFooter()
        self.f.close() # Close final file

    def writeHeader(self, v=''):
        self.write('<!--\nname: Open English Bible\ncontent: %(book)s %(chapter)s (OEB)\nauthor: Russell Allen\ndate:   4/6/2012 3:34:43 PM\n-->' % {"book": books.fullName(self.cb), "chapter": str(int(self.cc))})
        self.write('\n<!DOCTYPE html>')
        self.write('\n<html lang="en" dir="ltr">')
        self.write('\n<head>')
        self.write('\n\t<meta charset="utf-8" /> ')
        self.write('\n\t<title>%(book)s %(chapter)s (OEB)</title>' % {"book": books.fullName(self.cb), "chapter": str(int(self.cc))})
        self.write('\n\t<meta name="viewport" content="width=device-width, initial-scale=1" />')
        self.write('\n\t<script src="../../../js/mobile.js"></script>')
        self.write('\n\t<link href="../../../css/mobile.css" rel="stylesheet" />')
        self.write('\n</head>')
        self.write('\n<body>')
        self.write('\n<div data-role="page">')
        self.write('\n\t<div data-role="header">')
        self.write('\n\t\t<a href="%(book)s.%(chapter)s.html" data-icon="arrow-l">%(fullbook)s %(chapter)s</a>' % {"fullbook": books.fullName(self.previousChapter()[0]), "book": books.readerName(self.previousChapter()[0]), "chapter": str(self.previousChapter()[1])})
        self.write('\n\t\t<h1>%(book)s %(chapter)s (OEB)</h1>' % {"book": books.fullName(self.cb), "chapter": str(int(self.cc))})
        self.write('\n\t\t<a href="%(book)s.%(chapter)s.html" data-icon="arrow-r">%(fullbook)s %(chapter)s</a>' % {"fullbook": books.fullName(self.nextChapter()[0]), "book": books.readerName(self.nextChapter()[0]), "chapter": str(self.nextChapter()[1])})
        self.write('\n\t</div>')
        self.write('\n\t<div data-role="content">')
        self.write('\n<div class="chapter OEB nt %(book)s_%(chapter)s" data-osis="%(book)s.%(chapter)s" lang="en" dir="ltr">' % {"book": books.readerName(self.cb), "chapter": str(int(self.cc))})
        self.write('\n<h2 class="chapter-num">' + v + '</h2>\n<p>')

    def writeFooter(self):
        self.write('\n</div>')
        self.write('\n')
        self.write('\n\t</div>')
        self.write('\n\t<div data-role="footer">	')
        self.write('\n\t\t<div data-role="navbar">')
        self.write('\n\t\t\t<ul>')
        self.write('\n\t\t\t\t<li><a href="%(book)s.%(chapter)s.html" data-icon="arrow-l">%(fullbook)s %(chapter)s</a></li>' % {"fullbook": books.fullName(self.previousChapter()[0]), "book": books.readerName(self.previousChapter()[0]), "chapter": str(self.previousChapter()[1])})
        self.write('\n\t\t\t\t<li><a href="index.html" data-icon="home">Books</a></li>')
        self.write('\n\t\t\t\t<li><a href="%(book)s.%(chapter)s.html" data-icon="arrow-r">%(fullbook)s %(chapter)s</a></li>' % {"fullbook": books.fullName(self.nextChapter()[0]), "book": books.readerName(self.nextChapter()[0]), "chapter": str(self.nextChapter()[1])})
        self.write('\n\t\t\t</ul>')
        self.write('\n\t\t</div>')
        self.write('\n\t</div>')
        self.write('\n</div>')
        self.write('\n</body>')
        self.write('\n</html>')

    def previousChapter(self):
        t = self.tokenStream.copy()
        c = 1
        b = self.cb
        p = t.position()
        if t.peek().isC(): t.previous(1)
        while t.position() > 0:
            n = t.previous()
            if n.isC():
                c = n.value
                break
        if int(c) > int(self.cc):
            b = str(int(self.cb)-1)
        return (b, c)

    def nextChapter(self):
        t = self.tokenStream.copy()
        c = self.cc
        b = self.cb
        while not t.atEnd():
            n = next(t)
            if n.isC():
                c = n.value
                break
        if int(c) < int(self.cc): # We must have started new book
            b = str(int(self.cb)+1)
        return (b,c)

    def openNextFile(self):
        self.f = open(self.outputDir + '/' + books.readerName(self.cb) + '.' + str(int(self.cc)) + '.html', 'w')

    def incrementChapter(self, chapter):
        self.cc = chapter

    def write(self, unicodeString):
        self.f.write(unicodeString.encode('utf-8'))

    def writeIndent(self, level):
        if level == 0:
            self.indentFlag = False
            self.write('<br /><br />')
            return
        if not self.indentFlag:
            self.indentFlag = True
            self.write('<br />')
        self.write('<br />')
        self.write('&nbsp;&nbsp;&nbsp;&nbsp;' * level)

    def renderID(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write('</span>')
        if self.inParaFlag:
                self.inParaFlag = False
                self.write('\n</p>')
        self.write('\n</div>')
        self.tokenStream.previous(2) # Go back to end of last chapter
        self.writeFooter()
        self.f.close()
        self.tokenStream.next(2) # Go forward again to start of this chapter.
        self.cb = books.bookKeyForIdValue(token.value)
        self.incrementChapter(1)
        self.openNextFile()
        self.writeHeader()
        self.indentFlag = False

    def renderIDE(self, token):     pass
    def renderSTS(self, token):     pass
    def renderH(self, token):       self.write('\n<h1 class="book-name">' + token.value + '</h1>')
    def renderMT(self, token):      self.write('\n<h3>' + token.value + '</h3>')
    def renderMT2(self, token):      self.write('\n<h3>' + token.value + '</h3>')
    def renderMS(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write('</span>')
        if self.inParaFlag:
                self.inParaFlag = False
                self.write('\n</p>')
        self.write('\n<h4>' + token.value + '</h4>')
    def renderMS2(self, token):     self.write('\n<h5>' + token.value + '</h5>')
    def renderP(self, token):
        if self.inSpanFlag:
                self.inSpanFlag = False
                self.write('</span>')
        self.indentFlag = False
        if self.inParaFlag:
                self.inParaFlag = False
                self.write('\n</p>')
        self.inParaFlag = True
        self.write('\n<p>')
    def renderS(self, token):
        self.indentFlag = False
    def renderS2(self, token):
        self.indentFlag = False
    def renderC(self, token):
        if token.value.zfill(3) == '001':
            self.incrementChapter(token.value.zfill(3))
            self.write('\n<h2 class="chapter-num">' + token.value + '</h2>\n<p>')
            self.inParaFlag = True
        else:
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write('</span>')
            if self.inParaFlag:
                    self.inParaFlag = False
                    self.write('\n</p>')
            self.tokenStream.previous(2) # Go back to end of last chapter
            self.writeFooter()
            self.f.close()
            self.tokenStream.next(2) # Go forward again to start of this chapter.
            self.incrementChapter(token.value.zfill(3))
            self.openNextFile()
            self.writeHeader(token.value)
            self.inParaFlag = True
    def renderV(self, token):
        if '-' in token.value: # Complex, eg 42-43
            self.cv = token.value[:token.value.index('-')].zfill(3)
        else:
            self.cv = token.value.zfill(3)
        if self.cv == '001':
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write('</span>')
            self.inSpanFlag = True
            self.write('\n<span class="verse ' + books.readerName(self.cb) + "_" + str(int(self.cc)) + "_" + str(int(self.cv)) + '" data-osis="' + books.readerName(self.cb) + '.' + str(int(self.cc)) + "." + str(int(self.cv)) + '"><span class="verse-num v-1">' + token.value + '&nbsp;</span>')
        else:
            if self.inSpanFlag:
                    self.inSpanFlag = False
                    self.write('</span>')
            self.inSpanFlag = True
            self.write('\n<span class="verse ' + books.readerName(self.cb) + "_" + str(int(self.cc)) + "_" + str(int(self.cv)) + '" data-osis="' + books.readerName(self.cb) + '.' + str(int(self.cc)) + "." + str(int(self.cv)) + '"><span class="verse-num v-' + str(int(self.cv)) + '">' + token.value + '&nbsp;</span>')

    def renderWJS(self, token):     self.write('<span class="woc">')
    def renderWJE(self, token):     self.write('</span>')
    def renderTEXT(self, token):    self.write(token.value)
    def renderQ(self, token):       self.writeIndent(1)
    def renderQ1(self, token):      self.writeIndent(1)
    def renderQ2(self, token):      self.writeIndent(2)
    def renderQ3(self, token):      self.writeIndent(3)
    def renderNB(self, token):      self.writeIndent(0)
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      self.write('{')
    def renderFE(self, token):      self.write('}')
    def renderFP(self, token):      pass
    def renderIS(self, token):      self.write('<i>')
    def renderIE(self, token):      self.write('</i>')
    def renderBDS(self, token):     self.f.write('<b>')
    def renderBDE(self, token):     self.f.write('</b>')
    def renderBDITS(self, token):   self.f.write('<b><i>')
    def renderBDITE(self, token):   self.f.write('</b></i>')
    def renderB(self, token):       self.write('<p />')
    def renderD(self, token):       self.write('<p />')
    def renderADDS(self, token):    self.write('<i>')
    def renderADDE(self, token):    self.write('</i>')
    def renderLI(self, token):      self.write('<p />')
    def renderSP(self, token):      self.write('<p />')
    def renderNDS(self, token):     self.write(' ')
    def renderNDE(self, token):     self.write(' ')
    def renderPBR(self, token):     self.write('<br />')
    def renderD(self, token):       pass # For now
    def renderREM(self, token):     pass # This is for comments in the USFM
    def render_imt1(self, token):   self.write('\n<h3>' + token.value + '</h3>')
    def render_imt2(self, token):   self.write('\n<h3>' + token.value + '</h3>')
    def render_imt3(self, token):   self.write('\n<h3>' + token.value + '</h3>')


class TransformForReader(object):
    outputDir = ''
    patchedDir = ''
    prefaceDir = ''

    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == '\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def setupAndRun(self, patchedDir, outputDir):
        self.patchedDir = patchedDir
        self.outputDir = outputDir
        self.booksUsfm = books.loadBooks(patchedDir)
        self.printer = ReaderPrinter(self.outputDir)

        tokens = []
        print("    ** Parsing")
        for bookName in silNames:
            if bookName in self.booksUsfm:
                tokens = tokens + parseString(self.booksUsfm[bookName])
        self.tokenStream = TokenStream(tokens)

        print("    ** Rendering")
        self.printer.renderStream(self.tokenStream)

