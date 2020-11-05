import os
import maya.cmds as cmds
import pymel.core as pm

def getAllAssets(asset_dir):
    asset_dict = {}
    if asset_dir:
        for asset in os.listdir(asset_dir):
            asset_dict[asset] = asset_dir + '/' + asset

        return asset_dict


def getAllVersions(base_dir):
    if base_dir[-1] == '/':
        base_dir = base_dir[0:len(base_dir) - 1]
    all_files = os.listdir(base_dir)
    all_versions = {}
    for version in all_files:
        version_dir = base_dir + '/' + version
        if version[0] == 'v' and version[1].isdigit():
            version_num = int(version.split('v')[-1])
            all_versions[version_num] = version_dir
    return all_versions


class publishUI():

    def __init__(self):
        # Create UI
        if pm.window('Publish Asset', q=True, ex=True):
            pm.deleteUI('Publish Asset', wnd=True)
        self.window = pm.window('Publish Asset', title='Publish Asset')
        pm.window(self.window, e=True, width=250, height=50)
        pm.rowColumnLayout(numberOfColumns=2)
        self.source_directory = pm.workspace(q=True, dir=True) + 'Assets'

        self.all_assets = getAllAssets(self.source_directory)
        self.asset_dropdown = pm.optionMenu(label='Assets')
        for asset in self.all_assets:
            pm.menuItem(label=asset)
            self.asset_path = self.all_assets[asset]

        pm.separator(height=20, style='none')

        self.all_steps = ['model']
        self.step_dropdown = pm.optionMenu(label='Step')
        for step in self.all_steps:
            pm.menuItem(label=step)

        pm.separator(height=20, style='none')
        pm.separator(height=20, style='none')

        asset_button = pm.button(label='Export', c=pm.Callback(self._exportAsset))

        pm.showWindow(self.window)

    def _exportAsset(self, *args):
        selected_asset = pm.optionMenu(self.asset_dropdown, q=True, v=True)
        selected_step = pm.optionMenu(self.step_dropdown, q=True, v=True)
        asset_dir = self.all_assets[selected_asset]
        model_dir = asset_dir + '/Model/Publish'
        if not os.path.isdir(model_dir):
            os.makedirs(model_dir)

        all_versions = getAllVersions(model_dir)
        if not all_versions:
            padded_number = '001'
            export_dir = model_dir + '/v%s' % padded_number
            os.makedirs(export_dir)
        else:
            # delete previous source file
            previous_dir = model_dir + '/v' + str(len(all_versions)).zfill(3)
            previous_files = os.listdir(previous_dir)
            for previous_file in previous_files:
                ext = previous_file.split('.')[-1]
                if ext == 'mb':
                    os.remove(previous_dir + '/' + previous_file)

            version_number = str(len(all_versions) + 1)
            padded_number = version_number.zfill(3)
            version_name = 'v' + padded_number
            export_dir = model_dir + '/' + version_name
            os.makedirs(export_dir)

        fbx_file = selected_asset + '_' + selected_step + '.fbx'
        export_file = export_dir + '/' + fbx_file

        pm.exportSelected(export_file, f=1, typ='FBX export', pr=1, es=1,
                          options='groups=1;ptgroups=1;materials=1;smoothing=1;normals=1')

        abc_file = selected_asset + '_' + selected_step + '.abc'
        export_file = export_dir + '/' + abc_file
        cmds.AbcExport(jobArg=r'-frameRange 0 0 -stripNamespaces -uvWrite -worldSpace -writeVisibility -wholeFrameGeo -file %s'%export_file)

        export_source = export_dir + '/' + selected_asset + '_' + selected_step + '_source_' + padded_number + '.mb'
        pm.system.saveAs(export_source)
