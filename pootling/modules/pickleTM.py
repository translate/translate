#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module provides interface for pickle and unpickle base object of files

import os, tempfile, pickle
from PyQt4 import QtCore
from pootling.modules import World
from translate.storage import factory

def createStore(file):
    try:
        store = factory.getobject(file)
    except:
        store = None
    return store

def saveTM(TMpath):
    dic = unpickleStoreDic()
    diveSub = World.settings.value("diveIntoSub").toBool()
    path = str(TMpath)
    if (os.path.isfile(path)):
        store = createStore(path)
        if (store):
            dic[path] = store
    
    if (os.path.isdir(path)):
        storelist = []
        for root, dirs, files in os.walk(path):
            for file in files:
                store = createStore(os.path.join(root + '/' + file))
                if (store):
                    storelist.append(store)
            # whether dive into subfolder
            if (not diveSub):
                # not dive into subfolder
                break
        if (storelist):
            dic[path] = storelist
    pickleStoreDic(dic)
    return

def removeTM(TMpath):
    path = str(TMpath)
    dic = unpickleStoreDic()
    if (dic):
        try:
            del dic[path]
        except:
            pass
        pickleStoreDic(dic)
    return

def clear():
    dic = unpickleStoreDic()
    if (dic):
        dic = {}
        pickleStoreDic(dic)
    return

def pickleStoreDic(dic):
    filename = World.settings.value("fileStoredDic").toString()
    if (not filename):
        handle, filename = tempfile.mkstemp('','PKL')
    tmpFile = open(filename, 'w')
    if (dic):
        pickle.dump(dic, tmpFile)
    tmpFile.close()
    World.settings.setValue("fileStoredDic", QtCore.QVariant(filename))

def unpickleStoreDic():
    dic = {}
    filename = World.settings.value("fileStoredDic").toString()
    if (filename):
        tmpFile = open(filename, 'rb')
        try:
            dic = pickle.load(tmpFile)
        except:
            pass
        tmpFile.close()
    return dic

def getStore():
    dic = unpickleStoreDic()
    storelist = []
    if (dic):
        for k, v in dic.iteritems():
            if (not isinstance(v, list)):
                storelist.append(v)
            else:
                storelist += v
    return storelist
    
