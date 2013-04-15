
.. _php:

PHP
***

Many :wp:`PHP` programs make use of a localisable string array.  The toolkit
supports the full localisation of such files with :doc:`/commands/php2po` and
po2php.


.. _php#conformance:

Conformance
===========

Our format support allows:

* PHP simple variable syntax

  .. code-block:: php

      <?php
      $variable = 'string';
      $another_variable = "another string";


* PHP square bracket array syntax

  .. code-block:: php

      <?php
      $messages['language'] = 'Language';
      $messages['file'] = "File";


* PHP array syntax

  .. versionadded:: 1.7.0

  .. code-block:: php

      <?php
      // Can be 'array', 'Array' or 'ARRAY'.
      $lang = array(
         'name' => 'value',
         'name2' => "value2",
      );


* PHP define syntax

  .. versionadded:: 1.10.0

  .. code-block:: php

      <?php
      define('item', 'string');
      define("another_item", "another string");


* PHP escaping (both for `single
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
  and `double
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
  quoted strings)

  .. code-block:: php

      <?php
      $variable = 'string';
      $another_variable = "another string";


* Multiline entries

  .. code-block:: php

      <?php
      $lang = array(
         'name' => 'value',
         'info' => 'Some hosts disable automated mail sending
	        on their servers. In this case the following features
	        cannot be implemented.',
         'name2' => 'value2',
      );


* Various layouts of the id

  .. code-block:: php

      <?php
      $string['name'] = 'string';
      $string[name] = 'string';
      $string[ 'name' ] = 'string';


* Comments

  .. versionchanged:: 1.10.0

  .. code-block:: php

      <?php
      # Hash one-line comment
      $messages['language'] = 'Language';

      // Double slash one-line comment
      $messages['file'] = 'File';

      /*
         Multi-line
         comment
      */
      $messages['help'] = 'Help';


* Whitespace before end delimiter

  .. versionadded:: 1.10.0

  .. code-block:: php

      <?php
      $variable = 'string'     ;

      $string['name'] = 'string'     ;

      $lang = array(
         'name' => 'value'           ,
      );

      define('item', 'string'    );


.. _php#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* Nested arrays

  .. code-block:: php

      <?php
      $lang = array(
         'name' => 'value',
         'datetime' => array(
            'TODAY' => 'Today',
            'YESTERDAY'	=> 'Yesterday',
            'AGO' => array(
                0 => 'less than a minute ago',
                2 => '%d minutes ago',
                60 => '1 hour ago',
         ),
      );


* `Heredoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc>`_
* `Nowdoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.nowdoc>`_

