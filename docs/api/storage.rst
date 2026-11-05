storage
=======

.. automodule:: translate.storage
   :show-inheritance:

Editing existing units
----------------------

Use a unit's ``source`` property to change its source text, ``setcontext()`` to
change a supported context, and ``setid()`` to change an independent key. These
operations update the existing unit instead of replacing it, retaining its
translations and other metadata. They do not automatically mark translations
as needing review.

Key and context support depends on the format. The base ``setid()`` does
nothing, and an in-memory context is not necessarily serialized. Applications
must check format support before editing. Call ``unit.validate_id(new_key)``
before ``unit.setid(new_key)`` to check a proposed key without changing the
unit or its store. Invalid or unsafe string keys raise ``ValueError``. The
base validator checks common control characters; it does not establish that
every format can represent the key or round-trip it exactly.
File-level BOM detection is outside the scope of these key checks.

Fluent checks its message or term identifier grammar; comment units have no
editable identifier. Android resources check resource name syntax. RESX and
XLIFF 1 and 2 check XML character safety. PHP, Laravel PHP, properties, and
DTD check their respective key syntax. Java properties IDs use the serialized
key spelling, including backslash escapes, rather than the decoded key text.
PHP IDs similarly represent PHP source expressions; numeric offsets retain
PHP's normal key coercion. These format-specific checks should be used before
key edits, but a successful base-class check alone does not promise an exact
serialized round trip.

Where a format has an independent, exactly representable key,
``validate_id(value)`` succeeding means ``setid(value)`` will retain that ID
through serialization and reparsing. XLIFF IDs can be composite: XLIFF 1 may
include a file prefix, and XLIFF 2 may include an explicit or generated
segment ID. Their validators account for the current unit and its XML context;
generated XLIFF 2 segment IDs do not become explicit XML attributes when
reapplied. Dictionary-backed formats such as JSON, YAML, and TOML use paths
of keys and indexes, so their base validation alone cannot guarantee exact
path representation. Setters can also retain format-specific normalization:
PHP and Laravel PHP accept some source-style or shorthand names, XLIFF 1
accepts an unprefixed ID within its current file, and DTD uses an empty name
internally to omit an entity during conversion. Such inputs may be accepted
by ``setid()`` even when ``validate_id()`` does not promise exact
representation for them.

Source, key, and context setters invalidate attached store indexes. Use
``findid()``, ``findunit()``, or ``findunits()`` for subsequent lookups; they
rebuild the indexes when needed. Call ``makeindex()`` before accessing index
dictionaries directly after an edit. Add units through ``addunit()`` so their
setters can notify the store.

JSON supports changing nested key paths. YAML and TOML retain their original
documents to preserve formatting and comments; attached units support renaming
a key within its existing mapping, including nested mappings. Moving a stored
unit between mappings or renaming an array index raises ``ValueError``, as does
renaming to an existing key in the retained document.

XML source edits preserve language and text-node attributes and surrounding
metadata. Assigning the existing source text preserves inline markup; changing
the text replaces its inline content. Use the rich-source interface when the
replacement needs inline markup.


base
----

.. automodule:: translate.storage.base
   :members:
   :inherited-members:



catkeys
-------

.. automodule:: translate.storage.catkeys
   :members:
   :inherited-members:


cpo
---

.. automodule:: translate.storage.cpo
   :members:
   :inherited-members:


csvl10n
-------

.. automodule:: translate.storage.csvl10n
   :members:
   :inherited-members:


dtd
---

.. automodule:: translate.storage.dtd
   :members:
   :inherited-members:


_factory_classes
----------------

.. automodule:: translate.storage._factory_classes
   :members:
   :inherited-members:


factory
-------

.. automodule:: translate.storage.factory
   :members:
   :inherited-members:


fpo
---

.. automodule:: translate.storage.fpo
   :members:
   :inherited-members:


html
----

.. automodule:: translate.storage.html
   :members:
   :inherited-members:


ical
----

.. automodule:: translate.storage.ical
   :members:
   :inherited-members:


ini
---

.. automodule:: translate.storage.ini
   :members:
   :inherited-members:


jsonl10n
--------

.. automodule:: translate.storage.jsonl10n
   :members:
   :inherited-members:


lisa
----

Stores based on ``LISAfile``, including XLIFF 1.2 and 2.0, expose the per-store
``XMLutf8BOM`` option. Set ``store.XMLutf8BOM = True`` to write a UTF-8 byte order
mark (BOM), or ``False`` to omit it. The default, ``None``, preserves whether the
parsed input started with a UTF-8 BOM; new stores omit it. This default preserves
input BOMs that earlier versions discarded.

The option applies only to UTF-8 output and leaves other encodings unchanged.
Keep the store encoding as UTF-8; do not use ``utf-8-sig``. Both
``store.serialize(out)`` and ``bytes(store)`` write a single BOM before the XML
declaration when requested. The declaration still uses ``UTF-8`` or ``utf-8``,
according to ``XMLuppercaseEncoding``.
QPH stores also honor this option while retaining their declaration-free UTF-8
output.

.. automodule:: translate.storage.lisa
   :members:
   :inherited-members:


markdown
--------

.. automodule:: translate.storage.markdown
   :members:
   :inherited-members:


mo
--

.. automodule:: translate.storage.mo
   :members:
   :inherited-members:


mozilla_lang
------------

.. automodule:: translate.storage.mozilla_lang
   :members:
   :inherited-members:


odf_io
------

.. automodule:: translate.storage.odf_io
   :members:
   :inherited-members:


odf_shared
----------

.. automodule:: translate.storage.odf_shared
   :members:
   :inherited-members:


omegat
------

.. automodule:: translate.storage.omegat
   :members:
   :inherited-members:


oo
--

.. automodule:: translate.storage.oo
   :members:
   :inherited-members:


placeables
----------

.. automodule:: translate.storage.placeables
   :show-inheritance:


base
~~~~

.. automodule:: translate.storage.placeables.base
   :members:
   :inherited-members:


general
~~~~~~~

.. automodule:: translate.storage.placeables.general
   :members:
   :inherited-members:


interfaces
~~~~~~~~~~

.. automodule:: translate.storage.placeables.interfaces
   :members:
   :inherited-members:


lisa
~~~~

.. automodule:: translate.storage.placeables.lisa
   :members:
   :inherited-members:


parse
~~~~~

.. automodule:: translate.storage.placeables.parse
   :members:
   :inherited-members:


strelem
~~~~~~~

.. automodule:: translate.storage.placeables.strelem
   :members:
   :inherited-members:


terminology
~~~~~~~~~~~

.. automodule:: translate.storage.placeables.terminology
   :members:
   :inherited-members:


xliff
~~~~~

.. automodule:: translate.storage.placeables.xliff
   :members:
   :inherited-members:


php
---

.. automodule:: translate.storage.php
   :members:
   :inherited-members:


pocommon
--------

.. automodule:: translate.storage.pocommon
   :members:
   :inherited-members:


poheader
--------

.. automodule:: translate.storage.poheader
   :members:
   :inherited-members:


poparser
--------

.. automodule:: translate.storage.poparser
   :members:
   :inherited-members:


po
--

.. automodule:: translate.storage.po
   :members:
   :inherited-members:


poxliff
-------

.. automodule:: translate.storage.poxliff
   :members:
   :inherited-members:


properties
----------

.. automodule:: translate.storage.properties
   :members:
   :inherited-members:


pypo
----

.. automodule:: translate.storage.pypo
   :members:
   :inherited-members:


qm
--

.. automodule:: translate.storage.qm
   :members:
   :inherited-members:


qph
---

.. automodule:: translate.storage.qph
   :members:
   :inherited-members:


rc
--

.. automodule:: translate.storage.rc
   :members:
   :inherited-members:


statistics
----------

.. automodule:: translate.storage.statistics
   :members:
   :inherited-members:


subtitles
---------

.. automodule:: translate.storage.subtitles
   :members:
   :inherited-members:


symbian
-------

.. automodule:: translate.storage.symbian
   :members:
   :inherited-members:


tbx
---

.. automodule:: translate.storage.tbx
   :members:
   :inherited-members:


tiki
----

.. automodule:: translate.storage.tiki
   :members:
   :inherited-members:


tmx
---

.. automodule:: translate.storage.tmx
   :members:
   :inherited-members:


trados
------

.. automodule:: translate.storage.trados
   :members:
   :inherited-members:


ts2
---

.. automodule:: translate.storage.ts2
   :members:
   :inherited-members:


ts
--

.. automodule:: translate.storage.ts
   :members:
   :inherited-members:
   :deprecated:


txt
---

.. automodule:: translate.storage.txt
   :members:
   :inherited-members:


utx
---

.. automodule:: translate.storage.utx
   :members:
   :inherited-members:


wordfast
--------

.. automodule:: translate.storage.wordfast
   :members:
   :inherited-members:


workflow
--------

.. automodule:: translate.storage.workflow
   :members:
   :inherited-members:


xliff
-----

.. automodule:: translate.storage.xliff
   :members:
   :inherited-members:


xml_extract
-----------

.. automodule:: translate.storage.xml_extract
   :show-inheritance:


extract
~~~~~~~

.. automodule:: translate.storage.xml_extract.extract
   :members:
   :inherited-members:


generate
~~~~~~~~

.. automodule:: translate.storage.xml_extract.generate
   :members:
   :inherited-members:


misc
~~~~

.. automodule:: translate.storage.xml_extract.misc
   :members:
   :inherited-members:


unit_tree
~~~~~~~~~

.. automodule:: translate.storage.xml_extract.unit_tree
   :members:
   :inherited-members:


xpath_breadcrumb
~~~~~~~~~~~~~~~~

.. automodule:: translate.storage.xml_extract.xpath_breadcrumb
   :members:
   :inherited-members:


xml_name
--------

.. automodule:: translate.storage.xml_name
   :members:
   :inherited-members:
