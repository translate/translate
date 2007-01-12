                        Pootling (V.0.1.1)
Copyright (c) 2006 by The WordForge Foundation (All Rights Reserved)
                        ww.wordforge.org

Version 0.1.1  Date: 12 January 2007

Developed by:
  Hok Kakada (hokkakada@khmeros.info)
  Keo Sophon (keosophon@khmeros.info)
  San Titvirak (titvirak@khmeros.info)
  Seth Chanratha (sethchanratha@khmeros.info)

===========================================================
* How it works
* References
* Requirement
* Running
* Bug reporting

How it works
------------
Pootling is a program for translating PO and XLIFF files.

References
----------
Bugzilla: http://bugs.wordforge.org/
Wiki: http://translate.sourceforge.net/wiki

Requirements
------------

WordForge Translation Editor, pootling.v0.1.1, requires the Translate Toolkit. 
It requires a version that was not yet released at the time of this release of 
pootling, but you can find a beta version of the toolkit here: 
http://translate.sourceforge.net/snapshots/translate-toolkit-1.0beta/ 

Please note that this is not an official release and is for testing pootling 
0.1.1, there might be bugs if you use this beta version in other programs.
When translate-toolkit 1.0 is released, you are recommended to use it.

If you want the stable release of the toolkit, visit 
http://translate.sourceforge.net

The Translate Toolkit requires Python 2.3 or higher. It must be installed 
properly, i.e. it needs to be accessible in your PYTHONPATH. Please see the 
file README in the translate toolkit for details.

Other required tools:
----------------------
For Unix / Linux users:

sip-4.4.5 or higher a Python C/C++ Bindings Generator
http://www.riverbankcomputing.co.uk/sip/

PyQt-x11-gpl-4.0 or highe, the Python bindings for the Qt GUI toolkit
http://www.riverbankcomputing.co.uk/pyqt

Qt4.2 or higher, a GUI toolkit
http://www.trolltech.com/developer/downloads/qt

Python 2.3 or higher (shipped with most Linux distributions)
http://www.python.org/


For Windows users:

PyQt-x11-gpl-4.1.1, the Python bindings for the Qt GUI toolkit
http://www.riverbankcomputing.co.uk/pyqt/

Qt4.2.2, a GUI toolkit
http://www.trolltech.com/developer/downloads/qt

Khmer rendering in Qt4.2.2 on Windows:
http://sourceforge.net/project/showfiles.php?group_id=133361

minGW-3.1.0-1, ("Minimalistic GNU for Windows")
http://mingw.org/

Python2.5, a powerful programming language
http://www.python.org/


For making a Windows installer you will need sip:
sip-4.5.2, a Python C/C++ Bindings Generator
http://www.riverbankcomputing.co.uk/sip/

Running
-------

    python pootling-editor.py [OPTION] [filename]

if the filename is given, the editor will open the file.

options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

  
Bug Reporting/Feature requests
------------------------------
You can always report bugs or feature requests on the mailing list, but it is 
probably best to place your bug report in Bugzilla: http://bugs.wordforge.org/
Please use "pootling" as product

If you have a traceback or a patch then please include it.  Also please be 
quite specific about how the bug occurred and what you expected to happen.

If this is a feature request then try to be specific about how you think this 
feature should work.

