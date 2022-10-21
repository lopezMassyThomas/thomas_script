'''
Created on Oct 13, 2022

@author: Thomas
'''
import maya.cmds as mc
import maya.api.OpenMaya as om
import pymel.core as pm
import math
import time
from thomas_script.maya.scripts.characterRigTool import fonctions
from thomas_script.maya.utils import attributes, maths, shapes, transform, rigging, matrix

reload(fonctions)
reload(shapes)
reload(matrix)
reload(transform)

'''
NOTES:
'''
SETTINGS = []

class Quadruped:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.trans = transform
        self.matrix = matrix
        self.fonc = fonctions.Core()
        
    def getSelection(self, root):
        guideList = [] # Get selection.
        hierarchy = mc.listRelatives(root, ad=True, typ='transform')
        [guideList.append(node) for node in hierarchy if 'ref' in node] 
        guideList.insert(0, root)
        
        return guideList
    
    def build_leg(self, root, scale):
        if '_L' in root:
            side = SETTINGS[5]
            invertUp=True
            invertAim = False
            rotateUp = True
            uiSpacingX = 12
        else :
            side = SETTINGS[4]
            invertUp=False
            invertAim = True
            rotateUp = True
            uiSpacingX = -12
            
        baseName = root.split('_')[0] + side
        
        guideList = self.getSelection(root)
        guideList.reverse()
        
        mainGrp = mc.group(n=baseName+'_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        # Create joint chain ik (later used as ik joints)
        tag = 'ik'
        joints= self.fonc.create_oriented_jointChain(guideList, baseName, tag, invertUp, invertAim, rotateUp)

        # Create set of ikHandles.
        ikHandle = mc.ikHandle(sj=joints[0], ee=joints[2], sol='ikRPsolver')[0]
        footHandle = mc.ikHandle(sj=joints[2], ee=joints[3], sol='ikSCsolver')[0]
        toeHandle = mc.ikHandle(sj=joints[3], ee=joints[-1], sol='ikSCsolver')[0]
        
        # Get position foot.
        footLoc = mc.xform(joints[-2], t=True, ws=True, q=True)
        footRot = mc.xform(joints[-2], ro=True, ws=True, q=True)
        
        # Set handles main group
        handlesGrp = mc.group(n=baseName+'_ikHandles_grp', empty=True)
        mc.xform(handlesGrp, t=footLoc)

        # Group each handle.
        offsetList = []
        constrList = []
        origList = []
        for handle in [ikHandle, footHandle, toeHandle]:
            offset = mc.group(n=handle+'_offset', empty=True)
            constr = mc.group(offset, n=handle+'_constr')
            orig = mc.group(constr, n=handle+'_orig')
            
            mc.xform(orig, t=footLoc)
            mc.parent(handle, offset, a=True)
            mc.parent(orig, handlesGrp, a=True)
            
            offsetList.append(offset)
            constrList.append(constr)
            origList.append(orig)
            
        ### Create ik controls.
        ikCtrl = shapes.shpDico[str(2)](baseName+'_ik_ctrl', radius=4*scale)  # -square shape.
        mc.xform(ikCtrl, t=footLoc)
        ikOrig = self.trans.orig_Sel(ikCtrl)
        self.trans.orig_Sel(ikCtrl, suffix='_offset')
        
        self.matrix.matrixConstraint_old(ikCtrl, handlesGrp, mo=True)
        
        ankleCtrl = shapes.shpDico[str(1)](baseName+'_ikRot_ctrl', radius=2*scale)  # -circle shape.
        mc.xform(ankleCtrl, t=mc.xform(joints[-3], t=True, ws=True, q=True))
        mc.xform(ankleCtrl, ws=True, piv=footLoc)
        ankleCtrlOrig = self.trans.orig_Sel(ankleCtrl)
        mc.xform(ankleCtrlOrig, ws=True, piv=footLoc)
        mc.parent(ankleCtrlOrig, ikCtrl)

        self.matrix.matrixConstraint_old(ankleCtrl, constrList[0], mo=True, t=False, s=False)
        
        toeCtrl = shapes.shpDico[str(0)](baseName+'_toe_ctrl', radius=2*scale)  # -circle shape.
        mc.xform(toeCtrl, ro=(0,0,90), ws=True)
        mc.makeIdentity(toeCtrl, apply=True, t=1, r=1, s=1, n=0, pn=1)
        mc.xform(toeCtrl, t=footLoc, ro=footRot)
        mc.parent(self.trans.orig_Sel(toeCtrl), ikCtrl)
        
        self.matrix.matrixConstraint_old(toeCtrl, constrList[-1], mo=True, s=False)
       
        # Place pole vector ctrl
        posVector = self.fonc.getPoleVectorPosition(joints[0:3], distance=1)
        pvCtrl = shapes.shpDico[str(7)](baseName +'_ik_pVect_ctrl', radius=2*scale)  # -loc shape.
        mc.xform(pvCtrl, ws=True, t=(posVector.x, posVector.y, posVector.z))
        pvOrig = self.trans.orig_Sel(pvCtrl)
        
        # Create pole vector constraint.
        mc.poleVectorConstraint(pvCtrl, ikHandle)
        
        # Setup PV driver joints.
        tag = 'pVect'
        poleV_driver = self.fonc.create_oriented_jointChain([guideList[0], guideList[2]], baseName, tag, invertUp, invertAim)
        
        # Create PV ikHandle.
        pvHandle = mc.ikHandle(sj=poleV_driver[0], ee=poleV_driver[-1], sol='ikSCsolver')
        mc.parent(pvHandle[0], handlesGrp)
        
        # Connect PV ctrl and PV driver.
        mc.parentConstraint(poleV_driver[0], pvOrig, mo=True)

        # Organize under main grp.
        mc.setAttr(handlesGrp+'.inheritsTransform', 0)
        for item in [joints[0], ikOrig, handlesGrp, pvOrig, poleV_driver[0]]:
            mc.parent(item, mainGrp)
        mc.setAttr(poleV_driver[0]+'.visibility', 0)
        
        ### Create spring chain driver
        pm.loadPlugin('ikSpringSolver.mll')
        tag = 'spring'
        driverJoints= self.fonc.create_oriented_jointChain(guideList, 'driver'+baseName, tag, invertUp, invertAim, rotateUp)
        springhandle = mc.ikHandle(sj=driverJoints[0], ee=driverJoints[-2], sol='ikSpringSolver', ap=False)[0]
        
        # Create pole vector constraint.
        mc.poleVectorConstraint(pvCtrl, springhandle)
        
        # Organize.
        mc.parent(springhandle, handlesGrp)
        mc.parent(origList[0], driverJoints[2])
        mc.parent(origList[1], driverJoints[3])
        mc.parent(driverJoints[0], mainGrp)
        mc.setAttr(driverJoints[0]+'.visibility', 0)

        # OrientConstr ankle ctrl to follow Spring chain.
        mc.orientConstraint(origList[0], ankleCtrlOrig, mo=True)
        
        # Connect spring handle .twist to fix issue with Y rotation.
        decompose = mc.createNode('decomposeMatrix')
        mc.connectAttr('{}.worldMatrix[0]'.format(mainGrp), '{}.inputMatrix'.format(decompose))
        mc.connectAttr('{}.outputRotateY'.format(decompose), '{}.twist'.format(springhandle))

        return mainGrp