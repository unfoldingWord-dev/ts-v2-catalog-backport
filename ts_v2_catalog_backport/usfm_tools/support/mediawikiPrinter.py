# -*- coding: utf-8 -*-
#

import os
from .parseUsfm import parseString
from .books import bookKeyForIdValue, loadBooks, silNames

class DummyFile(object):
    def close(self):
        pass
    def write(self, str):
        pass

class MediaWikiPrinter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.f = DummyFile()
        self.cb = ''       # Current Book
        self.cc = '001'    # Current Chapter
        self.ccUnfil = '1' # same, not padded.
        self.cv = '001'    # Currrent Verse
        self.indentFlag   = False
        self.footnoteFlag = False

    def write(self, unicodeString):
        self.f.write(unicodeString.encode('utf-8'))

    def renderID(self, token):
        self.write('</p>')
        self.f.close()
        self.cb = bookKeyForIdValue(token.value)
        self.f = open(self.outputDir + '/c' + self.cb + '001.html', 'w')
        self.write('\n<!-- \\id ' + self.cb + ' -->')
        self.indentFlag = False
    def renderIDE(self, token):     pass
    def renderSTS(self, token):     pass
    def renderTOC2(self, token):    self.write(' Bible:' + token.value + '_# ')
    def renderH(self, token):       self.write('\n<!-- \\h ' + token.value + ' -->')
    def renderMT(self, token):      self.write('\n<!-- \\mt1 ' + token.value + ' -->')
    def renderMS(self, token):      pass
    def renderMS2(self, token):     pass
    def renderP(self, token):
        self.indentFlag = False
        self.write('\n\n')
    def renderS(self, token):
        self.indentFlag = False
        self.write('\n=== ' + token.value + ' === ')
    def renderS2(self, token):
        self.indentFlag = False
        pass
    def renderR(self, token):       self.write('\n<span class="srefs">' + token.value + '</span>')
    def renderC(self, token):
        self.cc = token.value.zfill(3)
        self.ccUnfil = token.getValue()
        if self.cc == '001':
            self.write('Bible:' + self.cb + '_' + token.value + ' ')
        else:
            self.write('\n\n')
            self.f.close()
            self.f = open(self.outputDir + '/c' + self.cb + self.cc + '.html', 'w')
            self.write('Bible:' + self.cb + '_' + token.value + ' ')
    def renderV(self, token):
        self.cv = token.value.zfill(3)
        if not self.cv == '001': self.write('<\span>\n')
        self.write('<span id="' + self.ccUnfil + '_' + token.getValue() + '"><sup>' + token.getValue() + '</sup>')

    def renderWJS(self, token):     pass
    def renderWJE(self, token):     pass
    def renderTEXT(self, token):
        if self.footnoteFlag:       self.footnoteFlag = False; self.write(' -->')
        self.write(token.getValue())
    def renderQ(self, token):       self.write('\n:')
    def renderQ1(self, token):      self.write('\n::')
    def renderQ2(self, token):      pass
    def renderQ3(self, token):      pass
    def renderNB(self, token):      pass
    def renderQTS(self, token):     pass
    def renderQTE(self, token):     pass
    def renderFS(self, token):      self.write('<ref><!-- '); self.footnoteFlag = True
    def renderFT(self, token):      self.write('\\ft ' + token.getValue())
    def renderFK(self, token):      self.write('\\fk ' + token.getValue())
    def renderFE(self, token):
        if self.footnoteFlag:       self.footnoteFlag = False; self.write(' -->')
        self.write('</ref>')
    def renderFP(self, token):
        self.indentFlag = False
        self.write('\n\n')
    def renderIS(self, token):      pass
    def renderIE(self, token):      pass
    def renderB(self, token):       pass
    def renderD(self, token):       pass
    def renderADDS(self, token):    pass
    def renderADDE(self, token):    pass
    def renderLI(self, token):      self.write('\n:<!-- \li -->')
    def renderSP(self, token):      pass
    def renderNDS(self, token):     pass
    def renderNDE(self, token):     pass
    def renderPBR(self, token):     pass
    def renderFR(self, token):      pass
    def renderFRE(self, token):     pass
    def renderXS(self, token):      pass
    def renderXE(self, token):      pass
    def renderXDCS(self, token):    pass
    def renderXDCE(self, token):    pass
    def renderXO(self, token):      pass
    def renderXT(self, token):      pass
    def renderM(self, token):       pass
    def renderMI(self, token):      pass
    def renderTLS(self, token):     pass
    def renderTLE(self, token):     pass
    def renderPI(self, token):      pass
    def renderSCS(self, token):     pass
    def renderSCE(self, token):     pass
    def renderD(self, token):       pass # For now
    def renderREM(self, token):     pass # This is for comments in the USFM

class Transform(object):

    def stripUnicodeHeader(self, unicodeString):
        if unicodeString[0] == '\ufeff':
            return unicodeString[1:]
        else:
            return unicodeString

    def translateBook(self, usfm):
         tokens = parseString(usfm)
         tp = MediaWikiPrinter(self.outputDir)
         for t in tokens: t.renderOn(tp)

    def setupAndRun(self, patchedDir, outputDir):
        self.outputDir = outputDir
        self.booksUsfm = loadBooks(patchedDir)

        for bookName in silNames:
            if bookName in self.booksUsfm:
                print(('     ' + bookName))
                self.translateBook(self.booksUsfm[bookName])
