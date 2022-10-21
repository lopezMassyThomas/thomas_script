'''
Created on Jan 10, 2022

@author: Thomas
'''
import maya.cmds as mc
import maya.api.OpenMaya as om
import pymel.core as pm
import math
import time
from thomas_script.maya.scripts.bipedRig_2 import fonctions
from thomas_script.maya.utils import attributes, maths, shapes, transform, rigging
from thomas_script.maya.scripts import matrixConstraint

'''
NOTES:
Basic torso guide done.
-Need to be able to update on the fly. But wait until testing with full build.
-
'''

class Guide:
    '''
    RigGuide create the base of the bipedRig Tool.
    This guide is suppose to be manipulated to fit the character and
    be use to build the final rig.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def guideCtrl(self, name, isRoot=None): 
        if isRoot:
            ctrl = shapes.shpDico[str(3)](name, radius=2)  # -Cube shape.
            colorID = 13
        else:
            ctrl = shapes.shpDico[str(1)](name, radius=2)  # -Cube shape. 
            colorID = 22
        loc = shapes.shpDico[str(7)](name+'loc', radius=4)  # -Loc shape.
        
        root_shp = mc.listRelatives(ctrl, s=True)
        loc_shp = mc.listRelatives(loc, s=True)
        
        mc.parent(loc_shp, ctrl, s=True, r=True)
        mc.delete(loc)
                
        for shape in [root_shp[0],loc_shp[0]]:
            mc.setAttr(shape + '.ove', 1)
            mc.setAttr(shape + '.ovc', colorID)
        ctrl = mc.rename(ctrl, name + '_ref')
        return ctrl
    
    def torso(self, spineNb):
        if mc.objExists('guide') is False:
            guideGrp = mc.group(n='guide', empty=True)
        else:
            guideGrp = 'guide'
            
        ctrlList = []
        origList = []
        rootCtrl = self.guideCtrl(name='spine_root', isRoot=True) # Create root control. 
        mc.parent(rootCtrl, guideGrp, r=True)
        ctrlList.append(rootCtrl)
        
        for nb in range(0,spineNb): # Create spine control.
            orig = mc.group(name='spine'+str(nb)+'_orig', empty=True)
            ctrl = self.guideCtrl(name='spine'+ str(nb))
            mc.parent(ctrl, orig, r=True)
            mc.parent(orig, rootCtrl, r=True)
            ctrlList.append(ctrl) 
            origList.append(orig)
            
        mc.setAttr('{}{}'.format(ctrlList[-1], '.translateY'), 60) # Set position chest.
                           
        # calculate and store weights for spacing elems.
        div = 1.0 / spineNb
        weightList = []
        invertWList = []
        x = div
        for i in range(1, spineNb):
            weightList.append(x)
            invertWList.append(x)
            x = x + div
        invertWList.reverse()

        for i in range(0, spineNb-1): # Space spine parts.
            mc.pointConstraint(ctrlList[0], origList[i], mo=False, w=invertWList[i])
            mc.pointConstraint(ctrlList[-1], origList[i], mo=False, w=weightList[i])
        
        # Create and set curve for visual reference.    
        posList = []
        knotList = []
        [posList.append((0,0,0)) for nb in range(-1,spineNb)]
        [knotList.append(nb) for nb in range(-1,spineNb)]

        curve = mc.curve(n='spine_guide_crv', d=1, p=posList, k=knotList)
        crv_shp = mc.listRelatives(curve, s=True)
        mc.setAttr(curve + '.template', 1)
        mc.setAttr(curve + '.inheritsTransform', 0)
        mc.parent(curve, rootCtrl, a=True)
        
        for nb in range(0,spineNb+1): # Link one cv per ctrl.
            cluster = mc.cluster('{}.cv[{}]'.format(curve, str(nb)))
            mc.parent(cluster[1], ctrlList[nb], r=True)
            mc.setAttr(cluster[1] + '.visibility', 0)

        return ctrlList
    
    def head(self, headNb):
        if mc.objExists('guide') is False:
            guideGrp = mc.group(n='guide', empty=True)
        else:
            guideGrp = 'guide'
                
        ctrlList = []
        origList = []
        rootCtrl = self.guideCtrl(name='neck_root', isRoot=True) # Create root control. 
        mc.parent(rootCtrl, guideGrp, r=True)
        ctrlList.append(rootCtrl) 
        
        for nb in range(0, headNb): # Create spine control.
            if nb == (headNb-1):
                name = 'head'
            else:
                name = 'neck' + str(nb)
            orig = mc.group(name = name + '_orig', empty=True)
            ctrl = self.guideCtrl(name = name)
            mc.parent(ctrl, orig, r=True)
            mc.parent(orig, ctrlList[-1], r=True)
            ctrlList.append(ctrl) 
            origList.append(orig)
            mc.setAttr('{}{}'.format(orig, '.translateY'), 10) # Set position chest.
               
    def arm(self):
        if mc.objExists('guide') is False:
            guideGrp = mc.group(n='guide', empty=True)
        else:
            guideGrp = 'guide'
        
        ctrlList = []
        origList = []
        rootCtrl = self.guideCtrl(name='L_arm_root', isRoot=True) # Create root control. 
        mc.xform(rootCtrl, ro=(-90, 0, 0), ws=True)
        
        elbowCtrl = self.guideCtrl(name='L_elbow') # Create root control.
        handCtrl = self.guideCtrl(name='L_wrist') # Create root control.
        
        
        [ctrlList.append(ctrl) for ctrl in [rootCtrl, elbowCtrl, handCtrl]]
        [mc.xform(ctrl, t=(20, 0, 0), ws=True) for ctrl in ctrlList[1:]]
        [mc.parent(ctrlList[i], ctrlList[i-1], r=True) for i in range(1, len(ctrlList))]
        mc.parent(rootCtrl, guideGrp, r=True)
        
        return
    
class Torso:
    
    def __init__(self):
        '''
        Constructor
        '''    
        self.trans = transform
        self.matrix = matrixConstraint
        self.fonc = fonctions.Core()
        
    def build_torso(self, root):
        
        guideList = [] # Get selection.
        hierarchy = mc.listRelatives(root, ad=True, typ='transform')
        hierarchy.insert(0, root)
        [guideList.append(node) for node in hierarchy if 'ref' in node]              

        mainGrp = mc.group(n='spine_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        ## Build setup for general spine orientation ctrl.----------------------
        mc.select(clear=True) # Build joints for ikHandle.
        jnt1 = mc.joint(n='spine_autoBend_0_jnt', r=True)
        jnt2 = mc.joint(n='spine_autoBend_1_jnt')
        self.trans.snap(jnt1, guideList[0])
        self.trans.snap(jnt2, guideList[-1])
        handle = mc.ikHandle(sj=jnt1, ee=jnt2)
        mc.parent(jnt1, mainGrp, a=True) # Parent to mainGrp.
        
        # Create control that drive the handle.
        ctrl = shapes.shpDico[str(2)]('spine_autoBend_ctrl', radius=10)  # -Square shape. 
        self.trans.snap(ctrl, guideList[-1])
        orig = self.trans.orig_Sel(ctrl)
        mc.parent(handle[0], ctrl)
        mc.parent(orig, mainGrp, a=True) # Parent to mainGrp.
        
        ## Build Ik controls.-------------------------------------------------
        ikCtrlList = []
        for name in ['spine_ik0', 'spine_ik1']: # Create, organize and orig controls.
            circle = shapes.shpDico[str(0)](name + '_0_ctrl', radius=10)  # -circle shape.
            sphere = shapes.shpDico[str(1)](name + '_1_ctrl', radius=2)  # -sphere shape.
            mc.parent(sphere, circle, r=True)
            ikCtrlList.append(circle)
            ikCtrlList.append(sphere)
        
            if name == 'spine_ik0': # Define position of sphere ctrls.
                self.trans.snap(circle, guideList[0])
                self.trans.snap(sphere, guideList[1])
                mc.parent(circle, mainGrp, a=True) # Parent to mainGrp.
                weight1 = 0.66
                weight2 = 0.33
            else :
                self.trans.snap(circle, guideList[-1]) # Positioning chest ctrl.
                self.trans.snap(sphere, guideList[-2])
                mc.parent(circle, jnt1, a=True)
                weight1 = 0.33
                weight2 = 0.66
        
            # Set position of sphere ctrls.     
            # constr1 = mc.pointConstraint(guideList[0], sphere, w=weight1, mo=False) 
            # constr2 = mc.pointConstraint(guideList[-1], sphere, w=weight2, mo=False)
            # mc.delete(constr1, constr2)

            self.trans.orig_Sel([circle,sphere]) 
        
            # Set rotation blend on chest Ik when general orient in use. 
            chestOrig = mc.listRelatives(ikCtrlList[-2], p=True)[0]
            mc.addAttr(ikCtrlList[-2], ln='blendRotation', at='float', k=True, dv=0.5)
        
            #deMat = mc.createNode('decomposeMatrix')
            pBlend = mc.createNode('pairBlend')
            mc.setAttr(pBlend+'.rotInterpolation', 1)
        
            mc.connectAttr(ikCtrlList[-2]+'.blendRotation', pBlend+'.weight')
            #mc.connectAttr(jnt1+'.worldMatrix[0]', deMat+'.inputMatrix')
            mc.connectAttr(jnt1+'.r', pBlend+'.inRotate2')
            #mc.connectAttr(deMat+'.outputRotate', pBlend+'.inRotate2')
            if name is 'spine_ik0':
                mc.connectAttr(pBlend+'.outRotate', chestOrig+'.r')
                mc.setAttr(ikCtrlList[-2]+'.blendRotation', 0)
            else:
                mc.connectAttr(pBlend+'.outRotateX', chestOrig+'.rotateX')
                mc.connectAttr(pBlend+'.outRotateZ', chestOrig+'.rotateZ')
                    
        ## Build curves.------------------------------------------------------
        ikCtrlList[-2], ikCtrlList[-1] = ikCtrlList[-1], ikCtrlList[-2] # Swap last two ctrls. 
        posList = []
        knotList = []
        [knotList.append(nb) for nb in range(0, len(ikCtrlList))]
        [posList.append(mc.xform(i, t=True, q=True, ws=True)) for i in ikCtrlList]
        
        curve01 = mc.curve(n='spine_linear_crv', d=1, p=posList, k=knotList)
        
        posList = []
        knotList = []
        [knotList.append(nb) for nb in range(0, len(guideList))]
        [posList.append(mc.xform(i, t=True, q=True, ws=True)) for i in guideList]
        
        curve02 = mc.curve(n='spine_cubic_crv', d=1, p=posList, k=knotList)
        
        mc.rebuildCurve(curve01, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s=4, d=3, tol=0.0001)
        mc.rebuildCurve(curve02, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=10, d=3, tol=0.0001)
        
        mc.wire(curve02, gw=False, en=1, ce=0, li=0, dds=[0,1000], w=curve01)
        mc.setAttr(curve01 + '.inheritsTransform', 0)
    
        mc.parent(curve01, curve02, curve01+'BaseWire', mainGrp, r=True) # Parent to mainGrp.
    
        for item in ikCtrlList: # Constraint CVs on ik ctrls using matrix node.
            cv = curve01 + '.controlPoints[' + str(ikCtrlList.index(item)) + ']'
            decompose = mc.createNode('decomposeMatrix')
            mc.connectAttr('{}.worldMatrix[0]'.format(item), '{}.inputMatrix'.format(decompose)) 
            mc.connectAttr('{}.outputTranslate'.format(decompose), cv)
    
        ## Build motionPath setUp.
        cnxList = []
        moPathList = []
        offset = 1.0/len(guideList[:-1])
        spacing = 0
        for i in range(0, len(guideList)):
            cnx = mc.group(n='spine' + str(i) + '_cnx', empty=True)
            mc.setAttr(cnx + '.inheritsTransform', 0)
            cnxList.append(cnx)
            moPath = mc.createNode('motionPath')
            moPathList.append(moPath)
            # Set motionPath node.
            mc.setAttr(moPath+ '.uValue', spacing)
            #mc.setAttr(moPath+'.inverseUp', 1)
            mc.setAttr(moPath+'.upAxis', 0)
            mc.connectAttr(curve02+'.worldSpace', moPath+'.geometryPath')
            mc.connectAttr(moPath+'.rotateOrder', cnx+'.rotateOrder')
            mc.connectAttr(moPath+'.allCoordinates', cnx+'.translate')
            mc.connectAttr(moPath+'.rotate', cnx+'.rotate')
            spacing = spacing+offset
    
        [mc.parent(cnxList[i], cnxList[i-1]) for i in range(1,len(cnxList))] 
    
        mc.parent(cnxList[0], mainGrp, a=True) # Parent to mainGrp.
    
        ## Build reference nodes.
        rotList = []
        posList = []
        root = mc.group(n='spine_reference', empty=True)
        for item in guideList: # Create each nodes for ref.
            i = guideList.index(item)
            rot = mc.group(n='spine_'+ str(i) +'_rot_ref', empty=True)
            pos = mc.group(n='spine_'+ str(i) +'_pos_ref', empty=True)
            mc.xform(pos, t=(1,0,0))
            mc.parent(rot, root, a=True)
            mc.parent(pos, root, a=True)
            rotList.append(rot)
            posList.append(pos)
    
        spacing = 0 # Reset variable.    
        for item in rotList: # Setup rotation along spine. Blend of pelvis and chest.
            pBlend = mc.createNode('pairBlend')
            dMat01 = mc.createNode('decomposeMatrix')
            dMat02 = mc.createNode('decomposeMatrix')
            mc.connectAttr(ikCtrlList[0] + '.worldMatrix[0]', dMat01+'.inputMatrix')
            mc.connectAttr(ikCtrlList[-1] + '.worldMatrix[0]', dMat02+'.inputMatrix')
            mc.connectAttr(dMat01 + '.outputTranslate', pBlend+'.inTranslate1')
            mc.connectAttr(dMat01 + '.outputRotate', pBlend+'.inRotate1')
            mc.connectAttr(dMat02 + '.outputTranslate', pBlend+'.inTranslate2')
            mc.connectAttr(dMat02 + '.outputRotate', pBlend+'.inRotate2')
            mc.connectAttr(pBlend + '.outRotate', item+'.rotate')
            mc.setAttr(pBlend+'.weight', spacing)
            mc.setAttr(pBlend+'.rotInterpolation', 1)
            spacing = spacing+offset
    
        [mc.parentConstraint(rotList[i], posList[i], mo=True) for i in range(0,len(posList))]   
        [mc.connectAttr(posList[i]+'.t', moPathList[i]+'.worldUpVector') for i in range(0,len(posList))] 
    
        mc.parent(root, mainGrp, r=True) # Parent to mainGrp.
        
        ## Build FK controls.                
        fkList = [] 
        for item in guideList:
            name = 'spine' + str(guideList.index(item)) + '_fk'
            ctrl = shapes.shpDico[str(2)](name+'_ctrl', radius=5)  # -Square shape. 
            fkList.append(ctrl)
            self.trans.snap(ctrl, item)
            driver = mc.group(n=name+'_dvr', empty=True)
            mc.parent(driver, ctrl, r=True)
        
            if item == guideList[0] or item == guideList[-1] :
                mc.delete(mc.listRelatives(ctrl, s=True))
        
        [mc.parent(fkList[i], fkList[i-1]) for i in range(1, len(fkList))]
        mc.parent(fkList[0], mainGrp, a=True) # Parent to mainGrp.
        self.trans.orig_Sel(fkList[1:-1])
        
        ## Connect cnx to Fk_orig.(Drives fk chain along curve)
        for i in range(1, len(fkList[:-1])):
            orig = mc.listRelatives(fkList[i], p=True)[0]
        
            if i == 1: # root.
                # Create nodes for root
                root_multMat = mc.createNode('multMatrix')
                root_deMat = mc.createNode('decomposeMatrix')
                # Connect nodes
                mc.connectAttr(cnxList[i-1]+'.worldMatrix[0]', root_multMat+'.matrixIn[0]')
                mc.connectAttr(mainGrp+'.worldInverseMatrix[0]', root_multMat+'.matrixIn[1]')
                mc.connectAttr(root_multMat+'.matrixSum', root_deMat+'.inputMatrix') 
                mc.connectAttr(root_deMat+'.outputTranslate', fkList[i-1]+'.t') 
                mc.connectAttr(root_deMat+'.outputRotate', fkList[i-1]+'.r')  
        
            # Create nodes for scale.
            scale_deMat = mc.createNode('decomposeMatrix')
            scale_multDiv = mc.createNode('multiplyDivide')
        
            # Create nodes for position/rotation.
            transfo_multMat = mc.createNode('multMatrix')
            transfo_deMat = mc.createNode('decomposeMatrix')
            transfo_multDiv = mc.createNode('multiplyDivide')
        
            # Setup nodes.
            mc.setAttr(scale_multDiv+'.operation', 2)
            [mc.setAttr(scale_multDiv+'.input1'+attr, 1) for attr in ['X', 'Y', 'Z']]
        
            # Connect nodes
                # scale.
            mc.connectAttr(mainGrp+'.worldMatrix[0]', scale_deMat+'.inputMatrix')
            mc.connectAttr(scale_deMat+'.outputScale', scale_multDiv+'.input2')
            mc.connectAttr(scale_multDiv+'.output', transfo_multDiv+'.input1')
                # transforms.
            mc.connectAttr(cnxList[i]+'.worldMatrix[0]', transfo_multMat+'.matrixIn[0]')
            mc.connectAttr(cnxList[i-1]+'.worldInverseMatrix[0]', transfo_multMat+'.matrixIn[1]')
            mc.connectAttr(transfo_multMat+'.matrixSum', transfo_deMat+'.inputMatrix')
            mc.connectAttr(transfo_deMat+'.outputTranslate', transfo_multDiv+'.input2')
            
            mc.connectAttr(transfo_multDiv+'.output', orig+'.t')
            mc.connectAttr(transfo_deMat+'.outputRotate', orig+'.r')
            
            #Fix bug. Position not updating after ConnectAttr.
            mc.xform(ikCtrlList[0], t=(0,1,0))
            mc.xform(ikCtrlList[0], t=(0,0,0))
            
        # Create nodes for chest
        index = fkList.index(fkList[-1])
        root_multMat = mc.createNode('multMatrix')
        root_deMat = mc.createNode('decomposeMatrix')
        # Connect nodes
        mc.connectAttr(cnxList[index]+'.worldMatrix[0]', root_multMat+'.matrixIn[0]')
        mc.connectAttr(cnxList[index-1]+'.worldInverseMatrix[0]', root_multMat+'.matrixIn[1]')
        mc.connectAttr(root_multMat+'.matrixSum', root_deMat+'.inputMatrix') 
        mc.connectAttr(root_deMat+'.outputTranslate', fkList[index]+'.t') 
        mc.connectAttr(root_deMat+'.outputRotate', fkList[index]+'.r')
        return mainGrp
        

    def build_skeleton(self, rootG, rootR):
        guideList = [] # Get selection.
        hierarchy = mc.listRelatives(rootG, ad=True, typ='transform')
        hierarchy.insert(0, rootG)
        [guideList.append(node) for node in hierarchy if 'ref' in node]              
        print guideList
    
        driversList = []
        childrens = mc.listRelatives(rootR, ad=True, typ='transform')
        [driversList.append(node) for node in childrens if '_dvr' in node]
        print driversList
    
        jntChain = self.fonc.createJntChain(name=None, list=guideList, autoOrient=False)
    

        # for i in range( 0, len(guideList ) ):
        #     self.matrix.matrixConstraint(driversList[0], jntChain[0], mo=False, t=True, ro=True, s=True)
        
class Head:
    
    def __init__(self):
        '''
        Constructor
        '''    
        self.trans = transform
        self.matrix = matrixConstraint
        
    def build_head(self, root):
        guideList = [] # Get selection.
        hierarchy = mc.listRelatives(root, ad=True, typ='transform')
        hierarchy.append(root)
        [guideList.append(node) for node in hierarchy if 'ref' in node]              
        guideList.reverse()
        
        mainGrp = mc.group(n='neck_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        ## Build FK controls.                
        fkList = [] 
        for item in guideList:
            if item == guideList[-1]:
                name = 'head' + '_fk'
            else:
                name = 'neck' + str(guideList.index(item)) + '_fk'
            ctrl = shapes.shpDico[str(2)](name+'_ctrl', radius=5)  # -Square shape. 
            fkList.append(ctrl)

            pos = mc.xform(item, q=True, t=True, ws=True)
            mc.xform(ctrl, t=pos)
            ref = mc.group(n=name+'_ref', empty=True)
            mc.parent(ref, ctrl, r=True)

        [mc.parent(fkList[i], fkList[i-1]) for i in range(1, len(fkList))]
        mc.parent(fkList[0], mainGrp, a=True) # Parent to mainGrp.
        self.trans.orig_Sel(fkList)
        self.trans.orig_Sel(fkList[-1], preffix='_cns')
        
class Arm:

    def __init__(self):
        '''
        Constructor
        '''    
        self.trans = transform
        self.matrix = matrixConstraint
        self.fonc = fonctions.Core()
        
    def build_arm(self, root):
        baseName = 'arm_'
        lSide = 'L_'
        rSide = 'R_'
        
        ## Get selection.
        guideList = [] 
        hierarchy = mc.listRelatives(root, ad=True, typ='transform')
        hierarchy.reverse()
        hierarchy.insert(0, root)
        [guideList.append(node) for node in hierarchy if 'ref' in node]   
        
        mainGrp = mc.group(n=baseName+lSide+'root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        jointRef = self.fonc.createJntChain('Toto', guideList, autoOrient=True)
        
        ## Build fk ctrl.
        fkCtrlList = []
        for item in guideList:
            name = baseName + lSide + str(guideList.index(item)) +'_fk_ctrl'
            ctrl = shapes.shpDico[str(3)](name, radius=5)  # -Cube shape. 
            fkCtrlList.append(ctrl)
            
            if guideList.index(item) == 0:
                mc.parent(ctrl, mainGrp, r=True)
            
        [mc.parent(fkCtrlList[i], fkCtrlList[i-1], r=True) for i in range(1, len(fkCtrlList))]
        
        [self.trans.snap(fkCtrlList[i], jointRef[i]) for i in range(0,len(fkCtrlList))]
        self.trans.orig_Sel(fkCtrlList)
        
        ## Build ik ctrl.
        ikCtrlList = []
        
                   
        
        