
.. _po#po_files:

PO Files
********
PO files use the file format of the Gettext tools.

.. seealso:: `Gettext manual <http://www.gnu.org/software/gettext/>`_ and
   `KDE style PO files <http://public.planetmirror.com/pub/kde/devel/gettext-kde/>`_

.. _po#supported_features:

Supported Features
==================

* Headers
* Plural forms and plural form handling
* Obsolete messages
* Message Context (msgctxt)
* Language header (since gettext version 0.17)
* Previous message ID and context (#| msgid and #| msgctxt)

.. _po#supported_comments:

Supported comments
==================

* normal comments

.. code-block:: po

    # this is another comment

* automatic comments

.. code-block:: po

    #. comment extracted from the source code

* source location comments

.. code-block:: po

    #: sourcefile.xxx:35

* typecomments

.. code-block:: po

    #, fuzzy

* msgidcomments

.. code-block:: po

    msgid "_: comment\n"
    "translation"

Also know as KDE style comments as they are used by KDE for message disambiguation and comments to translators. (support for this is being phased out)

* obsolete messages

.. code-block:: po

    #~ msgid "Blah"
    #~ msgstr "Bleeh"

* previous msgid and msgctxt

.. code-block:: po

    #| msgid "previous message"

.. _po#unsupported_features:

Unsupported Features
====================

None
