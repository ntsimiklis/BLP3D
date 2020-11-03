import pymel.core as pm
import maya.cmds as cmds


def deleteNamespaces():
    cmds.namespace(set=':')
    #
    skipNamespaces = ['UI', 'shared']
    def getNs(skipNamespaces):
        ns = []
        if cmds.namespaceInfo(lon=True):
            for i in cmds.namespaceInfo(lon=True):
                if not i in skipNamespaces:
                    ns.append(i)
        return ns
    ns = getNs(skipNamespaces)
    while ns:
        for i in ns:
            try:
                cmds.namespace(mv=[i, ':'], f=True)
                cmds.namespace(rm=i)
            except:
                if not i in skipNamespaces:
                    skipNamespaces.append(i)
        ns = getNs(skipNamespaces)