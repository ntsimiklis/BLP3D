import os
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

import PySide2.QtWidgets as Qt
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
from maya import OpenMayaUI
from shiboken2 import wrapInstance

import utils

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

def maya_main_window():
	main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), Qt.QWidget)

class PublishUI(Qt.QDialog):
    def __init__(self, parent=None):
        super(PublishUI, self).__init__(parent)
        self.setWindowTitle("Publish Menu")
        self.show_dir = utils.getWorkspace()
        # Right Layout
        right_layout = Qt.QHBoxLayout()

        # Left Layout
        left_layout = Qt.QVBoxLayout()
        self.button = Qt.QPushButton('Publish')
        self.button.clicked.connect(self.exportAsset)

        self.update_button = Qt.QPushButton('Refresh')
        self.update_button.clicked.connect(self.refreshDropdowns)

        self.context_toggle = Qt.QComboBox()
        self.context_toggle.addItems(['Assets', 'Shots', 'Crowd'])
        self.context_toggle.currentIndexChanged.connect(self.refreshDropdowns)

        self.asset_dropdown = Qt.QComboBox()
        self.asset_dropdown.currentIndexChanged.connect(self.refreshStep)

        self.step_dropdown = Qt.QComboBox()

        left_layout.addWidget(self.context_toggle)
        left_layout.addWidget(self.asset_dropdown)
        left_layout.addWidget(self.step_dropdown)
        left_layout.addWidget(self.button)

        # Main Layout
        main_layout = Qt.QHBoxLayout()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.refreshDropdowns()
        self.show()

    def refreshStep(self):

        current_context = self.context_toggle.currentText()
        if current_context != 'Crowd':
            return
        self.step_dropdown.clear()
        current_task = self.asset_dropdown.currentText()
        task_dir = self.show_dir + '/Crowd/%s'%current_task
        crowd_assets = getAllAssets(task_dir)
        for crowd_asset in crowd_assets:
            self.step_dropdown.addItem(crowd_asset)

    def refreshDropdowns(self):
        self.asset_dropdown.clear()
        self.step_dropdown.clear()
        current_context = self.context_toggle.currentText()
        search_dir = self.show_dir + '/' + current_context
        self.all_assets = getAllAssets(search_dir)
        for key in sorted(self.all_assets):
            self.asset_dropdown.addItem(key)
        self.shot_steps = ["Crowd", "Light", "Anim", "Camera"]
        self.asset_steps = ["Model", "Texture", "Materials", "Rig", "Anim", "Crowd"]
        if current_context == 'Assets':
            self.step_dropdown.addItems(self.asset_steps)
        elif current_context == 'Crowd':
            crowds = getAllAssets(search_dir + '/%s'%self.asset_dropdown.currentText())
            pass
        else:
            self.step_dropdown.addItems(self.shot_steps)

    def exportAsset(self):
        sel = pm.ls(sl=1)

        selected_asset = self.asset_dropdown.currentText()
        selected_step = self.step_dropdown.currentText()
        asset_dir = self.all_assets[selected_asset]
        task_dir = asset_dir + '/%s'%selected_step
        if not os.path.isdir(task_dir):
            os.makedirs(task_dir)

        all_versions = getAllVersions(task_dir)
        if not all_versions:
            padded_number = '001'
            export_dir = task_dir + '/v%s' % padded_number
            version_name = 'v001'
            os.makedirs(export_dir)
        else:
            # delete previous source file
            previous_dir = task_dir + '/v' + str(len(all_versions)).zfill(3)
            previous_files = os.listdir(previous_dir)
            if selected_step == 'Model' or selected_step == 'Anim':
                for previous_file in previous_files:
                    ext = previous_file.split('.')[-1]
                    if ext == 'mb':
                        os.remove(previous_dir + '/' + previous_file)

            version_number = str(len(all_versions) + 1)
            padded_number = version_number.zfill(3)
            version_name = 'v' + padded_number
            export_dir = task_dir + '/' + version_name
            os.makedirs(export_dir)
        file_name = selected_asset + '_' + selected_step + '_' + version_name
        export_file = export_dir + '/' + file_name

        if selected_step == 'Anim' or selected_asset == 'Motions':

            start = pm.playbackOptions( q=True,min=True )
            end = pm.playbackOptions( q=True,max=True )
            mel.eval("FBXExportSplitAnimationIntoTakes -clear;")
            mel.eval('FBXExportSplitAnimationIntoTakes -v \"%s\" %s %s'%(file_name, str(start), str(end)))
            mel.eval('FBXExport -f "%s" -s'%(export_file))
            #pm.exportSelected(export_file, f=1, typ='FBX export', pr=1, es=1, options='groups=1;ptgroups=1;materials=1;smoothing=1;normals=1')

            if selected_asset == 'Motions':
                self.dialog = Qt.QDialog()
                layout = Qt.QFormLayout()

                self.dialog.setWindowTitle("Character Select")
                self.files = []
                self.assets_dir = utils.getWorkspace() + '/Assets'
                asset_list = getAllAssets(self.assets_dir)
                self.asset_box = Qt.QComboBox()
                for asset in sorted(asset_list):
                    self.asset_box.addItem(asset)
                self.asset_box.currentIndexChanged.connect(self.getAssetChars)

                self.char_box = Qt.QComboBox()

                layout = Qt.QVBoxLayout()

                self.create_shot_button = Qt.QPushButton("Select")
                self.create_shot_button.clicked.connect(self.selectChar)
                layout.addWidget(self.asset_box)
                layout.addWidget(self.char_box)
                layout.addWidget(self.create_shot_button)

                self.getAssetChars()
                self.dialog.setLayout(layout)

                ans = self.dialog.exec_()
                gcha_file = self.files[-1]

                gmo_file = export_file + '.gmo'
                cmds.glmExportMotion(outputFile=gmo_file, fromRoot=str(sel[0]), characterFile=gcha_file, automaticFootprints=True)

        elif selected_asset == 'Caches':

            start = pm.playbackOptions( q=True,min=True )
            end = pm.playbackOptions( q=True,max=True )
            cmds.glmCrowdSimulationExporter(startFrame=start, endFrame=end, crowdFieldNode=str(sel[0]),
                                            exportFromCache=False, scExpAttrs=["particleId"], scExpName=selected_step,
                                            scExpOutDir=export_dir)

        else:
            pm.exportSelected(export_file, f=1, typ='FBX export', pr=1, es=1,
                              options='groups=1;ptgroups=1;materials=1;smoothing=1;normals=1')

            abc_file = selected_asset + '_' + selected_step + '.abc'
            export_file = export_dir + '/' + abc_file

            if sel:
                root = '-root %s'%sel[0]
                cmds.AbcExport(jobArg=r'-frameRange 0 0 -stripNamespaces -uvWrite -worldSpace -writeVisibility %s -wholeFrameGeo -file %s'%(root, export_file))

            export_source = export_dir + '/' + selected_asset + '_' + selected_step + '_source_' + padded_number + '.mb'
            #pm.system.saveAs(export_source)

            pm.exportSelected(export_file, f=1, typ='mayaBinary', pr=1, es=1,
                              options='groups=1;ptgroups=1;materials=1;smoothing=1;normals=1')

    def selectChar(self):
        self.dialog.close()

    def getCharFile(self, base_dir):
        extension = 'gcha'
        file_list = []
        for f in os.listdir(base_dir):
            f_ext = f.split('.')[-1]
            if f_ext == extension:
                file_list.append(f)
                file_list.append(base_dir + '/' + f)

        return file_list

    def getAssetChars(self):
        self.char_box.clear()
        current_asset = self.asset_box.currentText()
        current_dir = self.assets_dir + '/%s/Crowd/Character'%current_asset
        if os.path.isdir(current_dir):
            versions = getAllVersions(current_dir)
            greatest = max(versions.keys())
            ver = "v" + str(greatest).zfill(3)
            ver_dir = current_dir + '/%s'%ver
            self.files = self.getCharFile(ver_dir)
            self.char_box.addItem(self.files[0])

def run():
    main_window = maya_main_window()
    window = PublishUI(parent=main_window)
    window.resize(250, 100)



