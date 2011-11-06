from enigma import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, crawlDirectory
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigSelection, getConfigListEntry, config

import os
import sys
import re

class HddInfo(ConfigListScreen, Screen):
	def __init__(self, session, device):
		Screen.__init__(self, session)
		self.device = device
		self.list = []
		self.list.append(getConfigListEntry(_("Standby timeout:"), config.usage.hdd_standby))
		
		ConfigListScreen.__init__(self, self.list)
		
		self["key_green"] = Button("")
		self["key_red"] = Button(_("Ok"))
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["model"] = Label("Model: unknow")
		self["serial"] = Label("Serial: unknow")
		self["firmware"] = Label("Firmware: unknow")
		self["cylinders"] = Label("Cylinders: unknow")
		self["heads"] = Label("Heads: unknow")
		self["sectors"] = Label("Sectors: unknow")
		self["readDisk"] = Label("Read disk speed: unknow")
		self["readCache"] = Label("Read disk cache speed: unknow")
		self["temp"] = Label("Disk temperature: unknow")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.keyCancel,
			#"yellow": self.yellow,
			"red": self.keySave,
			"cancel": self.keyCancel,
		}, -2)
		
		self.onLayoutFinish.append(self.drawInfo)
	
	def drawInfo(self):
		device = "/dev/%s" % self.device
		#regexps
		modelRe = re.compile(r"Model Number:\s*([\w\-]+)")
		serialRe = re.compile(r"Serial Number:\s*([\w\-]+)")
		firmwareRe = re.compile(r"Firmware Revision:\s*([\w\-]+)")
		cylindersRe = re.compile(r"cylinders\s*(\d+)\s*(\d+)")
		headsRe = re.compile(r"heads\s*(\d+)\s*(\d+)")
		sectorsRe = re.compile(r"sectors/track\s*(\d+)\s*(\d+)")
		readDiskRe = re.compile(r"Timing buffered disk reads:\s*(.*)")
		readCacheRe = re.compile(r"Timing buffer-cache reads:\s*(.*)")
		tempRe = re.compile(r"%s:.*:(.*)" % device)
		
		# wake up disk... disk in standby may cause not correct value
		os.system("/sbin/hdparm -S 0 %s" % device)
		
		hdparm = os.popen("/sbin/hdparm -I %s" % device)
		for line in hdparm:
			model = re.findall(modelRe, line)
			if model:
				self["model"].setText("Model: %s" % model[0].lstrip())
			serial = re.findall(serialRe, line)
			if serial:
				self["serial"].setText("Serial: %s" % serial[0].lstrip())
			firmware = re.findall(firmwareRe, line)
			if firmware:
				self["firmware"].setText("Firmware: %s" % firmware[0].lstrip())
			cylinders = re.findall(cylindersRe, line)
			if cylinders:
				self["cylinders"].setText("Cylinders: %s (max) %s (current)" % (cylinders[0][0].lstrip(), cylinders[0][1].lstrip()))
			heads = re.findall(headsRe, line)
			if heads:
				self["heads"].setText("Heads: %s (max) %s (current)" % (heads[0][0].lstrip(), heads[0][1].lstrip()))
			sectors = re.findall(sectorsRe, line)
			if sectors:
				self["sectors"].setText("Sectors: %s (max) %s (current)" % (sectors[0][0].lstrip(), sectors[0][1].lstrip()))
		hdparm.close()
		hdparm = os.popen("/sbin/hdparm -t %s" % device)
		for line in hdparm:
			readDisk = re.findall(readDiskRe, line)
			if readDisk:
				self["readDisk"].setText("Read disk speed: %s" % readDisk[0].lstrip())
		hdparm.close()
		hdparm = os.popen("/sbin/hdparm -T %s" % device)
		for line in hdparm:
			readCache = re.findall(readCacheRe, line)
			if readCache:
				self["readCache"].setText("Read disk cache speed: %s" % readCache[0].lstrip())
		hdparm.close()
		hddtemp = os.popen("/var/sbin/hddtemp -q %s" % device)
		for line in hddtemp:
			temp = re.findall(tempRe, line)
			if temp:
				self["temp"].setText("Disk temperature: %s" % temp[0].lstrip())
		hddtemp.close()
	
