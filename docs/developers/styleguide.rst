.. _styleguide:

Translate Styleguide
====================

The Translate styleguide is the styleguide for all Translate projects,
including Translate Toolkit, Pootle, Virtaal and others.  Patches are required
to follow these guidelines.


pre-commit hooks
----------------

The Translate styleguide can be checked by `pre-commit`_. The Translate toolkit
repository repository contains configuration for it to verify the committed
files are sane. After installing it (it is already included in the
:file:`pyproject.toml`) turn it on by running ``pre-commit install`` in
Translate toolkit checkout. This way all your changes will be automatically
checked.

You can also trigger check manually, to check all files run:

.. code-block:: sh

    pre-commit run --all

.. _pre-commit: https://pre-commit.com/

.. _styleguide-python:

Python
------

The Python code follows :pep:`8` and is linted and formatted using `ruff
<https://docs.astral.sh/ruff/>`_. It is included the above-mentioned pre-commit
hooks.

Any new code should utilize :pep:`484` type hints. We're not checking this in
our CI yet as existing code does not yet include them.

.. _styleguide-docs:

Documentation
-------------

We use Sphinx_ to generate our API and user documentation. Read the
`reStructuredText primer`_ and `Sphinx documentation`_ as needed.


Special roles
^^^^^^^^^^^^^

We introduce a number of special roles for documentation:

* ``:issue:`` -- links to a toolkit issue Github.

  * ``:issue:`234``` gives: :issue:`234`
  * ``:issue:`broken <234>``` gives: :issue:`broken <234>`

* ``:opt:`` -- mark command options and command values.

  * ``:opt:`-P``` gives :opt:`-P`
  * ``:opt:`--progress=dots``` gives :opt:`--progress=dots`
  * ``:opt:`dots``` gives :opt:`dots`

* ``:man:`` -- link to a Linux man page.

  * ``:man:`msgfmt``` gives :man:`msgfmt`


Code and command line highlighting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All code examples and format snippets should be highlighted to make them easier
to read.  By default Sphinx uses Python highlighting of code snippets (but it
doesn't always work).  You will want to change that in these situations:

.. highlight:: rest

* The examples are not Python e.g. talking about INI file parsing.  In which
  case set the file level highlighting using::

     .. highlight:: ini

* There are multiple different code examples in the document, then use::

    .. code-block:: ruby

  before each code block.

* Python code highlighting isn't working, then force Python highlighting using::

    .. code-block:: python

.. note:: Generally we prefer explicit markup as this makes it easier for those
   following you to know what you intended.  So use ``.. code-block:: python``
   even though in some cases this is not required.

With *command line examples*, to improve readability use::

    .. code-block:: console

Add ``$`` command prompt markers and ``#`` comments as required, as shown in
this example:

.. code-block:: console

   $ cd docs
   $ make html  # Build all Sphinx documentation
   $ make linkcheck  # Report broken links


.. highlight:: python


User documentation
------------------

This is documentation found in ``docs/`` and that is published on Read the
Docs. The target is the end user so our primary objective is to make accessible,
readable and beautiful documents for them.


Docstrings
----------

All docstrings should follow :pep:`257` (Docstring Conventions) and be formatted
with reStructuredText as understood by Sphinx.

Basic formatting:
  Depending on the number of lines in the docstring, they are laid out
  differently.  If it's just one line, the closing triple quote is on the same
  line as the opening, otherwise the text is on the same line as the opening
  quote and the triple quote that closes the string on its own line:

  .. code-block:: python

    def foo():
        """This is a simple docstring."""


    def bar():
        """This is a longer docstring with so much information in there
        that it spans three lines.  In this case the closing triple quote
        is on its own line.
        """

Key guidelines from :pep:`257`:

- A docstring should have a brief one-line summary, ending with a period. Use
  the imperative mood: ``Do this``, ``Return that`` rather than ``Does ...``,
  ``Returns ...``.
- If there are more details there should be a blank line between the one-line
  summary and the rest of the text.  Use paragraphs and formatting as needed.
- Use proper capitalisation and punctuation.
- All public modules, functions, classes, and methods should have docstrings.

Type annotations and parameters:
  **Use type annotations instead of documenting parameters in docstrings.**

  For new code, always add :pep:`484` type hints to function signatures. This
  makes parameter types and return types explicit and machine-readable:

  .. code-block:: python

    def addunit(self, unit: TranslationUnit) -> None:
        """Append the given unit to the object's list of units.

        This method should always be used rather than trying to modify the
        list manually.
        """
        self.units.append(unit)

  Type annotations are preferred over `reST field lists`_ for documenting
  parameter types. Only use field lists when additional explanation beyond the
  type is necessary, or when working with legacy code that doesn't have type
  annotations:

  .. code-block:: python

    def legacy_function(bar):
        """Simple docstring for legacy code without type annotations.

        :param str bar: Description of what bar represents
        :return: Description of return value
        :rtype: int
        """

Cross-referencing code:
   When talking about other objects, methods, functions and variables,
   cross-reference them using Sphinx's `Python cross-referencing`_ syntax:

   - ``:class:`ClassName``` -- reference a class
   - ``:func:`function_name``` -- reference a function
   - ``:meth:`method_name``` -- reference a method
   - ``:mod:`module_name``` -- reference a module
   - ``:attr:`attribute_name``` -- reference an attribute

   Example:

   .. code-block:: python

    def process_unit(unit: TranslationUnit) -> None:
        """Process a translation unit.

        This delegates to :func:`validate_unit` and updates the
        :class:`TranslationStore`.
        """

Linking to external documentation:
   Use standard reStructuredText syntax for external links in docstrings:

   - Inline links: ```Link text <URL>`_``
   - Reference links: Define once with ``.. _label: URL`` and reference with
     ``label_``

Other directives:
   Use `paragraph-level markup`_ when needed, such as:

   - ``.. note::`` for important information
   - ``.. warning::`` for warnings
   - ``.. versionadded::`` and ``.. deprecated::`` for version information


Module header:
  The module header consists of a utf-8 encoding declaration, copyright
  attribution, license block and a standard docstring:

  .. code-block:: python

    #
    ... LICENSE BLOCK...

    """A brief description"""

..    """
        package.module
        ~~~~~~~~~~~~~~

..        A brief description goes here.

..        :copyright: (c) YEAR by AUTHOR.
        :license: LICENSE_NAME, see LICENSE_FILE for more details.
    """

Deprecation:
  Document the deprecation and version when deprecating features:

  .. code-block:: python

     from translate.misc.deprecation import deprecated


     @deprecated("Use util.run_fast() instead.")
     def run_slow():
         """Run fast

         .. deprecated:: 1.5
            Use :func:`run_fast` instead.
         """
         run_fast()


.. _reST field lists: http://sphinx-doc.org/domains.html#info-field-lists
.. _Python cross-referencing: http://sphinx-doc.org/domains.html#cross-referencing-python-objects
.. _Sphinx: http://sphinx-doc.org/
.. _reStructuredText primer: http://sphinx-doc.org/rest.html
.. _Sphinx documentation: http://sphinx-doc.org/contents.html
.. _paragraph-level markup: http://sphinx-doc.org/markup/para.html#paragraph-level-markup
