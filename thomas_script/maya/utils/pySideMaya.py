'''
Created on Sep 23, 2014

@author: damien
'''

import Qt

if Qt.__binding__ == "PySide2":
    import shiboken2 as shibo
else:
    import shiboken as shibo

#===============================================================================
#EIGHTVFX
#from common.utils import system
# if system.isInMaya():
#     import maya.OpenMayaUI as mui
#===============================================================================
import maya.OpenMayaUI as mui#HOME

from Qt import QtCore
from Qt import QtWidgets

def wrapinstance(ptr, base=None):
    """
    Utility to convert a pointer to a Qt class instance (PySide/PyQt compatible)

    :param ptr: Pointer to QObject in memory
    :type ptr: long or Swig instance
    :param base: (Optional) Base class to wrap with (Defaults to QObject, which should handle anything)
    :type base: QtGui.QWidget
    :return: QWidget or subclass instance
    :rtype: QtGui.QWidget
    """
    if ptr is None:
        return None
    ptr = long(ptr) #Ensure type
    if 'shibo' in globals():
        if base is None:
            qObj = shibo.wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtWidgets, cls):
                base = getattr(QtWidgets, cls)
            elif hasattr(QtWidgets, superCls):
                base = getattr(QtWidgets, superCls)
            else:
                base = QtWidgets.QWidget
        return shibo.wrapInstance(long(ptr), base)
    else:
        return None


def unwrap_instance(qt_object):
    '''Return pointer address for qt class instance
    '''
    return long(shibo.getCppPointer(qt_object)[0])


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapinstance(long(ptr))


def getMayaPath(qt_object):
    return mui.MQtUtil.fullName(long(unwrap_instance(qt_object)))


def toQtObject(mayaName):
    '''
    Given the name of a Maya UI element of any type,
    return the corresponding QWidget or QAction.
    If the object does not exist, returns None
    '''
    ptr = mui.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = mui.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = mui.MQtUtil.findMenuItem(mayaName)
    if ptr is not None:
        return wrapinstance(long(ptr))