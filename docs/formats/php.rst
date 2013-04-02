
.. _php:

PHP
***

Many `PHP <https://en.wikipedia.org/wiki/PHP>`_ programs make use of a
localisable string array.  The toolkit supports the full localisation of such
files with :doc:`/commands/php2po` and po2php.

.. _php#example:

Example
=======

The localisable string arrays appear like this:

.. code-block:: php

    <?php
    $string['name'] = 'value'

.. _php#conformance:

Conformance
===========

Our format support allows:

* PHP escaping (both for `single
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
  and `double
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
  quoted strings)
* Multiline entries
* PHP simple variable syntax

.. code-block:: php

    $variable = 'string';
    $another_variable = "another string";

* Various layouts of the id

  .. code-block:: php
  
      $string['name'];
      $string['name'] ;
      $string[name];
      $string[ 'name' ];

* PHP array syntax for localisation (since > 1.6.0)

  .. code-block:: php

      $lang = array(
         'name' => 'value',
         'name2' => 'value2',
      );

* PHP define syntax

.. code-block:: php

    define('item', 'string');
    define("another_item", "another string");

* Whitespace before end delimiter

  .. code-block:: php

      $string['name']     ;
      $string['name'] ;

.. _php#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* `herdoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc>`_
  and `nowdoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.nowdoc>`_
  are not managed
