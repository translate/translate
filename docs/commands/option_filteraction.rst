
.. _pages/toolkit/filteraction_action#--filteraction=action:

--filteraction=ACTION
*********************

.. _pages/toolkit/filteraction_action#none_default:

none (default)
==============

Take no action.  Messages from failing test will appear in the output file

.. _pages/toolkit/filteraction_action#warn:

warn
====

Print a warning but otherwise include the message in the output file.

.. _pages/toolkit/filteraction_action#exclude-serious:

exclude-serious
===============

Only exclude errors that are listed as serious by the convertor.  All other are included.

.. _pages/toolkit/filteraction_action#exclude-all:

exclude-all
===========

Exclude any message that fails a test.