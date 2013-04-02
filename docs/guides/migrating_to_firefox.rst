
.. _migrating_to_firefox:
.. _migrating_mozilla_translations_to_firefox:

Migrating Mozilla Translations to Firefox
*****************************************

This quickstart shows you how to migrate your existing translations of the
Mozilla suite to the Firefox web-browser.  The same instructions can be used to
migrate Thunderbird§.

Note: This guide assumes that you are or will be using PO files.

FIXME this page needs to be rewriten now that Mozilla is using CSV.  The steps
are more or less the same.  Look at :doc:`creating_mozilla_pot_files` which
talks about creating POT file from CVS. Then the process is mostly the same
except swap any reference to XPI to be the translations in Mozilla CVS.

.. _migrating_to_firefox#quick_start:

Quick Start
===========

#. :doc:`moz2po </commands/moz2po>` -t mozilla-1.7.3-langenus.xpi langXXYY.xpi xxYY-1.7.3
#. :doc:`moz2po </commands/moz2po>` -P firefox-1.0-en-US.xpi templates-ff-1.0
#. :doc:`/commands/pomigrate2` xxYY-1.7.3 xxYY-ff-1.0 templates-ff-1.0

.. _migrating_to_firefox#detailed_description:

Detailed Description
====================

.. _migrating_to_firefox#make_sure_your_mozilla_is_in_po_format:

Make sure your Mozilla is in PO format
--------------------------------------

If you are not currently using PO files to do your translations then you can
migrate an existing XPI to PO format.

.. _migrating_to_firefox#get_the_correct_en-us_xpi:

Get the correct en-US xpi
^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly make sure you have an XPI for your language then download a Mozilla
English (US) XPI for the same release::

  ftp://ftp.mozilla.org/pub/mozilla.org/mozilla/releases/mozilla1.7.3/linux-xpi/langenus.xpi

Change 1.7.3 to the release that you need.  Note: Linux and Windows
langenus.xpi are the same so no need to worry about that.

.. _migrating_to_firefox#create_mozilla_po_files_for_your_language:

Create Mozilla PO files for your language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now create the Mozilla PO files for your language using your existing XPI and
the en-US XPI.

::

    moz2po -t mozilla-1.7.3-langenus.xpi langXXYY.xpi xxYY-1.7.3

Where:

* mozilla-1.7.3-langenus.xpi is the langenus.xpi downloaded above
* langXXYY.xpi is your existing translated XPI with the same version and the
  en-US one downloaded.
* xxYY-1.7.3 is an output directory for the PO files

.. _migrating_to_firefox#create_firefox_pot_files:

Create Firefox POT files
------------------------

You need to create a set of Firefox PO Template files that you will use as
templates when you migrate your Mozilla translations.  Template files are
simply blank PO files.

.. _migrating_to_firefox#getting_the_en-us.xpi:

Getting the en-US.xpi
^^^^^^^^^^^^^^^^^^^^^

Rumour has it that the en-US XPI files for Firefox are different for Windows
and Linux.

* Linux -- Firefox 1.0:
  ftp://ftp.mozilla.org/pub/mozilla.org/firefox/releases/1.0/linux-i686/xpi/en-US.xpi
* Windows -- Firefox 1.0:
  ftp://ftp.mozilla.org/pub/mozilla.org/firefox/releases/1.0/win32/xpi/en-US.xpi

.. _migrating_to_firefox#create_the_pot_files:

Create the POT files
^^^^^^^^^^^^^^^^^^^^

::

    moz2po -P firefox-1.0-en-US.xpi templates-ff-1.0

Where:

* *-P* specifies that you want to create POT files instead of PO files
* *firefox-1.0-en-US.xpi* is an en-US.xpi for Firefox downloaded earlier
* *templates-ff-1.0* is the new directory that will contain the POT files

.. _migrating_to_firefox#migrate_the_mozilla_po_files_to_firefox:

Migrate the Mozilla PO files to Firefox
---------------------------------------

We will now take the existing Mozilla PO files and migrate them to Firefox.
Note that this tool only works on Linux (or an operating environment with bash
and the gettext tools).  If you need help ask at
`translate-devel@lists.sourceforge.net
<mailto:translate-devel@lists.sourceforge.net>`_.

::

  pomigrate2 xxYY-1.7.3 xxYY-ff-1.0 templates-ff-1.0

Where:

* *xxYY-1.7.3* contains your Mozilla PO files
* *xxYY-ff-1.0* will contain your new Firefox files
* *templates-ff-1.0* contains the Firefox template files

.. _migrating_to_firefox#how_does_it_do_the_migration:

How does it do the migration?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Things that are fully automated scare most people and justifiably so!  The
migration will do the following:

#. For each Firefox PO Template file

   * If there is one in your Mozilla folder

     * If there is only one file with that name

       * copy it to the correct Firefox PO location

     * Else

       * combine all the copies you find and then copy them to the Firefox PO
         location

   * Else

     * Initialise a blank PO file

#. Create a compendium file of all Mozilla PO files
#. Update all Firefox PO files optionally using the compendium

The result is that all Firefox files are at least initialised.  Many of them
are populated with conflicting entries clearly highlighted and ready for you to
fix.

.. _migrating_to_firefox#begin_translating:

Begin translating
-----------------

Your PO files are ready.  Begin translating with any of your usual PO editing
tools.
