                        Pootling (V.0.1.1)
Copyright (c) 2006 by The WordForge Foundation (All Rights Reserved)
                        ww.wordforge.org

Version 0.1.1  Date: 12 january 2007

Developed by:
  Hok Kakada (hokkakada@khmeros.info)
  Keo Sophon (keosophon@khmeros.info)
  San Titvirak (titvirak@khmeros.info)
  Seth Chanratha (sethchanratha@khmeros.info)

===========================================================
* How it works
* References
* Requirement/How to run
* Running
* Bug reporting
* Notes

How it works
------------
The idea is to have it worked with po file and can also handle most information in
XLIFF file.

References
----------
Bugzilla: http://bugs.wordforge.org/
Wiki: http://translate.sourceforge.net/wiki

Requirements/How to run
-------------------------

WordForge Translation Editor, pootling.v0.1.1, requires the Translate Toolkit package from 
http://translate.sourceforge.net/snapshots/translate-toolkit-1.0beta/ as it uses most of the other modules.
Please note that this is not an official release and is for testing pootling.v.0.1.1, there might be bugs if you use this beta version in other programs.
When translate-toolkit 1.0 is released, you are recommended to use it.

If you want the stable release, visit http://translate.sourceforge.net .

The Translate Toolkit requires Python 2.3 or higher.It must 
be installed properly i.e. it needs to be accessible in your Python Path. This
will normally be accomplished by installing it. Please read the README for details.

Other required tools:
----------------------
For Unix/ Linux System User:

sip-4.4.5 or higher, Python C/C++ Bindings Generator, is also needed and can be obtained from 
http://www.riverbankcomputing.co.uk/sip/

PyQt-x11-gpl-4.0 or higher, <http://www.riverbankcomputing.co.uk/pyqt/> - the Python bindings for
the Qt GUI toolkit

Qt4.2 or higher, a GUI toolkit, can be found here:
http://www.trolltech.com/developer/downloads/qt


For Windows User:

for running the source code on Windows:
PyQt-x11-gpl-4.1.1,  the Python bindings for the Qt GUI toolkit.
http://www.riverbankcomputing.co.uk/pyqt/

Qt4.2.2, a GUI toolkit, can be found here:
http://www.trolltech.com/developer/downloads/qt

Khmer rendering in Qt4.2.2 on Windows:
http://sourceforge.net/project/showfiles.php?group_id=133361

minGW-3.1.0-1, ("Minimalistic GNU for Windows")
http://mingw.org/

Python2.5, a powerful programming languge.
http://www.python.org/


For making Windows installer.
You will need sip for this.

sip-4.5.2., Python C/C++ Bindings Generator.
http://www.riverbankcomputing.co.uk/sip/

Running
--------    
    python pootling-editor.py
    
Usage:
-------- 
    python pootling-editor.py [OPTION] [filename]

if the filename is given, the editor will open the file.

options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

  
Bug Reporting/Feature requests
------------------------------
You can always report bugs or feature requests on the mailing list but because of the increase
in users and the fact that bug reports do go missing it is probably best to place your
bug report in Bugzilla: http://bugs.wordforge.org/

If you have a traceback or a patch then please include it.  Also please be quite specific
about how the bug occured and what you expected to happen.

If this is a feature request then try to be specific about how you think this feature should 
work.




