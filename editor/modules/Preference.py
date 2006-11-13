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
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
# 
# This module is working on Preferences

import sys
from PyQt4 import QtCore, QtGui
from ui.Ui_Preference import Ui_frmPreference
from modules.World import World

class Preference(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = None    

        #Personal Setting
        self.world = World()
        self.settings = QtCore.QSettings(self.world.settingOrg, self.world.settingApp)
        
    def initUI(self):
        """ get values and display them """
        self.overviewFont = self.getFont(self.widget[0])
        self.setCaption(self.ui.lblOverView, self.overviewFont)
        self.tuSourceFont = self.getFont(self.widget[1])
        self.setCaption(self.ui.lblSource, self.tuSourceFont)
        self.tuTargetFont = self.getFont(self.widget[2])
        self.setCaption(self.ui.lblTarget, self.tuTargetFont )
        self.commentFont = self.getFont(self.widget[3])
        self.setCaption(self.ui.lblComment, self.commentFont)
        
        self.ui.UserName.setText(self.settings.value("UserName").toString())
        self.ui.EmailAddress.setText(self.settings.value("EmailAddress").toString())
        self.ui.cbxFullLanguage.setEditText(self.settings.value("FullLanguage").toString())
        self.ui.cbxLanguageCode.setEditText(self.settings.value("Code").toString())        
        self.ui.SupportTeam.setText(self.settings.value("SupportTeam").toString())
        self.ui.cbxTimeZone.setEditText(self.settings.value("TimeZone").toString())
    
    def accepted(self):
        """ slot ok pressed """
        self.rememberFont(self.widget[0], self.overviewFont)
        self.rememberFont(self.widget[1], self.tuSourceFont)
        self.rememberFont(self.widget[2], self.tuTargetFont)
        self.rememberFont(self.widget[3], self.commentFont)

        self.settings.setValue("UserName", QtCore.QVariant(self.ui.UserName.text()))
        self.settings.setValue("EmailAddress", QtCore.QVariant(self.ui.EmailAddress.text()))
        self.settings.setValue("FullLanguage", QtCore.QVariant(self.ui.cbxFullLanguage.currentText()))
        self.settings.setValue("Code", QtCore.QVariant(self.ui.cbxLanguageCode.currentText()))
        self.settings.setValue("SupportTeam", QtCore.QVariant(self.ui.SupportTeam.text()))
        self.settings.setValue("TimeZone", QtCore.QVariant(self.ui.cbxTimeZone.currentText()))
        self.emit(QtCore.SIGNAL("settingsChanged"))
   
    def rememberFont(self, obj, fontObj):
        """input obj as string"""        
        # store font settings
        if (fontObj != None):    # TODO do we need this ???
            self.settings.setValue(str(obj + "Font"), QtCore.QVariant(fontObj.toString()))            
        
    def fontOverview(self):
        """ slot to open font selection dialog """
        self.overviewFont = self.setFont(self.widget[0])
        self.setCaption(self.ui.lblOverView, self.overviewFont)
        
    def fontSource(self):
        """ slot to open font selection dialog """
        self.tuSourceFont = self.setFont(self.widget[1])
        self.setCaption(self.ui.lblSource, self.tuSourceFont)
        
    def fontTarget(self):
        """ slot to open font selection dialog """
        self.tuTargetFont = self.setFont(self.widget[2])
        self.setCaption(self.ui.lblTarget, self.tuTargetFont)
        
    def fontComment(self):
        """ slot to open font selection dialog """
        self.commentFont = self.setFont(self.widget[3])
        self.setCaption(self.ui.lblComment, self.commentFont)
    
    def getFont(self, obj):
        """ return font object created from settings"""
        font = self.settings.value(str(obj + "Font"), QtCore.QVariant(self.defaultFont.toString()))        
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                return fontObj
        return self.defaultFont
    
    def defaultFonts(self):
        """slot Set default fonts"""
        self.setCaption(self.ui.lblOverView, self.defaultFont)
        self.overviewFont = self.defaultFont
        self.setCaption(self.ui.lblSource, self.defaultFont)
        self.tuSourceFont = self.defaultFont
        self.setCaption(self.ui.lblTarget, self.defaultFont)
        self.tuTargetFont = self.defaultFont
        self.setCaption(self.ui.lblComment, self.defaultFont)
        self.commentFont = self.defaultFont
        
    def setCaption(self, lable, fontObj):
        """ create the text from the font object and set the widget lable"""
        newText = fontObj.family() +",  "+ str(fontObj.pointSize())
        if (fontObj.bold()):
            newText.append(", " + self.tr("bold"))
        if (fontObj.italic()):
            newText.append(", " + self.tr("italic"))
        if (fontObj.underline()):
            newText.append(", " + self.tr("underline"))
        lable.setText(newText)
        
    def setFont(self, obj):
        """ open font dialog 
            return selected new font object or the old one if cancel was pressed """
        #get font settings
        oldFont = self.getFont(obj)
        newFont, okPressed = QtGui.QFontDialog.getFont(oldFont)
        if (okPressed):
            self.rememberFont(obj, newFont)
            return newFont
        return oldFont
      
    def showDialog(self):
        """ make the dialog visible """
        # lazy init 
        if (not self.ui):
            self.setWindowTitle(self.tr("Preferences"))
            self.setModal(True)        
            self.defaultFont = QtGui.QFont("Serif", 10)
            self.ui = Ui_frmPreference()
            self.ui.setupUi(self)  
            # connect signals
            self.connect(self.ui.chkHeaderAuto, QtCore.SIGNAL("stateChanged(int)"), self.ui.chkHeaderAuto.checkState) 
            self.connect(self.ui.bntOverview, QtCore.SIGNAL("clicked()"), self.fontOverview) 
            self.connect(self.ui.bntSource, QtCore.SIGNAL("clicked()"), self.fontSource) 
            self.connect(self.ui.bntTarget, QtCore.SIGNAL("clicked()"), self.fontTarget) 
            self.connect(self.ui.bntComment, QtCore.SIGNAL("clicked()"), self.fontComment) 
            self.connect(self.ui.bntDefaults, QtCore.SIGNAL("clicked()"), self.defaultFonts) 
            self.connect(self.ui.okButton, QtCore.SIGNAL("clicked()"), self.accepted)
            self.connect(self.ui.cbxFullLanguage, QtCore.SIGNAL("activated(int)"), self.setCodeIndex)
            self.connect(self.ui.cbxLanguageCode, QtCore.SIGNAL("activated(int)"), self.setLanguageIndex)
            self.widget = ["overview","tuSource","tuTarget","comment"]
            language = ['Afar','Abkhazian','Avestan','Afrikaans','Akan','Amharic','Aragonese','Arabic','Assamese','Avaric','Aymara','Azerbaijani','Bashkir','Byelorussian;Belarusian','Bulgarian','Bihari','Bislama','Bambara','Bengali; Bangla','Tibetan','Breton','Bosnian','Catalan','Chechen','Chamorro','Corsican','Cree','Czech','Church Slavic','Chuvash','Welsh','Danish','German','Divehi','Dzongkha; Bhutani','Ewe','Greek','English','Esperanto','Spanish','Estonian','Basque','Persian','Fulah','Finnish','Fijian; Fiji','Faroese','French','Frisian','Irish','Scots; Gaelic','Gallegan; Galician','Guarani','Gujarati','Manx','Hausa','Hebrew','Hindi','Hiri Motu','Croatian','Haitian; Haitian Creole','Hungarian','Armenian','Herero','Interlingua','Indonesian','Interlingue','Igbo','Sichuan Yi','Inupiak','Ido','Icelandic','Italian','Inuktitut','Japanese','Javanese','Georgian','Kongo','Kikuyu','Kuanyama','Kazakh','Kalaallisut; Greenlandic','Khmer','Kannada','Korean','Kanuri','Kashmiri','Kurdish','Komi','Cornish','Kirghiz','Latin','Letzeburgesch','Ganda','Limburgish; Limburger; Limburgan','Lingala','Lao; Laotian','Lithuanian','Luba-Katanga','Latvian; Lettish','Malagasy','Marshall','Maori','Macedonian','Malayalam','Mongolian','Moldavian','Marathi','Malay','Maltese','Burmese','Nauru','Norwegian Bokmaal','Ndebele, North','Nepali','Ndonga','Dutch','Norwegian Nynorsk','Norwegian','Ndebele, South','Navajo','Chichewa; Nyanja','Occitan; Provenc,al','Ojibwa','(Afan) Oromo','Oriya','Ossetian; Ossetic','Panjabi; Punjabi','Pali','Polish','Pashto, Pushto','Portuguese','Quechua','Rhaeto-Romance','Rundi; Kirundi','Romanian','Russian','Kinyarwanda','Sanskrit','Sardinian','Sindhi','Northern Sami','Sango; Sangro','Sinhalese','Slovak','Slovenian','Samoan','Shona','Somali','Albanian','Serbian','Swati','Sesotho','Sundanese','Swedish','Swahili','Tamil','Telugu','Tajik','Thai','Tigrinya','Turkmen','Tagalog','Tswana','Tonga','Turkish','Tsonga','Tatar','Twi','Tahitian','Uighur','Ukrainian','Urdu','Uzbek','Venda','Vietnamese','Volapuk','Walloon','Wolof','Xhosa','Yiddish','Yoruba','Zhuang','Chinese','Zulu']
            self.ui.cbxFullLanguage.addItems(language)                    
            code = ['aa','ab','ae','af','ak','am','an','ar','as','av','ay','az','ba','be','bg','bh','bi','bm','bn','bo','br','bs','ca','ce','ch','co','cr','cs','cu','cv','cy','da','de','dv','dz','ee','el','en','eo','es','et','eu','fa','ff','fi','fj','fo','fr','fy','ga','gd','gl','gn','gu','gv','ha','he','hi','ho','hr','ht','hu','hy','hz','ia','id','ie','ig','ii','ik','io','is','it','iu','ja','jv','ka','kg','ki','kj','kk','kl','km','kn','ko','kr','ks','ku','kv','kw','ky','la','lb','lg','li','ln','lo','lt','lu','lv','mg','mh','mi','mk','ml','mn','mo','mr','ms','mt','my','na','nb','nd','ne','ng','nl','nn','no','nr','nv','ny','oc','oj','om','or','os','pa','pi','pl','ps','pt','qu','rm','rn','ro','ru','rw','sa','sc','sd','se','sg','si','sk','sl','sm','sn','so','sq','sr','ss','st','su','sv','sw','ta','te','tg','th','ti','tk','tl','tn','to','tr','ts','tt','tw','ty','ug','uk','ur','uz','ve','vi','vo','wa','wo','xh','yi','yo','za','zh','zu']
            self.ui.cbxLanguageCode.addItems(code)           
            timeZone = ['(GMT-11:00) Midway Island, Samoa','(GMT-10:00) Hawaii','(GMT-09:00) Alaska','(GMT-08:00) Pacific Time(US & Canada); Tijuana','(GMT-07:00) Arizona','(GMT-07:00) Chihuahua, La Paz, Mazatlan','(GMT-07:00) Mountain Time(US & Canada)','(GMT-06:00) Central America','(GMT-06:00) Central Time(US & Canada)','(GMT-06:00) Guadalajara, Mexico City, Monterrey ','(GMT-06:00) Saskatchewan','(GMT-05:00) Bogota, Lima, Quito','(GMT-05:00) Eastern Time(US & Canada)','(GMT-05:00) Indiana (East)','(GMT-04:00) Atlantic Time (Canada)','(GMT-04:00) Caracas, La Paz','(GMT-04:00) Santiago','(GMT-03:30) NewFoundland','(GMT-03:00) Brasilia','(GMT-03:00) Buenos Aires, Georgetown','(GMT-03:00) Greenland','(GMT-02:00) Mid-Atlantic','(GMT-01:00) Azores','(GMT-01:00) Cape Verde Is.','(GMT) Casablanca, Monrovia','(GMT) Greenwich Mean Time: Dublin, Edinburgh, Lisbon, London','(GMT+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Viena','(GMT+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague','(GMT+01:00) Brussels, Copenhagen, Madrid, Paris','(GMT+01:00) Sarajevo, Skopje, Warsaw, Zagreb','(GMT+01:00) West Central Africa','(GMT+02:00) Athens, Beirut, Istanbul, Minsk','(GMT+02:00)  Bucharest','(GMT+02:00) Cairo','(GMT+02:00) Harare, Pretoria','(GMT+02:00) Helsinki, kyiv, Riga, Sofia, Tailinn, Vilnius','(GMT+02:00) Jerusalem','(GMT+03:00) Baghdad','(GMT+03:00) Brasilia','(GMT+03:00) Kuwait, Riyadh','(GMT+03:00) Moscow, St. Petersburg, Volgograd','(GMT+03:00) Nairobi','(GMT+03:30) Tehran','(GMT+04:00) Abu Dhabi, Muscat','(GMT+04:00) Baku, Tbilisi, Yerevan','(GMT+04:30) Kabul','(GMT+05:00) Ekaterinburg','(GMT+05:00) Islamabad, Karachi, Tashkent','(GMT+05:30) Chennai, Kolkata, Mumbia, New Delhi','(GMT+05:45) Kathmandu','(GMT+06:00) Almaty, Novosibirsk','(GMT+06:00) Astana, Dhaka','(GMT+06:00) Sri Jayawardenpura','(GMT+06:30) Rangoon','(GMT+07:00) Bangkok, Hanoi, Jakarta','(GMT+07:00) Krasnoyarsk','(GMT+08:00) Beijing, Chongging, Hong Kong, Urumqi','(GMT+08:00) Irkutsk, UlaanBataar','(GMT+08:00)   Kuala Lumpur, Singapore','(GMT+08:00) Perth','(GMT+08:00) Taipei','(GMT+08:00) Osaka, Sapporo, Tokyo','(GMT+09:00) Seoul','(GMT+09:00) Yakutsk','(GMT+09:30) Adelaide','(GMT+09:30) Darwin','(GMT+10:00) Brisbane','(GMT+10:00) Canberra, Melbourne, Sydney','(GMT+10:00)   Guam, Port Moresby','(GMT+10:00) Hobert']
            self.ui.cbxTimeZone.addItems(timeZone)            
        self.initUI()
        self.show()
        
    def setCodeIndex(self, index):
        """SetIndex for Combo box"""
        self.ui.cbxLanguageCode.setCurrentIndex(index)
  
    def setLanguageIndex(self, index):
        """SetIndex for Combo box"""
        self.ui.cbxFullLanguage.setCurrentIndex(index)

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    user = Preference()
    user.show()
    sys.exit(app.exec_())        
