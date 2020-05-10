
.. _html:

HTML
****

The Translate Toolkit is able to process HTML files using the :doc:`html2po
</commands/html2po>` converter.


.. _html#conformance:

Conformance
===========

* Can identify almost all HTML elements and attributes that are localisable.

* The localisable and localised text in the PO/POT files is fragments of HTML. 
  Therefore, reserved characters must be represented by HTML entities:
  
  - Content from HTML elements uses the HTML entities ``&amp;`` (&), ``&lt;``
    (<), and ``&gt;`` (>).

  - Content from HTML attributes uses the HTML entities ``&quot;`` (") or
    ``&apos;`` (').

* Leading and trailing tags are removed from the localisable text,
  but only in matching pairs. 

* Can cope with embedded PHP, as long as the documents remain valid HTML. If 
  you place PHP code inside HTML attributes, you need to make sure that the PHP
  doesn't contain special characters that interfere with the HTML.


.. _html#references:

References
==========

* `Reserved characters
  <https://developer.mozilla.org/en-US/docs/Glossary/Entity>`__
* `Using character entities
  <http://www.w3.org/International/questions/qa-escapes>`__
