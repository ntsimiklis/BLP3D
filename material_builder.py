import os
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

import PySide2.QtWidgets as Qt
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
from maya import OpenMayaUI
from shiboken2 import wrapInstance
from functools import partial

import utils
import publish

def maya_main_window():
	main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), Qt.QWidget)

class materialBuilderUI(Qt.QDialog):
    def __init__(self, parent=None):
        super(materialBuilderUI, self).__init__(parent)
        self.setWindowTitle("Material Builder")
        self.show_dir = utils.getWorkspace()
        # Right Layout
        right_layout = Qt.QHBoxLayout()

        self.tree_view = Qt.QTreeWidget()
        right_layout.addWidget(self.tree_view)

        self.tree_view.setHeaderLabels(['name', 'select', 'version', 'path'])

        # Left Layout
        left_layout = Qt.QVBoxLayout()
        self.button = Qt.QPushButton('Import')
        self.button.clicked.connect(self._importMaterials)

        self.update_button = Qt.QPushButton('Refresh')
        self.update_button.clicked.connect(self._refreshTree)


        left_layout.addWidget(self.button)
        left_layout.addWidget(self.update_button)

        # Main Layout
        main_layout = Qt.QHBoxLayout()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self._refreshTree()
        self.show()

    def _refreshTree(self, *args):
        self.tree_view.clear()
        asset_dir = self.show_dir + "/Assets/"
        assets = publish.getAllAssets(asset_dir)

        for asset in sorted(assets):

            task_dir = asset_dir + "%s/Materials/"%asset

            parent = Qt.QTreeWidgetItem(self.tree_view, [str(asset), " ", " ", " "])
            parent.setFlags(parent.flags() | QtCore.Qt.ItemIsEditable)
            self.version_box = Qt.QComboBox()
            if os.path.isdir(task_dir):
                task_ver_list = publish.getAllVersions(task_dir)

                if task_ver_list:
                    ver = "v" + str(max(task_ver_list)).zfill(3)

                    for version in task_ver_list:
                        self.version_box.addItem(str(version))
                    self.version_box.setCurrentIndex(len(task_ver_list) - 1)
                    self._updatePathColumn(self.version_box, parent)
                    self.version_box.currentIndexChanged.connect(partial(self._updatePathColumn, self.version_box, parent))
            self.asset_checkbox = Qt.QCheckBox()
            self.asset_checkbox.setStyleSheet("QCheckBox::indicator:unchecked"
                           "{"
                           "background-color : rgb(100, 100, 100);"
                           "}")

            self.tree_view.setItemWidget(parent, 1, self.asset_checkbox)
            self.tree_view.setItemWidget(parent, 2, self.version_box)



    def _updatePathColumn(self, widget, row, *args):
        current_version = widget.currentText()
        ver = "v" + str(current_version).zfill(3)
        asset_name = row.text(0)
        ver_dir = self.show_dir + "/Assets/%s/Materials/%s"%(asset_name, ver)
        paths = self._getFiles(ver_dir)
        for path in paths:
            row.setText(3, str(path))

    def _getFiles(self, base_dir):
        extension = 'mb'
        file_list = []
        for f in os.listdir(base_dir):
            f_ext = f.split('.')[-1]
            if f_ext == extension:
                file_list.append(base_dir + '/' + f)

        return file_list

    def _iterItems(self, root):
        child_count = root.childCount()
        item_list = []
        for i in range(child_count):
            item = root.child(i)
            item_list.append(item)

        return item_list


    def _importMaterials(self, *args):
        root = self.tree_view.invisibleRootItem()
        for item in self._iterItems(root):
            check_value = self.tree_view.itemWidget(item, 1)
            if check_value.isChecked() == True:
                file_path = item.text(3)
                material_reference = pm.createReference(file_path, returnNewNodes=True, namespace='material')
                groups = pm.ls(type='transform', assemblies=True)
                material_group = None
                for group_node in groups:
                    if str(group_node) == 'material_GRP':
                        material_group = group_node
                if not material_group:
                    material_group = pm.group(n='material_GRP')
                ref_nodes = pm.ls(material_reference, assemblies=True)
                for ref in ref_nodes:
                    if 'material' in ref.namespace():
                        pm.parent(ref, material_group)

def run():
    main_window = maya_main_window()
    window = materialBuilderUI(parent=main_window)
    window.resize(500, 500)



