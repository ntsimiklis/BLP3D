import os
import pymel.core as pm

def setProject():
    workspace_path = "C:/Users/nick.tsimiklis/Documents/Nick/Projects/SWG/"
    pm.workspace.chdir(workspace_path)
    pm.workspace(workspace_path, openWorkspace=True)