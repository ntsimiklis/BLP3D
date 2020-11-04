import PySide2.QtWidgets as Qt
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore
import pymel.core as pm
import os

class mainUI(Qt.QDialog):
    def __init__(self, parent=None):
        super(mainUI, self).__init__(parent)
        self.setWindowTitle("Asset Browser")
        self.show_dir = "C:/Users/nick.tsimiklis/Documents/Nick/Projects/SWG/"
        # Right Layout
        right_layout = Qt.QHBoxLayout()
        self.tree_view = Qt.QTreeWidget()
        right_layout.addWidget(self.tree_view)

        self.tree_view.setHeaderLabels(['name', 'version', 'path'])

        self.updateTree()

        # Left Layout
        left_layout = Qt.QVBoxLayout()
        self.button = Qt.QPushButton('Import')
        self.button.clicked.connect(self.getValue)

        self.update_button = Qt.QPushButton('Refresh')
        self.update_button.clicked.connect(self.updateTree)

        self.dropdown = Qt.QComboBox()
        self.dropdown.addItems(['SWG', 'Bank', 'BLP'])

        self.update_box = Qt.QPushButton('update box')
        self.update_box.clicked.connect(self.updateBox)

        left_layout.addWidget(self.dropdown)
        left_layout.addWidget(self.button)
        left_layout.addWidget(self.update_button)
        # left_layout.addWidget(self.update_box)

        # Main Layout
        main_layout = Qt.QHBoxLayout()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def updateTree(self):
        self.tree_view.clear()
        asset_dir = self.show_dir + "Assets/"
        assets = self.getAllAssets(asset_dir)

        for key, value in assets.items():
            parent = Qt.QTreeWidgetItem(self.tree_view, [str(key), " ", " "])
            parent.setExpanded(True)
            model_dir = value + "/Model/Publish"
            tex_dir = value + "/Texture"
            model_ver_list = None
            tex_ver_list = None

            child_model = Qt.QTreeWidgetItem(parent, ['Model', " ", " "])
            child_tex = Qt.QTreeWidgetItem(parent, ['Texture', " ", " "])
            if os.path.isdir(model_dir):
                model_ver_list = self.getAllVersions(model_dir)
            if os.path.isdir(tex_dir):
                tex_ver_list = self.getAllVersions(tex_dir)
            if model_ver_list:
                for model_ver in model_ver_list:
                    ver = "v" + str(model_ver).zfill(3)
                    path = self.getFiles(model_dir + "/" + ver, "abc")[0]
                    child = Qt.QTreeWidgetItem(child_model, [" ", str(model_ver), str(path)])
            if tex_ver_list:
                for tex_ver in tex_ver_list:
                    ver = "v" + str(tex_ver).zfill(3)
                    path = self.getFiles(tex_dir + "/" + ver, "png")[0]
                    child = Qt.QTreeWidgetItem(child_tex, [" ", str(tex_ver), str(path)])


    def updateBox(self):
        self.dropdown.clear()
        self.dropdown.addItems(['lolol', 'trololol'])

    def getValue(self):
        val = self.tree_view.selectedItems()
        child = val[0].child(0)
        if not child:
            print('leafNode')
        else:
            print('parent')
        print(val[0].text(1))

    def getAllAssets(self, asset_dir):
        asset_dict = {}
        if asset_dir:
            for asset in os.listdir(asset_dir):
                asset_dict[asset] = asset_dir + "/" + asset

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

    def getFiles(self, base_dir, extension):
        file_list = []
        for f in os.listdir(base_dir):
            f_ext = f.split('.')[-1]
            if f_ext == extension:
                file_list.append(base_dir + "/" + f)

        return file_list




window = mainUI()
window.show()

