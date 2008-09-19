#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""reads a set of .po or .pot files to produce a pootle-terminology.pot

See: http://translate.sourceforge.net/wiki/toolkit/poterminology for examples and
usage instructions
"""

from translate.lang import factory as lang_factory
from translate.misc import optrecurse
from translate.storage import po
from translate.storage import factory
import os
import re
import sys

class TerminologyOptionParser(optrecurse.RecursiveOptionParser):
    """a specialized Option Parser for the terminology tool..."""

    # handles c-format and python-format
    formatpat = re.compile(r"%(?:\([^)]+\)|[0-9]+\$)?[-+#0]*[0-9.*]*(?:[hlLzjt][hl])?[EFGXc-ginoprsux]")
    # handles XML/HTML elements (<foo>text</foo> => text)
    xmlelpat = re.compile(r"<(?:![[-]|[/?]?[A-Za-z_:])[^>]*>")
    # handles XML/HTML entities (&#32; &#x20; &amp; &my_entity;)
    xmlentpat = re.compile(r"&(?:#(?:[0-9]+|x[0-9a-f]+)|[a-z_:][\w.-:]*);",
                           flags=re.UNICODE|re.IGNORECASE)

    sortorders = [ "frequency", "dictionary", "length" ]

    files = 0
    units = 0

    def parse_args(self, args=None, values=None):
        """parses the command line options, handling implicit input/output args"""
        (options, args) = optrecurse.optparse.OptionParser.parse_args(self, args, values)
        # some intelligence as to what reasonable people might give on the command line
        if args and not options.input:
            if not options.output and len(args) > 1:
                options.input = args[:-1]
                args = args[-1:]
            else:
                options.input = args
                args = []
        if args and not options.output:
            options.output = args[-1]
            args = args[:-1]
        if not options.output:
            options.output = "pootle-terminology.pot"
        if args:
            self.error("You have used an invalid combination of --input, --output and freestanding args")
        if isinstance(options.input, list) and len(options.input) == 1:
            options.input = options.input[0]
            if options.inputmin == None:
                options.inputmin = 1
        elif options.inputmin == None:
            options.inputmin = 2
        return (options, args)

    def set_usage(self, usage=None):
        """sets the usage string - if usage not given, uses getusagestring for each option"""
        if usage is None:
            self.usage = "%prog " + " ".join([self.getusagestring(option) for option in self.option_list]) + \
                    "\n  input directory is searched for PO files, terminology PO file is output file"
        else:
            super(TerminologyOptionParser, self).set_usage(usage)

    def run(self):
        """parses the arguments, and runs recursiveprocess with the resulting options"""
        (options, args) = self.parse_args()
        options.inputformats = self.inputformats
        options.outputoptions = self.outputoptions
        self.usepsyco(options)
        self.recursiveprocess(options)

    def recursiveprocess(self, options):
        """recurse through directories and process files"""
        if self.isrecursive(options.input, 'input') and getattr(options, "allowrecursiveinput", True):
            if isinstance(options.input, list):
                inputfiles = self.recurseinputfilelist(options)
            else:
                inputfiles = self.recurseinputfiles(options)
        else:
            if options.input:
                inputfiles = [os.path.basename(options.input)]
                options.input = os.path.dirname(options.input)
            else:
                inputfiles = [options.input]
        if os.path.isdir(options.output):
            options.output = os.path.join(options.output,"pootle-terminology.pot")
        self.stopwords = {}
        self.stoprelist = []
        actions = { '+': frozenset(), ':': frozenset(['skip']),
                    '<': frozenset(['phrase']), '=': frozenset(['word']),
                    '>': frozenset(['word','skip']),
                    '@': frozenset(['word','phrase']) }
        if options.stopwordfile != None:
            stopfile = open(options.stopwordfile, "r")
            try:
                for stopline in stopfile:
                    stoptype = stopline[0]
                    if stoptype == '#' or stoptype == "\n":
                        continue
                    elif stoptype == '/':
                        self.stoprelist.append(re.compile(stopline[1:-1]+'$'))
                    else:
                        self.stopwords[stopline[1:-1]] = actions[stoptype]
            except KeyError, character:
                self.warning("Bad line in stopword list %s starts with" % (options.stopwordfile), options, sys.exc_info())
            stopfile.close()
        self.glossary = {}
        self.initprogressbar(inputfiles, options)
        for inputpath in inputfiles:
            self.files += 1
            fullinputpath = self.getfullinputpath(options, inputpath)
            success = True
            try:
                self.processfile(None, options, fullinputpath)
            except Exception, error:
                if isinstance(error, KeyboardInterrupt):
                    raise
                self.warning("Error processing: input %s" % (fullinputpath), options, sys.exc_info())
                success = False
            self.reportprogress(inputpath, success)
        del self.progressbar
        self.outputterminology(options)

    def clean(self, string, options):
        """returns the cleaned string that contains the text to be matched"""
        for accelerator in options.accelchars:
            string = string.replace(accelerator, "")
        string = self.formatpat.sub(" ", string)
        string = self.xmlelpat.sub(" ", string)
        string = self.xmlentpat.sub(" ", string)
        string = string.strip()
        return string

    def addphrases(self, words, skips, translation, partials=True):
        """adds (sub)phrases with non-skipwords and more than one word"""
        if (len(words) > skips + 1 and
            'skip' not in self.stopwords.get(words[0], frozenset()) and
            'skip' not in self.stopwords.get(words[-1], frozenset())):
            self.glossary.setdefault(' '.join(words), []).append(translation)
        if partials:
            part = list(words)
            while len(part) > 2:
                if 'skip' in self.stopwords.get(part.pop(), frozenset()):
                    skips -= 1
                if (len(part) > skips + 1 and
                    'skip' not in self.stopwords.get(part[0], frozenset()) and
                    'skip' not in self.stopwords.get(part[-1], frozenset())):
                    self.glossary.setdefault(' '.join(part), []).append(translation)

    def processfile(self, fileprocessor, options, fullinputpath):
        """process an individual file"""
        inputfile = self.openinputfile(options, fullinputpath)
        inputfile = factory.getobject(inputfile)
        sourcelang = lang_factory.getlanguage(options.sourcelanguage)
        rematchignore = frozenset(('word','phrase'))
        defaultignore = frozenset()
        for unit in inputfile.units:
            self.units += 1
            if unit.isheader():
                continue
            if unit.hasplural():
                continue
            if not options.invert:
                source = self.clean(unit.source, options)
                target = self.clean(unit.target, options)
            else:
                target = self.clean(unit.source, options)
                source = self.clean(unit.target, options)
            if len(source) <= 1:
                continue
            for sentence in sourcelang.sentences(source):
                words = []
                skips = 0
                for word in sourcelang.words(sentence):
                    if options.ignorecase or (options.foldtitle and word.istitle()):
                        word = word.lower()
                    ignore = defaultignore
                    if word in self.stopwords:
                        ignore = self.stopwords[word]
                    else:
                        for stopre in self.stoprelist:
                            if stopre.match(word) != None:
                                ignore = rematchignore
                                break
                    translation = (source, target, unit, fullinputpath)
                    if 'word' not in ignore:
                        # reduce plurals
                        root = word
                        if len(word) > 3 and word[-1] == 's' and word[0:-1] in self.glossary:
                            root = word[0:-1]
                        elif len(root) > 2 and root + 's' in self.glossary:
                            self.glossary[root] = self.glossary.pop(root + 's')
                        self.glossary.setdefault(root, []).append(translation)
                    if options.termlength > 1:
                        if 'phrase' in ignore:
                            # add trailing phrases in previous words
                            while len(words) > 2:
                                if 'skip' in self.stopwords.get(words.pop(0), defaultignore):
                                    skips -= 1
                                self.addphrases(words, skips, translation)
                            words = []
                            skips = 0
                        else:
                            words.append(word)
                            if 'skip' in ignore:
                                skips += 1
                            if len(words) > options.termlength + skips:
                                while len(words) > options.termlength + skips:
                                    if 'skip' in self.stopwords.get(words.pop(0), defaultignore):
                                        skips -= 1
                                self.addphrases(words, skips, translation)
                            else:
                                self.addphrases(words, skips, translation, partials=False)
                if options.termlength > 1:
                    # add trailing phrases in sentence after reaching end
                    while options.termlength > 1 and len(words) > 2:
                        if 'skip' in self.stopwords.get(words.pop(0), defaultignore):
                            skips -= 1
                        self.addphrases(words, skips, translation)

    def outputterminology(self, options):
        """saves the generated terminology glossary"""
        termfile = po.pofile()
        terms = {}
        locre = re.compile(r":[0-9]+$")
        print >> sys.stderr, ("%d terms from %d units in %d files" %
                              (len(self.glossary), self.units, self.files))
        for term, translations in self.glossary.iteritems():
            if len(translations) <= 1:
                continue
            filecounts = {}
            sources = {}
            termunit = po.pounit(term)
            locations = {}
            sourcenotes = {}
            transnotes = {}
            targets = {}
            fullmsg = False
            for source, target, unit, filename in translations:
                sources[source] = 1
                filecounts[filename] = filecounts.setdefault(filename, 0) + 1
                if term.lower() == self.clean(unit.source, options).lower():
                    fullmsg = True
                    target = self.clean(unit.target, options)
                    if options.ignorecase or (options.foldtitle and target.istitle()):
                        target = target.lower()
                    unit.settarget(target)
                    if target != "":
                        targets.setdefault(target, []).append(filename)
                    if term.lower() == unit.source.strip().lower():
                        sourcenotes[unit.getnotes("source code")] = None
                        transnotes[unit.getnotes("translator")] = None
                else:
                    unit.settarget("")
                unit.setsource(term)
                termunit.merge(unit, overwrite=False, comments=False)
                for loc in unit.getlocations():
                    locations.setdefault(locre.sub("", loc))
            numsources = len(sources)
            numfiles = len(filecounts)
            numlocs = len(locations)
            if numfiles < options.inputmin or numlocs < options.locmin:
                continue
            if fullmsg:
                if numsources < options.fullmsgmin:
                    continue
            elif numsources < options.substrmin:
                continue
            if len(targets.keys()) > 1:
                txt = '; '.join(["%s {%s}" % (target, ', '.join(files))
                                     for target, files in targets.iteritems()])
                if termunit.gettarget().find('};') < 0:
                    termunit.settarget(txt)
                    termunit.markfuzzy()
                else:
                    # if annotated multiple terms already present, keep as-is
                    termunit.addnote(txt, "translator")
            locmax = 2 * options.locmin
            if numlocs > locmax:
                for location in locations.keys()[0:locmax]:
                    termunit.addlocation(location)
                termunit.addlocation("(poterminology) %d more locations"
                                     % (numlocs - locmax))
            else:
                for location in locations.keys():
                    termunit.addlocation(location)
            for sourcenote in sourcenotes.keys():
                termunit.addnote(sourcenote, "source code")
            for transnote in transnotes.keys():
                termunit.addnote(transnote, "translator")
            for filename, count in filecounts.iteritems():
                termunit.othercomments.append("# (poterminology) %s (%d)\n" % (filename, count))
            terms[term] = (((10 * numfiles) + numsources, termunit))
        # reduce subphrase
        termlist = terms.keys()
        print >> sys.stderr, "%d terms after thresholding" % len(termlist)
        termlist.sort(lambda x, y: cmp(len(x), len(y)))
        for term in termlist:
            words = term.split()
            if len(words) <= 2:
                continue
            while len(words) > 2:
                words.pop()
                if terms[term][0] == terms.get(' '.join(words), [0])[0]:
                    del terms[' '.join(words)]
            words = term.split()
            while len(words) > 2:
                words.pop(0)
                if terms[term][0] == terms.get(' '.join(words), [0])[0]:
                    del terms[' '.join(words)]
        print >> sys.stderr, "%d terms after subphrase reduction" % len(terms.keys())
        termitems = terms.values()
        if options.sortorders == None:
            options.sortorders = self.sortorders
        while len(options.sortorders) > 0:
            order = options.sortorders.pop()
            if order == "frequency":
                termitems.sort(lambda x, y: cmp(y[0], x[0]))
            elif order == "dictionary":
                termitems.sort(lambda x, y: cmp(x[1].source.lower(), y[1].source.lower()))
            elif order == "length":
                termitems.sort(lambda x, y: cmp(len(x[1].source), len(y[1].source)))
            else:
                self.warning("unknown sort order %s" % order, options)
        for count, unit in termitems:
            termfile.units.append(unit)
        open(options.output, "w").write(str(termfile))

def find_installed_file(filename):
    root = __file__
    if os.path.islink(root):
        root = os.path.realpath(root)
    filepath = os.path.join( os.path.dirname(os.path.abspath(root)), os.path.pardir, 'share', filename )

    if not os.path.exists(filepath):
        return None
    return filepath

def main():
    formats = {"po":("po", None), "pot": ("pot", None), None:("po", None)}
    parser = TerminologyOptionParser(formats)
    parser.add_option("-I", "--ignore-case", dest="ignorecase",
        action="store_true", default=False, help="make all terms lowercase")
    parser.add_option("-F", "--fold-titlecase", dest="foldtitle",
        action="store_true", default=False, help="fold \"Title Case\" to lowercase")
    parser.add_option("", "--accelerator", dest="accelchars", default="",
        metavar="ACCELERATORS", help="ignores the given accelerator characters when matching")
    parser.add_option("-t", "--term-words", type="int", dest="termlength", default="3",
                      help="generate terms of up to LENGTH words (default 3)", metavar="LENGTH")
    parser.add_option("", "--inputs-needed", type="int", dest="inputmin",
                      help="omit terms appearing in less than MIN input files (default 1 - 2 if multiple input files)", metavar="MIN")
    parser.add_option("", "--fullmsg-needed", type="int", dest="fullmsgmin", default="1",
                      help="omit full message terms appearing in less than MIN different messages (default 1)", metavar="MIN")
    parser.add_option("", "--substr-needed", type="int", dest="substrmin", default="2",
                      help="omit substring-only terms appearing in less than MIN different messages (default 2)", metavar="MIN")
    parser.add_option("", "--locs-needed", type="int", dest="locmin", default="2",
                      help="omit terms appearing in less than MIN different original source files (default 2)", metavar="MIN")
    parser.add_option("", "--sort", dest="sortorders", action="append",
                      type="choice", choices=parser.sortorders, metavar="ORDER",
                      help="output sort order(s): %s (default is all orders in the above priority)" % ', '.join(parser.sortorders))
    parser.add_option("-S", "--stopword-list", type="string", dest="stopwordfile",
                      help="name of file containing stopword list", metavar="FILENAME", default=find_installed_file('stoplist-en'))
    parser.add_option("", "--source-language", dest="sourcelanguage", default="en",
                      help="the source language code (default 'en')", metavar="LANG")
    parser.add_option("-v", "--invert", dest="invert",
        action="store_true", default=False, help="invert the source and target languages for terminology")
    parser.set_usage()
    parser.description = __doc__
    parser.run()


if __name__ == '__main__':
    main()
