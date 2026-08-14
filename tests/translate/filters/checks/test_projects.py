"""Tests for the checks that only exist for a single project."""

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_gconf() -> None:
    """Test GNOME gconf errors."""
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


def test_dialogsizes() -> None:
    """Test Mozilla dialog sizes."""
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


def test_validxml() -> None:
    """Test wheather validxml recognize invalid xml/html expressions."""
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
