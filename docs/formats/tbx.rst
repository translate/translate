
.. _tbx:

TBX
***
TBX is the `LISA OSCAR standard
<https://www.gala-global.org/lisa-oscar-standards>`_ for terminology and term
exchange.

For information on more file formats, see :doc:`conformance`.


.. _tbx#references:

References
==========


* `Standard home page <https://www.tbxinfo.net/>`_
* `Specification
  <https://www.tbxinfo.net/wp-content/uploads/2020/12/TBXspecV1j.pdf>`_
* `ISO 30042
  <https://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=45797>`_
  -- TBX is an approved ISO standard
* `Additional TBX resources <https://www.tbxconvert.gevterm.net/>`_

You might also be interested in reading about `TBX-Basic
<https://ltac-global.github.io/TBX-Basic_dialect/>`_ -- a simpler,
reduced version of TBX with most of the useful features included.

Additional notes and examples about TBX are available in `Terminator TBX
conformance notes
<https://terminator.readthedocs.org/en/latest/tbx_conformance.html>`_ and on
`www.tbxinfo.net <https://www.tbxinfo.net/>`_ which might
help understanding this format.

Also you might want to use `TBXChecker
<https://sourceforge.net/projects/tbxutil/>`_ in order to check that TBX files
are valid. Check the `TBXChecker explanation
<https://www.tbxconvert.gevterm.net/tbx_checker_explanation.html>`_.


.. _tbx#conformance:

Conformance
===========


Translate Toolkit TBX format support allows:

* Basic TBX file creation
* Creating a bilingual TBX from CSV using :doc:`/commands/csv2tbx`
* Using ``<tig>`` tags only
* Extraction of parts of speech, definitions, and scoped notes
* Independent ordered alternatives within each language
* Preservation of term IDs and metadata when editing alternatives


.. _tbx#non-conformance:

Non-Conformance
===============


The following are not yet supported:

* Cross references
* Context
* Abbreviations
* ``<ntig>`` tag, read and write

Other features can be picked from the `Terminator TBX conformance notes
<https://terminator.readthedocs.org/en/latest/tbx_conformance.html>`_ which also
include examples and notes about the TBX format.


Language matching
=================


Language lookup first matches the requested code exactly, ignoring case and
``_`` versus ``-`` separators. If a bare language code has no exact match, its
Weblate language-data default-country variant is used when present. For example,
``en`` can select ``en-US`` and ``ko`` can select ``ko-KR``. An explicit ``en``
entry always takes precedence over ``en-US``.

Regional and script-qualified requests remain exact-only: ``en-GB`` does not
select ``en-US``, and ``en-US`` does not select ``en``. Unmatched languages remain
empty; target fallback does not reuse the source node for a distinct requested
language. Editing a matched language preserves its existing XML language tag.


Term alternatives
=================


``tbxunit.get_source_terms()`` and ``get_target_terms()`` return ordered
``TBXTerm`` records with text, optional ID, administrative status, and notes.
The ID comes from ``<tig>`` when present, falling back to the ``<term>`` ID.
Each ``TBXNote`` retains its origin, category, and scope (concept, language,
or term). Notes from unrelated languages or sibling terms are excluded.
The scalar ``source`` and ``target`` properties continue to return the first
term for compatibility with converters. Assigning ``None`` to ``target`` clears
that first term's text, retaining its metadata, sibling alternatives, and language
notes. The cleared scalar target is an empty string.

``set_source_terms()`` and ``set_target_terms()`` accept lists of strings.
They match unchanged occurrences first, then reuse remaining terms in order.
Reused terms retain their IDs and metadata; new terms do not require IDs.
An empty list clears an existing language to one empty term without term metadata,
preserving language notes and the required TBX structure. Its term list then
contains one record with empty text. Clearing a missing language leaves it absent.
When renaming and deleting terms together, this positional fallback can assign
the first unmatched term's metadata to a renamed alternative.

Languages are selected independently; term IDs do not pair translations
across languages. A missing selected target produces an empty term list.
A concept is obsolete only when all its nonempty terms are deprecated, including terms
in languages outside the selected source and target pair.
