#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2004-2007 Zuza Software Foundation
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

"""convert Gettext PO templates (.pot) to PO localization files, preserving existing translations

See: http://translate.sourceforge.net/wiki/toolkit/pot2po for examples and 
usage instructions
"""

from translate.storage import po
from translate.storage import factory
from translate.search import match
from translate.misc.multistring import multistring
from translate.tools import pretranslate

def convertpot(input_file, output_file, template_file, tm=None, min_similarity=75, fuzzymatching=True, **kwargs):
    input_store = po.pofile(input_file)
    template_store = None
    if template_file is not None:
        template_store = po.pofile(template_file)
    outputpo = convert_stores(input_store, template_store, tm, min_similarity, fuzzymatching, **kwargs)
    output_file.write(str(outputpo))
    return 1

def convert_stores(input_store, template_store, tm=None, min_similarity=75, fuzzymatching=True, **kwargs):
    """Adjusts the header of input_store, returns output_store. If 
    template_store exists, merge translations from it into output_store which 
    is returned"""
    input_store.makeindex()
    output_store = po.pofile()
    
    # header values
    charset = "UTF-8"
    encoding = "8bit"
    project_id_version = None
    pot_creation_date = None
    po_revision_date = None
    last_translator = None
    language_team = None
    mime_version = None
    plural_forms = None
    kwargs = {}

    if template_store is not None:
        for unit in template_store.units:
            if unit.isobsolete():
                unit.resurrect()
                
        template_store.makeindex()
        
        templateheadervalues = template_store.parseheader()
        for key, value in templateheadervalues.iteritems():
            if key == "Project-Id-Version":
                project_id_version = value
            elif key == "Last-Translator":
                last_translator = value
            elif key == "Language-Team":
                language_team = value
            elif key == "PO-Revision-Date":
                po_revision_date = value
            elif key in ("POT-Creation-Date", "MIME-Version"):
                # don't know how to handle these keys, or ignoring them
                pass
            elif key == "Content-Type":
                kwargs[key] = value
            elif key == "Content-Transfer-Encoding":
                encoding = value
            elif key == "Plural-Forms":
                plural_forms = value
            else:
                kwargs[key] = value

    matchers = []
    if fuzzymatching:
        if template_store:
            matcher = match.matcher(template_store, max_candidates=1, min_similarity=min_similarity, max_length=3000, usefuzzy=True)
            matcher.addpercentage = False
            matchers.append(matcher)
            
        if tm:
            matcher = pretranslate.memory(tm, max_candidates=1, min_similarity=min_similarity, max_length=1000)
            matcher.addpercentage = False
            matchers.append(matcher)
        
    inputheadervalues = input_store.parseheader()
    for key, value in inputheadervalues.iteritems():
        if key in ("Project-Id-Version", "Last-Translator", "Language-Team", "PO-Revision-Date", "Content-Type", "Content-Transfer-Encoding", "Plural-Forms"):
            # want to carry these from the template so we ignore them
            pass
        elif key == "POT-Creation-Date":
            pot_creation_date = value
        elif key == "MIME-Version":
            mime_version = value
        else:
            kwargs[key] = value
            
    output_header = output_store.makeheader(charset=charset, encoding=encoding, project_id_version=project_id_version,
        pot_creation_date=pot_creation_date, po_revision_date=po_revision_date, last_translator=last_translator,
        language_team=language_team, mime_version=mime_version, plural_forms=plural_forms, **kwargs)
    
    # Get the header comments and fuzziness state
    if template_store is not None and len(template_store.units) > 0:
        if template_store.units[0].isheader():
            if template_store.units[0].getnotes("translator"):
                output_header.addnote(template_store.units[0].getnotes("translator"), "translator")
            if input_store.units[0].getnotes("developer"):
                output_header.addnote(input_store.units[0].getnotes("developer"), "developer")
            output_header.markfuzzy(template_store.units[0].isfuzzy())
    elif len(input_store.units) > 0 and input_store.units[0].isheader():
        output_header.addnote(input_store.units[0].getnotes())
        
    output_store.addunit(output_header)
    
    # Do matching
    for input_unit in input_store.units:
        if input_unit.istranslatable():
            input_unit = pretranslate.pretranslate_unit(input_unit, template_store, matchers, mark_reused=True)

            if input_unit.hasplural() and len(input_unit.target) == 0:
                # found no translation; Let's ensure that we have the correct number of plural forms:
                nplurals, plural = output_store.getheaderplural()
                if nplurals and nplurals.isdigit() and nplurals != '2':
                    input_unit.target = multistring([""]*int(nplurals))
            output_store.addunit(input_unit)

    #Let's take care of obsoleted messages
    if template_store:
        newlyobsoleted = []
        for unit in template_store.units:
            if unit.isheader():
                continue
            if unit.target and not (input_store.findunit(unit.source) or hasattr(unit, "reused")):
                #not in .pot, make it obsolete
                unit.makeobsolete()
                newlyobsoleted.append(unit)
            elif unit.isobsolete():
                output_store.addunit(unit)
        for unit in newlyobsoleted:
            output_store.addunit(unit)
    return output_store

def main(argv=None):
    from translate.convert import convert
    formats = {"pot": ("po", convertpot), ("pot", "po"): ("po", convertpot)}
    parser = convert.ConvertOptionParser(formats, usepots=True, usetemplates=True, 
        allowmissingtemplate=True, description=__doc__)
    parser.add_option("", "--tm", dest="tm", default=None,
        help="The file to use as translation memory when fuzzy matching")
    parser.passthrough.append("tm")
    defaultsimilarity = 75
    parser.add_option("-s", "--similarity", dest="min_similarity", default=defaultsimilarity,
        type="float", help="The minimum similarity for inclusion (default: %d%%)" % defaultsimilarity)
    parser.passthrough.append("min_similarity")
    parser.add_option("--nofuzzymatching", dest="fuzzymatching", action="store_false", 
        default=True, help="Disable fuzzy matching")
    parser.passthrough.append("fuzzymatching")
    parser.run(argv)


if __name__ == '__main__':
    main()
