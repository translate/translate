.. _yaml:


YAML
====

.. versionadded:: 2.0.0

:wp:`YAML` is a common format for web data interchange. The two variants of
YAML files are supported:

* Plain YAML files.
* Ruby YAML localization files with root node as language. This variant
  supports plurals as well.


.. _yaml#non-conformance:

Non-Conformance
===============

The following are not yet supported (in most cases these are properly parsed,
but not saved in round trip):

* Booleans:

  .. code-block:: yaml

      foo: True
