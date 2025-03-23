# -*- coding: utf-8 -*-
from enigma import eDVBDB
from Tools.Directories import fileExists, resolveFilename, SCOPE_CONFIG

import time


class SSUBouquetHandler:
	SSU_BOUQUET_PREFIX = "userbouquet.ServiceScanUpdates"

	def __init__(self):
		self.service_scan_timestamp = int(time.time())
		self.ssu_bouquet_filepath_prefix = "%s/%s" % (resolveFilename(SCOPE_CONFIG), self.SSU_BOUQUET_PREFIX)
		self.index_bouquet_filepath_prefix = resolveFilename(SCOPE_CONFIG) + "/bouquets"

	@staticmethod
	def reloadBouquets():
		eDVBDB.getInstance().reloadBouquets()

	def doesSSUBouquetFileExists(self, bouquet_type):
		return fileExists("%s.%s" % (self.ssu_bouquet_filepath_prefix, bouquet_type))

	def getSSUIndexBouquetLine(self, bouquet_type):
		return '#SERVICE 1:7:%d:0:0:0:0:0:0:0:FROM BOUQUET "%s.%s" ORDER BY bouquet\n' % (1 if bouquet_type == "tv" else 2, self.SSU_BOUQUET_PREFIX, bouquet_type)

	def addToIndexBouquet(self, bouquet_type):
		filepath = "%s.%s" % (self.index_bouquet_filepath_prefix, bouquet_type)
		print("[ServiceScanUpdates] Add SSU bouquet to index file [%s]" % filepath)
		with open(filepath, "r") as index_bouquet_file:
			lines = index_bouquet_file.readlines()

		foundSSUIndexBouquetLine = False
		with open(filepath, "w") as index_bouquet_file:
			for line in lines:
				if line == self.getSSUIndexBouquetLine(bouquet_type):
					foundSSUIndexBouquetLine = True
				index_bouquet_file.write(line)
			if not foundSSUIndexBouquetLine:
				index_bouquet_file.write(self.getSSUIndexBouquetLine(bouquet_type))

	def addMarker(self):
		print("[ServiceScanUpdates] Add marker to SSU bouquet")
		from datetime import datetime
		datetime_string = datetime.fromtimestamp(self.service_scan_timestamp).strftime("%d.%m.%Y - %H:%M")
		return "#SERVICE 1:64:0:0:0:0:0:0:0:0:\n#DESCRIPTION ------- %s -------\n" % datetime_string

	def createSSUBouquet(self, services, bouquet_type):
		ssu_bouquet_list = ["#NAME Service Scan Updates\n", self.addMarker()]
		for service in services:
			ssu_bouquet_list.append("#SERVICE %s\n" % service)

		filepath = "%s.%s" % (self.ssu_bouquet_filepath_prefix, bouquet_type)
		print("[ServiceScanUpdates] Create SSU bouquet [%s]" % filepath)
		with open(filepath, "w") as ssu_bouquet_file:
			ssu_bouquet_file.write(''.join(ssu_bouquet_list))

	def appendToSSUBouquet(self, services, bouquet_type):
		ssu_bouquet_list = [self.addMarker()]
		for service in services:
			ssu_bouquet_list.append("#SERVICE %s\n" % service)

		filepath = "%s.%s" % (self.ssu_bouquet_filepath_prefix, bouquet_type)
		print("[ServiceScanUpdates] Append to SSU bouquet [%s]" % filepath)
		with open(filepath, "r") as ssu_bouquet_file:
			lines = ssu_bouquet_file.readlines()

		with open(filepath, "w") as ssu_bouquet_file:
			for line in lines:
				if line == "#NAME Service Scan Updates\n":
					line = line + ''.join(ssu_bouquet_list)
				ssu_bouquet_file.write(line)

