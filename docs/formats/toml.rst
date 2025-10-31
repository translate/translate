.. _toml:


TOML
====

.. versionadded:: 3.16.0

:wp:`TOML` is a common format for configuration files and is increasingly used
for localization. The translate toolkit supports two variants of TOML files:

* Plain TOML files - basic key-value pairs and nested tables.
* Go i18n TOML files - supports pluralized strings using CLDR plural
  categories (zero, one, two, few, many, other).


.. _toml#plain_toml:

Plain TOML
==========

Plain TOML files contain simple key-value pairs and nested structures:

.. code-block:: toml

    # Welcome message
    welcome = "Welcome to our application"

    [settings]
    app_name = "My App"
    description = "A great application"

    [settings.advanced]
    timeout = "30 seconds"


Keys are extracted as location identifiers, and comments are preserved as
translator notes.


.. _toml#go_i18n_toml:

Go i18n TOML
============

The Go i18n TOML format is commonly used by Go applications and Hugo static
site generators. It supports pluralized strings using CLDR plural categories:

.. code-block:: toml

    [reading_time]
    one = "One minute to read"
    other = "{{ .Count }} minutes to read"

    [items_count]
    zero = "No items"
    one = "One item"
    two = "Two items"
    few = "A few items"
    many = "Many items"
    other = "{{ .Count }} items"


When a table contains 2 or more keys that are all CLDR plural categories
(zero, one, two, few, many, other), it is automatically recognized as a
plural entry.

To use the Go i18n format, import ``GoI18nTOMLFile`` instead of ``TOMLFile``:

.. code-block:: python

    from translate.storage.toml import GoI18nTOMLFile

    store = GoI18nTOMLFile()
    store.parse(content)


.. _toml#supported_features:

Supported Features
==================

* **Nested tables**: Tables and nested tables using dot notation
  (``parent.child.key``)
* **Arrays**: Lists of strings with index notation (``list->[0]``)
* **Comments**: Developer comments are extracted as translator notes
* **String types**: Basic strings, literal strings (single quotes), and
  multiline strings (triple quotes)
* **Formatting preservation**: tomlkit library preserves original formatting
  during round-trips
* **Plurals** (Go i18n only): CLDR plural categories


.. _toml#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* Inline tables with nested structures
* Date and time values (parsed as strings)
* Mixed content arrays (only string arrays are localized)


.. _toml#example_usage:

Example Usage
=============

See :ref:`toml2po` for examples of converting TOML files to PO format and back.
