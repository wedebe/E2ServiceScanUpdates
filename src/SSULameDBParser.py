# -*- coding: utf-8 -*-
# Based on code from adenin and realriot
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

FLAG_SERVICE_NEW_FOUND = 64

class SSULameDBParser:
	def __init__(self, filename):
		self.filename = filename
		self.version = 4
		self.services = {}
		self.transponders = {}

		self.parse(self.load())

	def load(self):
		lamedb_file = None
		try:
			print("[ServiceScanUpdates] Reading file: " + self.filename)
			import codecs
			lamedb_file = codecs.open(self.filename, "r", encoding='utf-8', errors='ignore')
			lines = lamedb_file.readlines()
			if lines[0].find("/3/") != -1:
				self.version = 3
			elif lines[0].find("/4/") != -1:
				self.version = 4
			else:
				lines = None
				print("[ServiceScanUpdates] Unsupported lamedb version")
		except Exception as e:
			print("Exception: " + str(e))
			lines = None
		finally:
			if lamedb_file:
				lamedb_file.close()

		return lines

	def parse(self, lines):
		if lines is None:
			return

		import re
		reading_transponders = False
		reading_services = False
		tmp = []
		self.transponders = {}
		self.services = {}

		print("[ServiceScanUpdates] Parsing content of file: " + self.filename)
		for line in lines:
			line = line.rstrip('\n')
			if PY2:
				line = line.encode('utf-8')

			# Got END tag.
			if line == "end":
				reading_transponders = False
				reading_services = False
				continue

			# Got START tag for: transponders.
			if line == "transponders":
				reading_transponders = True
				continue

			# Got START tag for: services.
			if line == "services":
				reading_services = True
				continue

			# Read data for: transponders.
			# 1 - 00820000:1ce8:0071
			# 2 - s 12188000:27500000:1:4:130:2:0
			if reading_transponders:
				if line == "/":
					self.transponders[tmp[0]] = tmp[1].replace("\t", "").replace(" ", ":")
					tmp = []
				else:
					tmp.append(line)

			# Read data for: services.
			# 1 - 2889:00c00000:040f:0001:25:0:0
			# 2 - ARD-alpha HD
			# 3 - p:ARD,C:0000
			if reading_services:
				if line[0:2] == "p:":
					key = tmp[0].split(":")
					if len(key) == 6:
						service_id, dvb_namespace, transport_stream_id, original_network_id, service_type, service_number = tmp[0].split(':')
					elif len(key) == 7:
						service_id, dvb_namespace, transport_stream_id, original_network_id, service_type, service_number, source_id = tmp[0].split(':')
					else:
						continue

					transponder = dvb_namespace + ":" + service_id + ":" + original_network_id

					# Strip leading 0 from hex strings.
					service_id = re.sub("^0+", "", service_id)
					dvb_namespace = re.sub("^0+", "", dvb_namespace)
					transport_stream_id = re.sub("^0+", "", transport_stream_id)
					original_network_id = re.sub("^0+", "", original_network_id)
					service_type = str(hex(int(service_type))).lower()
					service_type = service_type[2:len(service_type)]
					service_type = re.sub("^0+", "", service_type)
					service_ref = "1:0:" + service_type.upper() + ":" + service_id.upper() + ":" + transport_stream_id.upper() + \
					              ":" + original_network_id.upper() + ":" + dvb_namespace.upper() + ":0:0:0:"

					self.services[service_ref] = {'service_id': service_id,  # Service id (SSID value from stream) in Hex.
					                              'dvb_namespace': dvb_namespace,  # DVB namespace in Hex.
					                              'transport_stream_id': transport_stream_id,  # Transport stream id in Hex.
					                              'original_network_id': original_network_id,  # Original network id in Hex.
					                              'service_type': service_type,  # Service type.
					                              'service_number': service_number,  # Service number in Decimal.
					                              'transponder': transponder,  # Transponder.
					                              'service_name': tmp[1]}  # Service name.

					# Split and parse provider data.
					provdata = []
					tmpprovdata = line.split(',')
					for tmpdata in tmpprovdata:
						psdata = tmpdata.split(':')
						if psdata[0] == "p":
							self.services[service_ref]['provider'] = psdata[1]
						else:
							data = {}
							# Strip leading 0 of hex fields.
							psdata[1] = re.sub("^0+", "", psdata[1])
							data[psdata[0]] = psdata[1]
							provdata.append(data)
					self.services[service_ref]['provider_data'] = provdata
					tmp = []
				# print('[ServiceScanUpdates] lamedb entry: ' + str(self.services[service_ref]))
				else:
					tmp.append(line)

	def getServiceBySRef(self, service_ref):
		try:
			return self.services[service_ref]
		except:
			return None

	def getServices(self):
		return self.services

	@staticmethod
	def isVideoService(service_ref):
		service_type = int(str(service_ref.split(':')[2]), 16)
		print("[ServiceScanUpdates] Check isVideoService [%s] (%d)" % (service_ref, service_type))
		# SD-Video or HD-Video
		return service_type in (1, 4, 5, 6, 11, 22, 23, 24,) or service_type in (17, 25, 26, 27, 28, 29, 30, 31,)

	@staticmethod
	def isRadioService(service_ref):
		service_type = int(str(service_ref.split(':')[2]), 16)
		# Radio
		return service_type in (2, 10,)

	@staticmethod
	def isDataService(service_ref):
		service_type = int(str(service_ref.split(':')[2]), 16)
		# Data
		if service_type in (3, 12, 13, 14, 15, 16, 128, 129,):
			result = True
		else:
			result = False
		return result

	@staticmethod
	def hasNewFlag(service_ref):
		from enigma import eDVBDB, eServiceReference
		return eDVBDB.getInstance().getFlag(eServiceReference(str(service_ref))) & FLAG_SERVICE_NEW_FOUND
