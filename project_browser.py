import os
import pymel.core as pm
import PySide2.QtWidgets as Qt
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
from maya import OpenMayaUI
from shiboken2 import wrapInstance

def maya_main_window():
	main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), Qt.QWidget)


class newAssetUI(Qt.QWidget):
    def __init__(self):
        Qt.QWidget.__init__(self)
        layout = Qt.QVBoxLayout()
        self.asset_name_field = Qt.QLineEdit()
        layout.addWidget(Qt.QLabel("Asset Name"))
        layout.addWidget(self.asset_name_field)

        self.create_asset_button = Qt.QPushButton("Create Asset")
        self.create_asset_button.clicked.connect(self.createAsset)
        layout.addWidget(self.create_asset_button)
        self.setLayout(layout)

    def createAsset(self):
        self.show_dir = pm.workspace(q=True, dir=True)
        asset_name = self.asset_name_field.text()
        asset_dir = self.show_dir + '/Assets/' + asset_name
        os.makedirs(asset_dir)

        asset_task_list = ["Sandbox", "Model", "Texture", "Lookdev", "Rig", "Anim"]

        for task in asset_task_list:
            task_dir = asset_dir + "/%s"%task
            os.makedirs(task_dir)

class newShotUI(Qt.QWidget):
    def __init__(self):
        Qt.QWidget.__init__(self)
        layout = Qt.QVBoxLayout()
        self.shot_name_field = Qt.QLineEdit()
        layout.addWidget(Qt.QLabel("Shot Name"))
        layout.addWidget(self.shot_name_field)

        self.create_shot_button = Qt.QPushButton("Create Shot")
        self.create_shot_button.clicked.connect(self.createShot)
        layout.addWidget(self.create_shot_button)
        self.setLayout(layout)

    def createShot(self):
        self.show_dir = pm.workspace(q=True, dir=True)
        shot_name = self.shot_name_field.text()
        shot_dir = self.show_dir + '/Shots/' + shot_name
        os.makedirs(shot_dir)

        shot_task_list = ["Sandbox", "Crowd", "Light", "Anim", "Camera"]

        for task in shot_task_list:
            task_dir = shot_dir + "/%s"%task
            os.makedirs(task_dir)


class mainUI(Qt.QDialog):
    def __init__(self, parent=None):
        super(mainUI, self).__init__(parent)
        self.setWindowTitle("Project Browser")
        self.show_dir = pm.workspace(q=True, dir=True)


        # Right Layout
        right_layout = Qt.QHBoxLayout()
        self.tree_view = Qt.QTreeWidget()
        right_layout.addWidget(self.tree_view)

        self.tree_view.setHeaderLabels(['type', 'name'])

        self.updateTree()

        # Left Layout
        left_layout = Qt.QVBoxLayout()
        self.new_asset_button = Qt.QPushButton('New Asset')
        self.new_asset_button.clicked.connect(self.newAsset)


        self.new_shot_button = Qt.QPushButton('New Shot')
        self.new_shot_button.clicked.connect(self.newShot)


        self.update_button = Qt.QPushButton('Refresh')
        self.update_button.clicked.connect(self.updateTree)


        self.dropdown = Qt.QComboBox()
        self.dropdown.addItems(['Assets', 'Shots'])



        left_layout.addWidget(self.dropdown)
        left_layout.addWidget(self.new_asset_button)
        left_layout.addWidget(self.new_shot_button)
        left_layout.addWidget(self.update_button)


        # Main Layout
        main_layout = Qt.QHBoxLayout()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.show()

    def updateTree(self):
        self.tree_view.clear()

        asset_dir = self.show_dir + "Assets/"
        assets = self.getAllAssets(asset_dir)
        assetParent = Qt.QTreeWidgetItem(self.tree_view, ["Assets", " ", " "])
        shot_dir = self.show_dir + "Shots/"
        shots = self.getAllAssets(shot_dir)
        shotParent = Qt.QTreeWidgetItem(self.tree_view, ["Shots", " ", " "])
        assetParent.setExpanded(True)
        shotParent.setExpanded(True)
        for key, value in assets.items():
            child_assets = Qt.QTreeWidgetItem(assetParent, [" ", str(key), " "])
        for key, value in shots.items():
            child_shots = Qt.QTreeWidgetItem(shotParent, [" ", str(key), " "])

    def newShot(self):
        self.w = newShotUI()
        self.w.resize(500,100)
        self.w.show()

    def newAsset(self):
        self.w = newAssetUI()
        self.w.resize(500,100)
        self.w.show()

    def getAllAssets(self, asset_dir):
        asset_dict = {}
        if asset_dir:
            for asset in os.listdir(asset_dir):
                asset_dict[asset] = asset_dir + asset
        return asset_dict


def run():
    main_window = maya_main_window()
    window = mainUI(parent=main_window)
    window.resize(900, 500)



