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
* `gotext <https://pkg.go.dev/golang.org/x/text/cmd/gotext>`_
* `ARB <https://github.com/google/app-resource-bundle/wiki/ApplicationResourceBundleSpecification>`_
