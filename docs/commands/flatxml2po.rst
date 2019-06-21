.. _flatxml2po:
.. _po2flatxml:

flatxml2po
**********

Converts flat XML (.xml) files to Gettext PO format, a simple monolingual and 
single-level XML.

.. _flatxml2po#usage:

Usage
=====

::

  flatxml2po [options] <xml> <po>
  po2flatxml [options] <po> <xml> [-t <base-xml>]

Where:

+-------------+--------------------------------------------------------+
| <xml>       | is a valid .xml file or directory of those files       |
+-------------+--------------------------------------------------------+
| <po>        | is a directory of PO or POT files                      |
+-------------+--------------------------------------------------------+
| <base-xml>  | is a template or the original file before translation. |
|             | required for roundtrips preserving extraneous data.    |
+-------------+--------------------------------------------------------+

Options (flatxml2po):

--version             show program's version number and exit
-h, --help            show this help message and exit
--manpage             output a manpage based on the help
--progress=PROGRESS   show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT
                      read from INPUT in xml format
-x EXCLUDE, --exclude=EXCLUDE
                      exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT
                      write to OUTPUT in po, pot formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-r ROOT, --root=ROOT  name of the XML root element (default: "root")
-v VALUE, --value=VALUE
                      name of the XML value element (default: "str")
-k KEY, --key=KEY     name of the XML key attribute (default: "key")
-n NS, --namespace=NS
                      XML namespace uri (default: None)


Options (po2flatxml):

--version             show program's version number and exit
-h, --help            show this help message and exit
--manpage             output a manpage based on the help
--progress=PROGRESS   show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT
                      read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE
                      exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT
                      write to OUTPUT in xml format
-t TEMPLATE, --template=TEMPLATE
                      read from TEMPLATE in xml format
-S, --timestamp       skip conversion if the output file has newer timestamp
-r ROOT, --root=ROOT  name of the XML root element (default: "root")
-v VALUE, --value=VALUE
                      name of the XML value element (default: "str")
-k KEY, --key=KEY     name of the XML key attribute (default: "key")
-n NS, --namespace=NS
                      XML namespace uri (default: None)
-w INDENT, --indent=INDENT
                      indent width in spaces, 0 for no indent (default: 2)

.. _flatxml2po#formats-supported:

Formats Supported
=================

Check :doc:`flat XML format </formats/flatxml>` document to see to which extent
the XML format is supported.

.. _flatxml2po#examples:

Examples
========

This example looks at roundtrip of flat XML translations as well as recovery of
existing translations.

First we need to create a set of POT files.::

  flatxml2po -P lang/en pot/

All .xml files found in the ``lang/en`` directory are converted to Gettext POT
files and placed in the ``pot`` directory.

If you are translating for the first time then you can skip the next step. If
you need to recover your existing translations then we do the following::

  flatxml2po -t lang/en lang/zu po-zu/

Using the English XML files found in ``lang/en`` and your existing Zulu
translation in ``lang/zu`` we create a set of PO files in ``po-zu``.  These
will now have your translations. Please be aware that in order for that to work
100% you need to have both English and Zulu at the same revision, if they are
not you will have to review all translations.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows::

  po2flatxml -t lang/en po-zu/ lang/zu

Your translations found in the Zulu PO directory, ``po-zu``, will be converted
to XML using the files in ``lang/en`` as templates and placing your new
translations in ``lang/zu``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.

.. _flatxml2po#limitations:

Limitations
===========

Indentation only supports spaces (specified with ``--indent`` greater than zero)
or flattened (no indentation, everything on a single line; specified with
``--indent`` set to zero). Tabs are not supported using po2flatxml.
