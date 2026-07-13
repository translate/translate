.. _formats:


Translation Related File Formats
********************************

These are the different storage formats for translations and files associated
with translations that are supported by the toolkit. See also
:doc:`conformance` for standards conformance.

The Translate Toolkit implements a set of :doc:`classes <base_classes>` for
handling translation files which allows for a uniform API which covers other
issues such as :doc:`quoting and escaping <quoting_and_escaping>` of text.

.. _formats#primary_translation_formats:

Primary translation formats
===========================

.. toctree::
   :maxdepth: 1

   xliff
   Gettext PO <po>

.. _formats#other_translation_formats:

Other translation formats
=========================

.. toctree::
   :maxdepth: 1
   :hidden:

   csv
   ini
   properties
   dtd
   gsi
   php
   ts
   rc
   strings
   stringsdict
   flex
   catkeys
   android
   resx
   mozilla_lang
   wxl

* :doc:`csv`
* :doc:`ini` (including Inno Setup .isl dialect)
* Java :doc:`properties` (also Mozilla derived properties files)
* Mozilla :doc:`dtd`
* OpenOffice.org :doc:`gsi` (Also called SDF)
* :doc:`php` translation arrays
* Qt Linguist :doc:`ts` (both 1.0 and 1.1 supported, 1.0 has a converter)
* Symbian localization files
* Windows :doc:`rc` files
* Mac OSX :doc:`strings` files (also used on the iPhone) (from version 1.8)
* Apple :doc:`stringsdict` plural files (from version 3.14)
* Adobe :doc:`flex` files (from version 1.8)
* Haiku :doc:`catkeys` (from version 1.8)
* :doc:`android` (supports storage, not conversion)
* :doc:`resx` .NET Resource files (.resx)
* Mozilla :doc:`.lang <mozilla_lang>` files
* WiX :doc:`wxl` localization files (.wxl)

.. _formats#translation_memory_formats:

Translation Memory formats
==========================

.. toctree::
   :maxdepth: 1
   :hidden:

   tmx
   wordfast

* :doc:`tmx`
* :doc:`wordfast`: TM
* Trados: .txt TM (from v1.9.0 -- read only)

.. _formats#glossary_formats:

Glossary formats
================

.. toctree::
   :maxdepth: 1
   :hidden:

   omegat_glossary
   qt_phrase_book
   tbx
   utx

* :doc:`omegat_glossary` (from v1.5.1)
* :doc:`qt_phrase_book`
* :doc:`tbx`
* :doc:`utx` (from v1.9.0)

.. _formats#formats_of_translatable_documents:

Formats of translatable documents
=================================

.. toctree::
   :maxdepth: 1
   :hidden:

   asciidoc
   flatxml
   fluent
   html
   ical
   json
   md
   mdx
   odf
   subtitles
   text
   toml
   wiki
   yaml

* :doc:`asciidoc`
* :doc:`flatxml` (single-level XML)
* :doc:`fluent` (used by Firefox, Anki, etc.)
* :doc:`html`
* :doc:`ical`
* :doc:`json`
* :doc:`md`
* :doc:`mdx`
* :wp:`OpenDocument` -- all ODF file types
* :doc:`subtitles` -- various formats (v1.4)
* :doc:`Text <text>` -- plain text with blocks separated by whitespace
* :doc:`toml`
* :doc:`Wiki <wiki>` -- :wp:`DokuWiki` and :wp:`MediaWiki` supported
* :doc:`yaml`

.. _formats#machine_readable_formats:

Machine readable formats
========================

.. toctree::
   :maxdepth: 1
   :hidden:

   mo
   qm

* Gettext :doc:`mo`
* Qt :doc:`qm` (read-only)

.. _formats#in_development:

In development
==============

.. _formats#unsupported_formats:

Unsupported formats
===================

Formats that we would like to support but don't currently support:

.. toctree::
   :maxdepth: 1
   :hidden:

   wml

* Wordfast:

  * `Glossary
    <https://www.wordfast.net/index.php?lang=engb&whichpage=specifications#glo>`_
    tab-delimited "source,target,comment" i.e. like OmegaT but unsure if any
    extension is required.

* Apple:

  * `AppleGlot <ftp://ftp.apple.com/developer/tool_chest/localization_tools/appleglot/appleglot_3.2_usersguide.pdf>`_
  * .plist -- see :issue:`633` and `plistlib
    <https://docs.python.org/2/library/plistlib.html>`_ for Python

* Adobe:

  * FrameMaker's Maker Interchange Format -- `MIF
    <https://help.adobe.com/en_US/FrameMaker/8.0/mif_reference.pdf>`_ (See also
    `python-gendoc <https://lino.sourceforge.net/src/100.html>`_, and `Perl MIF
    module
    <https://search.cpan.org/~rst/FrameMaker-MifTree-0.075/lib/FrameMaker/MifTree.pm>`_)
  * FrameMaker's `Maker Markup Language
    <https://www.adobe.com/support/downloads/detail.jsp?ftpID=137>`_ (MML)

* Microsoft

  * Word, Excel, etc (probably through usage of OpenOffice.org)
  * :wp:`OOXML` (at least at the text level we don't have to deal with much of
    the mess inside OOXML).  See also: `Open XML SDK v1
    <https://go.microsoft.com/fwlink/?LinkId=120908>`_
  * :wp:`Rich Text Format <Rich_Text_Format>` (RTF) see also `pyrtf-ng
    <https://code.google.com/p/pyrtf-ng/>`_
  * :wp:`Open XML Paper Specification <Open_XML_Paper_Specification>`

* XML related

  * Generic XML
  * :wp:`DocBook` (can be handled by KDE's :man:`xml2pot`)
  * `SVG <https://www.w3.org/TR/SVG/>`_

* :wp:`DITA <Darwin_Information_Typing_Architecture>`
* :wp:`PDF <Portable_Document_Format>` see `spec
  <https://www.adobe.com/devnet/pdf/pdf_reference.html>`_, `PDFedit
  <http://pdfedit.cz/en/index.html>`_
* :wp:`LaTeX` -- see `plasTeX
  <https://plastex.sourceforge.net/plastex/index.html>`_, a Python framework for
  processing LaTeX documents
* `unoconv <https://github.com/unoconv/unoconv>`_ -- Python bindings to
  OpenOffice.org UNO which could allow manipulation of all formats understood
  by OpenOffice.org.
* Trados:

  * TTX (`RWS compatibility information
    <https://www.trados.com/product/studio/FAQ/is-Trados-Studio-2024-compatible-with-previous-versions-of-Studio/>`_,
    `format discussion
    <https://timsfoster.wordpress.com/2005/07/05/beds-mattresses-and-open-standards/>`_)
  * MultiTerm XML (`MultiTerm Convert
    <https://www.trados.com/training/multiterm-for-translators-and-project-managers/>`_)
  * .tmw
  * .txt (You can interchange using TMX) `Format explanation
    <https://translate.google.com/translate?js=y&prev=_t&hl=en&ie=UTF-8&layout=1&eotf=1&u=http%3A%2F%2Fwww.diemohrs.de%2Ftipps2_neu.html&sl=auto&tl=en>`_.

* Tcl: .msg files.  `Good documentation
  <https://www.google.com/codesearch?hl=en&q=show:XvsRBDCljVk:M2kzUbm70Ts:D5EHICz0aaQ&sa=N&ct=rd&cs_p=https://www.scilab.org/download/4.0/scilab-4.0-src.tar.gz&cs_f=scilab-4.0/tcl/scipadsources/msg_files/AddingTranslations.txt>`_
* Installers:

  * NSIS installer: `Existing C++ implementation
    <https://web.archive.org/web/20090215073614/https://trac.vidalia-project.net/browser/vidalia/trunk/src/tools>`_
  * WiX -- MSI (Microsoft Installer) creator.  `Localization instructions
    <https://docs.firegiant.com/wix3/howtos/ui_and_localization/make_installer_localizable/>`_, `more notes on
    localisation
    <https://www.mail-archive.com/wix-users@lists.sourceforge.net/msg15489.html>`_.
    This is a custom XML format, another one!

* catgets/`gencat
  <https://pubs.opengroup.org/onlinepubs/009695399/utilities/gencat.html>`_:
  precedes gettext, looking in man packages is the best information I could
  find.  Also `LSB requires it
  <https://www.linuxbase.org/navigator/browse/cmd_single.php?cmd=list-by-name&Cname=gencat>`_.
  There is some info about the source (msgfile) format on `GNU website
  <https://www.gnu.org/software/libc/manual/html_node/The-message-catalog-files.html#The-message-catalog-files>`_
* :doc:`wml`
* `GlossML <https://www.maxprograms.com/glossml/glossml.pdf>`_
* Deja Vu External View: `Instructions sent to a translator
  <https://web.archive.org/web/20110815083944/https://dvx.atril.com/docs/DVX/InstructionsExternalView.pdf>`_, `Description
  of external view options and process
  <https://web.archive.org/web/20160321052547/https://simmer-lossner.com/lib/presentations/External_Proofreading_for_DVX.pdf>`_

.. _formats#unlikely_to_be_supported:

Unlikely to be supported
========================

These formats are either: too difficult to implement, undocumented, can be
processed using some intermediate format or used by too few people to justify
the effort.  Or some combination or these issues.

.. Mentioned but we want them at the end of the TOC or to move them to developer docs

.. toctree::
   :maxdepth: 1
   :hidden:

   conformance
   base_classes
   quoting_and_escaping
