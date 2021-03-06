from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox

from Common import TMP_SETTINGS_PWD, TMP_IMPORT_PWD, SettingsLoader
from Deflate import STDeflate

import os
import shutil

def SettingEntry(name, published):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/install_now.png"))
	return (pixmap, name, published)
	
def installSettings(id):
	try:
		shutil.rmtree(TMP_IMPORT_PWD)
	except:
		pass
	
	api = SAPCL()
	result = api.getChannelsSetting(id)
	if not result["result"]:
		return False
		
	STDeflate().deflate(result["filename"])
	
	settings = SettingsLoader()
	settings.apply()
	
	try:
		shutil.rmtree(TMP_SETTINGS_PWD)
	except Exception, e:
		pass
		
	try:
		shutil.rmtree(TMP_IMPORT_PWD)
	except Exception, e:
		pass

	try:
		os.unlink(result["filename"])
	except Exception, e:
		pass
		
	return True

class STSettings(Screen):
	def __init__(self, session, settings):
		Screen.__init__(self, session)
		
		self.session = session
		self.settings = settings

		self['list'] = List([])
		self["key_green"] = Button("")
		self["key_red"] = Button(_("Install"))
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
			"red": self.download
		}, -2)
		
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		for setting in self.settings:
			self.cachelist.append(SettingEntry(setting["name"], setting["published"]))
			
		self["list"].setList(self.cachelist)
		
	def downloadBackground(self):
		if not installSettings(self.settings[self.index]["id"]):
			self.session.open(MessageBox, _("Cannot download settings"), MessageBox.TYPE_ERROR)
			return
			
		self.session.open(MessageBox, _("Settings installed"), type = MessageBox.TYPE_INFO, timeout = 5)
		config.sifteam.settings.currentsettings.value = self.settings[self.index]["id"]
		config.sifteam.settings.currentsettingsdate.value = self.settings[self.index]["published"]
			
	def download(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		
		self.session.open(ExtraActionBox, _("Downloading settings"), _("Downloading ..."), self.downloadBackground)
		
	def quit(self):
		self.close()