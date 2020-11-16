from translate.storage.placeables import general


def test_placeable_numbers():
    """Check the correct functioning of number placeables"""
    assert general.NumberPlaceable(["25"]) in general.NumberPlaceable.parse(
        "Here is a 25 number"
    )
    assert general.NumberPlaceable(["-25"]) in general.NumberPlaceable.parse(
        "Here is a -25 number"
    )
    assert general.NumberPlaceable(["+25"]) in general.NumberPlaceable.parse(
        "Here is a +25 number"
    )
    assert general.NumberPlaceable(["25.00"]) in general.NumberPlaceable.parse(
        "Here is a 25.00 number"
    )
    assert general.NumberPlaceable(["2,500.00"]) in general.NumberPlaceable.parse(
        "Here is a 2,500.00 number"
    )
    assert general.NumberPlaceable(["1\u00a0000,99"]) in general.NumberPlaceable.parse(
        "Here is a 1\u00a0000,99 number"
    )


def test_placeable_newline():
    assert general.NewlinePlaceable.parse("A newline\n")[1] == general.NewlinePlaceable(
        ["\n"]
    )
    assert general.NewlinePlaceable.parse("First\nSecond")[
        1
    ] == general.NewlinePlaceable(["\n"])


def test_placeable_alt_attr():
    assert general.AltAttrPlaceable.parse(
        'Click on the <img src="image.jpg" alt="Image">'
    )[1] == general.AltAttrPlaceable(['alt="Image"'])


def test_placeable_qt_formatting():
    assert general.QtFormattingPlaceable.parse("One %1 %99 %L1 are all valid")[
        1
    ] == general.QtFormattingPlaceable(["%1"])
    assert general.QtFormattingPlaceable.parse("One %1 %99 %L1 are all valid")[
        3
    ] == general.QtFormattingPlaceable(["%99"])
    assert general.QtFormattingPlaceable.parse("One %1 %99 %L1 are all valid")[
        5
    ] == general.QtFormattingPlaceable(["%L1"])


def test_placeable_camelcase():
    assert general.CamelCasePlaceable.parse("CamelCase")[
        0
    ] == general.CamelCasePlaceable(["CamelCase"])
    assert general.CamelCasePlaceable.parse("iPod")[0] == general.CamelCasePlaceable(
        ["iPod"]
    )
    assert general.CamelCasePlaceable.parse("DokuWiki")[
        0
    ] == general.CamelCasePlaceable(["DokuWiki"])
    assert general.CamelCasePlaceable.parse("KBabel")[0] == general.CamelCasePlaceable(
        ["KBabel"]
    )
    assert general.CamelCasePlaceable.parse("_Bug") is None
    assert general.CamelCasePlaceable.parse("NOTCAMEL") is None


def test_placeable_space():
    assert general.SpacesPlaceable.parse(" Space at start")[
        0
    ] == general.SpacesPlaceable([" "])
    assert general.SpacesPlaceable.parse("Space at end ")[1] == general.SpacesPlaceable(
        [" "]
    )
    assert general.SpacesPlaceable.parse("Double  space")[1] == general.SpacesPlaceable(
        ["  "]
    )


def test_placeable_punctuation():
    assert (
        general.PunctuationPlaceable.parse(
            'These, are not. Special: punctuation; marks! Or are "they"?'
        )
        is None
    )
    assert general.PunctuationPlaceable.parse("Downloading…")[
        1
    ] == general.PunctuationPlaceable(["…"])


def test_placeable_xml_entity():
    assert general.XMLEntityPlaceable.parse("&brandShortName;")[
        0
    ] == general.XMLEntityPlaceable(["&brandShortName;"])
    assert general.XMLEntityPlaceable.parse("&#1234;")[0] == general.XMLEntityPlaceable(
        ["&#1234;"]
    )
    assert general.XMLEntityPlaceable.parse("&xDEAD;")[0] == general.XMLEntityPlaceable(
        ["&xDEAD;"]
    )


def test_placeable_xml_tag():
    assert general.XMLTagPlaceable.parse("<a>koei</a>")[0] == general.XMLTagPlaceable(
        ["<a>"]
    )
    assert general.XMLTagPlaceable.parse("<a>koei</a>")[2] == general.XMLTagPlaceable(
        ["</a>"]
    )
    assert general.XMLTagPlaceable.parse("<Exif.XResolution>")[
        0
    ] == general.XMLTagPlaceable(["<Exif.XResolution>"])
    assert general.XMLTagPlaceable.parse("<tag_a>")[0] == general.XMLTagPlaceable(
        ["<tag_a>"]
    )
    assert general.XMLTagPlaceable.parse('<img src="koei.jpg" />')[
        0
    ] == general.XMLTagPlaceable(['<img src="koei.jpg" />'])
    # We don't want this to be recognised, so we test for None - not sure if that is a stable assumption
    assert general.XMLTagPlaceable.parse("<important word>") is None
    assert general.XMLTagPlaceable.parse('<img ="koei.jpg" />') is None
    assert general.XMLTagPlaceable.parse('<img "koei.jpg" />') is None
    assert general.XMLTagPlaceable.parse('<span xml:space="preserve">')[
        0
    ] == general.XMLTagPlaceable(['<span xml:space="preserve">'])
    assert general.XMLTagPlaceable.parse(
        '<img src="http://translate.org.za/blogs/friedel/sites/translate.org.za.blogs.friedel/files/virtaal-7f_help.png" alt="Virtaal met lêernaam-pseudovertaling" style="border: 1px dotted grey;" />'
    )[0] == general.XMLTagPlaceable(
        [
            '<img src="http://translate.org.za/blogs/friedel/sites/translate.org.za.blogs.friedel/files/virtaal-7f_help.png" alt="Virtaal met lêernaam-pseudovertaling" style="border: 1px dotted grey;" />'
        ]
    )
    # Bug 933
    assert general.XMLTagPlaceable.parse(
        'This entry expires in %days% days. Would you like to <a href="%href%?PHPSESSID=5d59c559cf4eb9f1d278918271fbe68a" title="Renew this Entry Now">Renew this Entry Now</a> ?'
    )[1] == general.XMLTagPlaceable(
        [
            '<a href="%href%?PHPSESSID=5d59c559cf4eb9f1d278918271fbe68a" title="Renew this Entry Now">'
        ]
    )
    assert general.XMLTagPlaceable.parse(
        """<span weight='bold' size='larger'>Your Google Account is locked</span>"""
    )[0] == general.XMLTagPlaceable(["""<span weight='bold' size='larger'>"""])


def test_placeable_option():
    assert general.OptionPlaceable.parse("Type --help for this help")[
        1
    ] == general.OptionPlaceable(["--help"])
    assert general.OptionPlaceable.parse("Short -S ones also")[
        1
    ] == general.OptionPlaceable(["-S"])


def test_placeable_file():
    assert general.FilePlaceable.parse("Store in /home/user")[
        1
    ] == general.FilePlaceable(["/home/user"])
    assert general.FilePlaceable.parse("Store in ~/Download directory")[
        1
    ] == general.FilePlaceable(["~/Download"])


def test_placeable_email():
    assert general.EmailPlaceable.parse("Send email to info@example.com")[
        1
    ] == general.EmailPlaceable(["info@example.com"])
    assert general.EmailPlaceable.parse("Send email to mailto:info@example.com")[
        1
    ] == general.EmailPlaceable(["mailto:info@example.com"])


def test_placeable_caps():
    assert general.CapsPlaceable.parse("Use the HTML page")[1] == general.CapsPlaceable(
        ["HTML"]
    )
    assert general.CapsPlaceable.parse("I am") is None
    assert general.CapsPlaceable.parse("Use the A4 paper") is None
    assert general.CapsPlaceable.parse("In GTK+")[1] == general.CapsPlaceable(["GTK+"])
    #    assert general.CapsPlaceable.parse('GNOME-stuff')[0] == general.CapsPlaceable(['GNOME'])
    assert general.CapsPlaceable.parse("with XDG_USER_DIRS")[
        1
    ] == general.CapsPlaceable(["XDG_USER_DIRS"])


def test_placeable_formatting():
    fp = general.FormattingPlaceable
    assert fp.parse("There were %d cows")[1] == fp(["%d"])
    assert fp.parse("There were %Id cows")[1] == fp(["%Id"])
    assert fp.parse("There were %d %s")[3] == fp(["%s"])
    assert fp.parse("%1$s was kicked by %2$s")[0] == fp(["%1$s"])
    assert fp.parse("There were %Id cows")[1] == fp(["%Id"])
    assert fp.parse("There were % d cows")[1] == fp(["% d"])
    # only a real space is allowed as formatting flag
    assert fp.parse("There were %\u00a0d cows") is None
    assert fp.parse("There were %'f cows")[1] == fp(["%'f"])
    assert fp.parse("There were %#x cows")[1] == fp(["%#x"])

    # field width
    assert fp.parse("There were %3d cows")[1] == fp(["%3d"])
    assert fp.parse("There were %33d cows")[1] == fp(["%33d"])
    assert fp.parse("There were %*d cows")[1] == fp(["%*d"])

    # numbered variables
    assert fp.parse("There were %1$d cows")[1] == fp(["%1$d"])


def test_placeable_doubleat():
    dap = general.DoubleAtPlaceable
    assert dap.parse("There were @@number@@ cows")[1] == dap(["@@number@@"])
    assert dap.parse("There were @@number1@@ cows and @@number2@@ sheep")[1] == dap(
        ["@@number1@@"]
    )
    assert dap.parse("There were @@number1@@ cows and @@number2@@ sheep")[3] == dap(
        ["@@number2@@"]
    )


def test_placeable_brace():
    bp = general.BracePlaceable
    # Double braces
    assert bp.parse("There were {{number}} cows")[1] == bp(["{{number}}"])
    assert bp.parse("There were {{number1}} cows and {{number2}} sheep")[1] == bp(
        ["{{number1}}"]
    )
    assert bp.parse("There were {{number1}} cows and {{number2}} sheep")[3] == bp(
        ["{{number2}}"]
    )

    # Single braces
    assert bp.parse("There were {number} cows")[1] == bp(["{number}"])
    assert bp.parse("There were {number1} cows and {number2} sheep")[1] == bp(
        ["{number1}"]
    )
    assert bp.parse("There were {number1} cows and {number2} sheep")[3] == bp(
        ["{number2}"]
    )

    # Mixed single and double braces
    assert bp.parse("There were {number1} cows and {{number2}} sheep")[1] == bp(
        ["{number1}"]
    )
    assert bp.parse("There were {number1} cows and {{number2}} sheep")[3] == bp(
        ["{{number2}}"]
    )
    assert bp.parse("There were {{number1}} cows and {number2} sheep")[1] == bp(
        ["{{number1}}"]
    )
    assert bp.parse("There were {{number1}} cows and {number2} sheep")[3] == bp(
        ["{number2}"]
    )


def test_python_placeable():
    pfp = general.PythonFormattingPlaceable
    # No conversion
    assert pfp.parse("100%% correct")[1] == pfp(["%%"])

    # Mapping keys
    assert pfp.parse("There were %(number)d cows")[1] == pfp(["%(number)d"])
    assert pfp.parse("There were %(cows.number)d cows")[1] == pfp(["%(cows.number)d"])
    assert pfp.parse("There were %(number of cows)d cows")[1] == pfp(
        ["%(number of cows)d"]
    )

    # Conversion flags
    assert pfp.parse("There were %(number)03d cows")[1] == pfp(["%(number)03d"])
    assert pfp.parse("There were %(number) 3d cows")[1] == pfp(["%(number) 3d"])

    # Minimum field width
    assert pfp.parse("There were %(number)*d cows")[1] == pfp(["%(number)*d"])

    # Precision
    assert pfp.parse("There were %(number)3.1d cows")[1] == pfp(["%(number)3.1d"])

    # Length modifier
    assert pfp.parse("There were %(number)Ld cows")[1] == pfp(["%(number)Ld"])


# TODO: JavaMessageFormatPlaceable, UrlPlaceable, XMLTagPlaceable
