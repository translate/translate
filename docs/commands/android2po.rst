
.. _android2po:

android2po
**********

Converts Android resource files to Gettext PO format.

.. _android2po#usage:

Usage
=====

::

  android2po [options] <android> <po>

Where:

+------------+--------------------------------------------------------------+
| <android>  | is a valid Android resource file or directory of those files |
+------------+--------------------------------------------------------------+
| <po>       | is a directory of PO or POT files                            |
+------------+--------------------------------------------------------------+

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --manpage             output a manpage based on the help
  --progress=PROGRESS   show progress as: dots, none, bar, names, verbose
  --errorlevel=ERRORLEVEL
                        show errorlevel as: none, message, exception,
                        traceback
  -i INPUT, --input=INPUT
                        read from INPUT in xml format
  -x EXCLUDE, --exclude=EXCLUDE
                        exclude names matching EXCLUDE from input paths
  -o OUTPUT, --output=OUTPUT
                        write to OUTPUT in po, pot formats
  -t TEMPLATE, --template=TEMPLATE
                        read from TEMPLATE in xml format
  -S, --timestamp       skip conversion if the output file has newer timestamp
  --duplicates=DUPLICATESTYLE
                        what to do with duplicate strings (identical source
                        text): merge, msgctxt (default: 'msgctxt')

.. _android2po#examples:

Examples
========

These examples demonstrate the use of android2po:

  android2po -i strings-en.xml -o en.po

to simply convert *strings-en.xml* to *en.po*.

To convert a source and target Android resources files into a PO file:

  android2po -t strings-en.xml -i strings-ca.xml -o ca.po

*strings-en.xml* contains the template resource and *strings-ca.xml* the localised resource strings.
