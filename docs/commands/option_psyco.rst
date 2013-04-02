
.. _option_psyco:

--psyco=MODE
************

Psyco is an optimiser for Python programs.  It takes the sections that are run
often or that could benefit from being compiled and compiles them into machine
language.  This machine code is executed instead of the Python code.

If you didn't understand any of that then simply understand that it makes you
program run faster if it is installed.

By default it is switched on, so you can safely ignore this option and benefit
from psyco optimisations anyway.

.. note:: psyco only works on i386 architectures.

To install psyco, you can look for it in your distribution's packages, or
obtain it here: http://psyco.sourceforge.net/

.. _option_psyco#none:

none
====

Switch psyco optimisation off.

.. _option_psyco#full_default:

full (default)
==============

This is the default option, even if no :opt:`--psyco` command line options is
specified. It will try to optimise everything, so potentially it might consume
more memory.

.. _option_psyco#profile:

profile
=======

This tries to selectively compile certain program parts, and therefore should
consume less memory.
