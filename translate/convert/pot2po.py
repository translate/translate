#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2004-2006 Zuza Software Foundation
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

"""converts gettext .pot template to .po translation files, merging in existing translations if present"""

from translate.storage import po
from translate.storage import factory
from translate.search import match

# We don't want to reinitialise the TM each time, so let's store it here.
tmmatcher = None

def memory(tmfiles, max_candidates=1, min_similarity=75, max_length=1000):
    """Returns the TM store to use. Only initialises on first call."""
    global tmmatcher
    # Only initialise first time
    if tmmatcher is None:
      if isinstance(tmfiles, list):
        tmstore = [factory.getobject(tmfile) for tmfile in tmfiles]
      else:
        tmstore = factory.getobject(tmfiles)
      tmmatcher = match.matcher(tmstore, max_candidates=max_candidates, min_similarity=min_similarity, max_length=max_length)
    return tmmatcher

def convertpot(inputpotfile, outputpofile, templatepofile, tm=None, min_similarity=75):
  """reads in inputpotfile, adjusts header, writes to outputpofile. if templatepofile exists, merge translations from it into outputpofile"""
  inputpot = po.pofile(inputpotfile)
  outputpo = po.pofile()
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
  if templatepofile is not None:
    templatepo = po.pofile(templatepofile)
    for unit in templatepo.units:
      if unit.isobsolete():
        unit.resurrect()
    try:
      fuzzyfilematcher = match.matcher(templatepo, max_candidates=1, min_similarity=75, max_length=1000)
      fuzzyfilematcher.addpercentage = False
    except:
      fuzzyfilematcher = None
    templatepo.makeindex()
    templateheadervalues = templatepo.parseheader()
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
  try:
    fuzzyglobalmatcher = memory(tmfiles, max_candidates=1, min_similarity=75, max_length=1000)
    fuzzyglobalmatcher.addpercentage = False
  except:
    fuzzyglobalmatcher = None
  inputheadervalues = inputpot.parseheader()
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
  outputheaderpo = outputpo.makeheader(charset=charset, encoding=encoding, project_id_version=project_id_version,
    pot_creation_date=pot_creation_date, po_revision_date=po_revision_date, last_translator=last_translator,
    language_team=language_team, mime_version=mime_version, plural_forms=plural_forms, **kwargs)
  # Get the header comments and fuzziness state
  if templatepofile is not None:
    if templatepo.units[0].isheader():    
      if templatepo.units[0].getnotes():
        outputheaderpo.addnote(templatepo.units[0].getnotes())
      outputheaderpo.markfuzzy(templatepo.units[0].isfuzzy())
  elif inputpot.units[0].isheader():
    outputheaderpo.addnote(inputpot.units[0].getnotes())
  outputpo.units.append(outputheaderpo)
  # Do matching
  for inputpotunit in inputpot.units:
    if not inputpotunit.isheader():
      if templatepofile:
        possiblematches = []
        for location in inputpotunit.getlocations():
          templatepounit = templatepo.locationindex.get(location, None)
          if templatepounit is not None:
            possiblematches.append(templatepounit)
        if len(inputpotunit.getlocations()) == 0:
          templatepounit = templatepo.findunit(inputpotunit.source)
        if templatepounit:
          possiblematches.append(templatepounit)
        for templatepounit in possiblematches:
          if inputpotunit.source == templatepounit.source:
            inputpotunit.merge(templatepounit)
            break
        else: 
          if fuzzyfilematcher:
            fuzzycandidates = fuzzyfilematcher.matches(inputpotunit.source)
            if fuzzycandidates:
              inputpotunit.merge(fuzzycandidates[0])
              original = templatepo.findunit(fuzzycandidates[0].source)
              if original:
                original.reused = True
          if fuzzyglobalmatcher and not fuzzycandidates:
            fuzzycandidates = fuzzyglobalmatcher.matches(inputpotunit.source)
            if fuzzycandidates:
              inputpotunit.merge(fuzzycandidates[0])
        outputpo.units.append(inputpotunit)
      else:
        if fuzzyglobalmatcher:
          fuzzycandidates = fuzzyglobalmatcher.matches(inputpotunit.source)
          if fuzzycandidates:
            inputpotunit.merge(fuzzycandidates[0])
        outputpo.units.append(inputpotunit)

  #Let's take care of obsoleted messages
  if templatepofile:
    newlyobsoleted = []
    for unit in templatepo.units:
      if unit.target and not (inputpot.findunit(unit.source) or hasattr(unit, "reused")):
        #not in .pot, make it obsolete
        unit.makeobsolete()
        newlyobsoleted.append(unit)
      elif unit.isobsolete():
        outputpo.units.append(unit)
    outputpo.units.extend(newlyobsoleted)
  outputpofile.write(str(outputpo))
  return 1

def main(argv=None):
  from translate.convert import convert
  formats = {"pot": ("po", convertpot), ("pot", "po"): ("po", convertpot)}
  parser = convert.ConvertOptionParser(formats, usepots=True, usetemplates=True, description=__doc__)
  parser.add_option("", "--tm", dest="tm", default=None,
    help="The file to use as translation memory")
  parser.passthrough.append("tm")
  parser.add_option("-s", "--similarity", dest="min_similarity", default=75,
    help="The minimum similarity for inclusion")
  parser.passthrough.append("min_similarity")
  parser.run(argv)

