import pymel.core as pm
def loadMenu():
	MainMayaWindow = pm.language.melGlobals['gMainWindow']

	custom_menu = pm.menu('BLP', parent=MainMayaWindow)

	pm.menuItem(label='Publish Asset', command="import publish; reload(publish); publish.publishUI()", parent = custom_menu)
	pm.menuItem(label='Import Lightrig', command="import lightrig; reload(lightrig); lightrig.importLightRig()", parent = custom_menu)
	pm.menuItem(label='Asset Browser', command="import asset_browser; reload(asset_browser);", parent=custom_menu)
	pm.menuItem( divider=True )