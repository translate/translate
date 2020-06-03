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
* i18next
* Web Extension i18n
* `go-i18n <https://github.com/nicksnyder/go-i18n>`_
* `ARB <https://github.com/google/app-resource-bundle/wiki/ApplicationResourceBundleSpecification>`_
