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

class SetProjectUI(Qt.QDialog):
    def __init__(self, parent=None):
        super(SetProjectUI, self).__init__(parent)
        self.setWindowTitle("Set Project")
        self.setFixedWidth(200)
        self.setFixedHeight(100)

        self.button = Qt.QPushButton('Set Project')
        self.button.clicked.connect(self.setProject)

        # Main Layout
        main_layout = Qt.QHBoxLayout()

        main_layout.addWidget(self.button)

        self.setLayout(main_layout)


    def setProject(self):
        workspace_path = None;
        dialog = Qt.QFileDialog(self)
        dialog.setFileMode(Qt.QFileDialog.Directory)
        dialog.Option(Qt.QFileDialog.ShowDirsOnly)
        if dialog.exec_():
            workspace_path = str(dialog.selectedFiles()[0])

        if workspace_path:
            pm.workspace.chdir(workspace_path)
            pm.workspace(workspace_path, openWorkspace=True)


        print pm.workspace(q=True, dir=True)
        self.close()


def run():
    main_window = maya_main_window()
    window = SetProjectUI(parent=main_window)
    window.show()

