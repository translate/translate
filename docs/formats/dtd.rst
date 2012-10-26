
.. _pages/toolkit/dtd#mozilla_dtd_format:

Mozilla DTD format
******************

Mozilla makes use of a .dtd file to store many of its translatable elements, the :doc:`moz2po </commands/moz2po>` converter can handle these.

.. _pages/toolkit/dtd#references:

References
==========

* `XML specification <http://www.w3.org/TR/REC-xml/>`_

.. _pages/toolkit/dtd#features:

Features
========

* Comments - these are handled correctly and integrated with the unit
* Accelerators - if a unit has an associated access key entry then these are combined into a single unit
* Translator directive - all LOCALIZATION NOTE items such as DONT_TRANSLATE are handled and such items are discarded

.. _pages/toolkit/dtd#issues:

Issues
======

* We don't escape character entities like ``&lt;``, ``&#38;`` - this doesn't
  break anything but it would be nicer to see © rather than &copy;
