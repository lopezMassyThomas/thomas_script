'''
Created on Jan 13, 2017

@author: thomas
'''

import maya.cmds as mc
import sys
# import maya.OpenMaya as om
from Qt import QtCore
from Qt import QtWidgets
from thomas_script.maya.scripts.rigToolKit import rigToolKit
from thomas_script.maya.utils import riggingLib
from thomas_script.maya.utils import attributes, maths, shapes, transform, rigging

class Core(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.riggingLib = riggingLib.RiggingLib()
        self.ui = rigToolKit.Ui_riggingToolKit()
        self.shp = shapes
#===============================================================================
# BLENDSHAPE
#===============================================================================

    def connectBStoCtrl(self, itemCtrl, itemBS, indexBS, axis, clamp, minimum, maximum, MD, value, operation):
        ctrlAttr = '{}.{}'.format(itemCtrl, axis)
        BSattr = itemBS
        nodeIndex = 0

        if clamp is True:
            nodeIndex = nodeIndex + 1
        if MD is True:
            nodeIndex = nodeIndex + 2

        if nodeIndex == 0:
            mc.connectAttr(ctrlAttr, BSattr)
        if nodeIndex == 1:
            self.createClampNode(ctrlAttr, BSattr, indexBS, minimum, maximum)
        if nodeIndex == 2:
            self.createMDNode(ctrlAttr, BSattr, indexBS, value, operation)
        if nodeIndex == 3:
            self.createClamp_MD(ctrlAttr, BSattr, indexBS, minimum, maximum, value, operation)

    def createClampNode(self, ctrlAttr, BSattr, indexBS, minimum, maximum):
        BSname = BSattr.split('.')
        baseName = BSname[0]
        clampName = '{}_{}{}'.format(baseName, 'Clamp', indexBS)

        mc.createNode('clamp', n=clampName)
        Input = '{}.{}'.format(clampName, 'ipr')
        output = '{}.{}'.format(clampName, 'opr')
        inpMin = '{}.{}'.format(clampName, 'mnr')
        inpMax = '{}.{}'.format(clampName, 'mxr')

        mc.setAttr(inpMin, int(minimum))
        mc.setAttr(inpMax, int(maximum))

        mc.connectAttr(ctrlAttr, Input)
        mc.connectAttr(output, BSattr)

    def createMDNode(self, ctrlAttr, BSattr, indexBS, value, operation):
        BSname = BSattr.split('.')
        baseName = BSname[0]
        MDName = '{}_{}{}'.format(baseName, 'MD', indexBS)

        mc.createNode('multiplyDivide', n=MDName)
        Input = '{}.{}'.format(MDName, 'i1x')
        output = '{}.{}'.format(MDName, 'ox')
        input2 = '{}.{}'.format(MDName, 'i2x')
        opera = '{}.{}'.format(MDName, 'operation')

        mc.setAttr(opera, operation)
        mc.setAttr(input2, int(value))

        mc.connectAttr(ctrlAttr, Input)
        mc.connectAttr(output, BSattr)
        return MDName

    def createClamp_MD(self, ctrlAttr, BSattr, indexBS, minimum, maximum, value, operation):
        BSname = BSattr.split('.')
        baseName = BSname[0]
        MDName = '{}_{}{}'.format(baseName, 'MD', indexBS)
        clampName = '{}_{}{}'.format(baseName, 'Clamp', indexBS)

        mc.createNode('multiplyDivide', n=MDName)
        MDinput = '{}.{}'.format(MDName, 'i1x')
        MDoutput = '{}.{}'.format(MDName, 'ox')
        input2 = '{}.{}'.format(MDName, 'i2x')
        opera = '{}.{}'.format(MDName, 'operation')
        mc.setAttr(opera, operation)
        mc.setAttr(input2, int(value))

        mc.createNode('clamp', n=clampName)
        clampInput = '{}.{}'.format(clampName, 'ipr')
        clampOutput = '{}.{}'.format(clampName, 'opr')
        inpMin = '{}.{}'.format(clampName, 'mnr')
        inpMax = '{}.{}'.format(clampName, 'mxr')
        mc.setAttr(inpMin, int(minimum))
        mc.setAttr(inpMax, int(maximum))

        mc.connectAttr(ctrlAttr, clampInput)
        mc.connectAttr(clampOutput, MDinput)
        mc.connectAttr(MDoutput, BSattr)

# ===============================================================================
# Controllers
# ===============================================================================
    def getPreffix(self, baseName):
        sel = mc.ls(sl=True)  # Get selection.
        posSel = mc.xform(sel, q=True, ws=True, t=True)  # Get position of selection.
        # Get X position and look if R or L.
        if posSel[0] == 0:
            preffix = None
        if posSel[0] > 0:
            preffix = 'L_'
        if posSel[0] < 0:
            preffix = 'R_'
        newName = '{}{}'.format(preffix, baseName)  # Set new name.
        return newName

    def create_CtrlJointOnVert(self, baseName, createJnt, mirror, ctrlType, space):
        sel = mc.ls(sl=True)  # Get selection.

        if len(sel) > 1:  # Look if multi selection.
            for i in range(0, len(sel)):
                mc.select(sel[i])
                newName = baseName
                if mirror is True:  # Set preffix if mirror is true.
                    newName = self.getPreffix(baseName)

                indexName = '{}{}'.format(newName, str(i + 1))  # Set index into name.
                rigging.ctrlJoint_onVertex(indexName, createJnt, ctrlType, mirror=False, space=space)  # Create first object.

                if mirror is True:  # Create second object if mirror is true.
                    mc.select(sel[i])
                    mirrorSel = maths.getMirrorPos()
                    mc.select(mirrorSel)

                    newName = self.getPreffix(baseName)
                    indexName = '{}{}'.format(newName, str(i + 1))
                    rigging.ctrlJoint_onVertex(indexName, createJnt, ctrlType, mirror=True, space=space)
        else:  # Same but without index.
            newName = baseName
            if mirror is True:
                newName = self.getPreffix(baseName)
            rigging.ctrlJoint_onVertex(newName, createJnt, ctrlType, mirror=False, space=space)

            if mirror is True:
                mc.select(sel)
                mirrorSel = maths.getMirrorPos()
                mc.select(mirrorSel)

                newName = self.getPreffix(baseName)
                rigging.ctrlJoint_onVertex(newName, createJnt, ctrlType, mirror=True, space=space)

    
#===============================================================================
# TOOLS    
#===============================================================================
    def getSelection(self):
        sel = mc.ls(sl=True)
        return sel

    def softSelection(self):

        selection = om.MSelectionList()
        softSelection = om.MRichSelection()
        om.MGlobal.getRichSelection(softSelection)
        softSelection.getSelection(selection)

        dagPath = om.MDagPath()
        component = om.MObject()

        iter = om.MItSelectionList(selection, om.MFn.kMeshVertComponent)
        elements = []
        weights = []
        while not iter.isDone():
            iter.getDagPath(dagPath, component)
            dagPath.pop()
            node = dagPath.fullPathName()
            fnComp = om.MFnSingleIndexedComponent(component)

            for i in range(fnComp.elementCount()):
                # elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
                elements.append(fnComp.element(i))
                weights.append(fnComp.weight(i).influence())
            iter.next()
        return elements, weights