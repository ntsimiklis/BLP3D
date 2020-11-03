import os
import maya.cmds as cmds

def _null(*args):
    pass

ICON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/icons/'

class _shelf():
    def __init__(self, name="BLP", iconPath=ICON_DIR):
        self.name = name

        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        cmds.setParent(self.name)
        self.build()

    def build(self):
        pass

    def addButton(self, label, icon="", command=_null, doubleCommand=_null):
        cmds.setParent(self.name)
        if icon:
            icon = self.iconPath + icon
        cmds.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand,
                       imageOverlayLabel=label, olb=self.labelBackground, olc=self.labelColour)

    def _cleanOldShelf(self):
        if cmds.shelfLayout(self.name, ex=1):
            if cmds.shelfLayout(self.name, q=1, ca=1):
                for each in cmds.shelfLayout(self.name, q=1, ca=1):
                    cmds.deleteUI(each)
        else:
            cmds.shelfLayout(self.name, p="ShelfLayout")


class blyShelf(_shelf):
    def build(self):
        self.addButton(label='renamer', icon='renamer.png', command='import renamer; reload(renamer); renamer.renameUI()')
        self.addButton(label='delNS', icon='delNS.png', command='import utils; reload(utils); utils.deleteNamespaces()')

