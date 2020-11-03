import pymel.core as pm


class renameUI():
    def __init__(self):
        # Create UI
        if pm.window('Naming Tool', q=True, ex=True):
            pm.deleteUI('Naming Tool', wnd=True)
        self.window = pm.window('Naming Tool', title='Naming Tool')
        pm.window(self.window, e=True, width=250, height=50)
        pm.rowColumnLayout(numberOfColumns=2)
        pm.text(label='object:')
        self.object_text = pm.textField()
        pm.text(label='material:')
        self.material_text = pm.textField()
        pm.separator(height=20, style='none')
        self.rename_button = pm.button(label='apply', c=self._renameSetup)
        pm.showWindow(self.window)

    def _renameSetup(self, *args):
        selected_list = pm.ls(sl=True)

        object_name = pm.textField(self.object_text, q=True, text=True)
        material = pm.textField(self.material_text, q=True, text=True)
        for object in selected_list:
            name_tokens = (object_name, material, '1'.zfill(3))
            pm.rename(object, '_'.join(name_tokens))
