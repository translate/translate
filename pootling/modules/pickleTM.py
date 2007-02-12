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
from translate.search import match

def createStore(file):
    '''create a base object from file
    @param file: as a file path or object
    '''
    try:
        store = factory.getobject(file)
    except:
        store = None
    return store

def saveTM(TMpath):
    '''create base object of supported file, and save into TM dictionary
    @param TMpath: file or translation memory path as string'''
    dic = unpickleStoreDic()
    diveSub = World.settings.value("diveIntoSub").toBool()
    path = str(TMpath)
    
    # FIXME: this will make memory not up to date.
    if (dic.has_key(path)):
        return
    
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
    '''remove TM object of file from dictionary if it exists'''
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
    '''clear translation memory'''
    dic = unpickleStoreDic()
    if (dic):
        dic = {}
        pickleStoreDic(dic)
    return

def disableTM(TMpaths):
    '''remember specified TM path as disabledTM
    @param TMpaths: QStringList Object
    '''
    World.settings.setValue("disabledTM", QtCore.QVariant(TMpaths))
    
def pickleStoreDic(dic):
    '''pickle dictionary of TM objects into a tempo file
    @param dic: dictionary which has key as file and value as its base object'''
    filename = World.settings.value("fileStoredDic").toString()
    if (not filename):
        handle, filename = tempfile.mkstemp('','PKL')
    tmpFile = open(filename, 'w')
    if (dic):
        pickle.dump(dic, tmpFile)
    tmpFile.close()
    World.settings.setValue("fileStoredDic", QtCore.QVariant(filename))

def unpickleStoreDic():
    '''unpickle dictionary from file
    @return dic: dictionary which has key as file and value as its base object'''
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
    '''return storelist
    @return storelist: as a list of store
    '''
    dic = unpickleStoreDic()
    disabledTM = set(World.settings.value("disabledTM").toStringList())
    storelist = []
    if (dic):
        for k, v in dic.iteritems():
            if (QtCore.QString(k) in disabledTM):
                continue
            if (not isinstance(v, list)):
                storelist.append(v)
            else:
                storelist += v
    return storelist

def buildMatcher():
    '''build new matcher'''
    return match.matcher(getStore())
