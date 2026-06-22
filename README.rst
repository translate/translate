Translate Toolkit
-----------------

.. image:: https://img.shields.io/pypi/v/translate-toolkit.svg
    :alt: Released version
    :target: https://pypi.org/project/translate-toolkit/

.. image:: https://readthedocs.org/projects/translate-toolkit/badge/
    :target: https://docs.translatehouse.org/projects/translate-toolkit/en/latest/

.. image:: https://img.shields.io/pypi/pyversions/translate-toolkit.svg
    :alt: Supported Python versions
    :target: https://pypi.org/project/translate-toolkit/

.. image:: https://img.shields.io/pypi/l/translate-toolkit.svg
    :target: https://pypi.org/project/translate-toolkit/
    :alt: License

The Translate Toolkit is an essential toolkit for localization engineers. It
contains tools and documentation to help localizers convert, count, manipulate,
review and debug localization files with less repetitive work.

The software includes programs to convert localization formats to the common PO
and XLIFF formats. There are also programs to check and manage PO and XLIFF
files. The Toolkit is part of the Translate project, hosted at
<https://github.com/translate/translate>.

At its core the software contains Python classes for handling localization
storage formats such as DTD, properties, OpenOffice.org GSI/SDF, CSV, MO,
Qt .ts, TMX, TBX, WordFast txt, Gettext .mo, Windows RC, PO and XLIFF. It also
provides scripts to convert between these formats.


Features
--------

* Format converters for localization, translation and software formats, so
  translators can work in standard translation formats.
* Quality assurance tools for pattern searches, language-aware checks,
  terminology extraction and other review tasks.
* Python APIs that can be expanded with new formats, project types,
  localization tests and language modules.


Important Links
---------------

* `Latest release downloads <https://github.com/translate/translate/releases>`_
* `Documentation
  <https://docs.translatehouse.org/projects/translate-toolkit/en/latest/>`_,
  also use ``--help`` with any of the commands.
* The Translate Toolkit is released under the `GPL
  <https://github.com/translate/translate/blob/master/COPYING>`_ with
  `contributions from many people
  <https://github.com/translate/translate/blob/master/CREDITS>`_.
* `Reporting issues <https://github.com/translate/translate/issues>`_
* `Reporting security vulnerabilities
  <https://github.com/translate/translate/security/advisories/new>`_
* `Installation
  <https://docs.translatehouse.org/projects/translate-toolkit/en/latest/installation.html>`_
* `Release notes
  <https://docs.translatehouse.org/projects/translate-toolkit/en/latest/releases/index.html>`_
* `Source code <https://github.com/translate/translate>`_


Project goals
-------------

The vision of the Translate Project is to be a meta project for localizers
built on the premise that your language deserves to be a project on its own
right not a poor cousin of the main project.

Most projects are inattentive to the needs and difficulties experienced by
localizers. To that end the aim is to work towards creating tools and
documentation that allows localizers to focus on what they do best: translating
software.

Requirements
------------

The recommended installation is using ``uv`` or ``pip`` in a virtual
environment::

    uv pip install translate-toolkit

or::

    pip install translate-toolkit

You can also download a stable released version from
<https://github.com/translate/translate/releases> and install it manually.

The Toolkit requires Python 3.11 or newer. The required runtime dependencies
are ``lxml>=6.1.0,<7.0`` and ``unicode-segmentation-rs>=0.2.0,<0.3``.

There are several optional dependencies for format-specific features and speed
ups. They can be requested as extras during installation::

    # Install all optional dependencies
    pip install translate-toolkit[all]

    # Install selected optional dependencies
    pip install translate-toolkit[markdown,ini,ical,subtitles,yaml,spellcheck]

Available extras include ``chardet``, ``fluent``, ``ical``, ``ini``,
``levenshtein``, ``markdown``, ``php``, ``rc``, ``spellcheck``, ``subtitles``,
``toml`` and ``yaml``. Please check ``pyproject.toml`` for the current
dependency versions.

Program overview
----------------

Use ``--help`` to find the syntax and options for all programs.

.. note::

   This is a selection of the most commonly used tools. For the complete list
   of converters and tools, see the `command documentation
   <https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/index.html>`_.

* Converters::

        oo2po    - convert between OpenOffice.org GSI files and PO
        oo2xliff - convert between OpenOffice.org GSI files and XLIFF
        moz2po   - convert between Mozilla files and PO
        csv2po   - convert PO format to CSV for editing in a spreadsheet program
        php2po   - PHP localisable string arrays converter.
        ts2po    - convert Qt Linguist (.ts) files to PO
        txt2po   - convert simple text files to PO
        html2po  - convert HTML to PO (beta)
        md2po    - convert Markdown to PO
        xliff2po - XLIFF (XML Localisation Interchange File Format) converter
        prop2po  - convert Java .properties files to PO
        po2wordfast - Wordfast Translation Memory converter
        po2tmx   - TMX (Translation Memory Exchange) converter
        pot2po   - PO file initialiser
        csv2tbx  - Create TBX (TermBase eXchange) files from Comma Separated
                   Value (CSV) files
        ini2po   - convert .ini files to PO
        ical2po  - Convert iCalendar files (*.ics) to PO
        sub2po   - Convert many subtitle files to PO
        rc2po    - convert Windows Resource .rc files to PO
        resx2po  - convert .Net Resource (.resx) files to PO

* Tools (Quality Assurance)::

        pofilter - run any of the 40+ checks on your PO files
        pomerge  - merge corrected translations from pofilter back into
                   your existing PO files.
        poconflicts - identify conflicting use of terms
        porestructure - restructures po files according to poconflict directives
        pogrep   - find words in PO files

* Tools (Other)::

        pocompile - create a Gettext MO files from PO or XLIFF files
        pocount   - count translatable file formats (PO, XLIFF)
        podebug   - Create comment in your PO files' msgstr which can
                    then be used to quickly track down mistranslations
                    as the comments appear in the application.
        posegment - Break a PO or XLIFF files into sentence segments,
                    useful for creating a segmented translation memory.
        poswap    - uses a translation of another language that you
                    would rather use than English as source language
        poterminology - analyse PO or POT files to build a list of
                        frequently occurring words and phrases
