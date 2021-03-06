import pymel.core as pm
def loadMenu():
	MainMayaWindow = pm.language.melGlobals['gMainWindow']

	custom_menu = pm.menu('BLP', parent=MainMayaWindow)

	pm.menuItem(label='Set Project', command="import startup; reload(startup); startup.run()", parent = custom_menu)
	pm.menuItem(label='Publish Asset', command="import publish; reload(publish); publish.run()", parent = custom_menu)
	pm.menuItem(label='Material Builder', command="import material_builder; reload(material_builder); material_builder.run()", parent = custom_menu)
	pm.menuItem(label='Asset Browser', command="import asset_browser; reload(asset_browser); asset_browser.run()", parent=custom_menu)
	pm.menuItem(label='Project Browser', command="import project_browser; reload(project_browser); project_browser.run()", parent=custom_menu)
	pm.menuItem( divider=True )