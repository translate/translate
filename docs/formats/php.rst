
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

* `Single
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
  and `double
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
  quoted strings (both for keys and values)

  .. code-block:: html+php

      <?php
      $variable = 'string';
      $messages["language"] = 'Language';
      define('item', "another string");


* PHP simple variable syntax

  .. code-block:: html+php

      <?php
      $variable = 'string';
      $another_variable = "another string";


* PHP square bracket array syntax

  .. code-block:: html+php

      <?php
      $messages['language'] = 'Language';
      $messages['file'] = "File";
      $messages["window"] = 'Window';
      $messages["firewall"] = "Firewall";


* PHP array syntax

  .. versionadded:: 1.7.0

  .. code-block:: html+php

      <?php
      // Can be 'array', 'Array' or 'ARRAY'.
      $lang = array(
         'name' => 'value',
         'name2' => "value2",
         "key1" => 'value3',
         "key2" => "value4",
      );


* PHP define syntax

  .. versionadded:: 1.10.0

  .. code-block:: html+php

      <?php
      define('item', 'string');
      define('another_item', "another string");
      define("key", 'and another string');
      define("another_key", "yet another string");


* PHP `short array syntax <http://php.net/manual/en/language.types.array.php>`_

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = [
          "foo" => "bar",
          "bar" => "foo",
      ];


* `Heredoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc>`_

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = <<<EOT
      bar
      EOT;


* `Nowdoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.nowdoc>`_

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = <<<'EOD'
      Example of string
      spanning multiple lines
      using nowdoc syntax.
      EOD;


* Escape sequences (both for `single
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
  and `double
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
  quoted strings)

  .. code-block:: html+php

      <?php
      $variable = 'He said: "I\'ll be back"';
      $another_variable = "First line \n second line";
      $key = "\tIndented string";


* Multiline entries

  .. code-block:: html+php

      <?php
      $lang = array(
         'name' => 'value',
         'info' => 'Some hosts disable automated mail sending
	        on their servers. In this case the following features
	        cannot be implemented.',
         'name2' => 'value2',
      );


* Various layouts of the id

  .. code-block:: html+php

      <?php
      $string['name'] = 'string';
      $string[name] = 'string';
      $string[ 'name' ] = 'string';


* Comments

  .. versionchanged:: 1.10.0

  .. code-block:: html+php

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

  .. code-block:: html+php

      <?php
      $variable = 'string'     ;

      $string['name'] = 'string'     ;

      $lang = array(
         'name' => 'value'           ,
      );

      define('item', 'string'    );


* Nested arrays with any number of nesting levels

  .. versionadded:: 1.11.0

  .. code-block:: html+php

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
            'Converted' => 'Converted',
            'LAST' => 'last',
         ),
      );

* Whitespace in the array declaration

  .. versionadded:: 1.11.0

  .. code-block:: html+php

      <?php
      $variable = array    (
         "one" => "this",
         "two" => "that",
      );

* Blank array declaration, then square bracket syntax to fill that array

  .. versionadded:: 1.12.0

  .. code-block:: html+php

      <?php
      global $messages;
      $messages = array();

      $messages['language'] = 'Language';
      $messages['file'] = 'File';


* Unnamed arrays:

  .. versionadded:: 2.2.0

  .. code-block:: html+php

      <?php
      return array(
         "one" => "this",
      );


* Array entries without ending comma:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array(
         "one" => "this",
         "two" => "that"
      );


* Array entries with space before comma:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array(
         "one" => "this",
         "two" => "that"   ,
      );


* Nested arrays declared on the next line:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array(
          "one" =>
              array(
                  "two" => "dous",
              ),
      );


* Nested arrays with blank entries:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array(
          "one" => array(
                  "" => "",
                  "two" => "dous",
              ),
      );


* Strings with slash asterisk on them:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array(
          'foo' => 'Other value /* continued',
       );


* Array entries with value on next line:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array(
          'foo' =>
              'bar',
       );


* Array defined in a single line:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $variable = array( 'item1' => 'value1', 'item2' => 'value2', 'item3' => 'value3' );


* Keyless arrays:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $days = array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');


* Nested arrays without key for a nested array:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $lang = array(array("key" => "value"));


* Concatenation of strings and variables:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      $messages['welcome'] = 'Welcome ' . $name . '!';
      $messages['greeting'] = 'Hi ' . $name;


* Assignment in the same line a multiline comment ends:

  .. versionadded:: 2.3.0

  .. code-block:: html+php

      <?php
      /*
         Multi-line
         comment
      */ $messages['help'] = 'Help';


* Keyless arrays assigned to another array:

  .. code-block:: html+php

      <?php
      $messages['days_short'] = array('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');


* Laravel plurals are supported in the ``LaravelPHPFile`` class:

  .. code-block:: html+php

        <?php
        return [
            'apples' => 'There is one apple|There are many apples',
        ];


.. _php#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* There are currently no known limitations.
