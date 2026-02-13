from translate.storage.placeables import general


def test_placeable_numbers() -> None:
    """Check the correct functioning of number placeables."""
    result = general.NumberPlaceable.parse("Here is a 25 number")
    assert result
    # pylint: disable-next=unsupported-membership-test
    assert general.NumberPlaceable(["25"]) in result
    result = general.NumberPlaceable.parse("Here is a -25 number")
    assert result
    # pylint: disable-next=unsupported-membership-test
    assert general.NumberPlaceable(["-25"]) in result
    result = general.NumberPlaceable.parse("Here is a +25 number")
    assert result
    # pylint: disable-next=unsupported-membership-test
    assert general.NumberPlaceable(["+25"]) in result
    result = general.NumberPlaceable.parse("Here is a 25.00 number")
    assert result
    # pylint: disable-next=unsupported-membership-test
    assert general.NumberPlaceable(["25.00"]) in result
    result = general.NumberPlaceable.parse("Here is a 2,500.00 number")
    assert result
    # pylint: disable-next=unsupported-membership-test
    assert general.NumberPlaceable(["2,500.00"]) in result
    result = general.NumberPlaceable.parse("Here is a 1\u00a0000,99 number")
    assert result
    # pylint: disable-next=unsupported-membership-test
    assert general.NumberPlaceable(["1\u00a0000,99"]) in result


def test_placeable_newline() -> None:
    result = general.NewlinePlaceable.parse("A newline\n")
    assert result
    assert result[1] == general.NewlinePlaceable(["\n"])
    result = general.NewlinePlaceable.parse("First\nSecond")
    assert result
    assert result[1] == general.NewlinePlaceable(["\n"])


def test_placeable_alt_attr() -> None:
    result = general.AltAttrPlaceable.parse(
        'Click on the <img src="image.jpg" alt="Image">'
    )
    assert result
    assert result[1] == general.AltAttrPlaceable(['alt="Image"'])


def test_placeable_qt_formatting() -> None:
    result = general.QtFormattingPlaceable.parse("One %1 %99 %L1 are all valid")
    assert result
    assert result[1] == general.QtFormattingPlaceable(["%1"])
    assert result[3] == general.QtFormattingPlaceable(["%99"])
    assert result[5] == general.QtFormattingPlaceable(["%L1"])


def test_placeable_camelcase() -> None:
    result = general.CamelCasePlaceable.parse("CamelCase")
    assert result
    assert result[0] == general.CamelCasePlaceable(["CamelCase"])
    result = general.CamelCasePlaceable.parse("iPod")
    assert result
    assert result[0] == general.CamelCasePlaceable(["iPod"])
    result = general.CamelCasePlaceable.parse("DokuWiki")
    assert result
    assert result[0] == general.CamelCasePlaceable(["DokuWiki"])
    result = general.CamelCasePlaceable.parse("KBabel")
    assert result
    assert result[0] == general.CamelCasePlaceable(["KBabel"])
    assert general.CamelCasePlaceable.parse("_Bug") is None
    assert general.CamelCasePlaceable.parse("NOTCAMEL") is None


def test_placeable_space() -> None:
    result = general.SpacesPlaceable.parse(" Space at start")
    assert result
    assert result[0] == general.SpacesPlaceable([" "])
    result = general.SpacesPlaceable.parse("Space at end ")
    assert result
    assert result[1] == general.SpacesPlaceable([" "])
    result = general.SpacesPlaceable.parse("Double  space")
    assert result
    assert result[1] == general.SpacesPlaceable(["  "])


def test_placeable_punctuation() -> None:
    assert (
        general.PunctuationPlaceable.parse(
            'These, are not. Special: punctuation; marks! Or are "they"?'
        )
        is None
    )
    result = general.PunctuationPlaceable.parse("Downloading…")
    assert result
    assert result[1] == general.PunctuationPlaceable(["…"])


def test_placeable_xml_entity() -> None:
    result = general.XMLEntityPlaceable.parse("&brandShortName;")
    assert result
    assert result[0] == general.XMLEntityPlaceable(["&brandShortName;"])
    result = general.XMLEntityPlaceable.parse("&#1234;")
    assert result
    assert result[0] == general.XMLEntityPlaceable(["&#1234;"])
    result = general.XMLEntityPlaceable.parse("&xDEAD;")
    assert result
    assert result[0] == general.XMLEntityPlaceable(["&xDEAD;"])


def test_placeable_xml_tag() -> None:
    result = general.XMLTagPlaceable.parse("<a>koei</a>")
    assert result
    assert result[0] == general.XMLTagPlaceable(["<a>"])
    assert result[2] == general.XMLTagPlaceable(["</a>"])
    result = general.XMLTagPlaceable.parse("<Exif.XResolution>")
    assert result
    assert result[0] == general.XMLTagPlaceable(["<Exif.XResolution>"])
    result = general.XMLTagPlaceable.parse("<tag_a>")
    assert result
    assert result[0] == general.XMLTagPlaceable(["<tag_a>"])
    result = general.XMLTagPlaceable.parse('<img src="koei.jpg" />')
    assert result
    assert result[0] == general.XMLTagPlaceable(['<img src="koei.jpg" />'])
    # We don't want this to be recognised, so we test for None - not sure if that is a stable assumption
    assert general.XMLTagPlaceable.parse("<important word>") is None
    assert general.XMLTagPlaceable.parse('<img ="koei.jpg" />') is None
    assert general.XMLTagPlaceable.parse('<img "koei.jpg" />') is None
    result = general.XMLTagPlaceable.parse('<span xml:space="preserve">')
    assert result
    assert result[0] == general.XMLTagPlaceable(['<span xml:space="preserve">'])
    result = general.XMLTagPlaceable.parse(
        '<img src="http://translate.org.za/blogs/friedel/sites/translate.org.za.blogs.friedel/files/virtaal-7f_help.png" alt="Virtaal met lêernaam-pseudovertaling" style="border: 1px dotted grey;" />'
    )
    assert result
    assert result[0] == general.XMLTagPlaceable(
        [
            '<img src="http://translate.org.za/blogs/friedel/sites/translate.org.za.blogs.friedel/files/virtaal-7f_help.png" alt="Virtaal met lêernaam-pseudovertaling" style="border: 1px dotted grey;" />'
        ]
    )
    # Bug 933
    result = general.XMLTagPlaceable.parse(
        'This entry expires in %days% days. Would you like to <a href="%href%?PHPSESSID=5d59c559cf4eb9f1d278918271fbe68a" title="Renew this Entry Now">Renew this Entry Now</a> ?'
    )
    assert result
    assert result[1] == general.XMLTagPlaceable(
        [
            '<a href="%href%?PHPSESSID=5d59c559cf4eb9f1d278918271fbe68a" title="Renew this Entry Now">'
        ]
    )
    result = general.XMLTagPlaceable.parse(
        """<span weight='bold' size='larger'>Your Google Account is locked</span>"""
    )
    assert result
    assert result[0] == general.XMLTagPlaceable(
        ["""<span weight='bold' size='larger'>"""]
    )


def test_placeable_option() -> None:
    result = general.OptionPlaceable.parse("Type --help for this help")
    assert result
    assert result[1] == general.OptionPlaceable(["--help"])
    result = general.OptionPlaceable.parse("Short -S ones also")
    assert result
    assert result[1] == general.OptionPlaceable(["-S"])


def test_placeable_file() -> None:
    result = general.FilePlaceable.parse("Store in /home/user")
    assert result
    assert result[1] == general.FilePlaceable(["/home/user"])
    result = general.FilePlaceable.parse("Store in ~/Download directory")
    assert result
    assert result[1] == general.FilePlaceable(["~/Download"])


def test_placeable_email() -> None:
    result = general.EmailPlaceable.parse("Send email to info@example.com")
    assert result
    assert result[1] == general.EmailPlaceable(["info@example.com"])
    result = general.EmailPlaceable.parse("Send email to mailto:info@example.com")
    assert result
    assert result[1] == general.EmailPlaceable(["mailto:info@example.com"])


def test_placeable_caps() -> None:
    result = general.CapsPlaceable.parse("Use the HTML page")
    assert result
    assert result[1] == general.CapsPlaceable(["HTML"])
    assert general.CapsPlaceable.parse("I am") is None
    assert general.CapsPlaceable.parse("Use the A4 paper") is None
    result = general.CapsPlaceable.parse("In GTK+")
    assert result
    assert result[1] == general.CapsPlaceable(["GTK+"])
    #    assert general.CapsPlaceable.parse('GNOME-stuff')[0] == general.CapsPlaceable(['GNOME'])
    result = general.CapsPlaceable.parse("with XDG_USER_DIRS")
    assert result
    assert result[1] == general.CapsPlaceable(["XDG_USER_DIRS"])


def test_placeable_formatting() -> None:
    fp = general.FormattingPlaceable
    result = fp.parse("There were %d cows")
    assert result
    assert result[1] == fp(["%d"])
    result = fp.parse("There were %Id cows")
    assert result
    assert result[1] == fp(["%Id"])
    result = fp.parse("There were %d %s")
    assert result
    assert result[3] == fp(["%s"])
    result = fp.parse("%1$s was kicked by %2$s")
    assert result
    assert result[0] == fp(["%1$s"])
    result = fp.parse("There were %Id cows")
    assert result
    assert result[1] == fp(["%Id"])
    result = fp.parse("There were % d cows")
    assert result
    assert result[1] == fp(["% d"])
    # only a real space is allowed as formatting flag
    assert fp.parse("There were %\u00a0d cows") is None
    result = fp.parse("There were %'f cows")
    assert result
    assert result[1] == fp(["%'f"])
    result = fp.parse("There were %#x cows")
    assert result
    assert result[1] == fp(["%#x"])

    # field width
    result = fp.parse("There were %3d cows")
    assert result
    assert result[1] == fp(["%3d"])
    result = fp.parse("There were %33d cows")
    assert result
    assert result[1] == fp(["%33d"])
    result = fp.parse("There were %*d cows")
    assert result
    assert result[1] == fp(["%*d"])

    # numbered variables
    result = fp.parse("There were %1$d cows")
    assert result
    assert result[1] == fp(["%1$d"])


def test_placeable_doubleat() -> None:
    dap = general.DoubleAtPlaceable
    result = dap.parse("There were @@number@@ cows")
    assert result
    assert result[1] == dap(["@@number@@"])
    result = dap.parse("There were @@number1@@ cows and @@number2@@ sheep")
    assert result
    assert result[1] == dap(["@@number1@@"])
    assert result[3] == dap(["@@number2@@"])


def test_placeable_brace() -> None:
    bp = general.BracePlaceable
    # Double braces
    result = bp.parse("There were {{number}} cows")
    assert result
    assert result[1] == bp(["{{number}}"])
    result = bp.parse("There were {{number1}} cows and {{number2}} sheep")
    assert result
    assert result[1] == bp(["{{number1}}"])
    assert result[3] == bp(["{{number2}}"])

    # Single braces
    result = bp.parse("There were {number} cows")
    assert result
    assert result[1] == bp(["{number}"])
    result = bp.parse("There were {number1} cows and {number2} sheep")
    assert result
    assert result[1] == bp(["{number1}"])
    assert result[3] == bp(["{number2}"])

    # Mixed single and double braces
    result = bp.parse("There were {number1} cows and {{number2}} sheep")
    assert result
    assert result[1] == bp(["{number1}"])
    assert result[3] == bp(["{{number2}}"])
    result = bp.parse("There were {{number1}} cows and {number2} sheep")
    assert result
    assert result[1] == bp(["{{number1}}"])
    assert result[3] == bp(["{number2}"])


def test_python_placeable() -> None:
    pfp = general.PythonFormattingPlaceable
    # No conversion
    result = pfp.parse("100%% correct")
    assert result
    assert result[1] == pfp(["%%"])

    # Mapping keys
    result = pfp.parse("There were %(number)d cows")
    assert result
    assert result[1] == pfp(["%(number)d"])
    result = pfp.parse("There were %(cows.number)d cows")
    assert result
    assert result[1] == pfp(["%(cows.number)d"])
    result = pfp.parse("There were %(number of cows)d cows")
    assert result
    assert result[1] == pfp(["%(number of cows)d"])

    # Conversion flags
    result = pfp.parse("There were %(number)03d cows")
    assert result
    assert result[1] == pfp(["%(number)03d"])
    result = pfp.parse("There were %(number) 3d cows")
    assert result
    assert result[1] == pfp(["%(number) 3d"])

    # Minimum field width
    result = pfp.parse("There were %(number)*d cows")
    assert result
    assert result[1] == pfp(["%(number)*d"])

    # Precision
    result = pfp.parse("There were %(number)3.1d cows")
    assert result
    assert result[1] == pfp(["%(number)3.1d"])

    # Length modifier
    result = pfp.parse("There were %(number)Ld cows")
    assert result
    assert result[1] == pfp(["%(number)Ld"])


# TODO: JavaMessageFormatPlaceable, UrlPlaceable, XMLTagPlaceable
