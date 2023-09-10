from pytest import mark

from translate.filters import checks, spelling
from translate.lang import data
from translate.storage import po, xliff


def strprep(str1, str2, message=None):
    return (
        data.normalize(str1),
        data.normalize(str2),
        data.normalize(message),
    )


def check_category(filterfunction):
    """Checks whether ``filterfunction`` has defined a category or not."""
    return filterfunction.__name__ in filterfunction.__self__.categories


def passes(filterfunction, str1, str2):
    """returns whether the given strings pass on the given test, handling FilterFailures"""
    str1, str2, no_message = strprep(str1, str2)
    try:
        filterresult = filterfunction(str1, str2)
    except checks.FilterFailure:
        filterresult = False

    filterresult = filterresult and check_category(filterfunction)

    return filterresult


def fails(filterfunction, str1, str2, message=None):
    """returns whether the given strings fail on the given test, handling only FilterFailures"""
    str1, str2, message = strprep(str1, str2, message)
    try:
        filterresult = filterfunction(str1, str2)
    except checks.SeriousFilterFailure:
        filterresult = True
    except checks.FilterFailure as e:
        if message:
            exc_message = e.messages[0]
            filterresult = exc_message != message
            print(exc_message.encode("utf-8"))
        else:
            filterresult = False

    filterresult = filterresult and check_category(filterfunction)

    return not filterresult


def fails_serious(filterfunction, str1, str2, message=None):
    """returns whether the given strings fail on the given test, handling only SeriousFilterFailures"""
    str1, str2, message = strprep(str1, str2, message)
    try:
        filterresult = filterfunction(str1, str2)
    except checks.SeriousFilterFailure as e:
        if message:
            exc_message = e.messages[0]
            filterresult = exc_message != message
            print(exc_message.encode("utf-8"))
        else:
            filterresult = False

    filterresult = filterresult and check_category(filterfunction)

    return not filterresult


def test_defaults():
    """tests default setup and that checks aren't altered by other constructions"""
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.varmatches == []
    mozillachecker = checks.MozillaChecker()
    assert len(mozillachecker.config.varmatches) == 9
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.varmatches == []


def test_construct():
    """tests that the checkers can be constructed"""
    checks.StandardChecker()
    checks.MozillaChecker()
    checks.OpenOfficeChecker()
    checks.LibreOfficeChecker()
    checks.GnomeChecker()
    checks.KdeChecker()
    checks.IOSChecker()


def test_accelerator_markers():
    """test that we have the correct accelerator marker for the various default configs"""
    stdchecker = checks.StandardChecker()
    assert stdchecker.config.accelmarkers == []
    mozillachecker = checks.MozillaChecker()
    assert mozillachecker.config.accelmarkers == ["&"]
    ooochecker = checks.OpenOfficeChecker()
    assert ooochecker.config.accelmarkers == ["~"]
    lochecker = checks.LibreOfficeChecker()
    assert lochecker.config.accelmarkers == ["~"]
    gnomechecker = checks.GnomeChecker()
    assert gnomechecker.config.accelmarkers == ["_"]
    kdechecker = checks.KdeChecker()
    assert kdechecker.config.accelmarkers == ["&"]


def test_messages():
    """test that our helpers can check for messages and that these error messages can contain Unicode"""
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            validchars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
    )
    assert fails(
        stdchecker.validchars,
        "Some unexpected characters",
        "©",
        "Invalid characters: '©' (\\u00a9)",
    )
    stdchecker = checks.StandardChecker()
    assert fails_serious(
        stdchecker.escapes,
        r"A tab",
        r"'n Ṱab\t",
        r"""Escapes in original () don't match escapes in translation ('Ṱab\t')""",
    )


def test_accelerators():
    """tests accelerators"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert passes(stdchecker.accelerators, "&File", "&Fayile")
    assert fails(stdchecker.accelerators, "&File", "Fayile")
    assert fails(stdchecker.accelerators, "File", "&Fayile")
    assert passes(stdchecker.accelerators, "Mail && News", "Pos en Nuus")
    assert fails(stdchecker.accelerators, "Mail &amp; News", "Pos en Nuus")
    assert passes(stdchecker.accelerators, "&Allow", "&\ufeb2\ufee3\ufe8e\ufea3")
    assert fails(stdchecker.accelerators, "Open &File", "Vula& Ifayile")
    kdechecker = checks.KdeChecker()
    assert passes(kdechecker.accelerators, "&File", "&Fayile")
    assert fails(kdechecker.accelerators, "&File", "Fayile")
    assert fails(kdechecker.accelerators, "File", "&Fayile")
    gnomechecker = checks.GnomeChecker()
    assert passes(gnomechecker.accelerators, "_File", "_Fayile")
    assert fails(gnomechecker.accelerators, "_File", "Fayile")
    assert fails(gnomechecker.accelerators, "File", "_Fayile")
    assert fails(gnomechecker.accelerators, "_File", "_Fayil_e")
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.accelerators, "&File", "&Fayile")
    assert passes(
        mozillachecker.accelerators,
        "Warn me if this will disable any of my add&-ons",
        "&Waarsku my as dit enige van my byvoegings sal deaktiveer",
    )
    assert fails_serious(mozillachecker.accelerators, "&File", "Fayile")
    assert fails_serious(mozillachecker.accelerators, "File", "&Fayile")
    assert passes(mozillachecker.accelerators, "Mail &amp; News", "Pos en Nuus")
    assert fails_serious(mozillachecker.accelerators, "Mail &amp; News", "Pos en &Nuus")
    assert passes(mozillachecker.accelerators, "Mail & News", "Pos & Nuus")
    ooochecker = checks.OpenOfficeChecker()
    assert passes(ooochecker.accelerators, "~File", "~Fayile")
    assert fails(ooochecker.accelerators, "~File", "Fayile")
    assert fails(ooochecker.accelerators, "File", "~Fayile")

    # We don't want an accelerator for letters with a diacritic
    assert fails(ooochecker.accelerators, "F~ile", "L~êer")
    lochecker = checks.LibreOfficeChecker()
    assert passes(lochecker.accelerators, "~File", "~Fayile")
    assert fails(lochecker.accelerators, "~File", "Fayile")
    assert fails(lochecker.accelerators, "File", "~Fayile")

    # We don't want an accelerator for letters with a diacritic
    assert fails(lochecker.accelerators, "F~ile", "L~êer")

    # Bug 289: accept accented accelerator characters
    afchecker = checks.StandardChecker(
        checks.CheckerConfig(accelmarkers="&", targetlanguage="fi")
    )
    assert passes(afchecker.accelerators, "&Reload Frame", "P&äivitä kehys")

    trchecker = checks.StandardChecker(
        checks.CheckerConfig(accelmarkers="&", targetlanguage="tr")
    )
    assert passes(trchecker.accelerators, "&Download", "&İndir")
    assert passes(trchecker.accelerators, "&Business", "İ&ş")
    assert passes(trchecker.accelerators, "&Remove", "Kald&ır")
    assert passes(trchecker.accelerators, "&Three", "&Üç")
    assert passes(trchecker.accelerators, "&Three", "Ü&ç")
    assert passes(trchecker.accelerators, "&Before", "&Önce")
    assert passes(trchecker.accelerators, "Fo&ur", "D&ört")
    assert passes(trchecker.accelerators, "Mo&dern", "Ça&ğdaş")
    assert passes(trchecker.accelerators, "Mo&dern", "&Çağdaş")
    assert passes(trchecker.accelerators, "&February", "&Şubat")
    assert passes(trchecker.accelerators, "P&lain", "D&üz")
    assert passes(trchecker.accelerators, "GAR&DEN", "BA&Ğ")

    # Problems:
    # Accelerator before variable - see test_acceleratedvariables


@mark.xfail(reason="Accelerated variables needs a better implementation")
def test_acceleratedvariables():
    """test for accelerated variables"""
    # FIXME: disabled since acceleratedvariables has been removed, but these checks are still needed
    mozillachecker = checks.MozillaChecker()
    assert fails(mozillachecker.acceleratedvariables, "%S &Options", "&%S Ikhetho")
    assert passes(mozillachecker.acceleratedvariables, "%S &Options", "%S &Ikhetho")
    ooochecker = checks.OpenOfficeChecker()
    assert fails(
        ooochecker.acceleratedvariables,
        "%PRODUCTNAME% ~Options",
        "~%PRODUCTNAME% Ikhetho",
    )
    assert passes(
        ooochecker.acceleratedvariables,
        "%PRODUCTNAME% ~Options",
        "%PRODUCTNAME% ~Ikhetho",
    )
    lochecker = checks.LibreOfficeChecker()
    assert fails(
        lochecker.acceleratedvariables,
        "%PRODUCTNAME% ~Options",
        "~%PRODUCTNAME% Ikhetho",
    )
    assert passes(
        lochecker.acceleratedvariables,
        "%PRODUCTNAME% ~Options",
        "%PRODUCTNAME% ~Ikhetho",
    )


def test_acronyms():
    """tests acronyms"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.acronyms, "An HTML file", "'n HTML leer")
    assert fails(stdchecker.acronyms, "An HTML file", "'n LMTH leer")
    assert passes(stdchecker.acronyms, "It is HTML.", "Dit is HTML.")
    # We don't mind if you add an acronym to correct bad capitalisation in the original
    assert passes(stdchecker.acronyms, "An html file", "'n HTML leer")
    # We shouldn't worry about acronyms that appear in a musttranslate file
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=["OK"]))
    assert passes(stdchecker.acronyms, "OK", "Kulungile")
    # Assert punctuation should not hide accronyms
    assert fails(stdchecker.acronyms, "Location (URL) not found", "Blah blah blah")
    # Test '-W' (bug 283)
    assert passes(
        stdchecker.acronyms,
        "%s: option `-W %s' is ambiguous",
        "%s: opsie '-W %s' is dubbelsinnig",
    )


def test_blank():
    """tests blank"""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.blank, "Save as", " ")
    assert fails(stdchecker.blank, "_: KDE comment\\n\nSimple string", "  ")


def test_brackets():
    """tests brackets"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.brackets, "N number(s)", "N getal(le)")
    assert fails(stdchecker.brackets, "For {sic} numbers", "Vier getalle")
    assert fails(stdchecker.brackets, "For }sic{ numbers", "Vier getalle")
    assert fails(stdchecker.brackets, "For [sic] numbers", "Vier getalle")
    assert fails(stdchecker.brackets, "For ]sic[ numbers", "Vier getalle")
    assert passes(stdchecker.brackets, "{[(", "[({")


def test_compendiumconflicts():
    """tests compendiumconflicts"""
    stdchecker = checks.StandardChecker()
    assert fails(
        stdchecker.compendiumconflicts,
        "File not saved",
        r"""#-#-#-#-# file1.po #-#-#-#-#\n
Leer nie gestoor gestoor nie\n
#-#-#-#-# file1.po #-#-#-#-#\n
Leer nie gestoor""",
    )


def test_doublequoting():
    """tests double quotes"""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.doublequoting, "Hot plate", '"Ipuleti" elishisa')
    assert passes(stdchecker.doublequoting, '"Hot" plate', '"Ipuleti" elishisa')
    assert fails(stdchecker.doublequoting, "'Hot' plate", '"Ipuleti" elishisa')
    assert passes(stdchecker.doublequoting, '\\"Hot\\" plate', '\\"Ipuleti\\" elishisa')

    # We don't want the filter to complain about "untranslated" quotes in xml attributes
    frchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert passes(
        frchecker.doublequoting,
        'Click <a href="page.html">',
        'Clique <a href="page.html">',
    )
    assert fails(frchecker.doublequoting, 'Do "this"', 'Do "this"')
    assert passes(frchecker.doublequoting, 'Do "this"', "Do « this »")
    assert fails(frchecker.doublequoting, 'Do "this"', "Do « this » « this »")
    # This used to fail because we strip variables, and was left with an empty quotation that was not converted
    assert passes(
        frchecker.doublequoting, "Copying `%s' to `%s'", "Copie de « %s » vers « %s »"
    )

    vichecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(vichecker.doublequoting, 'Save "File"', "Lưu « Tập tin »")

    # Had a small exception with such a case:
    eschecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="es"))
    assert passes(
        eschecker.doublequoting,
        "<![CDATA[ Enter the name of the Windows workgroup that this server should appear in. ]]>",
        "<![CDATA[ Ingrese el nombre del grupo de trabajo de Windows en el que debe aparecer este servidor. ]]>",
    )


def test_doublespacing():
    """tests double spacing"""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.doublespacing, "Sentence.  Another sentence.", "Sin.  'n Ander sin."
    )
    assert passes(
        stdchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin. No double spacing.",
    )
    assert fails(
        stdchecker.doublespacing,
        "Sentence.  Another sentence.",
        "Sin. Missing the double space.",
    )
    assert fails(
        stdchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin.  Uneeded double space in translation.",
    )
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah %PROGRAMNAME Calc"
    )
    assert passes(
        ooochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah % PROGRAMNAME Calc"
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah %PROGRAMNAME Calc"
    )
    assert passes(
        lochecker.doublespacing, "Execute %PROGRAMNAME Calc", "Blah % PROGRAMNAME Calc"
    )


def test_doublewords():
    """tests doublewords"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.doublewords, "Save the rhino", "Save the rhino")
    assert fails(stdchecker.doublewords, "Save the rhino", "Save the the rhino")
    # Double variables are not an error
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", 1)]))
    assert passes(stdchecker.doublewords, "%s %s installation", "tsenyo ya %s %s")
    # Double XML tags are not an error
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.doublewords,
        "Line one <br> <br> line two",
        "Lyn een <br> <br> lyn twee",
    )
    # In some language certain double words are not errors
    st_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="st"))
    assert passes(
        st_checker.doublewords,
        "Color to draw the name of a message you sent.",
        "Mmala wa ho taka bitso la molaetsa oo o o rometseng.",
    )
    assert passes(st_checker.doublewords, "Ten men", "Banna ba ba leshome")
    assert passes(st_checker.doublewords, "Give SARS the tax", "Lekgetho le le fe SARS")


def test_endpunc():
    """tests endpunc"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.endpunc, "Question?", "Correct?")
    assert fails(stdchecker.endpunc, " Question?", "Wrong ?")
    # Newlines must not mask end punctuation
    assert fails(
        stdchecker.endpunc,
        "Exit change recording mode?\n\n",
        "Phuma esimeni sekugucula kubhalisa.\n\n",
    )
    mozillachecker = checks.MozillaChecker()
    assert passes(
        mozillachecker.endpunc,
        "Upgrades an existing $ProductShortName$ installation.",
        "Ku antswisiwa ka ku nghenisiwa ka $ProductShortName$.",
    )
    # Real examples
    assert passes(
        stdchecker.endpunc,
        "A nickname that identifies this publishing site (e.g.: 'MySite')",
        "Vito ro duvulela leri tirhisiwaka ku kuma sayiti leri ro kandziyisa (xik.: 'Sayiti ra Mina')",
    )
    assert fails(stdchecker.endpunc, "Question", "Wrong\u2026")
    # Making sure singlequotes don't confuse things
    assert passes(
        stdchecker.endpunc,
        "Pseudo-elements can't be negated '%1$S'.",
        "Pseudo-elemente kan nie '%1$S' ontken word nie.",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="km"))
    assert passes(
        stdchecker.endpunc,
        "In this new version, there are some minor conversion improvements on complex style in Openoffice.org Writer.",
        "នៅ​ក្នុង​កំណែ​ថ្មីនេះ មាន​ការ​កែសម្រួល​មួយ​ចំនួន​តូច​ទាក់​ទង​នឹង​ការ​បំលែង​ពុម្ពអក្សរ​ខ្មែរ​ ក្នុង​កម្មវិធី​ការិយាល័យ​ ស្លឹករឹត ដែល​មាន​ប្រើ​ប្រាស់​រចនាប័ទ្មស្មុគស្មាញច្រើន\u00a0។",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="zh"))
    assert passes(
        stdchecker.endpunc,
        "To activate your account, follow this link:\n",
        "要啟用戶口，請瀏覽這個鏈結：\n",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(
        stdchecker.endpunc,
        "Do you want to delete the XX dialog?",
        "Bạn có muốn xoá hộp thoại XX không?",
    )

    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert passes(stdchecker.endpunc, "Header:", "En-tête :")
    assert passes(stdchecker.endpunc, "Header:", "En-tête\u00a0:")


def test_endwhitespace():
    """tests endwhitespace"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.endwhitespace, "A setence.", "I'm correct.")
    assert passes(stdchecker.endwhitespace, "A setence. ", "I'm correct. ")
    assert fails(stdchecker.endwhitespace, "A setence. ", "'I'm incorrect.")
    assert passes(
        stdchecker.endwhitespace,
        "Problem with something: %s\n",
        "Probleem met iets: %s\n",
    )

    zh_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="zh"))
    # This should pass since the space is not needed in Chinese
    assert passes(zh_checker.endwhitespace, "Init. Limit: ", "起始时间限制：")


def test_escapes():
    """tests escapes"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.escapes, r"""A sentence""", "I'm correct.")
    assert passes(stdchecker.escapes, "A file\n", "'n Leer\n")
    assert fails_serious(stdchecker.escapes, r"blah. A file", r"bleah.\n'n leer")
    assert passes(stdchecker.escapes, r"A tab\t", r"'n Tab\t")
    assert fails_serious(stdchecker.escapes, r"A tab\t", r"'n Tab")
    assert passes(stdchecker.escapes, r"An escape escape \\", r"Escape escape \\")
    assert fails_serious(stdchecker.escapes, r"An escape escape \\", "Escape escape")
    assert passes(stdchecker.escapes, r"A double quote \"", r"Double quote \"")
    assert fails_serious(stdchecker.escapes, r"A double quote \"", "Double quote")
    # Escaped escapes
    assert passes(stdchecker.escapes, "An escaped newline \\n", "Escaped newline \\n")
    assert fails_serious(
        stdchecker.escapes, "An escaped newline \\n", "Escaped newline \n"
    )
    # Real example
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.escapes,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.escapes,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )


def test_newlines():
    """tests newlines"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.newlines, "Nothing to see", "Niks te sien")
    assert passes(stdchecker.newlines, "Correct\n", "Korrek\n")
    assert passes(stdchecker.newlines, "Correct\r", "Korrek\r")
    assert passes(stdchecker.newlines, "Correct\r\n", "Korrek\r\n")
    assert fails(stdchecker.newlines, "A file\n", "'n Leer")
    assert fails(stdchecker.newlines, "A file", "'n Leer\n")
    assert fails(stdchecker.newlines, "A file\r", "'n Leer")
    assert fails(stdchecker.newlines, "A file", "'n Leer\r")
    assert fails(stdchecker.newlines, "A file\n", "'n Leer\r\n")
    assert fails(stdchecker.newlines, "A file\r\n", "'n Leer\n")
    assert fails(stdchecker.newlines, "blah.\nA file", "bleah. 'n leer")
    # msgfmt errors
    assert fails(stdchecker.newlines, "One two\n", "Een\ntwee")
    assert fails(stdchecker.newlines, "\nOne two", "Een\ntwee")
    # Real example
    ooochecker = checks.OpenOfficeChecker()
    assert fails(
        ooochecker.newlines,
        "The arrowhead was modified without saving.\nWould you like to save the arrowhead now?",
        "Ṱhoho ya musevhe yo khwinifhadzwa hu si na u seiva.Ni khou ṱoda u seiva thoho ya musevhe zwino?",
    )
    lochecker = checks.LibreOfficeChecker()
    assert fails(
        lochecker.newlines,
        "The arrowhead was modified without saving.\nWould you like to save the arrowhead now?",
        "Ṱhoho ya musevhe yo khwinifhadzwa hu si na u seiva.Ni khou ṱoda u seiva thoho ya musevhe zwino?",
    )


def test_tabs():
    """tests tabs"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.tabs, "Nothing to see", "Niks te sien")
    assert passes(stdchecker.tabs, "Correct\t", "Korrek\t")
    assert passes(stdchecker.tabs, "Correct\tAA", "Korrek\tAA")
    assert fails_serious(stdchecker.tabs, "A file\t", "'n Leer")
    assert fails_serious(stdchecker.tabs, "A file", "'n Leer\t")
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.tabs,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.tabs,
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
        ",\t44\t;\t59\t:\t58\t{Tab}\t9\t{space}\t32",
    )


def test_filepaths():
    """tests filepaths"""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.filepaths,
        "%s to the file /etc/hosts on your system.",
        "%s na die leer /etc/hosts op jou systeem.",
    )
    assert fails(
        stdchecker.filepaths,
        "%s to the file /etc/hosts on your system.",
        "%s na die leer /etc/gasheer op jou systeem.",
    )
    assert passes(
        stdchecker.filepaths, "Text with <br />line break", "Teks met <br /> lynbreuk"
    )


def test_kdecomments():
    """tests kdecomments"""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.kdecomments,
        r"""_: I am a comment\n
A string to translate""",
        "'n String om te vertaal",
    )
    assert fails(
        stdchecker.kdecomments,
        r"""_: I am a comment\n
A string to translate""",
        r"""_: Ek is 'n commment\n
'n String om te vertaal""",
    )
    assert fails(
        stdchecker.kdecomments,
        """_: I am a comment\\n\n""",
        """_: I am a comment\\n\n""",
    )


def test_long():
    """tests long messages"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.long, "I am normal", "Ek is ook normaal")
    assert fails(
        stdchecker.long,
        "Short.",
        "Kort.......................................................................................",
    )
    assert fails(stdchecker.long, "a", "bc")


@mark.xfail(reason="FIXME: All fails() tests are not working")
def test_musttranslatewords():
    """tests stopwords"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(musttranslatewords=[]))
    assert passes(
        stdchecker.musttranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(musttranslatewords=["Mozilla"])
    )
    assert passes(
        stdchecker.musttranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik Mozilla natuurlik",
    )
    assert passes(
        stdchecker.musttranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik le mozille soos jy",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # should always pass if there are no stopwords in the original
    assert passes(
        stdchecker.musttranslatewords,
        "This uses something else. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # check that we can find words surrounded by punctuation
    assert passes(
        stdchecker.musttranslatewords,
        "Click 'Mozilla' button",
        "Kliek 'Motzille' knoppie",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "Click 'Mozilla' button",
        "Kliek 'Mozilla' knoppie",
    )
    assert passes(
        stdchecker.musttranslatewords,
        'Click "Mozilla" button',
        'Kliek "Motzille" knoppie',
    )
    assert fails(
        stdchecker.musttranslatewords,
        'Click "Mozilla" button',
        'Kliek "Mozilla" knoppie',
    )
    assert fails(
        stdchecker.musttranslatewords,
        'Click "Mozilla" button',
        "Kliek «Mozilla» knoppie",
    )
    assert passes(
        stdchecker.musttranslatewords,
        "Click (Mozilla) button",
        "Kliek (Motzille) knoppie",
    )
    assert fails(
        stdchecker.musttranslatewords,
        "Click (Mozilla) button",
        "Kliek (Mozilla) knoppie",
    )
    assert passes(stdchecker.musttranslatewords, "Click Mozilla!", "Kliek Motzille!")
    assert fails(stdchecker.musttranslatewords, "Click Mozilla!", "Kliek Mozilla!")
    ## We need to define more word separators to allow us to find those hidden untranslated items
    # assert fails(stdchecker.musttranslatewords, "Click OK", "Blah we-OK")
    # Don't get confused when variables are the same as a musttranslate word
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            varmatches=[
                ("%", None),
            ],
            musttranslatewords=["OK"],
        )
    )
    assert passes(
        stdchecker.musttranslatewords, "Click %OK to start", "Kliek %OK om te begin"
    )
    # Unicode
    assert fails(stdchecker.musttranslatewords, "Click OK", "Kiḽikani OK")


def test_notranslatewords():
    """tests stopwords"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=[]))
    assert passes(
        stdchecker.notranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Mozilla", "Opera"])
    )
    assert fails(
        stdchecker.notranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik le mozille natuurlik",
    )
    assert passes(
        stdchecker.notranslatewords,
        "This uses Mozilla of course",
        "hierdie gebruik Mozilla natuurlik",
    )
    assert fails(
        stdchecker.notranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik le mozille soos jy",
    )
    assert passes(
        stdchecker.notranslatewords,
        "This uses Mozilla. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # should always pass if there are no stopwords in the original
    assert passes(
        stdchecker.notranslatewords,
        "This uses something else. Don't you?",
        "hierdie gebruik Mozilla soos jy",
    )
    # Cope with commas
    assert passes(
        stdchecker.notranslatewords,
        "using Mozilla Task Manager",
        "šomiša Selaola Mošomo sa Mozilla, gomme",
    )
    # Find words even if they are embedded in punctuation
    assert fails(
        stdchecker.notranslatewords,
        "Click 'Mozilla' button",
        "Kliek 'Motzille' knoppie",
    )
    assert passes(
        stdchecker.notranslatewords, "Click 'Mozilla' button", "Kliek 'Mozilla' knoppie"
    )
    assert fails(stdchecker.notranslatewords, "Click Mozilla!", "Kliek Motzille!")
    assert passes(stdchecker.notranslatewords, "Click Mozilla!", "Kliek Mozilla!")
    assert fails(
        stdchecker.notranslatewords,
        "Searches (From Opera)",
        "adosako (kusukela ku- Ophera)",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Sun", "NeXT"])
    )
    assert fails(
        stdchecker.notranslatewords, "Sun/NeXT Audio", "Odio dza Ḓuvha/TeVHELAHO"
    )
    assert passes(stdchecker.notranslatewords, "Sun/NeXT Audio", "Odio dza Sun/NeXT")
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["sendmail"])
    )
    assert fails(
        stdchecker.notranslatewords,
        "because 'sendmail' could",
        "ngauri 'rumelameiḽi' a yo",
    )
    assert passes(
        stdchecker.notranslatewords,
        "because 'sendmail' could",
        "ngauri 'sendmail' a yo",
    )
    stdchecker = checks.StandardChecker(checks.CheckerConfig(notranslatewords=["Base"]))
    assert fails(
        stdchecker.notranslatewords,
        " - %PRODUCTNAME Base: Relation design",
        " - %PRODUCTNAME Sisekelo: Umsiko wekuhlobana",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Writer"])
    )
    assert fails(
        stdchecker.notranslatewords,
        "&[ProductName] Writer/Web",
        "&[ProductName] Umbhali/iWebhu",
    )
    # Unicode - different decompositions
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["\u1e3cike"])
    )
    assert passes(
        stdchecker.notranslatewords, "You \u1e3cike me", "Ek \u004c\u032dike jou"
    )


def test_numbers():
    """test numbers"""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.numbers,
        "Netscape 4 was not as good as Netscape 7.",
        "Netscape 4 was nie so goed soos Netscape 7 nie.",
    )
    # Check for correct detection of degree.  Also check that we aren't getting confused with 1 and 2 byte UTF-8 characters
    assert fails(stdchecker.numbers, "180° turn", "180 turn")
    assert passes(stdchecker.numbers, "180° turn", "180° turn")
    assert fails(stdchecker.numbers, "180° turn", "360 turn")
    assert fails(stdchecker.numbers, "180° turn", "360° turn")
    assert passes(stdchecker.numbers, "180~ turn", "180 turn")
    assert passes(stdchecker.numbers, "180¶ turn", "180 turn")
    # Numbers with multiple decimal points
    assert passes(stdchecker.numbers, "12.34.56", "12.34.56")
    assert fails(stdchecker.numbers, "12.34.56", "98.76.54")
    # Currency
    # FIXME we should probably be able to handle currency checking with locale inteligence
    assert passes(stdchecker.numbers, "R57.60", "R57.60")
    # FIXME - again locale intelligence should allow us to use other decimal seperators
    assert fails(stdchecker.numbers, "R57.60", "R57,60")
    assert fails(stdchecker.numbers, "1,000.00", "1 000,00")
    # You should be able to reorder numbers
    assert passes(
        stdchecker.numbers,
        "40-bit RC2 encryption with RSA and an MD5",
        "Umbhalo ocashile i-RC2 onamabhithi angu-40 one-RSA ne-MD5",
    )
    # Don't fail the numbers check if the entry is a dialogsize entry
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.numbers, "width: 12em;", "width: 20em;")


def test_persian_numbers():
    """test non latin numbers for Persian (RTL)"""
    fa_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fa"))
    assert passes(fa_checker.numbers, "&حرکت آهسته (۰.۵×)", "&Slow Motion (0.5×)")
    assert passes(fa_checker.numbers, "&حرکت آهسته (0.5×)", "&Slow Motion (0.5×)")
    assert passes(
        fa_checker.numbers, '<img alt="١۰" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        fa_checker.numbers, '<img alt="10" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        fa_checker.numbers, "دسترسی مسدود شده است (۴۰۳)", "Access denied (403)"
    )
    assert passes(fa_checker.numbers, "کتاب موزیلا، ۱۵:۱", "The Book of Mozilla, 15:1")
    assert passes(
        fa_checker.numbers,
        "<p>نشانی درخواست مشخصا(به عنوان مثال<q>mozilla.org:80</q>برای درگاه ۸۰ بر روی  mozilla.org)  ازدرگاهی استفاده می کندکه در حالت عادی به عنوان کاربردی <em>به غیر</em> از وبگردی استفاده می شود.مرورگر برای حفاظت و امنیت شما این درخواست را لغوکرد.</p>",
        "<p>The requested address specified a port (e.g. <q>mozilla.org:80</q> for port 80 on mozilla.org) normally used for purposes <em>other</em> than Web browsing. The browser has canceled the request for your protection and security.</p>",
    )
    assert passes(
        fa_checker.numbers,
        "دستور پردازشی <?%1$S?> دیگر تأثیری خارج از prolog ندارد (برای اطلاعات بیشتر، اشکال ۳۶۰۱۱۹ را مشاهده کنید).",
        "<?%1$S?> processing instruction does not have any effect outside the prolog anymore (see bug 360119).",
    )
    assert passes(
        fa_checker.numbers,
        "encoding حروف این سند بسیار دیرتر از آنکه مورد اثر واقع شود شناسایی شد.encoding فایل برای شناسایی باید به ۱۰۲۴ بایت اول فایل برای شناسایی منتقل شود.",
        "The character encoding declaration of document was found too late for it to take effect. The encoding declaration needs to be moved to be within the first 1024 bytes of the file.",
    )
    assert passes(
        fa_checker.numbers,
        "ویدئو یا صدا در این صفحه نرم‌افزار DRMای احتیاج دارد که نسخه ۶۴ بیتی از %1$S از آن پیشتیبانی نمی‌کند. %2$S",
        "The audio or video on this page requires DRM software that this 64-bit build of %1$S does not support. %2$S",
    )
    assert passes(
        fa_checker.numbers,
        "شما اندازه خیلی بزرگی برای حداقل اندازه قلم انتخاب کرده‌اید (بیش از ۲۴ پیکسل). این ممکن است باعث شود پیکربندی صفحاتی مانند این سخت یا غیرممکن بشود.",
        "You have selected a very large minimum font size (more than 24 pixels). This may make it difficult or impossible to use some important configuration pages like this one.",
    )


def test_bengali_numbers():
    """test non latin numbers for Bengali (LTR)"""
    bn_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="bn"))
    assert passes(bn_checker.numbers, "উচ্চ গতি (১.৫ গুন)", "&High Speed (1.5×)")
    assert passes(bn_checker.numbers, "উচ্চ গতি (0.5 গুন)", "&Slow Motion (0.5×)")
    assert passes(
        bn_checker.numbers, '<img alt="১০" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        bn_checker.numbers, '<img alt="10" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        bn_checker.numbers,
        "<strong>Mozilla-র বই</strong>১৫: ১ পাতা থেকে সংগৃহীত",
        "from <strong>The Book of Mozilla,</strong> 15:1",
    )
    assert passes(
        bn_checker.numbers,
        "ট্যাগ গুলি ২৫ টি অক্ষরের মধ্যে সীমাবদ্ধ",
        "Tags are limited to 25 characters",
    )
    assert passes(
        bn_checker.numbers,
        "পাসওয়ার্ড অন্তত ৮-টি অক্ষর বিশিষ্ট হওয়া আবশ্যক এবং এই ক্ষেত্রে ব্যবহারকারী অ্যাকাউন্টের নাম অথবা পুনরুদ্ধারের (key) পাসওয়ার্ড রূপে ব্যবহার করা যাবে না।",
        "Your password must be at least 8 characters long.  It cannot be the same as either your user name or your Recovery Key.",
    )


def test_arabic_numbers():
    """test non latin numbers for Arabic"""
    ar_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="ar"))
    assert passes(
        ar_checker.numbers,
        "أقصى طول للوسم ٢٥ حرفًا",
        "Tags are limited to 25 characters",
    )
    assert passes(ar_checker.numbers, "حركة ب&طيئة (٠٫٥×)", "&Slow Motion (0.5×)")
    assert passes(ar_checker.numbers, "متصفح &٣٦٠ الآمن", "&360 Secure Browser")
    assert passes(
        ar_checker.numbers,
        "من <strong>كتاب موزيلا،</strong> ١٥‏:١",
        "from <strong>The Book of Mozilla,</strong> 15:1",
    )
    assert passes(ar_checker.numbers, "١٧٥٪", "175%")


def test_assamese_numbers():
    """test non latin numbers for Assamese"""
    as_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="as"))
    assert passes(
        as_checker.numbers,
        "প্ৰতি ৩ ছেকেণ্ডত স্বচালিতভাৱে সতেজ কৰক",
        "Autorefresh every 3 seconds",
    )
    assert passes(
        as_checker.numbers,
        "পৃষ্ঠা পুনৰ ল'ড কৰা হৈছিল, কাৰণ HTML দস্তাবেজৰ আখৰ এনক'ডিং যোষণা ফাইলৰ প্ৰথম ১০২৪ বাইট পূৰ্বস্কেন কৰোতে পোৱা নগল। এনক'ডিং ঘোষণাক ফাইলৰ প্ৰথম ১০২৪ বাইটৰ মাজত স্থানান্তৰ কৰিব লাগিব।",
        "The page was reloaded, because the character encoding declaration of the HTML document was not found when prescanning the first 1024 bytes of the file. The encoding declaration needs to be moved to be within the first 1024 bytes of the file.",
    )
    assert passes(as_checker.numbers, "সংস্কৰণ ৩", "Version 3")
    assert passes(as_checker.numbers, "১৭৫%", "175%")


def test_options():
    """tests command line options e.g. --option"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.options, "--help", "--help")
    assert fails(stdchecker.options, "--help", "--hulp")
    assert fails(stdchecker.options, "--input=FILE", "--input=FILE")
    assert passes(stdchecker.options, "--input=FILE", "--input=LÊER")
    assert fails(stdchecker.options, "--input=FILE", "--tovoer=LÊER")
    # We don't want just any '--' to trigger this test - the error will be confusing
    assert passes(stdchecker.options, "Hello! -- Hi", "Hallo! &mdash; Haai")
    assert passes(stdchecker.options, "--blank--", "--vide--")


def test_printf():
    """tests printf style variables"""
    # This should really be a subset of the variable checks
    # Ideally we should be able to adapt based on #, directives also
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.printf, "I am %s", "Ek is %s")
    assert fails(stdchecker.printf, "I am %s", "Ek is %d")
    assert passes(stdchecker.printf, "I am %#100.50hhf", "Ek is %#100.50hhf")
    assert fails(stdchecker.printf, "I am %#100s", "Ek is %10s")
    assert fails(
        stdchecker.printf,
        "... for user %.100s on %.100s:",
        "... lomuntu osebenzisa i-%. I-100s e-100s:",
    )
    assert passes(stdchecker.printf, "%dMB", "%d MG")
    # Reordering
    assert passes(
        stdchecker.printf, "String %s and number %d", "String %1$s en nommer %2$d"
    )
    assert passes(
        stdchecker.printf, "String %1$s and number %2$d", "String %1$s en nommer %2$d"
    )
    assert passes(
        stdchecker.printf, "String %s and number %d", "Nommer %2$d and string %1$s"
    )
    assert passes(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %1$s en nommer %3$d en reële getal %2$f",
    )
    assert passes(
        stdchecker.printf,
        "String %1$s and real number %2$f and number %3$d",
        "String %1$s en nommer %3$d en reële getal %2$f",
    )
    assert passes(
        stdchecker.printf,
        "Real number %2$f and string %1$s and number %3$d",
        "String %1$s en nommer %3$d en reële getal %2$f",
    )
    assert fails(
        stdchecker.printf, "String %s and number %d", "Nommer %1$d and string %2$s"
    )
    assert fails(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %1$s en nommer %3$d en reële getal %2$d",
    )
    assert fails(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %1$s en nommer %3$d en reële getal %4$f",
    )
    assert fails(
        stdchecker.printf,
        "String %s and real number %f and number %d",
        "String %2$s en nommer %3$d en reële getal %2$f",
    )
    assert fails(
        stdchecker.printf,
        "Real number %2$f and string %1$s and number %3$d",
        "String %1$f en nommer %3$d en reële getal %2$f",
    )
    # checking python format strings
    assert passes(
        stdchecker.printf,
        "String %(1)s and number %(2)d",
        "Nommer %(2)d en string %(1)s",
    )
    assert passes(
        stdchecker.printf,
        "String %(str)s and number %(num)d",
        "Nommer %(num)d en string %(str)s",
    )
    assert fails(
        stdchecker.printf,
        "String %(str)s and number %(num)d",
        "Nommer %(nommer)d en string %(str)s",
    )
    assert fails(
        stdchecker.printf,
        "String %(str)s and number %(num)d",
        "Nommer %(num)d en string %s",
    )
    # checking omitted plural format string placeholder %.0s
    stdchecker.hasplural = 1
    assert passes(stdchecker.printf, "%d plurals", "%.0s plural")
    # checking Objective-C %@ format specification
    assert fails(stdchecker.printf, "I am %@", "Ek is @%")  # typo
    assert fails(
        stdchecker.printf, "Object %@ and object %@", "String %1$@ en string %3$@"
    )  # out of bounds
    assert fails(stdchecker.printf, "I am %@", "Ek is %s")  # wrong specification
    assert passes(
        stdchecker.printf, "Object %@ and string %s", "Object %1$@ en string %2$s"
    )  # correct sentence
    # Checking boost format.
    # Boost classic printf.
    assert passes(
        stdchecker.printf,
        "writing %1%,  x=%2% : %3%-th try",
        "escribindo %1%,  x=%2% : %3%-esimo intento",
    )
    # Reordering boost.
    assert passes(stdchecker.printf, "%1% %2% %3% %2% %1%", "%1% %2% %3% %2% %1%")
    # Boost posix format.
    assert passes(
        stdchecker.printf, "(x,y) = (%1$+5d,%2$+5d)", "(x,y) = (%1$+5d,%2$+5d)"
    )
    # Boost several ways to express the same.
    assert passes(stdchecker.printf, "(x,y) = (%+5d,%+5d)", "(x,y) = (%+5d,%+5d)")
    assert passes(stdchecker.printf, "(x,y) = (%|+5|,%|+5|)", "(x,y) = (%|+5|,%|+5|)")
    assert passes(
        stdchecker.printf, "(x,y) = (%1$+5d,%2$+5d)", "(x,y) = (%1$+5d,%2$+5d)"
    )
    assert passes(
        stdchecker.printf, "(x,y) = (%|1$+5|,%|2$+5|)", "(x,y) = (%|1$+5|,%|2$+5|)"
    )
    # Boost using manipulators.
    assert passes(
        stdchecker.printf, "_%1$+5d_ %1$d", "_%1$+5d_ %1$d"
    )  # This is failing.
    assert passes(stdchecker.printf, "_%1%_ %1%", "_%1%_ %1%")
    # Boost absolute tabulations.
    assert passes(stdchecker.printf, "%1%, %2%, %|40t|%3%", "%1%, %2%, %|40t|%3%")


def test_pythonbraceformat():
    """Tests python brace format placeholder"""
    stdchecker = checks.StandardChecker()
    # anonymous formats
    assert passes(
        stdchecker.pythonbraceformat,
        "String {} and number {}",
        "String {} en nommer {}",
    )
    assert passes(stdchecker.pythonbraceformat, "String {1}", "Nommer {} en string {}")
    assert passes(
        stdchecker.pythonbraceformat,
        "String {1} and number {0}",
        "Nommer {0} en string {1}",
    )
    assert fails(stdchecker.pythonbraceformat, "String {}, {}", "String {}")
    assert fails_serious(
        stdchecker.pythonbraceformat, "String {}", "String {} en nommer {}"
    )
    assert fails_serious(stdchecker.pythonbraceformat, "String {}", "Nommer {1}")
    assert fails_serious(stdchecker.pythonbraceformat, "String {0}", "Nommer {1}")
    assert fails_serious(stdchecker.pythonbraceformat, "String {0} {}", "Nommer {1}")
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.pythonbraceformat,
        "Time remaining: {[1] minutes }{[2] seconds}",
        "Tenpo che'l resta: {[1] minuti}{[2] secondi}",
    )

    # Named formats
    assert passes(
        stdchecker.pythonbraceformat,
        "String {str} and number {num}",
        "Nommer {num} en string {str}",
    )
    # TODO: check for a mixture of substitution techniques
    assert fails(
        stdchecker.pythonbraceformat,
        "String {str} and number {num}",
        "Nommer {num} en string %s",
    )
    assert fails_serious(
        stdchecker.pythonbraceformat,
        "String {str} and number {num}",
        "Nommer {onbekend} en string {str}",
    )


def test_puncspacing():
    """tests spacing after punctuation"""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.puncspacing, "One, two, three.", "Kunye, kubili, kuthathu."
    )
    assert passes(
        stdchecker.puncspacing, "One, two, three. ", "Kunye, kubili, kuthathu."
    )
    assert fails(stdchecker.puncspacing, "One, two, three. ", "Kunye, kubili,kuthathu.")
    assert passes(
        stdchecker.puncspacing, "One, two, three!?", "Kunye, kubili, kuthathu?"
    )

    # Some languages have padded puntuation marks
    frchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert passes(frchecker.puncspacing, 'Do "this"', "Do « this »")
    assert passes(frchecker.puncspacing, 'Do "this"', "Do «\u00a0this\u00a0»")
    assert fails(frchecker.puncspacing, 'Do "this"', "Do «this»")

    # Handle Bidi markers as non-characters
    hechecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="he"))
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u200f לך")  # RLM
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u200e לך")  # LRM
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202b לך")  # RLE
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202a לך")  # LRE
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202e לך")  # RLO
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202d לך")  # LRO
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u202c לך")  # PDF
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2069 לך")  # PDI
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2068 לך")  # FSI
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2067 לך")  # RLI
    assert passes(hechecker.puncspacing, "hi. there", "שלום.\u2066 לך")  # LRI

    # ZWJ and ZWNJ handling as non-characters
    archecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="ar"))
    assert passes(archecker.puncspacing, "hi. there", "السلام.\u200d عليكم")  # ZWJ
    assert passes(archecker.puncspacing, "hi. there", "السلام.\u200c عليكم")  # ZWNJ


def test_purepunc():
    """tests messages containing only punctuation"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.purepunc, ".", ".")
    assert passes(stdchecker.purepunc, "", "")
    assert fails(stdchecker.purepunc, ".", " ")
    assert fails(stdchecker.purepunc, "Find", "'")
    assert fails(stdchecker.purepunc, "'", "Find")
    assert passes(stdchecker.purepunc, "year measurement template|2000", "2000")


def test_sentencecount():
    """tests sentencecount messages"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.sentencecount, "One. Two. Three.", "Een. Twee. Drie.")
    assert passes(stdchecker.sentencecount, "One two three", "Een twee drie.")
    assert fails(stdchecker.sentencecount, "One. Two. Three.", "Een Twee. Drie.")
    assert passes(
        stdchecker.sentencecount, "Sentence with i.e. in it.", "Sin met d.w.s. in dit."
    )  # bug 178, description item 8
    el_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="el"))
    assert fails(
        el_checker.sentencecount,
        "First sentence. Second sentence.",
        "Πρώτη πρόταση. δεύτερη πρόταση.",
    )


def test_short():
    """tests short messages"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.short, "I am normal", "Ek is ook normaal")
    assert fails(stdchecker.short, "I am a very long sentence", "Ek")
    assert fails(stdchecker.short, "abcde", "c")


def test_singlequoting():
    """tests single quotes"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.singlequoting, "A 'Hot' plate", "Ipuleti 'elishisa' kunye")
    # FIXME this should pass but doesn't probably to do with our logic that got confused at the end of lines
    assert passes(stdchecker.singlequoting, "'Hot' plate", "Ipuleti 'elishisa'")
    # FIXME newlines also confuse our algorithm for single quotes
    assert passes(stdchecker.singlequoting, "File '%s'\n", "'%s' Faele\n")
    assert fails(stdchecker.singlequoting, "'Hot' plate", 'Ipuleti "elishisa"')
    assert passes(stdchecker.singlequoting, "It's here.", "Dit is hier.")
    # Don't get confused by punctuation that touches a single quote
    assert passes(stdchecker.singlequoting, "File '%s'.", "'%s' Faele.")
    assert passes(
        stdchecker.singlequoting, "Blah 'format' blah.", "Blah blah 'sebopego'."
    )
    assert passes(
        stdchecker.singlequoting, "Blah 'format' blah!", "Blah blah 'sebopego'!"
    )
    assert passes(
        stdchecker.singlequoting, "Blah 'format' blah?", "Blah blah 'sebopego'?"
    )
    # Real examples
    assert passes(
        stdchecker.singlequoting,
        "A nickname that identifies this publishing site (e.g.: 'MySite')",
        "Vito ro duvulela leri tirhisiwaka ku kuma sayiti leri ro kandziyisa (xik.: 'Sayiti ra Mina')",
    )
    assert passes(stdchecker.singlequoting, "isn't", "ayikho")
    assert passes(
        stdchecker.singlequoting,
        "Required (can't send message unless all recipients have certificates)",
        "Verlang (kan nie boodskappe versend tensy al die ontvangers sertifikate het nie)",
    )
    # Afrikaans 'n
    assert passes(
        stdchecker.singlequoting,
        "Please enter a different site name.",
        "Tik 'n ander werfnaam in.",
    )
    assert passes(
        stdchecker.singlequoting,
        '"%name%" already exists. Please enter a different site name.',
        '"%name%" bestaan reeds. Tik \'n ander werfnaam in.',
    )
    # Check that accelerators don't mess with removing singlequotes
    mozillachecker = checks.MozillaChecker()
    assert passes(
        mozillachecker.singlequoting,
        "&Don't import anything",
        "&Moenie enigiets invoer nie",
    )
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.singlequoting,
        "~Don't import anything",
        "~Moenie enigiets invoer nie",
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.singlequoting, "~Don't import anything", "~Moenie enigiets invoer nie"
    )


def test_vietnamese_singlequoting():
    vichecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(vichecker.singlequoting, "Save 'File'", "Lưu « Tập tin »")
    assert passes(vichecker.singlequoting, "Save `File'", "Lưu « Tập tin »")


@mark.xfail(reason="Bug #3408")
def test_persian_single_and_double_quote_fail_at_the_same_time():
    """Test Persian single and double quote failures in string with single quotes."""
    checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fa"))

    # With single quote check.
    assert fails(checker.singlequoting, "Path: '%S'", "مسیر: '%S'‎")
    assert fails(checker.singlequoting, "Path: '%S'", 'مسیر: "%S"‎')
    assert passes(checker.singlequoting, "Path: '%S'", "مسیر: «%S»")

    # With double quote check.
    assert passes(checker.doublequoting, "Path: '%S'", "مسیر: '%S'‎")
    assert passes(checker.doublequoting, "Path: '%S'", 'مسیر: "%S"‎')
    assert passes(checker.doublequoting, "Path: '%S'", "مسیر: «%S»")


def test_persian_quoting():
    """Test single and double quoting for Persian."""
    checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fa"))

    # Just double quoting.
    assert fails(checker.doublequoting, 'Path: "%S"', "مسیر: '%S'‎")
    assert fails(checker.doublequoting, 'Path: "%S"', 'مسیر: "%S"‎')
    assert passes(checker.doublequoting, 'Path: "%S"', "مسیر: «%S»")

    # Just XML quoting.
    assert passes(
        checker.singlequoting, '<area shape="circle">', '<area shape="circle">'
    )
    assert passes(
        checker.doublequoting, '<area shape="circle">', '<area shape="circle">'
    )

    # XML quoting and double quoting.
    assert passes(
        checker.singlequoting,
        'The "coords" attribute of the <area shape="circle"> tag has a negative radius.',
        'مشخصهٔ «coords» برچسب ‪<area shape="circle">‬ دارای «radius» منفی است.',
    )
    assert passes(
        checker.doublequoting,
        'The "coords" attribute of the <area shape="circle"> tag has a negative "radius".',
        'مشخصهٔ «coords» برچسب ‪<area shape="circle">‬ دارای «radius» منفی است.',
    )

    # Single quotes with variables in source fails both single and double quote
    # checks.
    assert fails(
        checker.singlequoting, "'%1$S' is not a directory", "'%1$S' یک شاخه نیست"
    )
    # TODO the following should fail.
    assert passes(
        checker.singlequoting, "'%1$S' is not a directory", '"%1$S" یک شاخه نیست'
    )
    assert fails(
        checker.doublequoting, "'%1$S' is not a directory", "'%1$S' یک شاخه نیست"
    )
    assert fails(
        checker.doublequoting, "'%1$S' is not a directory", '"%1$S" یک شاخه نیست'
    )
    # But works when using the right quoting in translation.
    assert passes(
        checker.singlequoting, "'%1$S' is not a directory", "«%1$S» یک شاخه نیست"
    )
    assert passes(
        checker.doublequoting, "'%1$S' is not a directory", "«%1$S» یک شاخه نیست"
    )

    # Mixing single quotes and and single quotes that shouldn't be translated.
    assert fails(
        checker.singlequoting, "Can't find property '%S'", "خاصیت '%S' یافت نشد"
    )
    assert passes(
        checker.singlequoting, "Can't find property '%S'", "خاصیت «%S» یافت نشد"
    )

    # Mixed single quotes do not trigger double quote check.
    assert passes(
        checker.doublequoting, "Can't find property '%S'", "خاصیت '%S' یافت نشد"
    )
    # TODO the following should pass.
    assert fails(
        checker.doublequoting, "Can't find property '%S'", "خاصیت «%S» یافت نشد"
    )

    # Single quotes that are not errors pass.
    assert passes(
        checker.singlequoting,
        "Request the version of a user's client.",
        "درخواست نسخه کلاینت کاربر.",
    )
    assert passes(
        checker.doublequoting,
        "Request the version of a user's client.",
        "درخواست نسخه کلاینت کاربر.",
    )


def test_simplecaps():
    """tests simple caps"""
    # Simple caps is a very vauge test so the checks here are mostly for obviously fixable problem
    # or for checking obviously correct situations that are triggering a failure.
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.simplecaps,
        "MB of disk space for the cache.",
        "MB yendzawo yediski etsala.",
    )
    # We should squash 'I' in the source text as it messes with capital detection
    assert passes(stdchecker.simplecaps, "if you say I want", "as jy se ek wil")
    assert passes(
        stdchecker.simplecaps, "sentence. I want more.", "sin. Ek wil meer he."
    )
    assert passes(
        stdchecker.simplecaps,
        "Where are we? I can't see where we are going.",
        "Waar is ons? Ek kan nie sien waar ons gaan nie.",
    )
    ## We should remove variables before checking
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("%", 1)]))
    assert passes(
        stdchecker.simplecaps, "Could not load %s", "A swi koteki ku panga %S"
    )
    assert passes(
        stdchecker.simplecaps,
        'The element "%S" is not recognized.',
        'Elemente "%S" a yi tiveki.',
    )
    stdchecker = checks.StandardChecker(checks.CheckerConfig(varmatches=[("&", ";")]))
    assert passes(
        stdchecker.simplecaps,
        "Determine how &brandShortName; connects to the Internet.",
        "Kuma &brandShortName; hlanganisa eka Internete.",
    )
    ## If source is ALL CAPS then we should just check that target is also ALL CAPS
    assert passes(stdchecker.simplecaps, "COUPDAYS", "COUPMALANGA")
    # Just some that at times have failed but should always pass
    assert passes(
        stdchecker.simplecaps,
        "Create a query  entering an SQL statement directly.",
        "Yakha sibuti singena SQL inkhomba yesitatimende.",
    )
    ooochecker = checks.OpenOfficeChecker()
    assert passes(
        ooochecker.simplecaps,
        "SOLK (%PRODUCTNAME Link)",
        "SOLK (%PRODUCTNAME Thumanyo)",
    )
    assert passes(
        ooochecker.simplecaps, "%STAROFFICE Image", "Tshifanyiso tsha %STAROFFICE"
    )
    lochecker = checks.LibreOfficeChecker()
    assert passes(
        lochecker.simplecaps, "SOLK (%PRODUCTNAME Link)", "SOLK (%PRODUCTNAME Thumanyo)"
    )
    assert passes(
        lochecker.simplecaps, "%STAROFFICE Image", "Tshifanyiso tsha %STAROFFICE"
    )
    assert passes(
        stdchecker.simplecaps,
        "Flies, flies, everywhere! Ack!",
        "Vlieë, oral vlieë! Jig!",
    )


@mark.skipif(
    not spelling.available or not spelling._get_checker("af"),
    reason="Spell checking for af is not available",
)
def test_spellcheck():
    """tests spell checking"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert passes(stdchecker.spellcheck, "Great trek", "Groot trek")
    assert fails(stdchecker.spellcheck, "Final deadline", "End of the road")
    # Bug 289: filters accelerators before spell checking
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(accelmarkers="&", targetlanguage="fi")
    )
    assert passes(stdchecker.spellcheck, "&Reload Frame", "P&äivitä kehys")
    # Ensure we don't check notranslatewords
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert fails(
        stdchecker.spellcheck, "Mozilla is wonderful", "Mozillaaa is wonderlik"
    )
    # We should pass the test if the "error" occurs in the English
    assert passes(
        stdchecker.spellcheck, "Mozillaxxx is wonderful", "Mozillaxxx is wonderlik"
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(targetlanguage="af", notranslatewords=["Mozilla"])
    )
    assert passes(stdchecker.spellcheck, "Mozilla is wonderful", "Mozilla is wonderlik")
    # Some variables were still being spell checked
    mozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="af")
    )
    assert passes(
        mozillachecker.spellcheck,
        "&brandShortName.labels; is wonderful",
        "&brandShortName.label; is wonderlik",
    )


def test_startcaps():
    """tests starting capitals"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.startcaps, "Find", "Vind")
    assert passes(stdchecker.startcaps, "find", "vind")
    assert fails(stdchecker.startcaps, "Find", "vind")
    assert fails(stdchecker.startcaps, "find", "Vind")
    assert passes(stdchecker.startcaps, "'", "'")
    assert passes(
        stdchecker.startcaps,
        "\\.,/?!`'\"[]{}()@#$%^&*_-;:<>Find",
        "\\.,/?!`'\"[]{}()@#$%^&*_-;:<>Vind",
    )
    # With leading whitespace
    assert passes(stdchecker.startcaps, " Find", " Vind")
    assert passes(stdchecker.startcaps, " find", " vind")
    assert fails(stdchecker.startcaps, " Find", " vind")
    assert fails(stdchecker.startcaps, " find", " Vind")
    # Leading punctuation
    assert passes(stdchecker.startcaps, "'Find", "'Vind")
    assert passes(stdchecker.startcaps, "'find", "'vind")
    assert fails(stdchecker.startcaps, "'Find", "'vind")
    assert fails(stdchecker.startcaps, "'find", "'Vind")
    # Unicode
    assert passes(stdchecker.startcaps, "Find", "Šind")
    assert passes(stdchecker.startcaps, "find", "šind")
    assert fails(stdchecker.startcaps, "Find", "šind")
    assert fails(stdchecker.startcaps, "find", "Šind")
    # Unicode further down the Unicode tables
    assert passes(
        stdchecker.startcaps, "A text enclosed...", "Ḽiṅwalwa ḽo katelwaho..."
    )
    assert fails(stdchecker.startcaps, "A text enclosed...", "ḽiṅwalwa ḽo katelwaho...")
    # Accelerators
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert passes(stdchecker.startcaps, "&Find", "Vi&nd")
    # Numbers - we really can't tell what should happen with numbers, so ignore
    # source or target that start with a number
    assert passes(stdchecker.startcaps, "360 degrees", "Grade 360")
    assert passes(stdchecker.startcaps, "360 degrees", "grade 360")

    # Language specific stuff
    afchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert passes(afchecker.startcaps, "A cow", "'n Koei")
    assert passes(afchecker.startcaps, "A list of ", "'n Lys van ")
    # should pass:
    # assert passes(afchecker.startcaps, "A 1k file", "'n 1k-lêer")
    assert passes(afchecker.startcaps, "'Do it'", "'Doen dit'")
    assert fails(afchecker.startcaps, "'Closer than'", "'nader as'")
    assert passes(afchecker.startcaps, "List", "Lys")
    assert passes(afchecker.startcaps, "a cow", "'n koei")
    assert fails(afchecker.startcaps, "a cow", "'n Koei")
    assert passes(afchecker.startcaps, "(A cow)", "('n Koei)")
    assert fails(afchecker.startcaps, "(a cow)", "('n Koei)")


def test_startpunc():
    """tests startpunc"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.startpunc, "<< Previous", "<< Correct")
    assert fails(stdchecker.startpunc, " << Previous", "Wrong")
    assert fails(stdchecker.startpunc, "Question", "\u2026Wrong")

    assert passes(
        stdchecker.startpunc, "<fish>hello</fish> world", "world <fish>hello</fish>"
    )

    # The inverted Spanish question mark should be accepted
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="es"))
    assert passes(
        stdchecker.startpunc,
        "Do you want to reload the file?",
        "¿Quiere recargar el archivo?",
    )

    # The Afrikaans indefinite article should be accepted
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="af"))
    assert passes(stdchecker.startpunc, "A human?", "'n Mens?")


def test_startwhitespace():
    """tests startwhitespace"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.startwhitespace, "A setence.", "I'm correct.")
    assert fails(stdchecker.startwhitespace, " A setence.", "I'm incorrect.")


def test_unchanged():
    """tests unchanged entries"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig(accelmarkers="&"))
    assert fails(stdchecker.unchanged, "Unchanged", "Unchanged")
    assert fails(stdchecker.unchanged, "&Unchanged", "Un&changed")
    assert passes(stdchecker.unchanged, "Unchanged", "Changed")
    assert passes(stdchecker.unchanged, "1234", "1234")
    assert passes(stdchecker.unchanged, "2×2", "2×2")  # bug 178, description item 14
    assert passes(stdchecker.unchanged, "I", "I")
    assert passes(stdchecker.unchanged, "   ", "   ")  # bug 178, description item 5
    assert passes(stdchecker.unchanged, "???", "???")  # bug 178, description item 15
    assert passes(
        stdchecker.unchanged, "&ACRONYM", "&ACRONYM"
    )  # bug 178, description item 7
    assert passes(stdchecker.unchanged, "F1", "F1")  # bug 178, description item 20
    assert fails(stdchecker.unchanged, "Two words", "Two words")
    # TODO: this still fails
    #    assert passes(stdchecker.unchanged, "NOMINAL", "NOMİNAL")
    gnomechecker = checks.GnomeChecker()
    assert fails(
        gnomechecker.unchanged,
        "Entity references, such as &amp; and &#169;",
        "Entity references, such as &amp; and &#169;",
    )
    # Variable only and variable plus punctuation messages should be ignored
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.unchanged, "$ProgramName$", "$ProgramName$")
    assert passes(
        mozillachecker.unchanged, "$file$ : $dir$", "$file$ : $dir$"
    )  # bug 178, description item 13
    assert fails(mozillachecker.unchanged, "$file$ in $dir$", "$file$ in $dir$")
    assert passes(mozillachecker.unchanged, "&brandShortName;", "&brandShortName;")
    # Don't translate words should be ignored
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(notranslatewords=["Mozilla"])
    )
    assert passes(
        stdchecker.unchanged, "Mozilla", "Mozilla"
    )  # bug 178, description item 10
    # Don't fail unchanged if the entry is a dialogsize, quite plausible that you won't change it
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.unchanged, "width: 12em;", "width: 12em;")
    assert fails(stdchecker.unchanged, "width: 12em;", "width: 12em;")
    assert passes(mozillachecker.unchanged, "7em", "7em")
    assert fails(stdchecker.unchanged, "7em", "7em")


def test_untranslated():
    """tests untranslated entries"""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.untranslated, "I am untranslated", "")
    assert passes(stdchecker.untranslated, "I am translated", "Ek is vertaal")
    # KDE comments that make it into translations should not mask untranslated test
    assert fails(
        stdchecker.untranslated,
        "_: KDE comment\\n\nI am untranslated",
        "_: KDE comment\\n\n",
    )


def test_validchars():
    """tests valid characters"""
    stdchecker = checks.StandardChecker(checks.CheckerConfig())
    assert passes(
        stdchecker.validchars,
        "The check always passes if you don't specify chars",
        "Die toets sal altyd werk as jy nie karacters specifisier",
    )
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            validchars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
    )
    assert passes(
        stdchecker.validchars,
        "This sentence contains valid characters",
        "Hierdie sin bevat ware karakters",
    )
    assert fails(stdchecker.validchars, "Some unexpected characters", "©®°±÷¼½¾")
    stdchecker = checks.StandardChecker(
        checks.CheckerConfig(
            validchars="⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰"
        )
    )
    assert passes(
        stdchecker.validchars,
        "Our target language is all non-ascii",
        "⠁⠂⠃⠄⠆⠇⠈⠉⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫",
    )
    assert fails(
        stdchecker.validchars,
        "Our target language is all non-ascii",
        "Some ascii⠁⠂⠃⠄⠆⠇⠈⠉⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫",
    )
    stdchecker = checks.StandardChecker(checks.CheckerConfig(validchars="\u004c\u032d"))
    assert passes(
        stdchecker.validchars, "This sentence contains valid chars", "\u004c\u032d"
    )
    assert passes(stdchecker.validchars, "This sentence contains valid chars", "\u1e3c")
    stdchecker = checks.StandardChecker(checks.CheckerConfig(validchars="\u1e3c"))
    assert passes(stdchecker.validchars, "This sentence contains valid chars", "\u1e3c")
    assert passes(
        stdchecker.validchars, "This sentence contains valid chars", "\u004c\u032d"
    )


def test_minimalchecker():
    """tests the Minimal quality checker"""
    from translate.storage import base

    # The minimal checker only checks for untranslated, unchanged and blank strings.
    # All other quality checks should be ignored.
    minimalchecker = checks.MinimalChecker()
    assert fails(minimalchecker.untranslated, "I am untranslated", "")
    assert passes(minimalchecker.untranslated, "I am translated", "Ek is vertaal")
    assert fails(minimalchecker.unchanged, "Unchanged", "Unchanged")
    assert passes(minimalchecker.unchanged, "Unchanged", "Changed")
    assert fails(minimalchecker.blank, "Blank string", " ")

    # Doublewords check is disabled.
    src, tgt, __ = strprep("Save the rhino", "Save the the rhino")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "doublewords" not in minimalchecker.run_filters(unit)

    # Printf check is disabled.
    src, tgt, __ = strprep("Non-matching printf variables", "Ek is %s")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "printf" not in minimalchecker.run_filters(unit)


def test_reducedchecker():
    """tests the Reduced quality checker"""
    from translate.storage import base

    # The reduced checker only runs the following tests:
    # untranslated, unchanged, blank, doublespacing, doublewords, spellcheck.
    # All other quality checks should be ignored.
    reducedchecker = checks.ReducedChecker()
    assert fails(reducedchecker.untranslated, "I am untranslated", "")
    assert passes(reducedchecker.untranslated, "I am translated", "Ek is vertaal")
    assert fails(reducedchecker.unchanged, "Unchanged", "Unchanged")
    assert passes(reducedchecker.unchanged, "Unchanged", "Changed")
    assert fails(reducedchecker.blank, "Blank string", " ")
    assert passes(
        reducedchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin. No double spacing.",
    )
    assert fails(
        reducedchecker.doublespacing,
        "Sentence. Another sentence.",
        "Sin.  Uneeded double space in translation.",
    )
    assert passes(reducedchecker.doublewords, "Save the rhino", "Save the rhino")
    assert fails(reducedchecker.doublewords, "Save the rhino", "Save the the rhino")

    # Printf check is disabled.
    src, tgt, __ = strprep("Non-matching printf variables", "Ek is %s")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "printf" not in reducedchecker.run_filters(unit)

    # Escapes check is disabled.
    src, tgt, __ = strprep("A file", "'n Leer\n")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    assert "escapes" not in reducedchecker.run_filters(unit)


def test_variables_kde():
    """tests variables in KDE translations"""
    # GNOME variables
    kdechecker = checks.KdeChecker()
    assert passes(
        kdechecker.variables,
        "%d files of type %s saved.",
        "%d leers van %s tipe gestoor.",
    )
    assert fails_serious(
        kdechecker.variables,
        "%d files of type %s saved.",
        "%s leers van %s tipe gestoor.",
    )


def test_variables_gnome():
    """tests variables in GNOME translations"""
    # GNOME variables
    gnomechecker = checks.GnomeChecker()
    assert passes(
        gnomechecker.variables,
        "%d files of type %s saved.",
        "%d leers van %s tipe gestoor.",
    )
    assert fails_serious(
        gnomechecker.variables,
        "%d files of type %s saved.",
        "%s leers van %s tipe gestoor.",
    )
    assert passes(gnomechecker.variables, "Save $(file)", "Stoor $(file)")
    assert fails_serious(gnomechecker.variables, "Save $(file)", "Stoor $(leer)")


def test_variables_mozilla():
    """tests variables in Mozilla translations"""
    # Mozilla variables
    mozillachecker = checks.MozillaChecker()
    assert passes(
        mozillachecker.variables,
        "Use the &brandShortname; instance.",
        "Gebruik die &brandShortname; weergawe.",
    )
    assert fails_serious(
        mozillachecker.variables,
        "Use the &brandShortname; instance.",
        "Gebruik die &brandKortnaam; weergawe.",
    )
    assert passes(mozillachecker.variables, "Save %file%", "Stoor %file%")
    assert fails_serious(mozillachecker.variables, "Save %file%", "Stoor %leer%")
    assert passes(mozillachecker.variables, "Save $file$", "Stoor $file$")
    assert fails_serious(mozillachecker.variables, "Save $file$", "Stoor $leer$")
    assert passes(
        mozillachecker.variables,
        "%d files of type %s saved.",
        "%d leers van %s tipe gestoor.",
    )
    assert fails_serious(
        mozillachecker.variables,
        "%d files of type %s saved.",
        "%s leers van %s tipe gestoor.",
    )
    assert passes(mozillachecker.variables, "Save $file", "Stoor $file")
    assert fails_serious(mozillachecker.variables, "Save $file", "Stoor $leer")
    assert passes(mozillachecker.variables, "About $ProgramName$", "Oor $ProgramName$")
    assert fails_serious(
        mozillachecker.variables, "About $ProgramName$", "Oor $NaamVanProgam$"
    )
    assert passes(mozillachecker.variables, "About $_CLICK", "Oor $_CLICK")
    assert fails_serious(mozillachecker.variables, "About $_CLICK", "Oor $_KLIK")
    assert passes(
        mozillachecker.variables, "About $_CLICK and more", "Oor $_CLICK en meer"
    )
    assert fails_serious(
        mozillachecker.variables, "About $_CLICK and more", "Oor $_KLIK en meer"
    )
    assert passes(mozillachecker.variables, "About $(^NameDA)", "Oor $(^NameDA)")
    assert fails_serious(mozillachecker.variables, "About $(^NameDA)", "Oor $(^NaamDA)")
    assert passes(
        mozillachecker.variables,
        "Open {{pageCount}} pages",
        "Make {{pageCount}} bladsye oop",
    )
    assert fails_serious(
        mozillachecker.variables,
        "Open {{pageCount}} pages",
        "Make {{bladTelling}} bladsye oop",
    )
    # Double variable problem
    assert fails_serious(
        mozillachecker.variables, "Create In &lt;&lt;", "Etsa ka Ho &lt;lt;"
    )
    # Variables at the end of a sentence
    assert fails_serious(
        mozillachecker.variables,
        "...time you start &brandShortName;.",
        "...lekgetlo le latelang ha o qala &LebitsoKgutshwane la kgwebo;.",
    )
    # Ensure that we can detect two variables of the same name with one faulty
    assert fails_serious(
        mozillachecker.variables,
        "&brandShortName; successfully downloaded and installed updates. You will have to restart &brandShortName; to complete the update.",
        "&brandShortName; ḽo dzhenisa na u longela khwinifhadzo zwavhuḓi. Ni ḓo tea u thoma hafhu &DzinaḼipfufhi ḽa pfungavhuṇe; u itela u fhedzisa khwinifha dzo.",
    )
    # We must detect entities in their fullform, ie with fullstop in the middle.
    assert fails_serious(
        mozillachecker.variables,
        "Welcome to the &pluginWizard.title;",
        "Wamkelekile kwi&Sihloko Soncedo lwe-plugin;",
    )
    # Variables that are missing in quotes should be detected
    assert fails_serious(
        mozillachecker.variables,
        '"%S" is an executable file.... Are you sure you want to launch "%S"?',
        '.... Uyaqiniseka ukuthi ufuna ukuqalisa I"%S"?',
    )
    # False positive $ style variables
    assert passes(
        mozillachecker.variables,
        "for reporting $ProductShortName$ crash information",
        "okokubika ukwaziswa kokumosheka kwe-$ProductShortName$",
    )
    # We shouldn't mask variables within variables.  This should highlight &brandShortName as missing and &amp as extra
    assert fails_serious(
        mozillachecker.variables, "&brandShortName;", "&amp;brandShortName;"
    )


def test_variables_openoffice():
    """tests variables in OpenOffice translations"""
    # OpenOffice.org variables
    for ooochecker in (checks.OpenOfficeChecker(), checks.LibreOfficeChecker()):
        assert passes(
            ooochecker.variables,
            "Use the &brandShortname; instance.",
            "Gebruik die &brandShortname; weergawe.",
        )
        assert fails_serious(
            ooochecker.variables,
            "Use the &brandShortname; instance.",
            "Gebruik die &brandKortnaam; weergawe.",
        )
        assert passes(ooochecker.variables, "Save %file%", "Stoor %file%")
        assert fails_serious(ooochecker.variables, "Save %file%", "Stoor %leer%")
        assert passes(ooochecker.variables, "Save %file", "Stoor %file")
        assert fails_serious(ooochecker.variables, "Save %file", "Stoor %leer")
        assert passes(ooochecker.variables, "Save %1", "Stoor %1")
        assert fails_serious(ooochecker.variables, "Save %1", "Stoor %2")
        assert passes(ooochecker.variables, "Save %", "Stoor %")
        assert fails_serious(ooochecker.variables, "Save %", "Stoor")
        assert passes(ooochecker.variables, "Save $(file)", "Stoor $(file)")
        assert fails_serious(ooochecker.variables, "Save $(file)", "Stoor $(leer)")
        assert passes(ooochecker.variables, "Save $file$", "Stoor $file$")
        assert fails_serious(ooochecker.variables, "Save $file$", "Stoor $leer$")
        assert passes(ooochecker.variables, "Save ${file}", "Stoor ${file}")
        assert fails_serious(ooochecker.variables, "Save ${file}", "Stoor ${leer}")
        assert passes(ooochecker.variables, "Save #file#", "Stoor #file#")
        assert fails_serious(ooochecker.variables, "Save #file#", "Stoor #leer#")
        assert passes(ooochecker.variables, "Save #1", "Stoor #1")
        assert fails_serious(ooochecker.variables, "Save #1", "Stoor #2")
        assert passes(ooochecker.variables, "Save #", "Stoor #")
        assert fails_serious(ooochecker.variables, "Save #", "Stoor")
        assert passes(ooochecker.variables, "Save ($file)", "Stoor ($file)")
        assert fails_serious(ooochecker.variables, "Save ($file)", "Stoor ($leer)")
        assert passes(ooochecker.variables, "Save $[file]", "Stoor $[file]")
        assert fails_serious(ooochecker.variables, "Save $[file]", "Stoor $[leer]")
        assert passes(ooochecker.variables, "Save [file]", "Stoor [file]")
        assert fails_serious(ooochecker.variables, "Save [file]", "Stoor [leer]")
        assert passes(ooochecker.variables, "Save $file", "Stoor $file")
        assert fails_serious(ooochecker.variables, "Save $file", "Stoor $leer")
        assert passes(ooochecker.variables, "Use @EXTENSION@", "Gebruik @EXTENSION@")
        assert fails_serious(
            ooochecker.variables, "Use @EXTENSUION@", "Gebruik @UITBRUIDING@"
        )
        # Same variable name twice
        assert fails_serious(
            ooochecker.variables,
            r"""Start %PROGRAMNAME% as %PROGRAMNAME%""",
            "Begin %PROGRAMNAME%",
        )


def test_variables_cclicense():
    """Tests variables in Creative Commons translations."""
    checker = checks.CCLicenseChecker()
    assert passes(checker.variables, "CC-GNU @license_code@.", "CC-GNU @license_code@.")
    assert fails_serious(
        checker.variables, "CC-GNU @license_code@.", "CC-GNU @lisensie_kode@."
    )
    assert passes(
        checker.variables,
        "Deed to the @license_name_full@",
        "Akte vir die @license_name_full@",
    )
    assert fails_serious(
        checker.variables,
        "Deed to the @license_name_full@",
        "Akte vir die @volle_lisensie@",
    )
    assert passes(
        checker.variables, "The @license_name_full@ is", "Die @license_name_full@ is"
    )
    assert fails_serious(
        checker.variables, "The @license_name_full@ is", "Die @iiilicense_name_full@ is"
    )
    assert fails_serious(checker.variables, "A @ccvar@", "'n @ccvertaaldeveranderlike@")


def test_variables_ios():
    """Test variables in iOS translations"""
    ioschecker = checks.IOSChecker()
    assert passes(ioschecker.variables, "Welcome $(NAME)", "Welkom $(NAME)")
    assert fails_serious(ioschecker.variables, "Welcome $(NAME)", "Welkom $(NAAM)")
    assert fails_serious(ioschecker.variables, "Welcome $(NAME)", "Welkom")

    assert passes(ioschecker.variables, "Welcome %@", "Welkom %@")
    assert fails_serious(ioschecker.variables, "Welcome %@", "Welkom $@")
    assert fails_serious(ioschecker.variables, "Welcome %@", "Welkom")
    assert passes(
        ioschecker.variables,
        "Downloading %1$@ at %2$@ speed",
        "Downloading at %2$@ speed the file %$1@",
    )


def test_xmltags():
    """tests xml tags"""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.xmltags, "Do it <b>now</b>", "Doen dit <v>nou</v>")
    assert passes(stdchecker.xmltags, "Do it <b>now</b>", "Doen dit <b>nou</b>")
    assert passes(
        stdchecker.xmltags,
        'Click <img src="img.jpg">here</img>',
        'Klik <img src="img.jpg">hier</img>',
    )
    assert fails(
        stdchecker.xmltags,
        'Click <img src="image.jpg">here</img>',
        'Klik <img src="prent.jpg">hier</img>',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <img src="img.jpg" alt="picture">here</img>',
        'Klik <img src="img.jpg" alt="prentjie">hier</img>',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <a title="tip">here</a>',
        'Klik <a title="wenk">hier</a>',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <div title="tip">here</div>',
        'Klik <div title="wenk">hier</div>',
    )
    assert passes(
        stdchecker.xmltags,
        "Start with the &lt;start&gt; tag",
        "Begin met die &lt;begin&gt;",
    )

    assert fails(
        stdchecker.xmltags,
        'Click <a href="page.html">',
        'Klik <a hverw="page.html">',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <a xml-lang="en" href="page.html">',
        'Klik <a xml-lang="af" href="page.html">',
    )
    assert passes(
        stdchecker.xmltags,
        'Click <div lang="en" dir="ltr">',
        'Klik <div lang="ar" dir="rtl">',
    )
    assert fails(
        stdchecker.xmltags,
        'Click <a href="page.html" target="koei">',
        'Klik <a href="page.html">',
    )
    assert fails(
        stdchecker.xmltags, "<b>Current Translation</b>", "<b>Traducción Actual:<b>"
    )
    assert passes(stdchecker.xmltags, "<Error>", "<Fout>")
    assert fails(
        stdchecker.xmltags,
        "%d/%d translated\n(%d blank, %d fuzzy)",
        "<br>%d/%d μεταφρασμένα\n<br>(%d κενά, %d ασαφή)",
    )
    assert fails(
        stdchecker.xmltags,
        '(and <a href="http://www.schoolforge.net/education-software" class="external">other open source software</a>)',
        '(en <a href="http://www.schoolforge.net/education-software" class="external">ander Vry Sagteware</a)',
    )
    assert fails(
        stdchecker.xmltags,
        'Because Tux Paint (and <a href="http://www.schoolforge.net/education-software" class="external">other open source software</a>) is free of cost and not limited in any way, a school can use it <i>today</i>, without waiting for procurement or a budget!',
        'Omdat Tux Paint (en <a href="http://www.schoolforge.net/education-software" class="external">ander Vry Sagteware</a)gratis is en nie beperk is op enige manier nie, kan \'n skool dit vandag</i> gebruik sonder om te wag vir goedkeuring of \'n begroting!',
    )
    assert fails(stdchecker.xmltags, "test <br />", "test <br>")
    assert fails(
        stdchecker.xmltags, "test <img src='foo.jpg'/ >", "test <img src='foo.jpg'  >"
    )

    # This used to cause an error (traceback), because of mismatch between
    # different regular expressions (because of the newlines)
    assert passes(
        stdchecker.xmltags,
        """<markup>
<span weight="bold" size="large"
style="oblique">
Can't create server !
</span>
</markup>""",
        """<markup>
<span weight="bold" size="large"
style="oblique">
No s'ha pogut crear el servidor
</span>
</markup>""",
    )
    frchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fr"))
    assert fails(
        frchecker.xmltags, 'Click <a href="page.html">', "Klik <a href=« page.html »>"
    )


@mark.xfail(reason="Bug #3506")
def test_bengali_mozilla_inverted_xmltags():
    """Test Bengali Mozilla XML tags."""
    bn_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn")
    )
    str_en = """We <a href="%(cofound_url)s" rel="external">co-founded</a> the <a href="%(whatwg_url)s" rel="external">WHAT-WG</a> to."""
    str_bn = """এর প্রচলন ঘটাতে আমরা <a href="%(whatwg_url)s" rel="external">WHAT-WG</a> প্রতিষ্ঠায় <a href="%(cofound_url)s" rel="external">সহযোগী</a> ছিলাম।ন।"""
    assert passes(bn_mozilla_checker.xmltags, str_en, str_bn)


def test_ooxmltags():
    """Tests the xml tags in OpenOffice.org translations for quality as done in gsicheck"""
    for ooochecker in (checks.OpenOfficeChecker(), checks.LibreOfficeChecker()):
        # some attributes can be changed or removed
        assert fails(
            ooochecker.xmltags,
            '<img src="a.jpg" width="400">',
            '<img src="b.jpg" width="500">',
        )
        assert passes(
            ooochecker.xmltags,
            '<img src="a.jpg" width="400">',
            '<img src="a.jpg" width="500">',
        )
        assert passes(
            ooochecker.xmltags,
            '<img src="a.jpg" width="400">',
            '<img src="a.jpg">',
        )
        assert passes(
            ooochecker.xmltags,
            '<img src="a.jpg">',
            '<img src="a.jpg" width="400">',
        )
        assert passes(
            ooochecker.xmltags, '<alt xml-lang="ab">text</alt>', "<alt>teks</alt>"
        )
        assert passes(
            ooochecker.xmltags,
            '<ahelp visibility="visible">bla</ahelp>',
            "<ahelp>blu</ahelp>",
        )
        assert fails(
            ooochecker.xmltags,
            '<ahelp visibility="visible">bla</ahelp>',
            '<ahelp visibility="invisible">blu</ahelp>',
        )
        assert fails(
            ooochecker.xmltags,
            '<ahelp visibility="invisible">bla</ahelp>',
            "<ahelp>blu</ahelp>",
        )
        # some attributes can be changed, but not removed
        assert passes(ooochecker.xmltags, '<link name="John">', '<link name="Jan">')
        assert fails(ooochecker.xmltags, '<link name="John">', '<link naam="Jan">')

        # Reported OOo error
        ## Bug 1910
        assert fails(
            ooochecker.xmltags,
            """<variable id="FehlendesElement">In a database file window, click the <emph>Queries</emph> icon, then choose <emph>Edit - Edit</emph>. When referenced fields no longer exist, you see this dialog</variable>""",
            """<variable id="FehlendesElement">Dans  une fenêtre de fichier de base de données, cliquez sur l'icône <emph>Requêtes</emph>, puis choisissez <emph>Éditer - Éditer</emp>. Lorsque les champs de référence n'existent plus, vous voyez cette boîte de dialogue</variable>""",
        )
        assert fails(
            ooochecker.xmltags,
            "<variable> <emph></emph> <emph></emph> </variable>",
            "<variable> <emph></emph> <emph></emp> </variable>",
        )


def test_functions():
    """tests to see that funtions() are not translated"""
    stdchecker = checks.StandardChecker()
    assert fails(stdchecker.functions, "blah rgb() blah", "blee brg() blee")
    assert passes(stdchecker.functions, "blah rgb() blah", "blee rgb() blee")
    assert fails(stdchecker.functions, "percentage in rgb()", "phesenthe kha brg()")
    assert passes(stdchecker.functions, "percentage in rgb()", "phesenthe kha rgb()")
    assert fails(stdchecker.functions, "rgb() in percentage", "brg() kha phesenthe")
    assert passes(stdchecker.functions, "rgb() in percentage", "rgb() kha phesenthe")
    assert fails(
        stdchecker.functions, "blah string.rgb() blah", "blee bleeb.rgb() blee"
    )
    assert passes(
        stdchecker.functions, "blah string.rgb() blah", "blee string.rgb() blee"
    )
    assert passes(stdchecker.functions, "or domain().", "domain() verwag.")
    assert passes(
        stdchecker.functions,
        "Expected url(), url-prefix(), or domain().",
        "url(), url-prefix() of domain() verwag.",
    )


def test_emails():
    """tests to see that email addresses are not translated"""
    stdchecker = checks.StandardChecker()
    assert fails(
        stdchecker.emails, "blah bob@example.net blah", "blee kobus@voorbeeld.net blee"
    )
    assert passes(
        stdchecker.emails, "blah bob@example.net blah", "blee bob@example.net blee"
    )


def test_urls():
    """tests to see that URLs are not translated"""
    stdchecker = checks.StandardChecker()
    assert fails(
        stdchecker.urls,
        "blah http://translate.org.za blah",
        "blee http://vertaal.org.za blee",
    )
    assert passes(
        stdchecker.urls,
        "blah http://translate.org.za blah",
        "blee http://translate.org.za blee",
    )


def test_simpleplurals():
    """test that we can find English style plural(s)"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.simpleplurals, "computer(s)", "rekenaar(s)")
    assert fails(stdchecker.simpleplurals, "plural(s)", "meervoud(e)")
    assert fails(
        stdchecker.simpleplurals,
        "Ungroup Metafile(s)...",
        "Kuvhanganyululani Metafaela(dzi)...",
    )

    # Test a language that doesn't use plurals
    stdchecker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="vi"))
    assert passes(stdchecker.simpleplurals, "computer(s)", "Máy tính")
    assert fails(stdchecker.simpleplurals, "computer(s)", "Máy tính(s)")


def test_nplurals():
    """
    Test that we can find the wrong number of plural forms. Note that this
    test uses a UnitChecker, not a translation checker.
    """
    checker = checks.StandardUnitChecker()
    unit = po.pounit("")

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer", "%d lêers"]
    assert checker.nplurals(unit)

    checker = checks.StandardUnitChecker(checks.CheckerConfig(targetlanguage="af"))
    unit.source = "%d files"
    unit.target = "%d lêer"
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer", "%d lêers"]
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer", "%d lêers", "%d lêeeeers"]
    assert not checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d lêer"]
    assert not checker.nplurals(unit)

    checker = checks.StandardUnitChecker(checks.CheckerConfig(targetlanguage="km"))
    unit.source = "%d files"
    unit.target = "%d ឯកសារ"
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d ឯកសារ"]
    assert checker.nplurals(unit)

    unit.source = ["%d file", "%d files"]
    unit.target = ["%d ឯកសារ", "%d lêers"]
    assert not checker.nplurals(unit)


def test_credits():
    """tests credits"""
    stdchecker = checks.StandardChecker()
    assert passes(stdchecker.credits, "File", "iFayile")
    assert passes(stdchecker.credits, "&File", "&Fayile")
    assert passes(stdchecker.credits, "translator-credits", "Ekke, ekke!")
    assert passes(stdchecker.credits, "Your names", "Ekke, ekke!")
    assert passes(stdchecker.credits, "ROLES_OF_TRANSLATORS", "Ekke, ekke!")
    kdechecker = checks.KdeChecker()
    assert passes(kdechecker.credits, "File", "iFayile")
    assert passes(kdechecker.credits, "&File", "&Fayile")
    assert passes(kdechecker.credits, "translator-credits", "Ekke, ekke!")
    assert fails(kdechecker.credits, "Your names", "Ekke, ekke!")
    assert fails(kdechecker.credits, "ROLES_OF_TRANSLATORS", "Ekke, ekke!")
    gnomechecker = checks.GnomeChecker()
    assert passes(gnomechecker.credits, "File", "iFayile")
    assert passes(gnomechecker.credits, "&File", "&Fayile")
    assert fails(gnomechecker.credits, "translator-credits", "Ekke, ekke!")
    assert passes(gnomechecker.credits, "Your names", "Ekke, ekke!")
    assert passes(gnomechecker.credits, "ROLES_OF_TRANSLATORS", "Ekke, ekke!")


def test_gconf():
    """test GNOME gconf errors"""
    gnomechecker = checks.GnomeChecker()
    # Let's cheat a bit and prepare the checker as the run_filters() method
    # would do by adding locations needed by the gconf test
    gnomechecker.locations = []
    assert passes(gnomechecker.gconf, 'Blah "gconf_setting"', 'Bleh "gconf_setting"')
    assert passes(gnomechecker.gconf, 'Blah "gconf_setting"', 'Bleh "gconf_steling"')
    gnomechecker.locations = ["file.schemas.in.h:24"]
    assert passes(gnomechecker.gconf, 'Blah "gconf_setting"', 'Bleh "gconf_setting"')
    assert fails(gnomechecker.gconf, 'Blah "gconf_setting"', 'Bleh "gconf_steling"')
    # redo the same, but with the new location comment:
    gnomechecker.locations = ["file.gschema.xml.in.in.h:24"]
    assert passes(gnomechecker.gconf, 'Blah "gconf_setting"', 'Bleh "gconf_setting"')
    assert fails(gnomechecker.gconf, 'Blah "gconf_setting"', 'Bleh "gconf_steling"')


def test_validxml():
    """test wheather validxml recognize invalid xml/html expressions"""
    lochecker = checks.LibreOfficeChecker()
    # Test validity only for xrm and xhp files
    lochecker.locations = ["description.xml"]
    assert passes(lochecker.validxml, "", "normal string")
    assert passes(lochecker.validxml, "", "<emph> only an open tag")
    lochecker.locations = ["readme.xrm"]
    assert passes(lochecker.validxml, "", "normal string")
    assert passes(lochecker.validxml, "", "<tt>closed formula</tt>")
    assert fails(lochecker.validxml, "", "<tt> only an open tag")
    lochecker.locations = ["wikisend.xhp"]
    assert passes(lochecker.validxml, "", "A <emph> well formed expression </emph>")
    assert fails(lochecker.validxml, "", "Missing <emph> close tag <emph>")
    assert fails(lochecker.validxml, "", "Missing open tag </emph>")
    assert fails(lochecker.validxml, "", "<emph/> is not a valid self-closing tag")
    assert fails(
        lochecker.validxml,
        "",
        '<ahelp hid="."> open tag not match with close tag</link>',
    )
    assert passes(
        lochecker.validxml,
        "",
        "Skip <IMG> because it is with capitalization so it is part of the text",
    )
    assert passes(
        lochecker.validxml,
        "",
        "Skip the capitalized <Empty>, because it is just a pseudo tag not a real one",
    )
    assert passes(
        lochecker.validxml, "", "Skip <br/> short tag, because no need to close it."
    )
    assert fails(
        lochecker.validxml, "", "<br></br> invalid, since should be self-closing tag"
    )
    # Larger tests
    assert passes(
        lochecker.validxml,
        "",
        "<bookmark_value>yazdırma; çizim varsayılanları</bookmark_value><bookmark_value>çizimler; yazdırma varsayılanları</bookmark_value><bookmark_value>sayfalar;sunumlarda sayfa adı yazdırma</bookmark_value><bookmark_value>yazdırma; sunumlarda tarihler</bookmark_value><bookmark_value>tarihler; sunumlarda  yazdırma</bookmark_value><bookmark_value>zamanlar; sunumları yazdırırken ekleme</bookmark_value><bookmark_value>yazdırma; sunumların gizli sayfaları</bookmark_value><bookmark_value>gizli sayfalar; sunumlarda yazdırma</bookmark_value><bookmark_value>yazdırma; sunumlarda ölçeklendirme olmadan</bookmark_value><bookmark_value>ölçekleme; sunumlar yazdırılırken</bookmark_value><bookmark_value>yazdırma; sunumlarda sayfalara sığdırma</bookmark_value><bookmark_value>sayfalara sığdırma; sunumlarda yazdırma ayarları</bookmark_value><bookmark_value>yazdırma; sunumlarda kapak sayfası</bookmark_value>",
    )
    # self-closing tag amongst other tag is valid
    assert passes(
        lochecker.validxml,
        "",
        '<link href="text/scalc/01/04060184.xhp#average">MITTELWERT</link>, <link href="text/scalc/01/04060184.xhp#averagea">MITTELWERTA</link>, <embedvar href="text/scalc/01/func_averageifs.xhp#averageifs_head"/>, <link href="text/scalc/01/04060184.xhp#max">MAX</link>, <link href="text/scalc/01/04060184.xhp#min">MIN</link>, <link href="text/scalc/01/04060183.xhp#large">KGRÖSSTE</link>, <link href="text/scalc/01/04060183.xhp#small">KKLEINSTE</link>',
    )
    assert fails(
        lochecker.validxml,
        "",
        'Kullanıcı etkileşimi verisinin kaydedilmesini ve bu verilerin gönderilmesini dilediğiniz zaman etkinleştirebilir veya devre dışı bırakabilirsiniz.  <item type="menuitem"><switchinline select="sys"><caseinline select="MAC">%PRODUCTNAME - Tercihler</caseinline><defaultinline>Araçlar - Seçenekler</defaultinline></switchinline> - %PRODUCTNAME - Gelişim Programı</item>\'nı seçin. Daha fazla bilgi için web sitesinde gezinmek için <defaultinline>Bilgi</emph> simgesine tıklayın.',
    )
    assert fails(
        lochecker.validxml,
        "",
        '<caseinline select="DRAW">Bir sayfanın içerik menüsünde ek komutlar vardır:</caseinline><caseinline select="IMPRESS">Bir sayfanın içerik menüsünde ek komutlar vardır:</caseinline></switchinline>',
    )
    assert fails(
        lochecker.validxml,
        "",
        "<bookmark_value>sunum; sihirbazı başlatmak<bookmark_value>nesneler; her zaman taşınabilir (Impress/Draw)</bookmark_value><bookmark_value>çizimleri eğriltme</bookmark_value><bookmark_value>aralama; sunumdaki sekmeler</bookmark_value><bookmark_value>metin nesneleri; sunumlarda ve çizimlerde</bookmark_value>",
    )


def test_hassuggestion():
    """test that hassuggestion() works"""
    checker = checks.StandardUnitChecker()

    po_store = po.pofile()
    po_store.addsourceunit("koeie")
    assert checker.hassuggestion(po_store.units[-1])

    xliff_store = xliff.xlifffile.parsestring(
        """
<xliff version='1.2'
       xmlns='urn:oasis:names:tc:xliff:document:1.2'>
<file original='hello.txt' source-language='en' target-language='fr' datatype='plaintext'>
<body>
    <trans-unit id='hi'>
        <source>Hello world</source>
        <target>Bonjour le monde</target>
        <alt-trans>
            <target xml:lang='es'>Hola mundo</target>
        </alt-trans>
    </trans-unit>
</body>
</file>
</xliff>
"""
    )
    assert not checker.hassuggestion(xliff_store.units[0])


def test_dialogsizes():
    """test Mozilla dialog sizes"""
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.dialogsizes, "width: 12em;", "width: 12em;")
    assert passes(
        mozillachecker.dialogsizes,
        "width: 12em; height: 36em",
        "width: 12em; height: 36em",
    )
    assert fails(mozillachecker.dialogsizes, "height: 12em;", "hoogde: 12em;")
    assert passes(mozillachecker.dialogsizes, "height: 12em;", "height: 24px;")
    assert fails(mozillachecker.dialogsizes, "height: 12em;", "height: 24xx;")
    assert fails(mozillachecker.dialogsizes, "height: 12.5em;", "height: 12,5em;")
    assert fails(
        mozillachecker.dialogsizes,
        "width: 36em; height: 18em;",
        "width: 30em; min-height: 20em;",
    )


def test_skip_checks_per_language_in_some_checkers():
    """Test some checks are skipped for some languages in Mozilla checker."""
    from translate.storage import base

    # Hijack checker config language ignoretests to test check is skipped.
    checker_config = checks.CheckerConfig(targetlanguage="gl")
    previous_ignoretests = checker_config.lang.ignoretests
    checker_config.lang.ignoretests = {
        "mozilla": ["accelerators"],
    }

    # Prepare the checkers and the unit.
    mozillachecker = checks.MozillaChecker(checkerconfig=checker_config)
    stdchecker = checks.StandardChecker(
        checkerconfig=checks.CheckerConfig(accelmarkers="&", targetlanguage="gl")
    )

    str1, str2, __ = strprep("&Check for updates", "আপডেইটসমূহৰ বাবে নিৰীক্ষণ কৰক")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    # Accelerators check is disabled for this language in MozillaChecker.
    assert "accelerators" not in mozillachecker.run_filters(unit)

    # But it is not in StandardChecker.
    assert "accelerators" in stdchecker.run_filters(unit)

    # Undo hijack.
    checker_config.lang.ignoretests = previous_ignoretests


def test_mozilla_no_accelerators_for_indic():
    """
    Test accelerators in MozillaChecker fails if accelerator in target.

    No-accelerators is a special behavior of accelerators check in some
    languages that is present in MozillaChecker.
    """
    mozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="as")
    )
    assert fails(mozillachecker.accelerators, "&File", "&Fayile")
    assert fails(mozillachecker.accelerators, "My add&-ons", "&Byvoengs mit")
    assert passes(mozillachecker.accelerators, "&File", "Fayile")
    assert fails(mozillachecker.accelerators, "File", "&Fayile")
    assert passes(mozillachecker.accelerators, "Mail &amp; News", "Po en Nuus")
    assert fails(mozillachecker.accelerators, "Mail &amp; News", "Po en &Nuus")
    assert passes(mozillachecker.accelerators, "Mail & News", "Pos & Nuus")


def test_noaccelerators_only_in_mozilla_checker():
    """
    Test no-accelerators check is only present in Mozilla checker.

    No-accelerators is a special behavior of accelerators check in some
    languages that is present in MozillaChecker.
    """
    from translate.storage import base

    asmozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="as")
    )
    glmozillachecker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="gl")
    )
    stdchecker = checks.StandardChecker(
        checkerconfig=checks.CheckerConfig(accelmarkers="&", targetlanguage="as")
    )

    # Accelerators check passes for Assamesse in Mozilla checker. It fails for
    # Assamesse in Standard checker or for other languages in Mozilla Checker.
    str1, str2, __ = strprep("&Check for updates", "আপডেইটসমূহৰ বাবে নিৰীক্ষণ কৰক")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    gl_failures = glmozillachecker.run_filters(unit)
    std_failures = stdchecker.run_filters(unit)

    assert "accelerators" not in asmozillachecker.run_filters(unit)
    assert "accelerators" in gl_failures
    assert "should not appear" not in gl_failures["accelerators"]
    assert "accelerators" in std_failures
    assert "should not appear" not in std_failures["accelerators"]

    # Accelerators check passes. The ampersand should be detected as part of
    # a variable.
    str1, str2, __ = strprep("About &brandFullName;", "&brandFullName; ৰ বিষয়ে")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    assert "accelerators" not in asmozillachecker.run_filters(unit)
    assert "accelerators" not in glmozillachecker.run_filters(unit)
    assert "accelerators" not in stdchecker.run_filters(unit)

    # Accelerators check fails for Assamesse in Mozilla checker since the
    # accelerator is present in the target. It passes for other languages or
    # other checkers.
    str1, str2, __ = strprep("&Cancel", "বাতিল কৰক (&C)")
    unit = base.TranslationUnit(str1)
    unit.target = str2

    as_failures = asmozillachecker.run_filters(unit)

    assert asmozillachecker.config.language_script == "assamese"
    assert "accelerators" in as_failures
    assert "should not appear" in as_failures["accelerators"]
    assert "accelerators" not in glmozillachecker.run_filters(unit)
    assert "accelerators" not in stdchecker.run_filters(unit)


def test_ensure_accelerators_not_in_target_if_not_in_source():
    """Test accelerators check works different for some languages in Mozilla."""
    from translate.storage import base

    af_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="af")
    )
    km_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="km")
    )

    # Afrikaans passes: Correct use of accesskeys.
    # Khmer fails: Translation shouldn't have an accesskey.
    src, tgt, __ = strprep("&One", "&Een")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    km_failures = km_mozilla_checker.run_filters(unit)

    assert "accelerators" not in af_mozilla_checker.run_filters(unit)
    assert "accelerators" in km_failures
    assert "should not appear" in km_failures["accelerators"]

    # Afrikaans fails: Translation is missing the accesskey.
    # Khmer passes: Translation doesn't need accesskey for this language.
    src, tgt, __ = strprep("&Two", "Twee")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    af_failures = af_mozilla_checker.run_filters(unit)

    assert "accelerators" in af_failures
    assert "Missing accelerator" in af_failures["accelerators"]
    assert "accelerators" not in km_mozilla_checker.run_filters(unit)

    # Afrikaans fails: No accesskey in the source, but yes on translation.
    # Khmer fails: Translation doesn't need accesskey, but it has accesskey.
    src, tgt, __ = strprep("Three", "&Drie")
    unit = base.TranslationUnit(src)
    unit.target = tgt

    af_failures = af_mozilla_checker.run_filters(unit)
    km_failures = km_mozilla_checker.run_filters(unit)

    assert "accelerators" in af_failures
    assert "Added accelerator" in af_failures["accelerators"]
    assert "accelerators" in km_failures
    assert "should not appear" in km_failures["accelerators"]


def test_ensure_bengali_languages_script_is_correct():
    """Test script for Bengali languages is correctly set."""
    bn_BD_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn_BD")
    )
    bn_IN_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn_IN")
    )
    bn_mozilla_checker = checks.MozillaChecker(
        checkerconfig=checks.CheckerConfig(targetlanguage="bn_IN")
    )
    assert bn_BD_mozilla_checker.config.language_script == "Beng"
    assert bn_IN_mozilla_checker.config.language_script == "Beng"
    assert bn_mozilla_checker.config.language_script == "Beng"


def test_category():
    """Tests checker categories aren't mixed up."""
    from translate.storage import base

    unit = base.TranslationUnit("foo")
    unit.target = "bar"

    standard_checker = checks.StandardChecker()
    assert standard_checker.categories == {}
    standard_checker.run_filters(unit)
    assert standard_checker.categories != {}
    assert "validxml" not in standard_checker.categories
    standard_categories_count = len(standard_checker.categories.values())

    libo_checker = checks.LibreOfficeChecker()
    assert libo_checker.categories == {}
    libo_checker.run_filters(unit)
    assert libo_checker.categories != {}
    assert "validxml" in libo_checker.categories

    standard_checker = checks.StandardChecker()
    assert standard_checker.categories == {}
    standard_checker.run_filters(unit)
    assert standard_checker.categories != {}
    assert len(standard_checker.categories.values()) == standard_categories_count
    assert "validxml" not in standard_checker.categories
