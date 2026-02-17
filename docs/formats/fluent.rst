Fluent
======

`Fluent <https://projectfluent.org/>`_ is a localization system developed by
Mozilla for natural-sounding translations. It is a monolingual format where
each language has its own set of ``.ftl`` files.

Example:

.. code-block:: none

   # Simple message
   hello = Hello World!

   # Message with a variable
   greeting = Hello { $name }!

   # Message with attributes
   login-input =
       .placeholder = email@example.com
       .aria-label = Login input
       .title = Login

Fluent is used by Firefox, Anki, and other projects. See the
`Fluent Syntax Guide <https://projectfluent.org/fluent/guide/>`_ for more
details on the format.

Convert Fluent files to PO format using :doc:`/commands/fluent2po`.
