
.. _pages/toolkit/php#php:

PHP
***

Many `PHP <https://en.wikipedia.org/wiki/PHP>`_ programs make use of a localisable string array.  The toolkit supports the full localisation of such files with :doc:`/commands/php2po` and po2php.

.. _pages/toolkit/php#example:

Example
=======

The localisable string arrays appear like this:

::

    <?php
    $string['name'] = 'value'

.. _pages/toolkit/php#conformance:

Conformance
===========

Our format support allows:

* PHP escaping (both for `single <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_ and `double <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_ quoted strings)
* Multiline entries
* Various layouts of the id::

    $string['name']
    $string[name]
    $string[ 'name' ]

* PHP array syntax for localisation (since > 1.6.0)::

    $lang = array(
       'name' => 'value',
       'name2' => 'value2',
    );

.. _pages/toolkit/php#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* `herdoc <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc>`_ and `nowdoc <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.nowdoc>`_ are not managed
