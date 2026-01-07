from io import BytesIO

from translate.lang import factory as lang_factory
from translate.storage import po, tmx, xliff
from translate.tools import posegment


class TestPOSegment:
    @staticmethod
    def posegment(
        posource,
        sourcelanguage,
        targetlanguage,
        stripspaces=True,
        onlyaligned=True,
    ):
        """Helper that convert po source without requiring files."""
        inputfile = BytesIO(posource.encode())
        inputpo = po.pofile(inputfile)
        sourcelang = lang_factory.getlanguage(sourcelanguage)
        targetlang = lang_factory.getlanguage(targetlanguage)
        convertor = posegment.segment(
            sourcelang, targetlang, stripspaces=stripspaces, onlyaligned=onlyaligned
        )
        return convertor.convertstore(inputpo)

    def test_en_ja_simple(self) -> None:
        posource = """
#: test/test.py:112
msgid ""
"Please let us know if you have any specific needs (A/V requirements, "
"multiple microphones, a table, etc).  Note for example that 'audio out' is "
"not provided for your computer unless you tell us in advance."
msgstr ""
"特に必要な物(A/V機器、複数のマイク、テーブルetc)があれば教えて下さい。例とし"
"て、コンピュータからの「音声出力」は事前にお知らせ頂いていない場合は提供でき"
"ないことに注意して下さい。"
"""
        poresult = self.posegment(posource, "en", "ja")
        out_unit = poresult.units[1]
        assert (
            out_unit.source
            == "Please let us know if you have any specific needs (A/V requirements, multiple microphones, a table, etc)."
        )
        assert (
            out_unit.target
            == "特に必要な物(A/V機器、複数のマイク、テーブルetc)があれば教えて下さい。"
        )
        out_unit = poresult.units[2]
        assert (
            out_unit.source
            == "Note for example that 'audio out' is not provided for your computer unless you tell us in advance."
        )
        assert (
            out_unit.target
            == "例として、コンピュータからの「音声出力」は事前にお知らせ頂いていない場合は提供できないことに注意して下さい。"
        )

    def test_en_ja_punctuation(self) -> None:
        """Checks that a half-width punctuation."""
        posource = """
#: docs/intro/contributing.txt:184
msgid ""
"Note that the latest Django trunk may not always be stable. When developing "
"against trunk, you can check Django's continuous integration builds."
msgstr ""
"開発中の､最新の Django ではステーブルとは限りません｡トランクバージョンで開発"
"を行う場合､ Django の継続インテグレーションビルドをチェックしてください｡"
"""
        poresult = self.posegment(posource, "en", "ja")
        out_unit = poresult.units[1]
        assert (
            out_unit.source
            == "Note that the latest Django trunk may not always be stable."
        )
        assert out_unit.target == "開発中の､最新の Django ではステーブルとは限りません｡"

        out_unit = poresult.units[2]
        assert (
            out_unit.source
            == "When developing against trunk, you can check Django's continuous integration builds."
        )
        assert (
            out_unit.target
            == "トランクバージョンで開発を行う場合､ Django の継続インテグレーションビルドをチェックしてください｡"
        )

    def test_transifex_po(self) -> None:
        """Checks that a po file with mismatched sentence counts is handled correctly."""
        posource = """# 8456b7744a02478cb75a9ad7f950d8cf
#: ../../../../1.8/docs/intro/contributing.txt:184
msgid ""
"Note that the latest Django trunk may not always be stable. When developing "
"against trunk, you can check `Django's continuous integration builds`__ to "
"determine if the failures are specific to your machine or if they are also "
"present in Django's official builds. If you click to view a particular "
"build, you can view the Configuration Matrix which shows failures broken "
"down by Python version and database backend."
msgstr ""
"開発中の､最新の Django ではステーブルとは限りません｡トランクバージョンで開発"
"を行う場合､ `Django の継続インテグレーションビルド`__ をチェックしてください｡"
"これで､テストの失敗があなたのマシンだけのものか､ Django 公式のビルドによるも"
"のかが分かります｡各ビルドについてのリンクをクリックすれば､ Configuration "
"Matrix という､ 各 Python のバージョン､ DB バックエンドに対応したテストの失"
"敗を閲覧できます｡"
"""
        poresult = self.posegment(posource, "en", "ja")
        # Should have at least 2 units: header + the unsegmented translation unit
        # (not segmented because sentence counts don't match: 3 vs 4)
        assert len(poresult.units) >= 2
        out_unit = poresult.units[1]
        # The unit should be preserved unsegmented since sentence counts don't match
        assert (
            out_unit.source
            == "Note that the latest Django trunk may not always be stable. When developing against trunk, you can check `Django's continuous integration builds`__ to determine if the failures are specific to your machine or if they are also present in Django's official builds. If you click to view a particular build, you can view the Configuration Matrix which shows failures broken down by Python version and database backend."
        )
        assert (
            out_unit.target
            == "開発中の､最新の Django ではステーブルとは限りません｡トランクバージョンで開発を行う場合､ `Django の継続インテグレーションビルド`__ をチェックしてください｡これで､テストの失敗があなたのマシンだけのものか､ Django 公式のビルドによるものかが分かります｡各ビルドについてのリンクをクリックすれば､ Configuration Matrix という､ 各 Python のバージョン､ DB バックエンドに対応したテストの失敗を閲覧できます｡"
        )


class TestXLIFFSegment:
    @staticmethod
    def xliff_segment(
        xliffsource,
        sourcelanguage,
        targetlanguage,
        stripspaces=True,
        onlyaligned=True,
    ):
        """Helper that converts xliff source without requiring files."""
        inputfile = BytesIO(xliffsource.encode())
        inputstore = xliff.xlifffile(inputfile)
        sourcelang = lang_factory.getlanguage(sourcelanguage)
        targetlang = lang_factory.getlanguage(targetlanguage)
        convertor = posegment.segment(
            sourcelang, targetlang, stripspaces=stripspaces, onlyaligned=onlyaligned
        )
        return convertor.convertstore(inputstore)

    def test_xliff_en_simple(self) -> None:
        """Test basic XLIFF segmentation."""
        xliffsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
  <file datatype="plaintext" original="test.txt" source-language="en" target-language="fr">
    <body>
      <trans-unit id="1" approved="yes">
        <source>This is the first sentence. This is the second sentence.</source>
        <target>Ceci est la première phrase. Ceci est la deuxième phrase.</target>
      </trans-unit>
    </body>
  </file>
</xliff>"""
        xliffresult = self.xliff_segment(xliffsource, "en", "fr")
        # Should have 2 units after segmentation
        assert len(xliffresult.units) == 2
        assert xliffresult.units[0].source == "This is the first sentence."
        assert xliffresult.units[0].target == "Ceci est la première phrase."
        assert xliffresult.units[1].source == "This is the second sentence."
        assert xliffresult.units[1].target == "Ceci est la deuxième phrase."

    def test_xliff_untranslated(self) -> None:
        """Test XLIFF segmentation with untranslated units."""
        xliffsource = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
  <file datatype="plaintext" original="test.txt" source-language="en" target-language="fr">
    <body>
      <trans-unit id="1">
        <source>First sentence. Second sentence.</source>
      </trans-unit>
    </body>
  </file>
</xliff>"""
        xliffresult = self.xliff_segment(xliffsource, "en", "fr")
        # Should have 2 units after segmentation with empty targets
        assert len(xliffresult.units) == 2
        assert xliffresult.units[0].source == "First sentence."
        assert xliffresult.units[0].target == ""
        assert xliffresult.units[1].source == "Second sentence."
        assert xliffresult.units[1].target == ""


class TestTMXSegment:
    @staticmethod
    def tmx_segment(
        tmxsource,
        sourcelanguage,
        targetlanguage,
        stripspaces=True,
        onlyaligned=True,
    ):
        """Helper that converts tmx source without requiring files."""
        inputfile = BytesIO(tmxsource.encode())
        inputstore = tmx.tmxfile(inputfile)
        sourcelang = lang_factory.getlanguage(sourcelanguage)
        targetlang = lang_factory.getlanguage(targetlanguage)
        convertor = posegment.segment(
            sourcelang, targetlang, stripspaces=stripspaces, onlyaligned=onlyaligned
        )
        return convertor.convertstore(inputstore)

    def test_tmx_en_simple(self) -> None:
        """Test basic TMX segmentation."""
        tmxsource = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header adminlang="en" creationtool="test" creationtoolversion="1.0"
          datatype="PlainText" o-tmf="UTF-8" segtype="sentence" srclang="en"/>
  <body>
    <tu>
      <tuv xml:lang="en">
        <seg>This is the first sentence. This is the second sentence.</seg>
      </tuv>
      <tuv xml:lang="fr">
        <seg>Ceci est la première phrase. Ceci est la deuxième phrase.</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""
        tmxresult = self.tmx_segment(tmxsource, "en", "fr")
        # Should have 2 units after segmentation
        assert len(tmxresult.units) == 2
        assert tmxresult.units[0].source == "This is the first sentence."
        assert tmxresult.units[0].target == "Ceci est la première phrase."
        assert tmxresult.units[1].source == "This is the second sentence."
        assert tmxresult.units[1].target == "Ceci est la deuxième phrase."
