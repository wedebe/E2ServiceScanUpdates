from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelectionNumber, ConfigSelection
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, gettext

PluginLanguageDomain = "ServiceScanUpdates"
PluginLanguagePath = "SystemPlugins/ServiceScanUpdates/locale/"


def isDreamOS():
	try:
		from enigma import eMediaDatabase
	except ImportError:
		result = False
	else:
		result = True
	return result


def localeInit():
	lang = language.getLanguage()[:2]
	os.environ["LANGUAGE"] = lang
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

if not isDreamOS():
	language.addCallback(localeInit())

#######################################################
# Initialize Configuration
config.plugins.servicescanupdates = ConfigSubsection()

config.plugins.servicescanupdates.add_new_tv_services = ConfigYesNo(default=True)
config.plugins.servicescanupdates.add_new_radio_services = ConfigYesNo(default=True)
config.plugins.servicescanupdates.clear_bouquet = ConfigYesNo(default=False)
