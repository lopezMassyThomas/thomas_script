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

'''
NOTES:
'''

SETTINGS = []

class Biped:
    
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
          
    def build_spine(self, root, scale):
        baseName = root.split('_')[0] + SETTINGS[3]
        
        guideList = self.getSelection(root)          

        mainGrp = mc.group(n=baseName+'_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        # Build setup for general spine orientation ctrl.----------------------
        mc.select(clear=True) # Build joints for ikHandle.
        jnt1 = mc.joint(n=baseName+'_autoBend_0_jnt', r=True)
        jnt2 = mc.joint(n=baseName+'_autoBend_1_jnt')
        self.trans.snap(jnt1, guideList[0])
        self.trans.snap(jnt2, guideList[-1])
        handle = mc.ikHandle(sj=jnt1, ee=jnt2)
        mc.parent(jnt1, mainGrp, a=True) # Parent to mainGrp.
        
        # Create control that drive the handle.
        ctrl = shapes.shpDico[str(2)](baseName+'_autoBend_ctrl', radius=8*scale)  # -Square shape. 
        self.trans.snap(ctrl, guideList[-1])
        orig = self.trans.orig_Sel(ctrl)
        mc.parent(handle[0], ctrl)
        mc.parent(orig, mainGrp, a=True) # Parent to mainGrp.
        
        ## Build Ik controls.-------------------------------------------------
        ikCtrlList = []
        for name in [baseName+'_ik0', baseName+'_ik1']: # Create, organize and orig controls.
            circle = shapes.shpDico[str(0)](name + '_0_ctrl', radius=8*scale)  # -circle shape.
            sphere = shapes.shpDico[str(1)](name + '_1_ctrl', radius=2*scale)  # -sphere shape.
            mc.parent(sphere, circle, r=True)
            ikCtrlList.append(circle)
            ikCtrlList.append(sphere)
        
            if name == baseName+'_ik0': # Define position of sphere ctrls.
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
        
            self.trans.orig_Sel([circle,sphere]) 
        
            # Set rotation blend on chest Ik when general orient in use. 
            chestOrig = mc.listRelatives(ikCtrlList[-2], p=True)[0]
            mc.addAttr(ikCtrlList[-2], ln='blendRotation', at='float', k=True, dv=0.5)
        
            #deMat = mc.createNode('decomposeMatrix')
            pBlend = mc.createNode('pairBlend')
            mc.setAttr(pBlend+'.rotInterpolation', 1)
        
            mc.connectAttr(ikCtrlList[-2]+'.blendRotation', pBlend+'.weight')
            mc.connectAttr(jnt1+'.r', pBlend+'.inRotate2')

            if name is baseName+'_ik0':
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
        
        curve01 = mc.curve(n=baseName+'_linear_crv', d=1, p=posList, k=knotList)
        
        posList = []
        knotList = []
        [knotList.append(nb) for nb in range(0, len(guideList))]
        [posList.append(mc.xform(i, t=True, q=True, ws=True)) for i in guideList]
        
        curve02 = mc.curve(n=baseName+'_cubic_crv', d=1, p=posList, k=knotList)
        
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
            cnx = mc.group(n=baseName +'_'+ str(i) + '_cnx', empty=True)
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
        root = mc.group(n=baseName+'_reference', empty=True)
        for item in guideList: # Create each nodes for ref.
            i = guideList.index(item)
            rot = mc.group(n=baseName+ '_'+ str(i) +'_rot_ref', empty=True)
            pos = mc.group(n=baseName+ '_' + str(i) +'_pos_ref', empty=True)
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
            name = baseName +'_'+str(guideList.index(item)) + '_fk'
            ctrl = shapes.shpDico[str(2)](name+'_ctrl', radius=8*scale)  # -Square shape. 
            fkList.append(ctrl)
            self.trans.snap(ctrl, item)
            driver = mc.group(n=name+'_drv', empty=True)
            mc.parent(driver, ctrl, r=True)
        
            if item == guideList[0] or item == guideList[-1] :
                mc.delete(mc.listRelatives(ctrl, s=True))
        
        [mc.parent(fkList[i], fkList[i-1]) for i in range(1, len(fkList))]
        mc.parent(fkList[0], mainGrp, a=True) # Parent to mainGrp.
        self.trans.orig_Sel(fkList[1:-1])
        
        ## Connect cnx to Fk_orig.(Drives fk chain along curve)
        for i in range(1, len(fkList)):
            orig = mc.listRelatives(fkList[i], p=True)[0]
            
            if i == fkList.index(fkList[-1]):
                orig = fkList[-1]
                
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
            
            
        return mainGrp

# HEAD

    def build_head(self, root, scale):
        guideList = self.getSelection(root)

        mainGrp = mc.group(n='neck_C_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        ## Build FK controls.                
        fkList = [] 
        for item in guideList:
            if item == guideList[-1]:
                name = 'head'+ SETTINGS[3] + '_fk'
            else:
                name = 'neck' + SETTINGS[3] + str(guideList.index(item)) + '_fk'
            ctrl = shapes.shpDico[str(2)](name+'_ctrl', radius=5*scale)  # -Square shape. 
            fkList.append(ctrl)

            pos = mc.xform(item, q=True, t=True, ws=True)
            mc.xform(ctrl, t=pos)
            ref = mc.group(n=name+'_drv', empty=True)
            mc.parent(ref, ctrl, r=True)

        [mc.parent(fkList[i], fkList[i-1]) for i in range(1, len(fkList))]
        mc.parent(fkList[0], mainGrp, a=True) # Parent to mainGrp.
        self.trans.orig_Sel(fkList)
        self.trans.orig_Sel(fkList[-1], suffix='_cns')
        
        return mainGrp
    
# ARMS     
        
    def build_shoulder(self, root, scale):
        baseName = root.split('_')[0]
        if '_L' in root:
            side = SETTINGS[5]
            invertUp=True
            invertAim = False
        else :
            side = SETTINGS[4]
            invertUp=False
            invertAim = True
            
        guideList = self.getSelection(root)

        mainGrp = mc.group(n='shoulder'+side+'_root', empty=True)
        
        tag = 'fk'
        jointRef = self.fonc.create_oriented_jointChain(guideList, baseName+side, tag, invertUp, invertAim)
        
        ## Build FK controls.
        fkList = [] 
        name = 'shoulder'+side
        ctrl = shapes.shpDico[str(2)](name+'_ctrl', radius=5*scale)  # -Square shape. 
        fkList.append(ctrl)
        self.trans.snap(ctrl, jointRef[0])
        
        mc.parent(ctrl, mainGrp, a=True) # Parent to mainGrp.
        ref = mc.group(n=name+'_drv', empty=True)
        mc.parent(ref, ctrl, r=True)

        orig = self.trans.orig_Sel(ctrl)
        self.trans.orig_Sel(ctrl, suffix='_cns')
        
        mc.delete(jointRef[0])
        
        return mainGrp
    
    def build_arm(self, root, scale):
        baseName = root.split('_')[0]
        if '_L' in root:
            side = SETTINGS[5]
            invertUp=True
            invertAim = False
            uiSpacingX = 12
        else :
            side = SETTINGS[4]
            invertUp=True
            invertAim = True
            uiSpacingX = -12
            
        ### Get selection.
        guideList = self.getSelection(root)
        
        mainGrp = mc.group(n=baseName+side+'_root', empty=True)
        posRoot = mc.xform(guideList[0], q=1, ws=1, t=1)
        mc.xform(mainGrp, t=posRoot)

        ###Create joint chain as ref (later used as ik joints)
        tag = 'ik'
        jointRef = self.fonc.create_oriented_jointChain(guideList, baseName+side, tag, invertUp, invertAim)
        rotNode = mc.group(n=jointRef[-1]+'_rot', empty=True)
        mc.parent(rotNode, jointRef[-1], r=True)
        # mc.xform(rotNode, ro=(0,0,0))
        
        ### Build fk ctrl.
        fkCtrlList = []
        for item in guideList:
            name = baseName + side + '_' + str(guideList.index(item)) +'_fk_ctrl'
            ctrl = shapes.shpDico[str(3)](name, radius=2*scale)  # -Cube shape. 
            fkCtrlList.append(ctrl)

        mc.parent(fkCtrlList[0], mainGrp, r=True)    
        [mc.parent(fkCtrlList[i], fkCtrlList[i-1], r=True) for i in range(1, len(fkCtrlList))]
        
        [self.trans.snap(fkCtrlList[i], jointRef[i]) for i in range(0,len(fkCtrlList))]
        self.trans.orig_Sel(fkCtrlList)
        
        fkRefList = []
        for ctrl in fkCtrlList:
            ref = mc.group(n=baseName + side + '_' + str(fkCtrlList.index(ctrl)) +'_skin_ref', empty=True)
            mc.parent(ref, ctrl, r=True)
            fkRefList.append(ref)
            
        ### Build ik ctrl.
        ikCtrlList = []
        ikOriglList = []
        
        ikCtrlList.append(shapes.shpDico[str(3)](baseName + side +'_ik_ctrl', radius=2*scale))  # -Cube shape.
        ikCtrlList.append(shapes.shpDico[str(1)](baseName + side +'_ik_rot_ctrl', radius=2.5*scale))  # -Sphere shape.
        ref = mc.group(n=ikCtrlList[0]+'_ref', empty=True)
        
        # Prep for mirror behavior.
        offset = mc.group(n=ikCtrlList[0]+'_offset', empty=True)
        mc.parent(ikCtrlList[0], offset, a=True)
        mc.parent(offset, mainGrp)
        
        scaleX = 1
        if '_R' in root:
            scaleX = -1
        mc.setAttr(offset+'.scaleX', scaleX)
        
        pos = mc.xform(fkCtrlList[-1], q=True, t=True, ws=True)
        mc.xform(ikCtrlList[0], t=pos, ws=True)
        
        mc.parent(ref, ikCtrlList[-1], ikCtrlList[0])

        [ikOriglList.append(self.trans.orig_Sel(ctrl)) for ctrl in ikCtrlList]
        
        [mc.setAttr(item+'.scaleZ', 1) for item in ikCtrlList] # Clean scale attribute caused by mirroring.
        [mc.setAttr(item+'.scaleZ', 1) for item in ikOriglList]
        mc.setAttr(ref+'.scaleZ', 1)
        [self.trans.snap(item, fkCtrlList[-1]) for item in [ikOriglList[-1], ref]]

        #Place pole vector ctrl
        posVector = self.fonc.getPoleVectorPosition(jointRef, distance=5)
        pvCtrl = shapes.shpDico[str(7)](baseName + side +'_ik_pVect_ctrl', radius=2*scale)  # -loc shape.
        mc.xform(pvCtrl, ws=True, t=(posVector.x, posVector.y, posVector.z))
        
        ### Setup ik/poleVector.
        tag = 'pVect'
        poleV_driver = self.fonc.create_oriented_jointChain([guideList[0], guideList[-1]], baseName, tag, invertUp, invertAim)
        pvOrig = self.trans.orig_Sel(pvCtrl)
        mc.parentConstraint(poleV_driver[0], pvOrig, mo=True, sr=('x', 'y', 'z'))
        
        #Create ikhandles.
        handlesGrp = mc.group(n=baseName+side+'_handles_grp', empty=True)
        ikHandle = mc.ikHandle(sj=jointRef[0], ee=jointRef[-1], sol='ikRPsolver')
        pvHandle = mc.ikHandle(sj=poleV_driver[0], ee=poleV_driver[-1], sol='ikSCsolver')
        mc.parent(ikHandle[0], pvHandle[0], handlesGrp)
        
        #Organize under mainGrp.
        mc.parent(jointRef[0], mainGrp, a=True)
        mc.parent(poleV_driver[0], mainGrp, a=True)
        mc.parent(pvOrig, mainGrp, a=True)
        mc.parent(handlesGrp, mainGrp, a=True)
        
        #Connect ctrl and handles.
        mc.pointConstraint(ref, handlesGrp, mo=True)
        mc.poleVectorConstraint(pvCtrl, ikHandle[0])
        
        ### Create UI ctrl.
        ui_ctrl = shapes.shpDico[str(5)](baseName+side+'_UI', radius=1*scale)  # -Cube shape. 
        pos = mc.xform(guideList[0], q=1, ws=1, t=1)
        pos = [pos[0]+uiSpacingX, pos[1]+10, pos[2]]
        mc.xform(ui_ctrl, ws=1, t=pos)
        mc.parent(ui_ctrl, mainGrp, a=True)
        self.set_UI_ctrl(ui_ctrl)
        
        #Setup ik_rot_ctrl orient constraint.
        rot_ctrl_constr = mc.orientConstraint(ref, ikOriglList[-1], mo=True)
        mc.orientConstraint(jointRef[-1], ikOriglList[-1], mo=True)
        mc.connectAttr(ui_ctrl+'.ikRotRef', rot_ctrl_constr[0]+'.'+ref+'W0')
        
        invertNode = mc.createNode('reverse')
        mc.connectAttr(ui_ctrl+'.ikRotRef', invertNode+'.inputX')
        mc.connectAttr(invertNode+'.outputX', rot_ctrl_constr[0]+'.'+jointRef[-1]+'W1')
        
        ###Set ik_Ctrl position constraint switch
        inflList = ['ROOT_ctrl', 'spine_C_ik0_0_ctrl', 'spine_C_ik1_0_ctrl', 'head_C_fk_ctrl']
        infListState = []
        for infl in inflList:
            if mc.objExists(infl) is True:
                infListState.append(True)
            else:
                infListState.append(False)
        if all(infListState) is True:
            for i in range(0,4):
                constrNode = mc.parentConstraint(inflList[i], offset, mo=True)
                weightId = '.'+inflList[i]+'W'+str(i)
                
                conditionNode = mc.createNode('condition')
                mc.setAttr(conditionNode+'.colorIfTrueR', 1)
                mc.setAttr(conditionNode+'.colorIfFalseR', 0)
                mc.setAttr(conditionNode+'.secondTerm', i)
                
                mc.connectAttr(ui_ctrl+'.ikPosRef', conditionNode+'.firstTerm')
                
                mc.connectAttr(conditionNode+'.outColorR', constrNode[0]+weightId)

        ###Create ik/fk switch
        jntDriverList = []
        for x in fkCtrlList:
            jntDriverList.append(mc.group(n=baseName + side + str(fkCtrlList.index(x)) + '_drv', empty=True))
        
        driverGrp = mc.group(n=baseName + side +'_driver_grp', empty=True)
        mc.parent(driverGrp, mainGrp, a=True)
        mc.makeIdentity(driverGrp, apply=True, t=1, r=1, s=1, n=0, pn=1)
        mc.setAttr(driverGrp + '.inheritsTransform', 0)
        [mc.parent(driver, driverGrp, a=True) for driver in jntDriverList]

        jointRef[-1] = rotNode
        blendNodes = self.fonc.ikFk_switch(fkCtrlList, jointRef, jntDriverList)
        for node in blendNodes:
            mc.connectAttr(ui_ctrl+'.FKIK', node+'.weight')
        mc.orientConstraint(ikCtrlList[-1], rotNode, mo=True)
        
        # Set up visibility.
        revNode = mc.createNode('reverse')
        mc.connectAttr(ui_ctrl+'.FKIK', ikOriglList[0]+'.visibility')
        mc.connectAttr(ui_ctrl+'.FKIK', pvOrig+'.visibility')
        mc.connectAttr(ui_ctrl+'.FKIK', revNode+'.inputX')
        mc.connectAttr(revNode+'.outputX', fkCtrlList[0]+'.visibility')

        return mainGrp
    
    def twistJoints(self, refList, reference=None):
        splitName = refList[0].split('_')
        if '_L' in refList[0]:
            side = '_L'
        else :
            side = '_R'
            
        topGrp = mc.group(n=splitName[0]+side+'_twistJoints_grp', empty=True)
        
        for ref in refList[0:2]:

            splitName = ref.split('_')    
            name = splitName[0]+'_'+splitName[1]

            mainGrp = mc.group(n=name+'_grp', empty=True, p=topGrp)
            self.matrix.matrixConstraint_old(ref, mainGrp, mo=False, s=False)

            jntPos1 = mc.xform(ref, q=1, t=1, ws=1)
            jntPos2 = mc.xform(refList[refList.index(ref)+1], q=1, t=1, ws=1)
        
            mc.select(cl=1)
            twistRefJnt1 = mc.joint(n=name+ 'TwistRef1_jnt', radius=1, p=jntPos1)
            twistRefJnt2 = mc.joint(n=name + 'TwistRef2_jnt', radius=1, p=jntPos2)
            mc.joint(twistRefJnt1, e=1, zso=1, oj='xyz', sao='yup')
            mc.parent(twistRefJnt1, mainGrp)
            
            handle = mc.ikHandle(sj=twistRefJnt1, ee=twistRefJnt2, sol='ikSCsolver')[0]
            mc.parent(handle, mainGrp, a=True)
            
            if refList.index(ref) == 0 and reference is not None:
                reference = reference
                blendAmount = 1
                blendIncrement = -0.25
                if side == '_R':
                    blendAmount = -1
                    blendIncrement = 0.25
            else:
                reference = refList[refList.index(ref)+1]
                blendAmount = 0
                blendIncrement = 0.25
                if side == '_R':
                    blendIncrement = -0.25
                    
            mc.orientConstraint(reference, handle, mo=True)
            
            length = maths.getDistance(mc.xform(ref, q=True, t=True, ws=True), mc.xform(refList[refList.index(ref)+1], q=True, t=True, ws=True))
            spacing = length/4
            if side == '_R':
                spacing = spacing *-1
                
            offset = 0
            driverList = []
            splitName = ref.split('_')
            for i in range(0,5):
                newName = splitName[0]+ '_'+ splitName[1]+'_'+str(i)
                driver = mc.group(n=newName+'_drv', empty=True)
                driverList.append(driver)
                mc.parent(driver, mainGrp, r=True)
                mc.setAttr(driver+'.translateX', offset)
                offset += spacing
            
            #blendAmount = 0
            for driver in driverList:
                if driver == driverList[-1] and refList.index(ref) != 0:
                    self.matrix.matrixConstraint_old(refList[-1], driver, mo=False, s=False)
                    break
                blendNode = mc.createNode('multDoubleLinear')
                mc.connectAttr(twistRefJnt1+'.rotateX', blendNode+'.input1')
                mc.connectAttr(blendNode+'.output', driver+'.rotateX')
                
                mc.setAttr(blendNode+'.input2', blendAmount)
                blendAmount += blendIncrement
                
        for item in refList:
            name = item.replace('_drv', '_ref')
            mc.rename(item, name) 
            
        return topGrp
    
    
    def build_hand(self, root, scale):
        if '_L' in root:
            side = SETTINGS[5]
        else :
            side = SETTINGS[4]
            
        guideList = self.getSelection(root)

        mainGrp = mc.group(n='hand'+side+'_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])

        cns = mc.group(n='hand'+side+'_cns', empty=True)
        ref = mc.group(n='hand'+side+'_ref', empty=True)
        mc.parent(cns, mainGrp, r=True)
        mc.parent(ref, cns, r=True)
        
        fingerRoots = []
        for x in guideList[1:]:
            if 'root' in x:
                fingerRoot = self.buildFinger(x, scale)
                mc.parent(fingerRoot, ref, a=True)
                fingerRoots.append(fingerRoot)
                mc.xform(fingerRoot, s=(1,1,1))
        
        palmCtrl = shapes.shpDico[str(1)](name='palm'+side+'_ctrl', radius=1.5*scale)  # -Sphere shape.
        self.trans.snap(palmCtrl, guideList[1])
        
        palmRoot = mc.group(n='palm'+side+'_orig', empty=True)
        mc.parent(palmRoot, ref, a=True)
        mc.parent(palmCtrl, palmRoot, a=True)
        
        mc.parent(mc.group(n='palm'+side+'_drv', empty=True), palmCtrl, r=True)
        self.trans.orig_Sel(palmCtrl)
        
        mc.parentConstraint(palmCtrl, fingerRoots[-1], mo=True)
        constr = mc.parentConstraint(fingerRoots[-1], fingerRoots[-2], mo=True)
        mc.parentConstraint(fingerRoots[-3], fingerRoots[-2], mo=True)
        
        mc.setAttr(constr[0]+".interpType", 2)
        
        return mainGrp
      
    def buildFinger(self, root, scale):
        baseName = root.split('_')[0]
        if '_L' in root:
            side = '_L'
            invertUp=False
            invertAim = False
        else :
            side = '_R'
            invertUp=False
            invertAim = True
            
        ### Get selection.
        guideList = self.getSelection(root)
        guideList = guideList[:-1]
        
        mainGrp = mc.group(n=baseName+side+'_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])

        ###Create joint chain as ref (later used as ik joints)
        tag = 'skin'
        jointRef = self.fonc.create_oriented_jointChain(guideList, baseName+side, tag, invertUp, invertAim)

        ### Build fk ctrl.
        fkCtrlList = []
        for item in guideList:
            name = baseName + side + '_' + str(guideList.index(item)) +'_fk_ctrl'
            ctrl = shapes.shpDico[str(8)](name, radius=5*scale)  # -Lolipop shape.
            if side == '_R':
                mc.xform(ctrl, ro=(0,0,180), ws=True)
                mc.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0, pn=1)
            fkCtrlList.append(ctrl)

        mc.parent(fkCtrlList[0], mainGrp, r=True)    
        [mc.parent(fkCtrlList[i], fkCtrlList[i-1], r=True) for i in range(1, len(fkCtrlList))]
        
        [self.trans.snap(fkCtrlList[i], jointRef[i]) for i in range(0,len(fkCtrlList))]
        self.trans.orig_Sel(fkCtrlList)
        
        fkRefList = []
        for ctrl in fkCtrlList:
            ref = mc.group(n=baseName + side + '_' + str(fkCtrlList.index(ctrl)) +'_drv', empty=True)
            mc.parent(ref, ctrl, r=True)
            fkRefList.append(ref)
        mc.delete(jointRef[0])
        
        return mainGrp
        
    def set_UI_ctrl(self, ctrl):
        mc.addAttr(ctrl, ln='FKIK', nn='FKIK', at='float', min=0, max=1, dv=0, k=1, r=1, w=1, s=1)
        mc.addAttr(ctrl, ln='ikPosRef', at='enum', en='Root_ctrl:Body_ctrl:Chest_ctrl:Head_ctrl:', k=1, r=1, w=1, s=1)
        mc.addAttr(ctrl, ln='ikRotRef', at='enum', en='Free:Ik_ctrl:', k=1, r=1, w=1, s=1)
        
    
    def build_foot(self, root, scale):
        names = ['ball', 'heel', 'tip', 'toe', 'foot']
        if '_L' in root:
            side = SETTINGS[5]
            invertUp=False
            invertAim = False
            aim = 1
            up = -1
        else :
            side = SETTINGS[4]
            invertUp=False
            invertAim = True
            aim = -1
            up = 1
            
        guideList = self.getSelection(root)
        
        mainGrp = mc.group(n='foot'+side+'_root', empty=True)
        self.trans.snap(mainGrp, guideList[0])
        
        # Create foot joints used for skinning.
        tag = 'ik'
        footJoints = self.fonc.create_oriented_jointChain(guideList[:-1], 'foot'+side, tag, invertUp, invertAim)
        mc.parent(footJoints[0], mainGrp, a=True)
        
        guideList.reverse()
        tag ='revIk'
        jointRef = self.fonc.create_oriented_jointChain(guideList, 'foot'+side, tag, invertUp, invertAim)
        mc.parent(jointRef[0], mainGrp, a=True)
        
        ## Build IK controls.
        # Setup ball ctrl.
        ballCtrl = shapes.shpDico[str(0)](names[0] + side +'_ctrl', radius=4*scale)  # -Circle shape.
        pos = mc.xform(guideList[2], q=True, ws=True, t=True)
        posY = mc.xform(guideList[0], q=True, ws=True, t=True)[1]
        mc.xform(ballCtrl, t=(pos[0], posY, pos[2]))
        mc.parent(ballCtrl, mainGrp, a=True)
        ikOrig = self.trans.orig_Sel(ballCtrl)

        # Setup ctrls.
        ctrlList = []
        for i in range(0, len(guideList[:-1])):
            name = names[i+1] + side 
            ctrl = shapes.shpDico[str(0)](name+'_ctrl', radius=2*scale)  # -Circle shape.
            ctrlList.append(ctrl)
        
        mc.parent(ctrlList[0], ballCtrl, r=True)    
        [mc.parent(ctrlList[i], ctrlList[i-1], r=True) for i in range(1, len(ctrlList))]        
        
        [self.trans.snap(ctrlList[i], jointRef[i]) for i in range(0,len(ctrlList))]
        self.trans.orig_Sel(ctrlList)
        
        [self.matrix.matrixConstraint_old(ctrlList[i], jointRef[i], mo=False, s=False) for i in range(0, len(ctrlList))]
        
        ikToeCtrl = shapes.shpDico[str(3)](names[3] + side +'_ik' + '_ctrl', radius=2*scale)  # -Cube shape.
        self.trans.snap(ikToeCtrl, footJoints[1])
        mc.parent(ikToeCtrl, ctrlList[-2], a=True)
        ikToeOrig = self.trans.orig_Sel(ikToeCtrl)
        
        ## Build FK controls.
        fkToeCtrl = shapes.shpDico[str(3)](names[3] + side +'_fk' + '_ctrl', radius=2*scale)  # -Cube shape.
        mc.parent(fkToeCtrl, mainGrp, a=True)
        self.trans.snap(fkToeCtrl, footJoints[1])
        fkOrig = self.trans.orig_Sel(fkToeCtrl)
        
        refFk = mc.group(n=names[3] + side +'_fk' +'_ref', empty=True)
        refIk = mc.group(n=names[3] + side +'_ik' +'_ref', empty=True)
        mc.parent(refFk, fkToeCtrl, r=True)
        mc.parent(refIk, mainGrp, r=True)
        self.trans.snap(refIk, fkToeCtrl)
        refIkorig = self.trans.orig_Sel(refIk)
        self.matrix.matrixConstraint_old(footJoints[1], refIkorig, mo=True)
        
        driverGrp = mc.group(n=names[3] + side +'_driver_grp', empty=True)
        mc.parent(driverGrp, mainGrp, a=True)
        mc.makeIdentity(driverGrp, apply=True, t=1, r=1, s=1, n=0, pn=1)
        mc.setAttr(driverGrp + '.inheritsTransform', 0)
        driver = mc.group(n=names[3] + side +'_drv', empty=True)
        mc.parent(driver, driverGrp, a=True)

        blendNodes = self.fonc.ikFk_switch([refFk], [refIk], [driver])
        if mc.objExists('leg'+ side + '_UI' +'.FKIK'):
            for node in blendNodes:
                mc.connectAttr('leg'+ side + '_UI' +'.FKIK', node+'.weight')

            name = 'leg' + side + '_root'
            #Find leg elements.
            joints = mc.listRelatives(name, ad=True, typ='joint')
    
            all = mc.listRelatives(name, ad=True, typ='transform')
            
            #Cleaning.
            decompMat = mc.listConnections(mc.listRelatives(joints[0], c=True), d=True, p=True)[0]
            mc.disconnectAttr(mc.listRelatives(joints[0], c=True)[0]+'.worldMatrix', decompMat)
            mc.connectAttr(joints[0]+'.worldMatrix', decompMat)
            
            for item in all:
                if '_rot' in item:
                    mc.delete(item)
                    break
            
            fkControls = []
            [fkControls.append(item) for item in all if 'fk' in item and 'ctrl' in item]
            
            ikControls = []
            [ikControls.append(item) for item in all if 'ik_ctrl' in item]
            
            aimConstr = mc.aimConstraint(driver, fkControls[1], aim=(aim,0,0), u=(0,up,0), wu=(0,1,0))
            mc.delete(aimConstr)
            
            aimConstr = mc.aimConstraint(driver, joints[0], aim=(aim,0,0), u=(0,up,0), wu=(0,1,0))
            mc.delete(aimConstr)
    
            #Organize.
            mc.parent(footJoints[1], joints[0], a=True)
            mc.delete(footJoints[0])
            handle01 = mc.ikHandle(sj=joints[0], ee=footJoints[1], sol='ikSCsolver')[0]
            handle02 = mc.ikHandle(sj=footJoints[1], ee=footJoints[-1], sol='ikSCsolver')[0]
    
            mc.parent(handle01, jointRef[2], a=True)
            Handle02Orig = mc.group(n='ikToe'+side+'HandleOrig', empty=True)
            self.trans.snap(Handle02Orig, ikToeOrig)
            mc.parent(handle02, Handle02Orig, a=True)
            mc.parent(Handle02Orig, jointRef[1], a=True)
            self.matrix.matrixConstraint_old(ikToeCtrl, Handle02Orig, mo=True, s=False)
        
        return mainGrp, fkOrig, ikOrig