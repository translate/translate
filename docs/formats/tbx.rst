
.. _pages/toolkit/tbx#tbx:

TBX
***
TBX is the LISA standard for terminology and term exchange.

For information on more file formats, see :doc:`conformance`.

.. _pages/toolkit/tbx#references:

References
==========

  * `Standard home page <http://www.lisa.org/Term-Base-eXchange.32.0.html>`_
  * `Specification <http://www.lisa.org/TBX-Specification.33.0.html>`_
  * `ISO 30042 <http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=45797>`_ - TBX is an approved ISO standard

You might also be interested in reading about `TBX-Basic <http://www.lisa.org/TBX-Basic.926.0.html>`_ - a simpler, reduced version of TBX with most of the useful features included.

.. _pages/toolkit/tbx#standard_conformance:

Standard conformance
====================

.. _pages/toolkit/tbx#done:

Done
----
  * Basic file creation
  * Creating a bilingual list from CSV with :doc:`/commands/csv2tbx`
  * Using <tig> tags, not ntig

.. _pages/toolkit/tbx#todo:

Todo
----
  * id attributes for termEntry tags
  * ntig, read and write
  * multiple languages
  * synonyms
  * cross references
  * abbreviations
  * definitions
  * context
  * parts of speech

.. _pages/toolkit/tbx#implementation_notes_for_missing_features:

Implementation notes for missing features
=========================================

Note here:

  * NLS - South African National Language Services - Multilingual Maths Dictionary

.. _pages/toolkit/tbx#synonyms:

Synonyms
--------
NLS: Extra listing\\
TBX:

::

    <termNote type="termNote">synonym</termNote>

according to this TBX documentation. In another place:

::

    <termNote type="termType">synonym</termNote>

inside a <termGrp>, following <term>

.. _pages/toolkit/tbx#definition:

Definition
----------
NLS: term {definition/contextual information}\\
TBX

::

    <descripGrp>
       <descrip type="definition">The longish definition of the term</descrip>
    </descripGrp>

inside langSet
<descript> can probably be used directly under langSet

.. _pages/toolkit/tbx#context:

Context
-------
NLS: term {definition/contextual information} (see above)\\
TBX:

::

    <descrip type="context">A usually somewhat longer contextual sentence.</descrip>

inside <ntig>

.. _pages/toolkit/tbx#parts_of_speech:

Parts of speech
---------------
NLS: term v.  (or adj, or n.)\\
TBX:

::

    <termNote type="partOfSpeech" >noun</termNote>

following <term>

.. _pages/toolkit/tbx#cross_reference:

Cross reference
---------------
NLS: alternate term -> real lemma\\
TBX: <ref> TODO

.. _pages/toolkit/tbx#abbreviations:

Abbreviations
-------------
NLS: same as alternate term: a.m. -> before noon\\
TBX: TODO

.. _pages/toolkit/tbx#tbx_cheat_sheet:

TBX cheat sheet
===============

  - source word in English
  - definition in English
  - translation of source word to XX
  - definition in XX
  - comment
  - syntactic group
  - one or more tags
  - a reference number

::

    <termEntry id="4324 (8)">
        <note>tag1, tag2, tag3 (7) -
    (Actually not clear what the best mapping to TBX is in this case.)</note>
        <langSet xml:lang="en">
            <tig>
                <term>sound (1)</term>
                <termNote type="partOfSpeech">noun (6)</termNote>
            </tig>
            <descripGrp>
                <descrip type="definition">Something you can hear (2) -
    definition with an associated external source)</descrip>
                <xref type="xSource" target="http://www.something.org/?id=234">Glossmaster</xref>
            </descripGrp>
            <note>Any random note about the term. (5)
    (Actually there are ways of storing pretty specific stuff in specific spaces,
    but while it seems the comment could be a more verbose definition, examples,
    usage notes or anything else, we'll use this generic way.)
            </note>
        </langSet>
        <langSet xml:lang="af">
            <tig>
                <term>klank (3)</term>
            </tig>
            <descrip type="definition">Iets wat jy kan hoor (4) -
    definition without an external source)</descrip>
            <note>A note in the target language (5).</note>
        </langSet>
    </termEntry>

Note that the <xref> tags are optional (as are just about everything except termEntry, langSet and tig). They allow to link to an external source. An internal source can also be specified, or the definition can be specified without a source as shown for the term "klank".

.. _pages/toolkit/tbx#tbx_requirements_by_galician_translation_team_proxecto_trasno:

TBX requirements by Galician translation team (Proxecto Trasno)
***************************************************************

Here you have a list of `TBX requirements <http://www.certima.net/glosima/?28-xustificacion-das-escollas-de>`_ needed by the `Galician translation team (Proxecto Trasno) <http://www.trasno.net>`_. Its translation to english is below. You can see a terminology management system software specification draft in http://translate.sourceforge.net/wiki/developers/terminology_management_system

A very important feature is to allow the exporting using pretty printing (like in the first example below) since the exported glossaries should be able to be read both by humans and software.

Before the example you can see a list priorizing the features from more interesting and needed to less interesting and needed.

The chosen TBX tags are determined by the needs of our terminology management system (the galician translation team one). That terminology management system needs several glossaries, each glossary has several concepts, and each concept can have several definitions (only one definition per language in a given concept), and also can have several translations for each concept (several translations per language in a given concept). The concepts will also have associated some links to get more information (several links per language in a given concept). Also is needed to have defined several languages. 

Now we have a list of all the needed entities lets go with the list of attributes for each of that entities:

Each glossary has a name and a description.

Each concept has an unique id, a subject field (which is another concept in the same glossary), it can have several concepts that people may wish to see (lets call it related concepts), and it can also have a parent concept (broader concept).

Each link has a type (image, Wikipedia page,...), the address of the link, and a tiny description.

Each definition has a definition text.

We want to save the ISO 639 code of each language.

Each translation can have a translation text, it has an unique id, the part of speech, the grammatical genre (if applicable), the grammatical number (if applicable), a field that indicates if the translation is an abbreviation or an acronym, an explaining note, examples of use (created by the people that make the terminology), links to examples of real use (a corpus or translation database), a field that indicates if the translation is completed or if it is still incomplete (completion status), and we also need to save the translation administrative status (if it is a recommedend translation, a not recommended one, or if it is a forbidden translation) and the reason why the translation has the actual administrative status (a simple text string) that only applies when the administrative status is other than "recommended".

Once listed the needs we proceeded with reading the TBX ISO 300042 standard in search of the elements that support these needs, and we found at least one tag (or attribute) for every need, except for only a few that doesn't have. We should comment that TBX stores the information grouping it by concepts, and within each concept part of the information is stored at the beginning of the concept and other part of that information (the language-dependant information) is splited between the different languages, and within every language section it is splited another time between the translations of that language. This way it has a three level structure: concept level, language level and translation level (also called term level).

Next we list the needs and the tag chosen for that need, indicating the level in which the tag goes:

* **Glossary name:** if we match glossary with TBX file, then the glossary name is the TBX file title, the label <title>. It goes on the file header.

* **Glossary description:** if we match glossary with TBX file then we can use a <p> tag inside <sourceDesc> tag. It goes on the file header.

* **Concept:** the <termEntry> tag from TBX standard represents a concept. This tag encloses the concept level.

* **Concept identifier:** the <termEntry> tag has an attribute named "id".

* **Concept subject field:** the TBX standard defines the <descrip> tag with "subjectField" in its "type" attribute to represent the concept subject field (***<descrip type="subjectField">subject field name</descrip>***). Since there is no way to refer to another concept we should use some of the translations of the subject field concept (the concept that is the subject field of the current concept) to put inside the subject field tag. It goes in concept level. **The lack of a way in TBX standard to refer to another concept within the same glossary as subject field to make self-contained glossaries is a real lack or we haven't identified the way to do this using TBX??**

* **Related concepts:** the TBX standard suggest the use of the tag ***<ref type="crossReference" target="cid­23">some text...</ref>*** where “cid­23” is the value of the related concept id, and "some text..." is one of the related concept translations (the first english recommended one, for example). It goes on concept level.

* **Broader concept:** TBX defines the use of the tag <descrip> with the value "broaderConceptGeneric" in its "type" attribute and a text between its opening and closing tags. Also it allows the use of the "target" attribute to refer to the broader concept. It goes on concept level. Example ***<descrip type="broaderConceptGeneric" target="cid­23">broader concept name</descrip>***

* **Link:** according to TBX standard the tag that defines external links to outside the current file is the <xref> tag. This tag has the following structure: ***<xref type="xGraphic" target="sports/cricket/bat.jpg">cricket bat</xref>*** where "type" is the link type, "target" is the link address and the text between the opening and closing tags is a short description. It goes on language level.

* **Link type:** the <xref> tag has an attribute named "type" that defines the link type. This attribute can have the values "xGraphic" if it is an image, "externalCrossReference" if it is a link to an external resource (for example a link to Wikipedia). It can have other values, but for now they are considered not important.

* **Link address:** the <xref> tag has an attribute named "target" which is the link address.

* **Link description:** the link description can go between the opening and closing tags

* **Definition:** to save the definitions it should be used the <descrip> tag with the value "definition" in its "type" attribute. It goes on the language level. Example: ***<descrip type="definition">alternate name for a person...</descrip>*** can be the definition for "nickname".

* **Definition text:** the definition text goes between the opening and closing <descrip> tags.

* **Language:** in TBX the <langSet> tag represents a language, but no language list is stored inside the TBX file. So if there is a <langSet> tag for a given language somewhere inside the TBX file, then this particular language is defined in that TBX file. Inside each concept only can exist one <langSet> per language, but a given language can have a <langSet> in each <termEntry>. It is essential that at least one <langSet> tag is present in every <termEntry> tag. The <langSet> tag encloses the language level. It goes on concept level.

* **Language code:** the <langSet> tag has an attribute named "xml:lang" which stores some ISO 639 code value. Example: ***<langSet xml:lang="gl">***

* **Translation:** the TBX standard defines two different tags to enclose the translation level: <tig> and <ntig>. The <tig> tag provides all the needed functionalities, like also the <ntig> tag does, but the <ntig> also has a lot of undesired and unnecessary functionalities that complicate the TBX file structure in an unnecessary way making its size grow and making dificult to a person read the file with a text editor. Besides the TBX-Basic standard only uses the <tig> tag. So we decided to only use the <tig> tag.

* **Translation text:** the translation text goes between the opening and closing of the <term> tag that goes on the translation level (under the <tig> tag). Example: ***<term>nickname</term>***

* **Translation identifier:** the <tig> tag has an attribute named "id" in which we put the identifier. Example: ***<tig id="tid­59">...</tig>***

* **Part of speech:** for storing the part of speech TBX suggests the use of the <termNote> tag indicating in the "type" attribute the value "partOfSpeech". The TBX standard doesn't defines a part of speech values list (like noun, verb...), but the TBX-Basic standard (a simplified subset of TBX) defines a short list of part of speech values which we can reuse and that can be completed if necessary. It goes on translation level. Example: ***<termNote type="partOfSpeech">noun</termNote>***

* **Grammatical gender:** TBX specifies that the grammatical gender should be specified using the <termNote> tag indicating the value "grammaticalGender" in the "type" attribute. Like in the previous point, TBX doesn't define a gender list so we will have to use the defined in TBX-Basic. It goes on the translation level. Example: ***<termNote type="grammaticalGender">masculine</termNote>***

* **Grammatical number:** TBX says that for saving the grammatical number it should be used a <termNote> tag with the value "grammaticalNumber" in its "type" attribute. For the grammatical number we are going to use the list defined in TBX-Basic. The grammatical should only be put when not putting it could lead to misunderstanding. It goes on the translation level. Example: ***<termNote type="grammaticalNumber">plural</termNote>***

* **Acronym:** to indicate that a translation is an acronym we can use the <termNote> tag with the "termType" value on its attribute "type" and the text "acronym" between its opening and closing tags. It goes on the translation level. Example: ***<termNote type="termType">acronym</termNote>***

* **Abbreviation:** Like in the previous point but putting now "abbreviation" between the opening and the closing tags. It goes on the translation level.

* **Translation explaining note:** for the notes TBX defines the use of the <termNote> tag with the value "usageNote" on its "type" attribute with the explanatory note text between its opening and closing tags. It goes on the translation level. Example: ***<termNote type="usageNote">Don't abuse of that translation...</termNote>***

* **Example of use:** for the examples of use made ad hoc we are going to use the <descrip> tag with the value "context" on its "type" attribute and the example text between its opening and closing tags. It goes on the translation level. We are not going to use <descrip type="sampleSentence"> since it doesn't appear both in TBX and in TBX-Basic, and also we are not going to use <descrip type="example"> since in it is not mandatory to include the translation text in the example. Example: ***<descrip type="context">example text</descrip>***

* **Link to real use example:** it is used for references to corpus (translations databases, like open-tran.eu). TBX says that such references should be indicated using the <xref> tag with the value "corpusTrace" on its "type" attribute. It goes on the translation level. Example: ***<xref type="corpusTrace" target="http:*en.gl.open-tran.eu/suggest/window">Window on open-tran.eu</xref>**//

* **Completion status:** we are going to use the <termNote> tag with the value "processStatus" in its "type" attribute and the text "provisionallyProcessed" between its opening and closing tags to indicate that not all the translation information is not approved or that some of that information are not included on the system yet. In case being completed this tag shouldn't appear, despite TBX defines the values "unprocessed" and "finalized". It goes on the translation level. Example: ***<termNote type="processStatus">provisionallyProcessed</termNote>***

* **Administrative status:** to indicate the administrative status of the translation we are going to do the way TBX specifies and not how TBX-Basic does since we are using a superset of TBX-Basic. TBX specifies the use of the <termNote> tag with the value "administrativeStatus" on its "type" attribute and the text that indicates the status between its opening and closing tags. TBX defines a list of several states but we are only going to use three of them: "preferredTerm­admn­sts" to indicate that this is a recommended translation, "admittedTerm­admn­sts" to indicate that it is a valid translation but that be prefer not to use it since there is another one that is recommended, and "deprecatedTerm­admn­sts" to indicate that this translation is forbidden (for not being a valid translation for a given language for some reasons: false friend,...). It goes on the translation level. Example: ***<termNote type="administrativeStatus">preferredTerm­admn­sts</termNote>***

* **Administrative status reason:** TBX doesn't define any way to save the reason why a translation has a given administrative status. Due to that we decided to use the 

.. note::

    tag for specifying the reason. Since this tag is also used for saving notes we are considering to use the <termNoteGrp> to group it together with the administrative status tag. Maybe some languages are not going to use that, but in galician it is very very important. Note that the reason is not specified if the administrative status is "preferredTerm­admn­sts". It goes on the translation level. Example: **galicism**

Below you can see a diagram that shows the levels and the data that goes in each level. Click on the image to enlarge.

.. image:: /_static/tbx_levels_structure.png

.. _pages/toolkit/tbx#features_priorization:

Features priorization
=====================

The upper ones are the most needed and interesting:

  * Definition
  * Several translations in the same language for the same concept
  * Part of speech
  * Grammatical gender
  * Grammatical number
  * Concept subject field
  * Pretty printing
  * Use of tig tag by default
  * Link to external resources (including its type, address and description)
  * Completion status
  * Administrative status
  * Administrative status reason
  * Translation explaining note
  * Translation identifier
  * Related concepts
  * Broader concept
  * Acronym
  * Abbreviation
  * Example of use
  * Link to real use example

.. _pages/toolkit/tbx#example_for_galician_tbx_requirements:

Example for galician TBX requirements
=====================================

::

    <?xml version='1.0' encoding='UTF-8'?>
    <!DOCTYPE martif SYSTEM 'TBXcoreStructV02.dtd'>
    <martif type='TBX' xml:lang='en'>
        <martifHeader>
            <fileDesc>
                <titleStmt>
                    <title>Localization glossary</title>
                </titleStmt>
                <sourceDesc>
                    <p>Test glossary with concepts from software localization...</p>
                </sourceDesc>
            </fileDesc>
            <encodingDesc>
                <p type='XCSURI'>http://www.lisa.org/fileadmin/standards/tbx/TBXXCSV02.xcs</p>
            </encodingDesc>
        </martifHeader>
        <text>
            <body>

                <termEntry id="cid-23">
                    <descrip type="subjectField">computer science</descrip><!-- enclosed text in english since it is the glossary 
                    language (see martif opening tag) -->
                    <ref type="crossReference" target="cid-12">microprocessor</ref><!-- enclosed text in english since it is the 
                    glossary language (see martif opening tag) -->
                    <ref type="crossReference" target="cid-16">keyboard</ref><!-- enclosed text in english since it is the glossary 
                    language (see martif opening tag) -->
                    <descrip type="broaderConceptGeneric" target="cid-7">hardware</descrip><!-- enclosed text in english since it is 
                    the glossary language (see martif opening tag) -->

                    <langSet xml:lang="en">
                        <descrip type="definition">A computer is a programmable machine that receives input, stores and manipulates 
    data, and provides output in a useful format.</descrip>
                        <xref type="xGraphic" target="http://en.wikipedia.org/wiki/File:HPLaptopzv6000series.jpg">computer image</xref>
                        <xref type="externalCrossReference" target="http://en.wikipedia.org/wiki/Computer">English Wikipedia computer page</xref>

                        <tig id="tid-59">
                            <term>computer</term>
                        </tig>
                        <tig>
                            <term>PC</term>
                            <termNote type="termType">acronym</termNote><!-- "PC" is an acronym of "Personal Computer" -->
                            <termNote type="administrativeStatus">admittedTerm-admn-sts</termNote>
                            <termNote type="usageNote">Do not abuse of using this translation.</termNote>
                        </tig>
                        <tig>
                            <term>comp.</term>
                            <termNote type="termType">abbreviation</termNote><!-- "comp." is an abbreviation of "computer" -->
                            <termNote type="administrativeStatus">admittedTerm-admn-sts</termNote>
                        </tig>
                    </langSet>

                    <langSet xml:lang="es">
                        <descrip type="definition">Máquina  electrónica que recibe y procesa datos para convertirlos en información 
    útil</descrip><!-- definition text in spanish -->

                        <tig>
                            <term>sistema</term>
                            <termNote type="administrativeStatus">admittedTerm-admn-sts</termNote>
                        </tig>
                        <tig>
                            <term>equipo</term>
                            <termNote type="administrativeStatus">deprecatedTerm-admn-sts</termNote>
                            <termNote type="processStatus">provisionallyProcessed</termNote>
                        </tig>
                        <tig>
                            <term>ordenador</term>
                            <termNote type="partOfSpeech">noun</termNote>
                            <termNote type="grammaticalGender">masculine</termNote>
                            <termNote type="grammaticalNumber">singular</termNote>
                            <termNote type="administrativeStatus">preferredTerm-admn-sts</termNote>
                            <descrip type="context">El ordenador personal ha supuesto la generalización de la informática.</descrip><!-- example phrase -->
                            <xref type="corpusTrace" target="http://es.en.open-tran.eu/suggest/ordenador">ordenador en open-tran.eu</xref><!-- enclosed text in spanish -->
                        </tig>
                        <tig>
                            <term>computador</term>
                            <termNote type="administrativeStatus">deprecatedTerm-admn-sts</termNote>
                        </tig>
                        <tig>
                            <term>computadora</term>
                            <termNote type="administrativeStatus">deprecatedTerm-admn-sts</termNote>
                        </tig>
                    </langSet>

                    <langSet xml:lang="fr">
                        <descripGrp><!-- Using descripGrp tags for enclosing the definition and its source -->
                            <descrip type="definition">Un ordinateur est une machine dotée d'une unité de traitement lui permettant 
    d'exécuter des programmes enregistrés. C'est un ensemble de circuits électroniques permettant de manipuler des données sous forme 
    binaire, ou bits. Cette machine permet de traiter automatiquement les données, ou informations, selon des séquences d'instructions 
    prédéfinies appelées aussi programmes.
                            Elle interagit avec l'environnement grâce à des périphériques comme le moniteur, le clavier, la souris, 
    l'imprimante, le modem, le lecteur de CD (liste non-exhaustive). Les ordinateurs peuvent être classés selon plusieurs critères 
    (domaine d'application, taille ou architecture).</descrip>
                            <xref type="xSource" target="http://fr.wikipedia.org/wiki/Ordinateur">Wikipedia: ordinateur</xref>
                        </descripGrp>

                        <tig>
                            <term>ordinateur</term>
                        </tig>
                    </langSet>
                </termEntry>

                <termEntry id="cid-27"><!-- Another concept -->
                    <descrip type="subjectField">computer science</descrip>

                    <langSet xml:lang="en">
                        <descrip type="definition">A technical standard is an established norm or requirement. It is usually a formal 
    document that establishes uniform engineering or technical criteria, methods, processes and practices. In contrast, a custom, 
    convention, company product, corporate standard, etc. which becomes generally accepted and dominant is often called a de facto standard.</descrip>

                        <tig>
                            <term>standard</term>
                            <termNote type="partOfSpeech">noun</termNote>
                            <termNote type="administrativeStatus">preferredTerm-admn-sts</termNote>
                        </tig>
                    </langSet>

                    <langSet xml:lang="gl">
                        <descrip type="definition">Norma que mediante documentos técnicos fixa a especificación de determinado tema.</descrip>

                        <tig>
                            <term>estándar</term>
                            <termNote type="administrativeStatus">preferredTerm-admn-sts</termNote>
                        </tig>

                        <tig>
                            <term>standard</term>
                            <termGrp><!-- Example of administrative status along with its reason -->
                                <termNote type="administrativeStatus">deprecatedTerm­admn­sts</termNote>
                                <note>Razón: anglicismo</note><!-- the translation of the enclosed text is: "Reason: anglicism" -->
                            </termGrp>
                        </tig>
                    </langSet>
                </termEntry>

            </body>
        </text>
    </martif>

