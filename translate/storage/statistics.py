from translate import lang
from translate.lang import factory

class Statistics(object):
    """Manages statistics for storage objects."""

    def __init__(self):
        self.sourcelanguage = 'en'
        self.targetlanguage = 'en'

        self.stats = {}

    def fuzzy_units(self):
        count = 0
        for unit in self.getunits():
            if unit.isfuzzy():
                count += 1
        return count

    def translated_units(self):
        """Return a list of translated units."""

        translated = []
        units = self.getunits()
        for unit in units:
            if unit.istranslated():
                translated.append(unit)
        return translated

    def translated_unitcount(self):
        """Returns the number of translated units."""

        translated_unitcount = len(self.translated_units())
        return translated_unitcount

    def untranslated_units(self):
        """Return a list of untranslated units."""

        untranslated = []
        units = self.getunits()
        for unit in units:
            if not unit.istranslated():
                untranslated.append(unit)
        return untranslated

    def untranslated_unitcount(self):
        """Returns the number of untranslated units."""

        return len(self.untranslated_units())

    def getunits(self):
        """Returns a list of all units in this object."""
        return []

    def get_source_text(self, units):
        """Joins the unit source strings in a single string of text."""
        source_text = ""
        for unit in units:
            source_text += unit.source + " "
        return source_text

    def wordcount(self, text):
        """Returns the number of words in the given text."""

        language = lang.factory.getlanguage(self.sourcelanguage)
        return len(language.words(text))

    def source_wordcount(self):
        units = self.getunits()
        source_text = self.get_source_text(units)
        return self.wordcount(source_text)

    def translated_wordcount(self):
        """Returns the number of translated words in this object."""

        text = self.get_source_text(self.translated_units())
        return self.wordcount(text)

    def untranslated_wordcount(self):
        """Returns the number of untranslated words in this object."""

        text = self.get_source_text(self.untranslated_units())
        return self.wordcount(text)
