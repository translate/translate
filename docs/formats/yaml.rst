.. _yaml:


YAML
====

.. versionadded:: 2.0.0

:wp:`YAML` is a common format for web data interchange.


.. _yaml#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* Multiline strings:

  .. code-block:: yaml

      include_newlines: |
                  exactly as you see
                  will appear these three
                  lines of poetry


* Abbreviated lists:

  .. code-block:: yaml

      first-name: [Sun, Mon, Tue, Wed, Thu, Fri, Sat]


* Abbreviated dictionaries:

  .. code-block:: yaml

      martin: {name: Martin D'vloper, job: Developer, skill: Elite}


* Quoted strings:

  .. code-block:: yaml

      foo: "quote, double"
      bar: 'quote, single'


* Escaped quotes:

  .. code-block:: yaml

      foo: "Hello \"World\"."
      bar: 'Hello \'World\'.'


* Avoid escaping quotes:

  .. code-block:: yaml

      spamm: 'avoid escaping "double quote"'
      eggs: "avoid escaping 'single quote'"


* Newlines:

  .. code-block:: yaml

      foo: "Hello \n World."


* Booleans:

  .. code-block:: yaml

      foo: True
