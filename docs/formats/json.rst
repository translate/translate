JSON
====

.. versionadded:: 1.9.0

:wp:`JSON` is a common format for web data interchange.

Example:

.. code-block:: json

   {
       "firstName": "John",
       "lastName": "Smith",
       "age": 25,
       "address": {
           "streetAddress": "21 2nd Street",
           "city": "New York",
           "state": "NY",
           "postalCode": 10021
       },
       "phoneNumbers": [
           {
               "type": "home",
               "number": "212 555-1234"
           },
           {
               "type": "fax",
               "number": "646 555-4567"
           }
       ]
   }

Following JSON dialects are supported

* Plain JSON files.
* i18next v3 & v4
* Web Extension i18n
* `go-i18n v1 & v2 <https://github.com/nicksnyder/go-i18n>`_
  V1 translation objects preserve explicit plural identifiers and empty forms. Use ``unit.plural_forms`` to edit them by name.
* `gotext <https://pkg.go.dev/golang.org/x/text/cmd/gotext>`_
  Plural selectors expose their category cases through ``plural_forms``.
  Named edits retain the selector argument and existing case metadata.
* `ARB <https://github.com/google/app-resource-bundle/wiki/ApplicationResourceBundleSpecification>`_
* `FormatJS <https://formatjs.io/docs/getting-started/message-extraction/>`_
* `RESJSON <https://docs.rws.com/en-US/sdl-passolo-help-785448/add-in-for-javascript-object-notation-json-file-format-types-410873>`_ (JavaScript Resource File)

Go-i18n v2 plural objects
-------------------------

Use ``unit.plural_forms`` to edit categories by name. A JSON object with one
category remains an object, including when it has no description. A scalar
translation without notes remains a scalar. Adding notes serializes it as an
object with the fields ``description`` and ``other``.
