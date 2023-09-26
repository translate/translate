from translate.lang import af, factory


def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("af")
    sentences = language.sentences("Normal case. Nothing interesting.")
    assert sentences == ["Normal case.", "Nothing interesting."]
    sentences = language.sentences("Wat? 'n Fout?")
    assert sentences == ["Wat?", "'n Fout?"]
    sentences = language.sentences("Dit sal a.g.v. 'n fout gebeur.")
    assert sentences == ["Dit sal a.g.v. 'n fout gebeur."]
    sentences = language.sentences(
        "Weet nie hoe om lêer '%s' te open nie.\nMiskien is dit 'n tipe beeld wat nog nie ondersteun word nie.\n\nKies liewer 'n ander prent."
    )
    assert len(sentences) == 3


def test_capsstart():
    """Tests that the indefinite article ('n) doesn't confuse startcaps()."""
    language = factory.getlanguage("af")
    assert not language.capsstart("")
    assert language.capsstart("Koeie kraam koeie")
    assert language.capsstart("'Koeie' kraam koeie")
    assert not language.capsstart("koeie kraam koeie")
    assert language.capsstart("\n\nKoeie kraam koeie")
    assert language.capsstart("'n Koei kraam koeie")
    assert language.capsstart("'n 'Koei' kraam koeie")
    assert not language.capsstart("'n koei kraam koeie")
    assert language.capsstart("\n\n'n Koei kraam koeie")


def test_transliterate_cyrillic():
    def trans(text):
        print(("Orig: %s" % text).encode("utf-8"))
        trans = af.tranliterate_cyrillic(text)
        print(("Trans: %s" % trans).encode("utf-8"))
        return trans

    assert trans("Борис Николаевич Ельцин") == "Boris Nikolajewitj Jeltsin"
