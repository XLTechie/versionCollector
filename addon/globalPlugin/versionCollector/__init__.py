from datetime import datetime
from typing import Callable, Optional, List
from dataclasses import dataclass

import globalPluginHandler
import appModuleHandler
import api
from addonHandler import initTranslation
from logHandler import log
from NVDAObjects import NVDAObject
from scriptHandler import script

initTranslation()

@dataclass
class _AppData:
	"""Properties representing a piece of software by its metadata.
	Metadata includes name, version, bitness, and last seen timestamp.
	When comparisons are made, the lastSeen is ignored.
	"""
	__slots__ = [ "name", "is64bit", "version", "lastSeen" ]
	name: str
	is64bit: Optional[bool]
	version: Optional[str]
	lastSeen: datetime.timestamp

	def __eq__(self, other):
		if not isinstance(other, _AppData):
			return False
		if (
			self.name == other.name
			and self.version == other.version
			and self.is64bit == other.is64bit
		):
			return True
		else:
			return False

#: The main in-memory listing of per-app metadata
_appDataCache: List[_AppData] = []
#: Represents whether the LHS of the cache needs to be updated on disk. Forces an immediate cache save.
_dirtyCache: bool = False
#: Represents whether the RHS of the cache needs to be updated on disk. Doesn't force a cache save cycle.
_dirtyDates: bool = False

def isCached(app: _AppData) -> bool:
	if getCacheIndexOf(app) < 0:
		return False
	else:
		return True

def getCacheIndexOf(app) -> int:
	try:
		ind = _appDataCache.index(app)
	except ValueError:
		ind = -1
	return ind

def updateCacheDate(app, index: int) -> None:
	global _dirtyDates
	if index < 0:  # We weren't given an index, yet some how the caller knows app is cached
		index = getCacheIndexOf(app)
		if index < 0:  # Something weird is going on
			raise RuntimeError(f"Was asked to update date for an item not in the cache! {app}")
	_appDataCache[index].lastSeen = app.lastSeen
	_dirtyDates = True

def addToCache(app: _AppData, checked: bool = False) -> None:
	global _dirtyCache
	if not checked:
		if isCached(app):
			raise RuntimeError(f"Tried to add an already cached app to the cache! {app}")
	# Adding . . .
	_appDataCache.append(app)
	_dirtyCache = True
	log.debug(f"Added an app to the cache. {app}")

def _logState(message: Optional[str] = None) -> None:
	"""A debugging function which writes everything the add-on knows to the log.
	@param message An optional message to put at the top.
	"""
	#return  # Comment to disable this function
	log.debug("".join((
		"" if message is None else (message + "\n"),
		"Dumping all in-memory data.\n",
		"\tThe dates are " + ("" if _dirtyDates else "not ") + "dirty.\n",
		"\tThe cache is " + ("" if _dirtyCache else "not ") + "dirty.\n",
		"\tThe cache contains:\n",
		"\n".join(
			f"\t{app.name} | {app.is64bit} | {app.version} | {app.lastSeen}" for app in _appDataCache
		)
	)))

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.currentApp: Optional[_AppData] = None
		# Run our handler whenever the application changes
		appModuleHandler.post_appSwitch.register(self.handleAppSwitch)
		_logState("Initializing...")

	@script(gesture="kb:NVDA+Control+l", description="Temporary add-on action")
	def script_logState(self, gesture):
		_logState()

	def handleAppSwitch(self):
		"""Called as a registered extensionPoint, whenever appModuleHandler detects an application switch."""
		obj = api.getForegroundObject()
		# Handle a strange case. This is mentioned in core code. FixMe
		if obj.processHandle == 0:
			return
		currentApp = self.normalizeAppInfo(
			getattr(obj.appModule, "appName", None),
			getattr(obj.appModule, "productName", None),
			getattr(obj.appModule, "productVersion", None),
			getattr(obj.appModule, "is64BitProcess", None)
		)
		# If the current app is not the same as the previously known app, we have a new app
		if currentApp != self.currentApp:
			self.currentApp = currentApp
			ind = getCacheIndexOf(currentApp)
			if ind < 0:
				addToCache(currentApp, True)
			else:  # It's in the cache already, update the date only
				updateCacheDate(currentApp, ind)

	def normalizeAppInfo(self, shortName: str, longName: str, version: str, is64bit: bool) -> _AppData:
		"""Returns an AppData representation of the passed app metadata.
		It converts short and long names into a single (hopefully) non-repetitive name.
		Sets the lastSeen property to now.
		"""
		if longName is None or longName == "":  # No longName
			# If neither kind of name is set, this is a bad conversion, and we fail
			if shortName is None or shortName == "":
				raise ValueError("Names not set: probably not a module.")
			else:  # We can only go with the shortName
				appName = shortName.title()
		else:  # We have a longName; assume we have a shortName as well
			# If the shortName appears inside the longName, we can throw away the redundant shortName
			if longName.lower().find(shortName.lower()) >= 0:
				appName = longName
			else:  # We need both, such as for Windows Notepad
				appName = f"{shortName.title()} ({longName})"
		# Did we get a version?
		if version is not None and version != "":
			appVersion = version
		else:
			appVersion = None
		return _AppData(
			name=appName, version=appVersion, is64bit=is64bit,
			lastSeen=datetime.timestamp(datetime.now())
		)

	def _getAppModule(self, obj) -> "appModuleHandler.AppModule":
		"""Retrieves the appModule representing the application the obj is a part of by
		asking L{appModuleHandler}.
		(Based on a private method in NVDA core.)
		@return: the appModule
		"""
		if not hasattr(obj,'_appModuleRef'):
			mod = appModuleHandler.getAppModuleForNVDAObject(obj)
			if mod:
				return mod
		else:
			return obj._appModuleRef()
