# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.config import config, ConfigInteger, ConfigSelection, getConfigListEntry, NoSave
from Components.Button import Button
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from enigma import eServiceReference, eServiceCenter, gFont, eTimer, eConsoleAppContainer, ePicLoad, loadPNG, getDesktop, eListboxPythonMultiContent, eListbox, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from . import _

version = "1.1"

sz_w = getDesktop(0).size().width()


class SSUSetupScreen(ConfigListScreen, Screen):
	if sz_w == 1920:
		skin = """
		<screen name="SSUSetupScreen" position="center,170" size="1200,820" title="Service Scan Updates">
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="295,70" scale="stretch" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="305,5" size="295,70" scale="stretch" alphatest="on" />
			<eLabel text="HELP" position="1110,30" size="80,35" backgroundColor="#777777" valign="center" halign="center" font="Regular;24"/>
			<widget name="key_red" position="10,5" zPosition="1" size="295,70" font="Regular;30" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<widget name="key_green" position="310,5" zPosition="1" size="300,70" font="Regular;30" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<widget name="config" position="10,90" itemHeight="35" size="1180,540" enableWrapAround="1" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="10,650" zPosition="2" size="1180,2" />
			<widget name="help" position="10,655" size="1180,145" font="Regular;32" />
		</screen>"""
	else:
		skin = """
		<screen name="SISettingsScreen" position="center,120" size="800,530" title="Service Scan Updates">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="200,40" scale="stretch" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="200,0" size="200,40" scale="stretch" alphatest="on" />
			<eLabel text="HELP" position="735,15" size="60,25" backgroundColor="#777777" valign="center" halign="center" font="Regular;18"/>
			<widget name="key_red" position="0,0" zPosition="1" size="200,40" font="Regular;22" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<widget name="key_green" position="200,0" zPosition="1" size="200,40" font="Regular;22" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" shadowColor="black" shadowOffset="-2,-2" />
			<widget name="config" position="5,50" itemHeight="30" size="790,390" enableWrapAround="1" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,445" zPosition="2" size="800,2" />
			<widget name="help" position="5,450" size="790,65" font="Regular;22" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self.session = session
		self.list = []

		ConfigListScreen.__init__(self, self.list, session=session)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self["help"] = Label("")

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "HelpActions"],
		                                 {
			                                 "red": self.keyCancel,
			                                 "green": self.keySave,
			                                 "save": self.keySave,
			                                 "cancel": self.keyCancel,
			                                 "ok": self.keySave,
			                                 "displayHelp": self.help,
		                                 }, -2)

		self.onLayoutFinish.append(self.layoutFinished)
		self["config"].onSelectionChanged.append(self.updateHelp)

	def layoutFinished(self):
		self.populateList()

	def populateList(self):
		self.list = [
			getConfigListEntry(_("Add new TV services"), config.plugins.servicescanupdates.add_new_tv_services, _("Create 'Service Scan Updates' bouquet for new TV services?")),
			getConfigListEntry(_("Add new radio services"), config.plugins.servicescanupdates.add_new_radio_services, _("Create 'Service Scan Updates' bouquet for new radio services?")),
			getConfigListEntry(_("Clear bouquet at each search"), config.plugins.servicescanupdates.clear_bouquet, _("Empty the 'Service Scan Updates' bouquet on every scan, otherwise the new services will be appended?")),
		]
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def updateHelp(self):
		cur = self["config"].getCurrent()
		if cur:
			self["help"].text = cur[2]

	def help(self):
		self.session.open(SSUHelpScreen)


class SSUHelpScreen(Screen):
	if sz_w == 1920:
		skin = """
		<screen name="SSUHelpScreen" position="center,170" size="1200,820" title="Service Scan Updates">
			<widget name="help" position="20,5" size="1100,780" font="Regular;30" />
		</screen>"""
	else:
		skin = """
		<screen name="SSUHelpScreen" position="center,120" size="800,530" title="Service Scan Updates">
			<widget name="help" position="10,5" size="760,500" font="Regular;21" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session

		self["help"] = ScrollLabel("")

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		                                 {
			                                 "red": self.close,
			                                 "cancel": self.close,
			                                 "ok": self.close,
		                                 }, -2)

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		help_txt = _("This plugin creates a favorites bouquet (for TV and Radio) with the name 'Service Scan Updates'.\n")
		help_txt += _("All new services found during the scan are inserted there together with a marker.\n")
		help_txt += _("This allows you to quickly and clearly see which new services were found,\n")
		help_txt += _("and you can add individual services to your own Favorites bouquets as usual.\n\n")
		help_txt += _("In order for the 'Service Scan Updates' bouquet to be displayed,\n")
		help_txt += _("the option 'Allow multiple bouquets' must be activated in the system settings of the box.")
		self["help"].setText(help_txt)
