import os
from functools import partial
import pymel.core as pm
import PySide2.QtWidgets as Qt
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
from maya import OpenMayaUI
from shiboken2 import wrapInstance

import utils

def maya_main_window():
	main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), Qt.QWidget)

class mainUI(Qt.QDialog):
    def __init__(self, parent=None):
        super(mainUI, self).__init__(parent)
        self.setWindowTitle("Asset Browser")
        self.show_dir = utils.getWorkspace()

        # Right Layout
        right_layout = Qt.QHBoxLayout()
        self.tree_view = Qt.QTreeWidget()
        right_layout.addWidget(self.tree_view)

        self.tree_view.setHeaderLabels(['name', 'version', 'path'])

        # Left Layout
        left_layout = Qt.QVBoxLayout()
        self.button = Qt.QPushButton('Import')
        self.button.clicked.connect(self.importAsset)

        self.update_button = Qt.QPushButton('Refresh')
        self.update_button.clicked.connect(self.updateTree)

        self.context_toggle = Qt.QComboBox()
        self.context_toggle.addItems(['Assets', 'Shots'])
        self.context_toggle.currentIndexChanged.connect(self.updateTree)

        left_layout.addWidget(self.context_toggle)
        left_layout.addWidget(self.button)
        left_layout.addWidget(self.update_button)

        # Main Layout
        main_layout = Qt.QHBoxLayout()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.updateTree()
        self.show()

    @QtCore.Slot(Qt.QComboBox)
    def updateTree(self, *args):
        current_context = self.context_toggle.currentText()

        self.tree_view.clear()
        asset_dir = self.show_dir + "/%s/"%current_context
        assets = self.getAllAssets(asset_dir)

        for key in sorted(assets):
            parent = Qt.QTreeWidgetItem(self.tree_view, [str(key), " ", " "])
            parent.setExpanded(True)
            asset_path = assets[key]
            task_list = []
            if current_context == 'Assets':
                task_list = ["Model", "Texture", "Materials", "Rig", "Anim", "Crowd"]
            else:
                task_list = ["Plate", "Crowd", "Light", "Anim", "Camera"]

            for task in task_list:
                task_dir = asset_path + "/%s/"%task
                task_ver_list = None
                task_child = Qt.QTreeWidgetItem(parent, ["%s"%task, " ", " "])
                if os.path.isdir(task_dir):
                    task_ver_list = self.getAllVersions(task_dir)
                if task_ver_list:
                    self.version_box = Qt.QComboBox()

                    for version in task_ver_list:
                        self.version_box.addItem(str(version))
                    self.version_box.setCurrentIndex(len(task_ver_list)-1)

                    ver = "v" + str(max(task_ver_list)).zfill(3)
                    paths = self.getFiles(task_dir + ver, task)
                    if paths:
                        child = Qt.QTreeWidgetItem(task_child, [" ", " ", str(paths[0])])
                        child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
                        self.tree_view.setItemWidget(child, 1, self.version_box)
                        #partial(self.updatePathColumn(self.version_box, child))
                        #lambda widget = self.version_box: self.updatePathColumn(widget, child)
                        self.version_box.currentIndexChanged.connect(partial(self.updatePathColumn,self.version_box, child))
                    '''
                    for version in task_ver_list:
                        ver = "v" + str(version).zfill(3)
                        paths = self.getFiles(task_dir + ver, task)

                        if paths != None:
                            for path in paths:
                                child = Qt.QTreeWidgetItem(task_child, [" ", str(version), str(path)])
                    '''

    def updatePathColumn(self, widget, column, *args):
        #current_version = widget + 1
        current_version = widget.currentText()
        ver = "v" + str(current_version).zfill(3)
        task_name = column.parent().text(0)
        asset_name = column.parent().parent().text(0)
        current_context = self.context_toggle.currentText()
        ver_dir = self.show_dir + "/%s/%s/%s/%s"%(current_context, asset_name, task_name, ver)
        paths = self.getFiles(ver_dir, task_name)
        if paths:
            column.setText(2, str(paths[0]))

    def importAsset(self):
        val = self.tree_view.selectedItems()
        child = val[0].child(0)
        if not child:
            print('Attempting Import')
        else:
            print('Please Select a File')
            return
        print(val[0].text(2))
        task = val[0].parent().text(0)
        file = val[0].text(2)
        if task == 'Model':
            pm.AbcImport(file)
        elif task == 'Anim':
            pm.FBXImport('-file', file, '-s')
        elif task == 'Rig':
            pm.createReference(file)
        else:
            pm.importFile(file)

    def getAllAssets(self, asset_dir):
        asset_dict = {}
        if asset_dir:
            for asset in os.listdir(asset_dir):
                asset_dict[asset] = asset_dir + asset
        return asset_dict

    def getAllVersions(self, base_dir):
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

    def getFiles(self, base_dir, task):
        TASK_EXTENSIONS = {'Model':'abc', "Texture":"png", "Plate":"png", "Materials":"mb", "Rig":"mb", "Anim":"fbx", "Crowd":"gscb", "Light":"mb", "Camera":"mb" }
        extension = TASK_EXTENSIONS[task]
        if task == 'Texture' or task == 'Plate':
            return self.getFileSequence(base_dir, extension)
        else:
            file_list = []
            for f in os.listdir(base_dir):
                f_ext = f.split('.')[-1]
                if f_ext == extension:
                    file_list.append(base_dir + '/' + f)

            return file_list

    def getFileSequence(self, base_dir, extension):
        file_list = []
        for f in os.listdir(base_dir):
            f_ext = f.split('.')[-1]
            tkns = f.split('_')
            if f_ext == extension:
                if tkns[1] == '1001':
                    fseq = tkns[0] + "_<UDIM>_" + tkns[-1]
                    file_list.append(fseq)
        return file_list

def run():
    main_window = maya_main_window()
    window = mainUI(parent=main_window)
    window.resize(900, 500)



