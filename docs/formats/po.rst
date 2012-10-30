
.. _pages/toolkit/po#po_files:

PO Files
********
PO files use the file format of the Gettext tools.

.. seealso:: `Gettext manual <http://www.gnu.org/software/gettext/>`_ and
   `KDE style PO files <http://public.planetmirror.com/pub/kde/devel/gettext-kde/>`_

.. _pages/toolkit/po#supported_features:

Supported Features
==================

* Headers
* Plural forms and plural form handling
* Obsolete messages
* Message Context (msgctxt)
* Language header (since gettext version 0.17)
* Previous message ID and context (#| msgid and #| msgctxt)

.. _pages/toolkit/po#supported_comments:

Supported comments
==================

* normal comments ::

    # this is another comment

* automatic comments ::

    #. comment extracted from the source code

* source location comments ::

    #: sourcefile.xxx:35

* typecomments ::

    #, fuzzy

* msgidcomments ::

    magid "_: within msgid\n"

Also know as KDE style comments as they are used by KDE for message disambiguation and comments to translators. (support for this is being phased out)

* obsolete messages ::

    #~ msgid "Blah"
    #~ msgstr "Bleeh"

* previous msgid and msgctxt ::

    #| msgid "previous message"

.. _pages/toolkit/po#unsupported_features:

Unsupported Features
====================

.. _pages/toolkit/po#alternate_language:

Alternate language
------------------

::

  msgid "English"
  msgid[af] "Engels"

(This was proposed but not yet accepted in a released version of Gettext.)
