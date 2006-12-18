 #!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module is working on the main windows of Editor

from optparse import OptionParser
from modules import MainEditor
import sys

if (sys.argv[0].endswith('py')):
    py = 'python '
else:
    py = ''
usage = py + """%prog [OPTION] [filename]\n
if the filename is given, the editor will open the file."""

strVersion = """%prog Version 0.1\n
Copyright (C) 2006 The WordForge Foundation. www.khmeros.info.
This is free software. You may redistribute copies of it under the terms of
the GNU Lesser General Public License <http://www.gnu.org/licenses/lgpl.html>.
There is NO WARRANTY, to the extent permitted by law.
Written by Hok Kakada, Keo Sophon, San Titvirak, Seth Chanratha.
"""
parser = OptionParser(usage = usage, version = strVersion)
                  
(options, args) = parser.parse_args()
argc = len(args)
if (len(sys.argv) == 1):
    MainEditor.main()

inputFileName = args[0]
MainEditor.main(inputFileName)
