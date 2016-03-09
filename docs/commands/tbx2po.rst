
.. _tbx2po:

tbx2po
******

Convert between :doc:`TermBase eXchange (.tbx) glossary </formats/tbx>` format
and :doc:`Gettext PO </formats/po>` format.

.. _tbx2po#usage:

Usage
=====

::

  tbx2po <tbx> <po>

Where:

+--------+------------------------+
| <tbx>  | is a TBX file          |
+--------+------------------------+
| <po>   | is the target PO file  |
+--------+------------------------+

Options (tbx2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT    read from INPUT in csv format
-x EXCLUDE, --exclude=EXCLUDE    exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT   write to OUTPUT in tbx format
-S, --timestamp      skip conversion if the output file has newer timestamp


.. _tbx2po#examples:

Examples
========

These examples demonstrate the use of tbx2po::

  tbx2po terms.tbx terms.po

to simply convert *terms.tbx* to *terms.po*.

To convert a directory recursively to another directory with the same structure
of files::

  tbx2po tbx-dir po-target-dir

This will convert TBX files in *tbx-dir* to PO files placed in
*po-target-dir*.



.. _tbx2po#notes:

Notes
=====

For conformance to the standards and to see which features are implemented, see
:doc:`/formats/po` and :doc:`/formats/tbx`.
