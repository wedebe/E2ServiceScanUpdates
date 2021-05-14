# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Components.config import config
from Components.ServiceScan import ServiceScan
from Tools.Directories import resolveFilename, SCOPE_CONFIG
from . import _

from .SSULameDBParser import SSULameDBParser

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

baseServiceScan_execBegin = None
baseServiceScan_execEnd = None
# baseServiceScan_scanStatusChanged = None

preScanDB = None


def dictHasKey(dictionary, key):
	if PY2:
		return dictionary.has_key(key)
	else:
		return key in dictionary


def ServiceScan_execBegin(self):
	print("[ServiceScanUpdates] ServiceScan_execBegin [%s]" % str(self.scanList[self.run]["flags"]))
	global preScanDB
	if not preScanDB and config.plugins.servicescanupdates.add_new_tv_services.value or config.plugins.servicescanupdates.add_new_radio_services.value:
		preScanDB = SSULameDBParser(resolveFilename(SCOPE_CONFIG) + "/lamedb")
	baseServiceScan_execBegin(self)


def ServiceScan_execEnd(self, onClose = True):
	print("[ServiceScanUpdates] ServiceScan_execEnd (%d) [%s]" % (self.state, str(self.scanList[self.run]["flags"])))
	if self.state == self.Done:
		if config.plugins.servicescanupdates.add_new_tv_services.value or config.plugins.servicescanupdates.add_new_radio_services.value:
			postScanDB = SSULameDBParser(resolveFilename(SCOPE_CONFIG) + "/lamedb")
			postScanServices = postScanDB.getServices()

			global preScanDB
			if preScanDB:
				preScanServices = preScanDB.getServices()

				newTVServices = []
				newRadioServices = []

				# New services
				for service_ref in postScanServices.keys():
					if not dictHasKey(preScanServices, service_ref):
						if SSULameDBParser.isVideoService(service_ref):
							newTVServices.append(service_ref)
						elif SSULameDBParser.isRadioService(service_ref):
							newRadioServices.append(service_ref)

				from .SSUBouquetHandler import SSUBouquetHandler
				bouquet_handler = SSUBouquetHandler()

				# TV services
				print("[ServiceScanUpdates] Found %d new TV services" % len(newTVServices))
				if config.plugins.servicescanupdates.add_new_tv_services.value and len(newTVServices) > 0:
					bouquet_handler.addToIndexBouquet("tv")
					if config.plugins.servicescanupdates.clear_bouquet.value:
						bouquet_handler.createSSUBouquet(newTVServices, "tv")
					else:
						if bouquet_handler.doesSSUBouquetFileExists("tv"):
							bouquet_handler.appendToSSUBouquet(newTVServices, "tv")
						else:
							bouquet_handler.createSSUBouquet(newTVServices, "tv")

				# Radio services
				print("[ServiceScanUpdates] Found %d new radio services" % len(newRadioServices))
				if config.plugins.servicescanupdates.add_new_radio_services.value and len(newRadioServices) > 0:
					bouquet_handler.addToIndexBouquet("radio")
					if config.plugins.servicescanupdates.clear_bouquet.value:
						bouquet_handler.createSSUBouquet(newTVServices, 'radio')
					else:
						if bouquet_handler.doesSSUBouquetFileExists("radio"):
							bouquet_handler.appendToSSUBouquet(newTVServices, "radio")
						else:
							bouquet_handler.createSSUBouquet(newTVServices, "radio")

				bouquet_handler.reloadBouquets()

				# Reset pre scan db
				preScanDB = None

	baseServiceScan_execEnd(self)


# def ServiceScan_scanStatusChanged(self):
# 	#print("[ServiceScanUpdates] ServiceScan_scanStatusChanged (%d)" % self.state)
# 	baseServiceScan_scanStatusChanged(self)


##############################################

def autostart(reason, **kwargs):
	if reason == 0 and "session" in kwargs:
		session = kwargs["session"]

		global baseServiceScan_execBegin
		if baseServiceScan_execBegin is None:
			baseServiceScan_execBegin = ServiceScan.execBegin
		ServiceScan.execBegin = ServiceScan_execBegin

		global baseServiceScan_execEnd
		if baseServiceScan_execEnd is None:
			baseServiceScan_execEnd = ServiceScan.execEnd
		ServiceScan.execEnd = ServiceScan_execEnd

		# global baseServiceScan_scanStatusChanged
		# if baseServiceScan_scanStatusChanged is None:
		# 	baseServiceScan_scanStatusChanged = ServiceScan.scanStatusChanged
		# ServiceScan.scanStatusChanged = ServiceScan_scanStatusChanged


def SSUMain(session, **kwargs):
	from .SSUSetupScreen import SSUSetupScreen
	session.open(SSUSetupScreen)


def SSUMenuItem(menuid, **kwargs):
	if menuid == "scan":
		return [("Service Scan Updates " + _("Setup"), SSUMain, "servicescanupdates", None)]
	else:
		return []


##############################################

def Plugins(**kwargs):
	return [
		PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart),
		PluginDescriptor(name="Service Scan Updates " + _("Setup"), description=_("Updates during service scan"), where=PluginDescriptor.WHERE_MENU, fnc=SSUMenuItem)
	]
