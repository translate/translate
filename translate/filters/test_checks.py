# -*- coding: utf-8 -*-
from translate.filters import checks

def test_defaults():
    """tests default setup and that checks aren't altered by other constructions"""
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.varmatches == []
    mozillachecker = checks.MozillaChecker()
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.varmatches == []

def test_construct():
    """tests that the checkers can be constructed"""
    stdchecker = checks.StandardChecker()
    mozillachecker = checks.MozillaChecker()
    ooochecker = checks.OpenOfficeChecker()
    gnomechecker = checks.GnomeChecker()
    kdechecker = checks.KdeChecker()

def test_accelerator_markers():
    """test that we have the correct accelerator marker for the various default configs"""
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.accelmarkers == []
    mozillachecker = checks.MozillaChecker()
    assert mozillachecker.config.accelmarkers == ["&"]
    ooochecker = checks.OpenOfficeChecker()
    assert ooochecker.config.accelmarkers == ["~"]
    gnomechecker = checks.GnomeChecker()
    assert gnomechecker.config.accelmarkers == ["_"]
    kdechecker = checks.KdeChecker()
    assert kdechecker.config.accelmarkers == ["&"]
    
def test_accelerators():
    """tests accelerators"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert checks.passes(stdchecker.accelerators, "&File", "&Fayile") 
    assert checks.fails(stdchecker.accelerators, "&File", "Fayile") 
    assert checks.fails(stdchecker.accelerators, "File", "&Fayile") 
    assert checks.passes(stdchecker.accelerators, "Mail && News", "Pos en Nuus") 
    assert checks.fails(stdchecker.accelerators, "Mail &amp; News", "Pos en Nuus") 
    assert checks.passes(stdchecker.accelerators, "&Allow", u'&\ufeb2\ufee3\ufe8e\ufea3')
    assert checks.fails(stdchecker.accelerators, "Open &File", "Vula& Ifayile") 
    kdechecker = checks.KdeChecker()
    assert checks.passes(kdechecker.accelerators, "&File", "&Fayile") 
    assert checks.fails(kdechecker.accelerators, "&File", "Fayile") 
    assert checks.fails(kdechecker.accelerators, "File", "&Fayile") 
    gnomechecker = checks.GnomeChecker()
    assert checks.passes(gnomechecker.accelerators, "_File", "_Fayile") 
    assert checks.fails(gnomechecker.accelerators, "_File", "Fayile") 
    assert checks.fails(gnomechecker.accelerators, "File", "_Fayile") 
    mozillachecker = checks.MozillaChecker()
    assert checks.passes(mozillachecker.accelerators, "&File", "&Fayile") 
    assert checks.fails_serious(mozillachecker.accelerators, "&File", "Fayile") 
    assert checks.fails_serious(mozillachecker.accelerators, "File", "&Fayile") 
    assert checks.passes(mozillachecker.accelerators, "Mail &amp; News", "Pos en Nuus") 
    assert checks.fails_serious(mozillachecker.accelerators, "Mail &amp; News", "Pos en &Nuus") 
    assert checks.fails_serious(mozillachecker.accelerators, "&File", "Fayile") 
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.accelerators, "~File", "~Fayile") 
    assert checks.fails(ooochecker.accelerators, "~File", "Fayile") 
    assert checks.fails(ooochecker.accelerators, "File", "~Fayile") 
    # Problems:
    # Accelerator before variable - see test_acceleratedvariables

def xtest_acceleratedvariables():
    """test for accelerated variables"""
    # FIXME: disabled since acceleratedvariables has been removed, but these checks are still needed
    mozillachecker = checks.MozillaChecker()
    assert checks.fails(mozillachecker.acceleratedvariables, "%S &Options", "&%S Ikhetho")
    assert checks.passes(mozillachecker.acceleratedvariables, "%S &Options", "%S &Ikhetho")
    ooochecker = checks.OpenOfficeChecker()
    assert checks.fails(ooochecker.acceleratedvariables, "%PRODUCTNAME% ~Options", "~%PRODUCTNAME% Ikhetho")
    assert checks.passes(ooochecker.acceleratedvariables, "%PRODUCTNAME% ~Options", "%PRODUCTNAME% ~Ikhetho")
    

def test_accronyms():
    """tests acronyms"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.acronyms, "An HTML file", "'n HTML leer")
    assert checks.fails(stdchecker.acronyms, "An HTML file", "'n LMTH leer")
    # We don't mind if you add an acronym to correct bad capitalisation in the original
    assert checks.passes(stdchecker.acronyms, "An html file", "'n HTML leer")
    # We shouldn't worry about acronyms that appear in a musttranslate file
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=["OK"]))
    assert checks.passes(stdchecker.acronyms, "OK", "Kulungile")
    # Assert punctuation should not hide accronyms
    assert checks.fails(stdchecker.acronyms, "Location (URL) not found", "Blah blah blah")

def test_blank():
    """tests blank"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.blank, "Save as", " ")
    assert checks.fails(stdchecker.blank, "_: KDE comment\\n\nSimple string", "  ")

def test_brackets():
    """tests brackets"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.brackets, "N number(s)", "N getal(le)")
    assert checks.fails(stdchecker.brackets, "For {sic} numbers", "Vier getalle")
    assert checks.fails(stdchecker.brackets, "For }sic{ numbers", "Vier getalle")
    assert checks.fails(stdchecker.brackets, "For [sic] numbers", "Vier getalle")
    assert checks.fails(stdchecker.brackets, "For ]sic[ numbers", "Vier getalle")
    assert checks.passes(stdchecker.brackets, "{[(", "[({")

def test_compendiumconflicts():
    """tests compendiumconflicts"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.compendiumconflicts, "File not saved", r"""#-#-#-#-# file1.po #-#-#-#-#\n
Leer nie gestoor gestoor nie\n
#-#-#-#-# file1.po #-#-#-#-#\n
Leer nie gestoor""")

def test_doublequoting():
    """tests double quotes"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.doublequoting, "Hot plate", "\"Ipuleti\" elishisa")
    assert checks.passes(stdchecker.doublequoting, "\"Hot\" plate", "\"Ipuleti\" elishisa")
    assert checks.fails(stdchecker.doublequoting, "'Hot' plate", "\"Ipuleti\" elishisa")
    assert checks.passes(stdchecker.doublequoting, "\\\"Hot\\\" plate", "\\\"Ipuleti\\\" elishisa")
    
def test_doublespacing():
    """tests double spacing"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.doublespacing, "Sentence.  Another sentence.", "Sin.  'n Ander sin.")
    assert checks.passes(stdchecker.doublespacing, "Sentence. Another sentence.", "Sin. No double spacing.")
    assert checks.fails(stdchecker.doublespacing, "Sentence.  Another sentence.", "Sin. Missing the double space.")
    assert checks.fails(stdchecker.doublespacing, "Sentence. Another sentence.", "Sin.  Uneeded double space in translation.")
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah %PROGRAMNAME Calc")
    assert checks.passes(ooochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah % PROGRAMNAME Calc")

def test_doublewords():
    """tests doublewords"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.doublewords, "Save the rhino", "Save the rhino")
    assert checks.fails(stdchecker.doublewords, "Save the rhino", "Save the the rhino")
    # Double variables are not an error
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", 1)]))
    assert checks.passes(stdchecker.doublewords, "%s %s installation", "tsenyo ya %s %s")

def test_endpunc():
    """tests endpunc"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.endpunc, "Question?", "Correct?")
    assert checks.fails(stdchecker.endpunc, " Question?", "Wrong ?")
    # Newlines must not mask end punctuation
    assert checks.fails(stdchecker.endpunc, "Exit change recording mode?\n\n", "Phuma esimeni sekugucula kubhalisa.\n\n")
    mozillachecker = checks.MozillaChecker()
    assert checks.passes(mozillachecker.endpunc, "Upgrades an existing $ProductShortName$ installation.", "Ku antswisiwa ka ku nghenisiwa ka $ProductShortName$.")
    # Real examples
    assert checks.passes(stdchecker.endpunc, "A nickname that identifies this publishing site (e.g.: 'MySite')", "Vito ro duvulela leri tirhisiwaka ku kuma sayiti leri ro kandziyisa (xik.: 'Sayiti ra Mina')")
    assert checks.fails(stdchecker.endpunc, "Question", u"Wrong\u2026")
    # Making sure singlequotes don't confuse things
    assert checks.passes(stdchecker.endpunc, "Pseudo-elements can't be negated '%1$S'.", "Pseudo-elemente kan nie '%1$S' ontken word nie.")

def test_endwhitespace():
    """tests endwhitespace"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.endwhitespace, "A setence. ", "I'm correct. ")
    assert checks.fails(stdchecker.endwhitespace, "A setence. ", "'I'm incorrect.")

def test_escapes():
    """tests escapes"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.escapes, r"""_: KDE comment\n
A sentence""", "I'm correct.")
    assert checks.passes(stdchecker.escapes, "A file\n", "'n Leer\n")
    assert checks.fails_serious(stdchecker.escapes, r"blah. A file", r"bleah.\n'n leer")
    assert checks.passes(stdchecker.escapes, r"A tab\t", r"'n Tab\t")
    assert checks.fails_serious(stdchecker.escapes, r"A tab\t", r"'n Tab")
    assert checks.passes(stdchecker.escapes, r"An escape escape \\", r"Escape escape \\")
    assert checks.fails_serious(stdchecker.escapes, r"An escape escape \\", "Escape escape")
    assert checks.passes(stdchecker.escapes, r"A double quote \"", r"Double quote \"")
    assert checks.fails_serious(stdchecker.escapes, r"A double quote \"", "Double quote")
    # Escaped escapes
    assert checks.passes(stdchecker.escapes, "An escaped newline \\n", "Escaped newline \\n")
    assert checks.fails_serious(stdchecker.escapes, "An escaped newline \\n", "Escaped newline \n")
    # Real example
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.escapes, ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32", ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32")

def test_newlines():
    """tests newlines"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.newlines, "Nothing to see", "Niks te sien")
    assert checks.passes(stdchecker.newlines, "Correct\n", "Korrek\n")
    assert checks.passes(stdchecker.newlines, "Correct\r", "Korrek\r")
    assert checks.passes(stdchecker.newlines, "Correct\r\n", "Korrek\r\n")
    assert checks.fails(stdchecker.newlines, "A file\n", "'n Leer")
    assert checks.fails(stdchecker.newlines, "A file", "'n Leer\n")
    assert checks.fails(stdchecker.newlines, "A file\r", "'n Leer")
    assert checks.fails(stdchecker.newlines, "A file", "'n Leer\r")
    assert checks.fails(stdchecker.newlines, "A file\n", "'n Leer\r\n")
    assert checks.fails(stdchecker.newlines, "A file\r\n", "'n Leer\n")
    assert checks.fails(stdchecker.newlines, "blah.\nA file", "bleah. 'n leer")
    # Real example
    ooochecker = checks.OpenOfficeChecker()
    assert checks.fails(ooochecker.newlines, "The arrowhead was modified without saving.\nWould you like to save the arrowhead now?", "Ṱhoho ya musevhe yo khwinifhadzwa hu si na u seiva.Ni khou ṱoda u seiva thoho ya musevhe zwino?")

def test_tabs():
    """tests tabs"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.tabs, "Nothing to see", "Niks te sien")
    assert checks.passes(stdchecker.tabs, "Correct\t", "Korrek\t")
    assert checks.passes(stdchecker.tabs, "Correct\tAA", "Korrek\tAA")
    assert checks.fails_serious(stdchecker.tabs, "A file\t", "'n Leer")
    assert checks.fails_serious(stdchecker.tabs, "A file", "'n Leer\t")
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.tabs, ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32", ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32")

def test_filepaths():
    """tests filepaths"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.filepaths, "%s to the file /etc/hosts on your system.", "%s na die leer /etc/hosts op jou systeem.")
    assert checks.fails(stdchecker.filepaths, "%s to the file /etc/hosts on your system.", "%s na die leer /etc/gasheer op jou systeem.")
    
def test_kdecomments():
    """tests kdecomments"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.kdecomments, r"""_: I am a comment\n
A string to translate""", "'n String om te vertaal")
    assert checks.fails(stdchecker.kdecomments, r"""_: I am a comment\n
A string to translate""", r"""_: Ek is 'n commment\n
'n String om te vertaal""")
    assert checks.fails(stdchecker.kdecomments, """_: I am a comment\\n\n""", """_: I am a comment\\n\n""")

def test_long():
    """tests long messages"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.long, "I am normal", "Ek is ook normaal")
    assert checks.fails(stdchecker.long, "Short.", "Kort.......................................................................................")
    assert checks.fails(stdchecker.long, "a", "bc")

def test_musttranslatewords():
    """tests stopwords"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=[]))
    assert checks.passes(stdchecker.musttranslatewords, "This uses Mozilla of course", "hierdie gebruik le mozille natuurlik")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=["Mozilla"]))
    assert checks.passes(stdchecker.musttranslatewords, "This uses Mozilla of course", "hierdie gebruik le mozille natuurlik")
    assert checks.fails(stdchecker.musttranslatewords, "This uses Mozilla of course", "hierdie gebruik Mozilla natuurlik")
    assert checks.passes(stdchecker.musttranslatewords, "This uses Mozilla. Don't you?", "hierdie gebruik le mozille soos jy")
    assert checks.fails(stdchecker.musttranslatewords, "This uses Mozilla. Don't you?", "hierdie gebruik Mozilla soos jy")
    # should always pass if there are no stopwords in the original
    assert checks.passes(stdchecker.musttranslatewords, "This uses something else. Don't you?", "hierdie gebruik Mozilla soos jy")
    # check that we can find words surrounded by punctuation
    assert checks.passes(stdchecker.musttranslatewords, "Click 'Mozilla' button", "Kliek 'Motzille' knoppie")
    assert checks.fails(stdchecker.musttranslatewords, "Click 'Mozilla' button", "Kliek 'Mozilla' knoppie")
    assert checks.passes(stdchecker.musttranslatewords, 'Click "Mozilla" button', 'Kliek "Motzille" knoppie')
    assert checks.fails(stdchecker.musttranslatewords, 'Click "Mozilla" button', 'Kliek "Mozilla" knoppie')
    assert checks.fails(stdchecker.musttranslatewords, 'Click "Mozilla" button', u'Kliek «Mozilla» knoppie')
    assert checks.passes(stdchecker.musttranslatewords, "Click (Mozilla) button", "Kliek (Motzille) knoppie")
    assert checks.fails(stdchecker.musttranslatewords, "Click (Mozilla) button", "Kliek (Mozilla) knoppie")
    assert checks.passes(stdchecker.musttranslatewords, "Click Mozilla!", "Kliek Motzille!")
    assert checks.fails(stdchecker.musttranslatewords, "Click Mozilla!", "Kliek Mozilla!")
    ## We need to define more word separators to allow us to find those hidden untranslated items
    #assert checks.fails(stdchecker.musttranslatewords, "Click OK", "Blah we-OK")
    # Don't get confused when variables are the same as a musttranslate word
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", None),], musttranslatewords=["OK"]))
    assert checks.passes(stdchecker.musttranslatewords, "Click %OK to start", "Kliek %OK om te begin")
    # Unicode
    assert checks.fails(stdchecker.musttranslatewords, "Click OK", u"Kiḽikani OK")

def test_notranslatewords():
    """tests stopwords"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=[]))
    assert checks.passes(stdchecker.notranslatewords, "This uses Mozilla of course", "hierdie gebruik le mozille natuurlik")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Mozilla","Opera"]))
    assert checks.fails(stdchecker.notranslatewords, "This uses Mozilla of course", "hierdie gebruik le mozille natuurlik")
    assert checks.passes(stdchecker.notranslatewords, "This uses Mozilla of course", "hierdie gebruik Mozilla natuurlik")
    assert checks.fails(stdchecker.notranslatewords, "This uses Mozilla. Don't you?", "hierdie gebruik le mozille soos jy")
    assert checks.passes(stdchecker.notranslatewords, "This uses Mozilla. Don't you?", "hierdie gebruik Mozilla soos jy")
    # should always pass if there are no stopwords in the original
    assert checks.passes(stdchecker.notranslatewords, "This uses something else. Don't you?", "hierdie gebruik Mozilla soos jy")
    # Cope with commas
    assert checks.passes(stdchecker.notranslatewords, "using Mozilla Task Manager", u"šomiša Selaola Mošomo sa Mozilla, gomme")
    # Find words even if they are embedded in punctuation
    assert checks.fails(stdchecker.notranslatewords, "Click 'Mozilla' button", "Kliek 'Motzille' knoppie")
    assert checks.passes(stdchecker.notranslatewords, "Click 'Mozilla' button", "Kliek 'Mozilla' knoppie")
    assert checks.fails(stdchecker.notranslatewords, "Click Mozilla!", "Kliek Motzille!")
    assert checks.passes(stdchecker.notranslatewords, "Click Mozilla!", "Kliek Mozilla!")
    assert checks.fails(stdchecker.notranslatewords, "Searches (From Opera)", "adosako (kusukela ku- Ophera)")
    assert checks.fails(stdchecker.notranslatewords, "Searches (From Opera)", "adosako (kusukela ku- Ophera)")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Sun","NeXT"]))
    assert checks.fails(stdchecker.notranslatewords, "Sun/NeXT Audio", "Odio dza Ḓuvha/TeVHELAHO")
    assert checks.passes(stdchecker.notranslatewords, "Sun/NeXT Audio", "Odio dza Sun/NeXT")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["sendmail"]))
    assert checks.fails(stdchecker.notranslatewords, "because 'sendmail' could", "ngauri 'rumelameiḽi' a yo")
    assert checks.passes(stdchecker.notranslatewords, "because 'sendmail' could", "ngauri 'sendmail' a yo")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Base"]))
    assert checks.fails(stdchecker.notranslatewords, " - %PRODUCTNAME Base: Relation design", " - %PRODUCTNAME Sisekelo: Umsiko wekuhlobana")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Writer"]))
    assert checks.fails(stdchecker.notranslatewords, "&[ProductName] Writer/Web", "&[ProductName] Umbhali/iWebhu")

def test_numbers():
    """test numbers"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.numbers, "Netscape 4 was not as good as Netscape 7.", "Netscape 4 was nie so goed soos Netscape 7 nie.")
    # Check for correct detection of degree.  Also check that we aren't getting confused with 1 and 2 byte UTF-8 characters
    assert checks.fails(stdchecker.numbers, "180° turn", "180 turn")
    assert checks.passes(stdchecker.numbers, "180° turn", "180° turn")
    assert checks.fails(stdchecker.numbers, "180° turn", "360 turn")
    assert checks.fails(stdchecker.numbers, "180° turn", "360° turn")
    assert checks.passes(stdchecker.numbers, "180~ turn", "180 turn")
    assert checks.passes(stdchecker.numbers, "180¶ turn", "180 turn")
    # Numbers with multiple decimal points
    assert checks.passes(stdchecker.numbers, "12.34.56", "12.34.56")
    assert checks.fails(stdchecker.numbers, "12.34.56", "98.76.54")
    # Currency
    # FIXME we should probably be able to handle currency checking with locale inteligence
    assert checks.passes(stdchecker.numbers, "R57.60", "R57.60")
    # FIXME - again locale intelligence should allow us to use other decimal seperators
    assert checks.fails(stdchecker.numbers, "R57.60", "R57,60")
    assert checks.fails(stdchecker.numbers, "1,000.00", "1 000,00")
    # You should be able to reorder numbers
    assert checks.passes(stdchecker.numbers, "40-bit RC2 encryption with RSA and an MD5", "Umbhalo ocashile i-RC2 onamabhithi angu-40 one-RSA ne-MD5")

def test_printf():
    """tests printf style variables"""
    # This should really be a subset of the variable checks
    # Ideally we should be able to adapt based on #, directives also
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.printf, "I am %s", "Ek is %s")
    assert checks.fails(stdchecker.printf, "I am %s", "Ek is %d")
    assert checks.passes(stdchecker.printf, "I am %#100.50hhf", "Ek is %#100.50hhf")
    assert checks.fails(stdchecker.printf, "I am %#100s", "Ek is %10s")
    assert checks.fails(stdchecker.printf, "... for user %.100s on %.100s:", "... lomuntu osebenzisa i-%. I-100s e-100s:")
    # Reordering
    assert checks.passes(stdchecker.printf, "String %s and number %d", "String %1$s en nommer %2$d")
    assert checks.passes(stdchecker.printf, "String %1$s and number %2$d", "String %1$s en nommer %2$d")
    assert checks.passes(stdchecker.printf, "String %s and number %d", "Nommer %2$d and string %1$s")
    assert checks.fails(stdchecker.printf, "String %s and number %d", "Nommer %1$d and string %2$s")

def test_puncspacing():
    """tests spacing after punctuation"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.puncspacing, "One, two, three.", "Kunye, kubili, kuthathu.")
    assert checks.passes(stdchecker.puncspacing, "One, two, three. ", "Kunye, kubili, kuthathu.")
    assert checks.fails(stdchecker.puncspacing, "One, two, three. ", "Kunye, kubili,kuthathu.")
    assert checks.passes(stdchecker.puncspacing, "One, two, three!?", "Kunye, kubili, kuthathu?")

def test_purepunc():
    """tests messages containing only punctuation"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.purepunc, ".", ".")
    assert checks.passes(stdchecker.purepunc, "", "")
    assert checks.fails(stdchecker.purepunc, ".", " ")

def test_sentencecount():
    """tests sentencecount messages"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.sentencecount, "One. Two. Three.", "Een. Twee. Drie.")
    assert checks.fails(stdchecker.sentencecount, "One two three", "Een twee drie.")
    assert checks.fails(stdchecker.sentencecount, "One. Two. Three.", "Een Twee. Drie.")
    assert checks.passes(stdchecker.sentencecount, "Sentence with i.e. in it.", "Sin met d.w.s. in dit.")

def test_short():
    """tests short messages"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.short, "I am normal", "Ek is ook normaal")
    assert checks.fails(stdchecker.short, "I am a very long sentence", "Ek")
    assert checks.fails(stdchecker.short, "abcde", "c")

def test_singlequoting():
    """tests single quotes"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.singlequoting, "A 'Hot' plate", "Ipuleti 'elishisa' kunye")
    # FIXME this should pass but doesn't probably to do with our logic that got confused at the end of lines
    assert checks.passes(stdchecker.singlequoting, "'Hot' plate", "Ipuleti 'elishisa'")
    # FIXME newlines also confuse our algorithm for single quotes
    assert checks.passes(stdchecker.singlequoting, "File '%s'\n", "'%s' Faele\n")
    assert checks.fails(stdchecker.singlequoting, "'Hot' plate", "Ipuleti \"elishisa\"")
    assert checks.passes(stdchecker.singlequoting, "It's here.", "Dit is hier.")
    # We shouldn't see single quotes in KDE comments
    assert checks.passes(stdchecker.singlequoting, r"""_: 'Migrating' formats.\n
Converting...""", "Kugucula...")
    # Don't get confused by punctuation that touches a single quote
    assert checks.passes(stdchecker.singlequoting, "File '%s'.", "'%s' Faele.")
    assert checks.passes(stdchecker.singlequoting, "Blah 'format' blah.", "Blah blah 'sebopego'.")
    assert checks.passes(stdchecker.singlequoting, "Blah 'format' blah!", "Blah blah 'sebopego'!")
    assert checks.passes(stdchecker.singlequoting, "Blah 'format' blah?", "Blah blah 'sebopego'?")
    # Real examples
    assert checks.passes(stdchecker.singlequoting, "A nickname that identifies this publishing site (e.g.: 'MySite')", "Vito ro duvulela leri tirhisiwaka ku kuma sayiti leri ro kandziyisa (xik.: 'Sayiti ra Mina')")
    assert checks.passes(stdchecker.singlequoting, "isn't", "ayikho")
    # Afrikaans 'n
    assert checks.passes(stdchecker.singlequoting, "Please enter a different site name.", "Tik 'n ander werfnaam in.")
    assert checks.passes(stdchecker.singlequoting, "\"%name%\" already exists. Please enter a different site name.", "\"%name%\" bestaan reeds. Tik 'n ander werfnaam in.")
    # Check that accelerators don't mess with removing singlequotes
    mozillachecker = checks.MozillaChecker()
    assert checks.passes(mozillachecker.singlequoting, "&Don't import anything", "&Moenie enigiets invoer nie")
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.singlequoting, "~Don't import anything", "~Moenie enigiets invoer nie")

def test_simplecaps():
    """tests simple caps"""
    # Simple caps is a very vauge test so the checks here are mostly for obviously fixable problem
    # or for checking obviously correct situations that are triggering a failure.
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.simplecaps, "MB of disk space for the cache.", "MB yendzawo yediski etsala.")
    # We should squash 'I' in the source text as it messes with capital detection
    assert checks.passes(stdchecker.simplecaps, "if you say I want", "as jy se ek wil")
    assert checks.passes(stdchecker.simplecaps, "sentence. I want more.", "sin. Ek wil meer he.")
    ## We should remove variables before checking
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", 1)]))
    assert checks.passes(stdchecker.simplecaps, "Could not load %s", "A swi koteki ku panga %S")
    assert checks.passes(stdchecker.simplecaps, "The element \"%S\" is not recognized.", "Elemente \"%S\" a yi tiveki.")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("&", ";")]))
    assert checks.passes(stdchecker.simplecaps, "Determine how &brandShortName; connects to the Internet.", "Kuma &brandShortName; hlanganisa eka Internete.")
    ## If source is ALL CAPS then we should just check that target is also ALL CAPS
    assert checks.passes(stdchecker.simplecaps, "COUPDAYS", "COUPMALANGA")
    # KDE commens should be removed
    assert checks.passes(stdchecker.simplecaps, "_: KDE COMMENTS\\n\nA string", "Dimpled ring")
    # Just some that at times have failed but should always pass
    assert checks.passes(stdchecker.simplecaps, "Create a query  entering an SQL statement directly.", "Yakha sibuti singena SQL inkhomba yesitatimende.")
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.simplecaps, "SOLK (%PRODUCTNAME Link)", "SOLK (%PRODUCTNAME Thumanyo)")
    assert checks.passes(ooochecker.simplecaps, "%STAROFFICE Image", "Tshifanyiso tsha %STAROFFICE")

def test_spellcheck():
    """tests spell checking"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert checks.passes(stdchecker.spellcheck, "Great trek", "Groot trek")
    assert checks.fails(stdchecker.spellcheck, "Final deadline", "End of the road")

def test_startcaps():
    """tests starting capitals"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.startcaps, "Find", "Vind")
    assert checks.passes(stdchecker.startcaps, "find", "vind")
    assert checks.fails(stdchecker.startcaps, "Find", "vind")
    assert checks.fails(stdchecker.startcaps, "find", "Vind")
    assert checks.fails(stdchecker.startcaps, "Find", "'")
    assert checks.fails(stdchecker.startcaps, "'", "Find")
    assert checks.passes(stdchecker.startcaps, "'", "'")
    assert checks.passes(stdchecker.startcaps, "\\.,/?!`'\"[]{}()@#$%^&*_-;:<>Find", "\\.,/?!`'\"[]{}()@#$%^&*_-;:<>Vind")
    # With leading whitespace
    assert checks.passes(stdchecker.startcaps, " Find", " Vind")
    assert checks.passes(stdchecker.startcaps, " find", " vind")
    assert checks.fails(stdchecker.startcaps, " Find", " vind")
    assert checks.fails(stdchecker.startcaps, " find", " Vind")
    # Leading punctuation
    assert checks.passes(stdchecker.startcaps, "'Find", "'Vind")
    assert checks.passes(stdchecker.startcaps, "'find", "'vind")
    assert checks.fails(stdchecker.startcaps, "'Find", "'vind")
    assert checks.fails(stdchecker.startcaps, "'find", "'Vind")
    # Unicode
    assert checks.passes(stdchecker.startcaps, "Find", u"Šind")
    assert checks.passes(stdchecker.startcaps, "find", u"šind")
    assert checks.fails(stdchecker.startcaps, "Find", u"šind")
    assert checks.fails(stdchecker.startcaps, "find", u"Šind")
    # Unicode further down the Unicode tables
    assert checks.passes(stdchecker.startcaps, "A text enclosed...", u"Ḽiṅwalwa ḽo katelwaho...")
    assert checks.fails(stdchecker.startcaps, "A text enclosed...", u"ḽiṅwalwa ḽo katelwaho...")

    # Accelerators
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert checks.passes(stdchecker.startcaps, "&Find", "Vi&nd")

def test_startpunc():
    """tests startpunc"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.startpunc, "<< Previous", "<< Correct")
    assert checks.fails(stdchecker.startpunc, " << Previous", "Wrong")
    assert checks.fails(stdchecker.startpunc, "Question", u"\u2026Wrong")

def test_startwhitespace():
    """tests startwhitespace"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.startwhitespace, "A setence.", "I'm correct.")
    assert checks.fails(stdchecker.startwhitespace, " A setence.", "I'm incorrect.")

def test_unchanged():
    """tests unchanged entries"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert checks.fails(stdchecker.unchanged, "Unchanged", "Unchanged") 
    assert checks.fails(stdchecker.unchanged, "&Unchanged", "Un&changed") 
    assert checks.passes(stdchecker.unchanged, "Unchanged", "Changed") 
    assert checks.passes(stdchecker.unchanged, "1234", "1234") 
    assert checks.passes(stdchecker.unchanged, "I", "I") 
    assert checks.passes(stdchecker.unchanged, "   ", "   ") 
    assert checks.passes(stdchecker.unchanged, "&ACRONYM", "&ACRONYM") 
    assert checks.fails(stdchecker.unchanged, r"""_: KDE comment\n
Unchanged""", r"Unchanged") 
    # Variable only and variable plus punctuation messages should be ignored
    mozillachecker = checks.MozillaChecker()
    assert checks.passes(mozillachecker.unchanged, "$ProgramName$", "$ProgramName$") 
    assert checks.passes(mozillachecker.unchanged, "$file$ : $dir$", "$file$ : $dir$") 
    assert checks.fails(mozillachecker.unchanged, "$file$ in $dir$", "$file$ in $dir$") 
    # Don't translate words should be ignored
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Mozilla"]))
    assert checks.passes(stdchecker.unchanged, "Mozilla", "Mozilla") 

def test_untranslated():
    """tests untranslated entries"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.untranslated, "I am untranslated", "")
    assert checks.passes(stdchecker.untranslated, "I am translated", "Ek is vertaal")
    # KDE comments that make it into translations should not mask untranslated test
    assert checks.fails(stdchecker.untranslated, "_: KDE comment\\n\nI am untranslated", "_: KDE comment\\n\n")

def test_validchars():
    """tests valid characters"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig())
    assert checks.passes(stdchecker.validchars, "The check always passes if you don't specify chars", "Die toets sal altyd werk as jy nie karacters specifisier")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(validchars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'))
    assert checks.passes(stdchecker.validchars, "This sentence contains valid characters", "Hierdie sin bevat ware karakters")
    assert checks.fails(stdchecker.validchars, "Some unexpected characters", "©®°±÷¼½¾")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(validchars='⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰'))
    assert checks.passes(stdchecker.validchars, "Our target language is all non-ascii", "⠁⠂⠃⠄⠆⠇⠈⠉⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫")
    assert checks.fails(stdchecker.validchars, "Our target language is all non-ascii", "Some ascii⠁⠂⠃⠄⠆⠇⠈⠉⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫")

def test_variables_kde():
    """tests variables in KDE translations"""
    # GNOME variables
    kdechecker = checks.KdeChecker()
    assert checks.passes(kdechecker.variables, "%d files of type %s saved.", "%d leers van %s tipe gestoor.")
    assert checks.fails_serious(kdechecker.variables, "%d files of type %s saved.", "%s leers van %s tipe gestoor.")

def test_variables_gnome():
    """tests variables in GNOME translations"""
    # GNOME variables
    gnomechecker = checks.GnomeChecker()
    assert checks.passes(gnomechecker.variables, "%d files of type %s saved.", "%d leers van %s tipe gestoor.")
    assert checks.fails_serious(gnomechecker.variables, "%d files of type %s saved.", "%s leers van %s tipe gestoor.")
    assert checks.passes(gnomechecker.variables, "Save $(file)", "Stoor $(file)")
    assert checks.fails_serious(gnomechecker.variables, "Save $(file)", "Stoor $(leer)")

def test_variables_mozilla():
    """tests variables in Mozilla translations"""
    # Mozilla variables
    mozillachecker = checks.MozillaChecker()
    assert checks.passes(mozillachecker.variables, "Use the &brandShortname; instance.", "Gebruik die &brandShortname; weergawe.")
    assert checks.fails_serious(mozillachecker.variables, "Use the &brandShortname; instance.", "Gebruik die &brandKortnaam; weergawe.")
    assert checks.passes(mozillachecker.variables, "Save %file%", "Stoor %file%")
    assert checks.fails_serious(mozillachecker.variables, "Save %file%", "Stoor %leer%")
    assert checks.passes(mozillachecker.variables, "Save $file$", "Stoor $file$")
    assert checks.fails_serious(mozillachecker.variables, "Save $file$", "Stoor $leer$")
    assert checks.passes(mozillachecker.variables, "%d files of type %s saved.", "%d leers van %s tipe gestoor.")
    assert checks.fails_serious(mozillachecker.variables, "%d files of type %s saved.", "%s leers van %s tipe gestoor.")
    assert checks.passes(mozillachecker.variables, "Save $file", "Stoor $file")
    assert checks.fails_serious(mozillachecker.variables, "Save $file", "Stoor $leer")
    assert checks.passes(mozillachecker.variables, "About $ProgramName$", "Oor $ProgramName$")
    assert checks.fails_serious(mozillachecker.variables, "About $ProgramName$", "Oor $NaamVanProgam$")
    assert checks.passes(mozillachecker.variables, "About $_CLICK", "Oor $_CLICK")
    assert checks.fails_serious(mozillachecker.variables, "About $_CLICK", "Oor $_KLIK")
    assert checks.passes(mozillachecker.variables, "About $(^NameDA)", "Oor $(^NameDA)")
    assert checks.fails_serious(mozillachecker.variables, "About $(^NameDA)", "Oor $(^NaamDA)")
    # Double variable problem
    assert checks.fails_serious(mozillachecker.variables, "Create In &lt;&lt;", "Etsa ka Ho &lt;lt;")
    # Variables at the end of a sentence
    assert checks.fails_serious(mozillachecker.variables, "...time you start &brandShortName;.", "...lekgetlo le latelang ha o qala &LebitsoKgutshwane la kgwebo;.")
    # Ensure that we can detect two variables of the same name with one faulty
    assert checks.fails_serious(mozillachecker.variables, "&brandShortName; successfully downloaded and installed updates. You will have to restart &brandShortName; to complete the update.", "&brandShortName; ḽo dzhenisa na u longela khwinifhadzo zwavhuḓi. Ni ḓo tea u thoma hafhu &DzinaḼipfufhi ḽa pfungavhuṇe; u itela u fhedzisa khwinifha dzo.")
    # We must detect entities in their fullform, ie with fullstop in the middle.
    assert checks.fails_serious(mozillachecker.variables, "Welcome to the &pluginWizard.title;", "Wamkelekile kwi&Sihloko Soncedo lwe-plugin;")
    # Variables that are missing in quotes should be detected
    assert checks.fails_serious(mozillachecker.variables, "\"%S\" is an executable file.... Are you sure you want to launch \"%S\"?", ".... Uyaqiniseka ukuthi ufuna ukuqalisa I\"%S\"?")
    # False positive $ style variables
    assert checks.passes(mozillachecker.variables, "for reporting $ProductShortName$ crash information", "okokubika ukwaziswa kokumosheka kwe-$ProductShortName$")
    # We shouldn't mask variables within variables.  This should highlight &brandShortName as missing and &amp as extra
    assert checks.fails_serious(mozillachecker.variables, "&brandShortName;", "&amp;brandShortName;")

def test_variables_openoffice():
    """tests variables in OpenOffice translations"""
    # OpenOffice.org variables
    ooochecker = checks.OpenOfficeChecker()
    assert checks.passes(ooochecker.variables, "Use the &brandShortname; instance.", "Gebruik die &brandShortname; weergawe.")
    assert checks.fails_serious(ooochecker.variables, "Use the &brandShortname; instance.", "Gebruik die &brandKortnaam; weergawe.")
    assert checks.passes(ooochecker.variables, "Save %file%", "Stoor %file%")
    assert checks.fails_serious(ooochecker.variables, "Save %file%", "Stoor %leer%")
    assert checks.passes(ooochecker.variables, "Save %file", "Stoor %file")
    assert checks.fails_serious(ooochecker.variables, "Save %file", "Stoor %leer")
    assert checks.passes(ooochecker.variables, "Save %1", "Stoor %1")
    assert checks.fails_serious(ooochecker.variables, "Save %1", "Stoor %2")
    assert checks.passes(ooochecker.variables, "Save %", "Stoor %")
    assert checks.fails_serious(ooochecker.variables, "Save %", "Stoor")
    assert checks.passes(ooochecker.variables, "Save $(file)", "Stoor $(file)")
    assert checks.fails_serious(ooochecker.variables, "Save $(file)", "Stoor $(leer)")
    assert checks.passes(ooochecker.variables, "Save $file$", "Stoor $file$")
    assert checks.fails_serious(ooochecker.variables, "Save $file$", "Stoor $leer$")
    assert checks.passes(ooochecker.variables, "Save ${file}", "Stoor ${file}")
    assert checks.fails_serious(ooochecker.variables, "Save ${file}", "Stoor ${leer}")
    assert checks.passes(ooochecker.variables, "Save #file#", "Stoor #file#")
    assert checks.fails_serious(ooochecker.variables, "Save #file#", "Stoor #leer#")
    assert checks.passes(ooochecker.variables, "Save #1", "Stoor #1")
    assert checks.fails_serious(ooochecker.variables, "Save #1", "Stoor #2")
    assert checks.passes(ooochecker.variables, "Save #", "Stoor #")
    assert checks.fails_serious(ooochecker.variables, "Save #", "Stoor")
    assert checks.passes(ooochecker.variables, "Save ($file)", "Stoor ($file)")
    assert checks.fails_serious(ooochecker.variables, "Save ($file)", "Stoor ($leer)")
    assert checks.passes(ooochecker.variables, "Save $[file]", "Stoor $[file]")
    assert checks.fails_serious(ooochecker.variables, "Save $[file]", "Stoor $[leer]")
    assert checks.passes(ooochecker.variables, "Save [file]", "Stoor [file]")
    assert checks.fails_serious(ooochecker.variables, "Save [file]", "Stoor [leer]")
    assert checks.passes(ooochecker.variables, "Save $file", "Stoor $file")
    assert checks.fails_serious(ooochecker.variables, "Save $file", "Stoor $leer")
    # Same variable name twice
    assert checks.fails_serious(ooochecker.variables, r"""Start %PROGRAMNAME% as %PROGRAMNAME%""", "Begin %PROGRAMNAME%")
    # Variables hidden in KDE comments
    assert checks.passes(ooochecker.variables, r"""_: Do not translate %PROGRAMNAME% in the text\n
Start %PRODUCTNAME%""", "Begin %PRODUCTNAME%")
    # Check how this interacts with the same variable name being repeated
    assert checks.passes(ooochecker.variables, r"""_: Do not translate %PROGRAMNAME% in the text\n
Start %PROGRAMNAME%""", "Begin %PROGRAMNAME%")

def test_xmltags():
    """tests xml tags"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.xmltags, "Do it <b>now</b>", "Doen dit <v>nou</v>")
    assert checks.passes(stdchecker.xmltags, "Do it <b>now</b>", "Doen dit <b>nou</b>")
    assert checks.passes(stdchecker.xmltags, "Click <img src=\"img.jpg\">here</img>", "Klik <img src=\"img.jpg\">hier</img>")
    assert checks.fails(stdchecker.xmltags, "Click <img src=\"image.jpg\">here</img>", "Klik <img src=\"prent.jpg\">hier</img>")
    assert checks.passes(stdchecker.xmltags, "Click <img src=\"img.jpg\" alt=\"picture\">here</img>", "Klik <img src=\"img.jpg\" alt=\"prentjie\">hier</img>")
    assert checks.passes(stdchecker.xmltags, "Start with the &lt;start&gt; tag", "Begin met die &lt;begin&gt;")

    assert checks.fails(stdchecker.xmltags, "Click <a href=\"page.html\">", "Klik <a hverw=\"page.html\">")
    assert checks.passes(stdchecker.xmltags, "Click <a xml-lang=\"en\" href=\"page.html\">", "Klik <a xml-lang=\"af\" href=\"page.html\">")
    assert checks.fails(stdchecker.xmltags, "Click <a href=\"page.html\" target=\"koei\">", "Klik <a href=\"page.html\">")
    assert checks.fails(stdchecker.xmltags, "<b>Current Translation</b>", "<b>Traducción Actual:<b>")
    assert checks.passes(stdchecker.xmltags, "<Error>", "<Fout>")
    assert checks.fails(stdchecker.xmltags, "%d/%d translated\n(%d blank, %d fuzzy)", "<br>%d/%d μεταφρασμένα\n<br>(%d κενά, %d ασαφή)")

def test_ooxmltags():
    """Tests the xml tags in OpenOffice.org translations for quality as done in gsicheck"""
    ooochecker = checks.OpenOfficeChecker()
    #some attributes can be changed or removed
    assert checks.fails(ooochecker.xmltags, "<img src=\"a.jpg\" width=\"400\">", "<img src=\"b.jpg\" width=\"500\">")
    assert checks.passes(ooochecker.xmltags, "<img src=\"a.jpg\" width=\"400\">", "<img src=\"a.jpg\" width=\"500\">")
    assert checks.passes(ooochecker.xmltags, "<img src=\"a.jpg\" width=\"400\">", "<img src=\"a.jpg\">")
    assert checks.passes(ooochecker.xmltags, "<img src=\"a.jpg\">", "<img src=\"a.jpg\" width=\"400\">")
    assert checks.passes(ooochecker.xmltags, "<alt xml-lang=\"ab\">text</alt>", "<alt>teks</alt>")
    assert checks.passes(ooochecker.xmltags, "<ahelp visibility=\"visible\">bla</ahelp>", "<ahelp>blu</ahelp>")
    assert checks.fails(ooochecker.xmltags, "<ahelp visibility=\"visible\">bla</ahelp>", "<ahelp visibility=\"invisible\">blu</ahelp>")
    assert checks.fails(ooochecker.xmltags, "<ahelp visibility=\"invisible\">bla</ahelp>", "<ahelp>blu</ahelp>")
    #some attributes can be changed, but not removed
    assert checks.passes(ooochecker.xmltags, "<link name=\"John\">", "<link name=\"Jan\">")
    assert checks.fails(ooochecker.xmltags, "<link name=\"John\">", "<link naam=\"Jan\">")

def test_functions():
    """tests to see that funtions() are not translated"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.functions, "blah rgb() blah", "blee brg() blee")
    assert checks.passes(stdchecker.functions, "blah rgb() blah", "blee rgb() blee")
    assert checks.fails(stdchecker.functions, "percentage in rgb()", "phesenthe kha brg()")
    assert checks.passes(stdchecker.functions, "percentage in rgb()", "phesenthe kha rgb()")
    assert checks.fails(stdchecker.functions, "rgb() in percentage", "brg() kha phesenthe")
    assert checks.passes(stdchecker.functions, "rgb() in percentage", "rgb() kha phesenthe")
    assert checks.fails(stdchecker.functions, "blah string.rgb() blah", "blee bleeb.rgb() blee")
    assert checks.passes(stdchecker.functions, "blah string.rgb() blah", "blee string.rgb() blee")
    assert checks.passes(stdchecker.functions, "or domain().", "domain() verwag.")
    assert checks.passes(stdchecker.functions, "Expected url(), url-prefix(), or domain().", "url(), url-prefix() of domain() verwag.")

def test_emails():
    """tests to see that email addresses are not translated"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.emails, "blah bob@example.net blah", "blee kobus@voorbeeld.net blee")
    assert checks.passes(stdchecker.emails, "blah bob@example.net blah", "blee bob@example.net blee")

def test_urls():
    """tests to see that URLs are not translated"""
    stdchecker = checks.StandardChecker()
    assert checks.fails(stdchecker.urls, "blah http://translate.org.za blah", "blee http://vertaal.org.za blee")
    assert checks.passes(stdchecker.urls, "blah http://translate.org.za blah", "blee http://translate.org.za blee")

def test_simpleplurals():
    """test that we can find English style plural(s)"""
    stdchecker = checks.StandardChecker()
    assert checks.passes(stdchecker.simpleplurals, "computer(s)", "rekenaar(s)")
    assert checks.fails(stdchecker.simpleplurals, "plural(s)", "meervoud(e)")
    assert checks.fails(stdchecker.simpleplurals, "Ungroup Metafile(s)...", "Kuvhanganyululani Metafaela(dzi)...")
