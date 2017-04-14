# -*- coding: utf-8 -*-

from translate.lang import factory as lang_factory
from translate.misc import wStringIO
from translate.storage import po
from translate.tools import posegment


class TestPOSegment:

    def posegment(self, posource, sourcelanguage, targetlanguage, stripspaces=True, onlyaligned=True):
        """helper that convert po source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        sourcelang = lang_factory.getlanguage(sourcelanguage)
        targetlang = lang_factory.getlanguage(targetlanguage)
        convertor = posegment.segment(sourcelang, targetlang, stripspaces=stripspaces, onlyaligned=onlyaligned)
        outputpo = convertor.convertstore(inputpo)
        return outputpo

    def test_en_ja_simple(self):
        posource = '''
#: test/test.py:112
msgid ""
"Please let us know if you have any specific needs (A/V requirements, "
"multiple microphones, a table, etc).  Note for example that 'audio out' is "
"not provided for your computer unless you tell us in advance."
msgstr ""
"特に必要な物(A/V機器、複数のマイク、テーブルetc)があれば教えて下さい。例とし"
"て、コンピュータからの「音声出力」は事前にお知らせ頂いていない場合は提供でき"
"ないことに注意して下さい。"
'''
        poresult = self.posegment(posource, "en", "ja")
        out_unit = poresult.units[1]
        assert out_unit.source == "Please let us know if you have any specific needs (A/V requirements, multiple microphones, a table, etc)."
        assert out_unit.target == u"特に必要な物(A/V機器、複数のマイク、テーブルetc)があれば教えて下さい。"
        out_unit = poresult.units[2]
        assert out_unit.source == "Note for example that 'audio out' is not provided for your computer unless you tell us in advance."
        assert out_unit.target == u"例として、コンピュータからの「音声出力」は事前にお知らせ頂いていない場合は提供できないことに注意して下さい。"

    def test_en_ja_punctuation(self):
        """checks that a half-width punctuation"""
        posource = u'''
#: docs/intro/contributing.txt:184
msgid ""
"Note that the latest Django trunk may not always be stable. When developing "
"against trunk, you can check Django's continuous integration builds."
msgstr ""
"開発中の､最新の Django ではステーブルとは限りません｡トランクバージョンで開発"
"を行う場合､ Django の継続インテグレーションビルドをチェックしてください｡"
'''
        poresult = self.posegment(posource, "en", "ja")
        out_unit = poresult.units[1]
        assert out_unit.source == "Note that the latest Django trunk may not always be stable."
        assert out_unit.target == u"開発中の､最新の Django ではステーブルとは限りません｡"

        out_unit = poresult.units[2]
        assert out_unit.source == "When developing against trunk, you can check Django's continuous integration builds."
        assert out_unit.target == u"トランクバージョンで開発を行う場合､ Django の継続インテグレーションビルドをチェックしてください｡"
