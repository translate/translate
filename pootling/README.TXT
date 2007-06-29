                        Pootling (V.0.2)
Copyright (c) 2006 by The WordForge Foundation (All Rights Reserved)
                        ww.wordforge.org

Version 0.2 rc1 Date: 31 Jun 2007

Developed by:
  Hok Kakada (hokkakada@khmeros.info)
  Keo Sophon (keosophon@khmeros.info)
  San Titvirak (titvirak@khmeros.info)
  Seth Chanratha (sethchanratha@khmeros.info)

===========================================================
* How it works
* References
* Requirement
* Installation
* Running
* Bug reporting

How it works
------------
Pootling, a WordForge Translation Offline Editor, is a user friendly translation program that makes the translation process simpler. It is an offspring of Pootle, a web-based translation engine.  Pootling is a very advanced compuer-aided localization based on the intelligent use of Translation Manager, Glossary manager and Catalog Manager.
Pootling can handle a number of file types such as PO, XLIFF, TMX, TBX...
is a program for translating PO and XLIFF files.

Please read its manual for how to use it.

References
----------
Bugzilla: http://bugs.wordforge.org/
Wiki: http://translate.sourceforge.net/wiki
website: www.khmeros.info

Main Requirements
------------

WordForge Translation Editor, pootling.v0.2, requires the Translate Toolkit 1.0.1 or later version.  that can be downloaded at https://sourceforge.net/project/showfiles.php?group_id=91920&package_id=97082 


The Translate Toolkit requires Python 2.3 or higher. It must be installed 
properly, i.e. it needs to be accessible in your PYTHONPATH. Please see the 
file README in the translate toolkit for details.

Other required tools:
----------------------
For Developers on Unix / Linux platform:

sip-4.4.5 or higher a Python C/C++ Bindings Generator
http://www.riverbankcomputing.co.uk/sip/

PyQt-x11-gpl-4.0 or higher, the Python bindings for the Qt GUI toolkit
http://www.riverbankcomputing.co.uk/pyqt

Qt4.1 or higher, a GUI toolkit
http://www.trolltech.com/developer/downloads/qt

Python 2.3 or higher (shipped with most Linux distributions)
http://www.python.org/


For Dovelopers on Windows platform:

PyQt-x11-gpl-4.1.1, the Python bindings for the Qt GUI toolkit
http://www.riverbankcomputing.co.uk/pyqt/

Qt4.2.2, a GUI toolkit
http://www.trolltech.com/developer/downloads/qt

Khmer rendering in Qt4.2.2 on Windows:
http://sourceforge.net/project/showfiles.php?group_id=133361

minGW-3.1.0-1, ("Minimalistic GNU for Windows")
http://mingw.org/

Python2.4 or higher, a powerful programming language
http://www.python.org/


For making a Windows installer you will need sip:
sip-4.5.2, a Python C/C++ Bindings Generator
http://www.riverbankcomputing.co.uk/sip/

Installation
------------
We provide a number of way to have pootling installed.
1. RPM package:
       1. You must be root: 
             su
       2. Install
             rpm -ihv pootling-editor.rpm
2.Compile from source:
            python pootlingsetup.py
Then you can run pootling-editor.py command as other commands.

Running from source code
-----------------------

    python pootling-editor.py [OPTION] [filename]

if the filename is given, the editor will open the file.

options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Running as a simple user
-----------------------
In this release, we try to make it easy for our end users.
Download only Easy-Pootling, go into this folder and double click on the pootling executable file.
You will get Pootling to run only one click (no other requirements)

Note: Unfortunately, This Easy-Pootling support only python2.5

Bug Reporting/Feature requests
------------------------------
You can always report bugs or feature requests on the mailing list, but it is 
probably best to place your bug report in Bugzilla: http://bugs.wordforge.org/
Please use "pootling" as product

If you have a traceback or a patch then please include it.  Also please be 
quite specific about how the bug occurred and what you expected to happen.

If this is a feature request then try to be specific about how you think this 
feature should work.

