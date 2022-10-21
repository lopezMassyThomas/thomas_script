'''
Created on Jan 10, 2022

@author: Thomas
'''
import maya.cmds as mc
import maya.api.OpenMaya as om
import pymel.core as pm
import math
import time
from thomas_script.maya.scripts.characterRigTool import biped_core, quadruped_core, fonctions
from thomas_script.maya.utils import attributes, maths, shapes, transform, rigging, matrix
#from thomas_script.maya.scripts import matrixConstraint
reload(biped_core)
reload(quadruped_core)
reload(fonctions)
reload(shapes)
reload(matrix)

'''
NOTES:
Basic spine guide done.
-Need to be able to update on the fly. But wait until testing with full build.
-
'''

SETTINGS = []

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
        self.trans = transform
        
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

    def guideChain(self, names, length, spineNb, axisPlane='y'):
        #Check for guide main group.
        if mc.objExists('guide') is False:
            guideGrp = mc.group(n='guide', empty=True)
        else:
            guideGrp = 'guide'
            
        #Define names.
        name01 = names[0]
        name02 = names[0]
        name03 = names[0]
        if len(names) == 2:
            name03 = names[-1]
        if len(names) == 3:
            name02 = names[1]
            name03 = names[-1]
                
        ctrlList = []
        origList = []
        rootCtrl = self.guideCtrl(name=name01+'_root', isRoot=True) # Create root control. 
        mc.parent(rootCtrl, guideGrp, r=True)
        ctrlList.append(rootCtrl)
        
        for nb in range(0,spineNb): # Create spine control.
            
            if nb == spineNb-1 :
                orig = mc.group(name=name03+str(nb)+'_orig', empty=True)
                ctrl = self.guideCtrl(name=name03+ str(nb), isRoot=True)
            else:
                orig = mc.group(name=name02+str(nb)+'_orig', empty=True)
                ctrl = self.guideCtrl(name=name02+ str(nb))
            mc.parent(ctrl, orig, r=True)
            mc.parent(orig, rootCtrl, r=True)
            ctrlList.append(ctrl) 
            origList.append(orig)
        
        if 'y' in axisPlane:
            axis = '.translateY'
        if 'x' in axisPlane:
            axis = '.translateX'
        if '-' in axisPlane:
            length = length*-1
            
        mc.setAttr('{}{}'.format(ctrlList[-1], axis), length) # Set length.
                           
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

        curve = mc.curve(n=name01+'_guide_crv', d=1, p=posList, k=knotList)
        crv_shp = mc.listRelatives(curve, s=True)
        mc.setAttr(curve + '.template', 1)
        mc.setAttr(curve + '.inheritsTransform', 0)
        mc.parent(curve, rootCtrl, a=True)
        
        for nb in range(0,spineNb+1): # Link one cv per ctrl.
            cluster = mc.cluster('{}.cv[{}]'.format(curve, str(nb)))
            mc.parent(cluster[1], ctrlList[nb], r=True)
            mc.setAttr(cluster[1] + '.visibility', 0)

        return ctrlList
        
    # def spine(self, spineNb):
    #     if mc.objExists('guide') is False:
    #         guideGrp = mc.group(n='guide', empty=True)
    #     else:
    #         guideGrp = 'guide'
    #
    #     ctrlList = []
    #     origList = []
    #     rootCtrl = self.guideCtrl(name='spine_root', isRoot=True) # Create root control. 
    #     mc.parent(rootCtrl, guideGrp, r=True)
    #     ctrlList.append(rootCtrl)
    #
    #     for nb in range(0,spineNb): # Create spine control.
    #         orig = mc.group(name='spine'+str(nb)+'_orig', empty=True)
    #         if nb == spineNb-1 :
    #             ctrl = self.guideCtrl(name='spine'+ str(nb), isRoot=True)
    #         else:
    #             ctrl = self.guideCtrl(name='spine'+ str(nb))
    #         mc.parent(ctrl, orig, r=True)
    #         mc.parent(orig, rootCtrl, r=True)
    #         ctrlList.append(ctrl) 
    #         origList.append(orig)
    #
    #     mc.setAttr('{}{}'.format(ctrlList[-1], '.translateY'), 60) # Set position chest.
    #
    #     # calculate and store weights for spacing elems.
    #     div = 1.0 / spineNb
    #     weightList = []
    #     invertWList = []
    #     x = div
    #     for i in range(1, spineNb):
    #         weightList.append(x)
    #         invertWList.append(x)
    #         x = x + div
    #     invertWList.reverse()
    #
    #     for i in range(0, spineNb-1): # Space spine parts.
    #         mc.pointConstraint(ctrlList[0], origList[i], mo=False, w=invertWList[i])
    #         mc.pointConstraint(ctrlList[-1], origList[i], mo=False, w=weightList[i])
    #
    #     # Create and set curve for visual reference.    
    #     posList = []
    #     knotList = []
    #     [posList.append((0,0,0)) for nb in range(-1,spineNb)]
    #     [knotList.append(nb) for nb in range(-1,spineNb)]
    #
    #     curve = mc.curve(n='spine_guide_crv', d=1, p=posList, k=knotList)
    #     crv_shp = mc.listRelatives(curve, s=True)
    #     mc.setAttr(curve + '.template', 1)
    #     mc.setAttr(curve + '.inheritsTransform', 0)
    #     mc.parent(curve, rootCtrl, a=True)
    #
    #     for nb in range(0,spineNb+1): # Link one cv per ctrl.
    #         cluster = mc.cluster('{}.cv[{}]'.format(curve, str(nb)))
    #         mc.parent(cluster[1], ctrlList[nb], r=True)
    #         mc.setAttr(cluster[1] + '.visibility', 0)
    #
    #     return ctrlList
    
    # def head(self, headNb):
    #     if mc.objExists('guide') is False:
    #         guideGrp = mc.group(n='guide', empty=True)
    #     else:
    #         guideGrp = 'guide'
    #
    #     ctrlList = []
    #     origList = []
    #     rootCtrl = self.guideCtrl(name='neck_root', isRoot=True) # Create root control. 
    #     mc.parent(rootCtrl, guideGrp, r=True)
    #     ctrlList.append(rootCtrl)
    #
    #     for nb in range(0,headNb): # Create spine control.
    #         if nb == headNb-1 :
    #             orig = mc.group(name='head'+str(nb)+'_orig', empty=True)
    #             ctrl = self.guideCtrl(name='head'+ str(nb), isRoot=True)
    #         else:
    #             orig = mc.group(name='neck'+str(nb)+'_orig', empty=True)
    #             ctrl = self.guideCtrl(name='neck'+ str(nb))
    #         mc.parent(ctrl, orig, r=True)
    #         mc.parent(orig, rootCtrl, r=True)
    #         ctrlList.append(ctrl) 
    #         origList.append(orig)
    #
    #     mc.setAttr('{}{}'.format(ctrlList[-1], '.translateY'), 60) # Set position chest.
    #
    #     # calculate and store weights for spacing elems.
    #     div = 1.0 / headNb
    #     weightList = []
    #     invertWList = []
    #     x = div
    #     for i in range(1, headNb):
    #         weightList.append(x)
    #         invertWList.append(x)
    #         x = x + div
    #     invertWList.reverse()
    #
    #     for i in range(0, headNb-1): # Space spine parts.
    #         mc.pointConstraint(ctrlList[0], origList[i], mo=False, w=invertWList[i])
    #         mc.pointConstraint(ctrlList[-1], origList[i], mo=False, w=weightList[i])
    #
    #     # Create and set curve for visual reference.    
    #     posList = []
    #     knotList = []
    #     [posList.append((0,0,0)) for nb in range(-1,headNb)]
    #     [knotList.append(nb) for nb in range(-1,headNb)]
    #
    #     curve = mc.curve(n='neck_guide_crv', d=1, p=posList, k=knotList)
    #     crv_shp = mc.listRelatives(curve, s=True)
    #     mc.setAttr(curve + '.template', 1)
    #     mc.setAttr(curve + '.inheritsTransform', 0)
    #     mc.parent(curve, rootCtrl, a=True)
    #
    #     for nb in range(0,headNb+1): # Link one cv per ctrl.
    #         cluster = mc.cluster('{}.cv[{}]'.format(curve, str(nb)))
    #         mc.parent(cluster[1], ctrlList[nb], r=True)
    #         mc.setAttr(cluster[1] + '.visibility', 0)
    #
    #     return ctrlList
    #

    
    def createGuide(self, *args):
        key = args[0]
        partNb = args[1]
        
        if 'spine' in key:
            names=['spine']
            ctrls = self.guideChain(names, 60, partNb)
            
        if 'head' in key:
            names=['neck', 'head']
            ctrls = self.guideChain(names, 20, partNb)
            
        if 'shoulder' in key:
            side='_L'
            names=['shoulder'+side]
            ctrls = self.guideChain(names, 20, partNb, axisPlane='x')

        if 'arm' in key:
            side='_L'
            names=['arm'+side]
            ctrls = self.guideChain(names, 60, partNb, axisPlane='x')

        if 'leg' in key:
            side='_L'
            names=['leg'+side]
            ctrls = self.guideChain(names, 60, partNb, axisPlane='x')
            mc.xform(ctrls[0], ro=(0, 0, -90), ws=True)
            
        if 'hand' in key:
            side='_L'
            names=['hand'+side]

            ctrls = self.guideChain(names, 5, partNb, axisPlane='x')

            fingerNames = [['thumb'+side], ['index'+side], ['middle'+side], ['ring'+side], ['pinky'+side]]
            fingerPartNb = 3
            fingerCtrls = []
            [fingerCtrls.append(self.guideChain(name, 15, fingerPartNb, axisPlane='x')) for name in fingerNames]
            
            transZ = 4
            for ctrl in fingerCtrls:
                root = ctrl[0]
                mc.xform(root, ws=True, s=(0.5, 0.5, 0.5))
                mc.xform(root, ws=True, t=(10, 0, transZ))
                transZ = transZ-2
                mc.parent(root, ctrls[0], r=True)
                
        if 'foot' in key:
            side='_L'
            names=['foot'+side]
            
            ctrls = self.guideChain(names, 60, partNb, axisPlane='x')
            mc.xform(ctrls[0], t=(0,10,0), ws=True)
            mc.xform(ctrls[-1], t=(0,0,0), ws=True)
            
            [self.trans.snap(ctrl, ctrls[-1]) for ctrl in ctrls[1:-1]]
            
            spacing = [10, 15]
            [mc.setAttr(ctrls[i+1]+'.translateZ', spacing[i]) for i in range(0, len(ctrls[1:-1]))]
            
        if 'BackLeg' in key:
            side='_L'
            names=['qLeg'+side]
            ctrls = self.guideChain(names, 60, partNb, axisPlane='y')
            
        return ctrls
    
    def mirrorGuide(self, *args):
        key = args[0]
        partNb = args[1]
        roots = mc.listRelatives('guide', c=True)

        refNodes = []
        for root in roots:
            if key in root:
                nodes = mc.listRelatives(root, ad=True, typ='transform')
                refNodes.append(root)
                
        [refNodes.append(node) for node in nodes if '_ref' in node ]

        # Duplicate / rename.
        side='_R'
        names=[key+side]
        mainCtrls = self.guideChain(names, 20, partNb, axisPlane='x')

        self.trans.snap(mainCtrls[0], refNodes[0])
        if 'hand' in key:
            self.trans.snap(mainCtrls[-1], refNodes[1])
        else:
            self.trans.snap(mainCtrls[-1], refNodes[-1])
            
        for i in range(1, len(mainCtrls)-1):
            self.trans.snap(mainCtrls[i], refNodes[i])
        
        for node in refNodes: # Mirror any sub root element.
            if 'root' in node and key not in node:
                part = []
                name = node.split('_')[0]
                names=[name+side]
                nodes = mc.listRelatives(node, ad=True, typ='transform')
                [part.append(node) for node in nodes if '_ref' in node ]
                ctrls = self.guideChain(names, 20, len(part), axisPlane='x')
        
                mc.xform(ctrls[0], s=(0.5, 0.5, 0.5), ws=True)
                self.trans.snap(ctrls[0], node)
                self.trans.snap(ctrls[-1], part[-1])
                for i in range(1, len(ctrls)-1):
                    self.trans.snap(ctrls[i], part[i-1])
        
                mc.parent(ctrls[0], mainCtrls[0], a=True)    
        # Mirror.
        temp = mc.group(empty=True, w=True)
        mc.parent(mainCtrls[0], temp)
        mc.setAttr(temp+'.scaleX', -1)
        mc.parent(mainCtrls[0], 'guide')
        mc.delete(temp)
        return
    
    def createBiped(self):
        spine = self.createGuide('spine', 4)
        mc.setAttr(spine[0]+'.translateY', 70)
        
        neck = self.createGuide('neck/head', 2)
        self.trans.snap(neck[0], spine[-1])
        
        shoulder = self.createGuide('shoulder', 1)
        self.trans.snap(shoulder[0], spine[-1])
        
        arm = self.createGuide('arm', 2)
        self.trans.snap(arm[0], shoulder[-1])
        
        leg = self.createGuide('leg', 2)
        mc.setAttr(leg[0]+'.translateX', 10)
        mc.setAttr(leg[0]+'.translateY', 70)
        
        hand = self.createGuide('hand', 1)
        self.trans.snap(hand[0], arm[-1])
        
        foot = self.createGuide('foot', 3)
        mc.setAttr(foot[0]+'.translateX', 10)
        mc.setAttr(foot[0]+'.translateY', 10)
        
        return
      
class Rig:
    
    def __init__(self):
        '''
        Constructor
        '''
        self.fonc = fonctions.Core()
        self.trans = transform
        self.matrix = matrix
        self.biped = biped_core.Biped()
        self.quadruped = quadruped_core.Quadruped()
        # self.spine = Spine()
        # self.head = Head()
        # self.arm = Arm()
        # self.leg = Leg()
    
    def orginizeInput(self, list):
        newList = []
        nameList = ['spine', 'neck', 'shoulder', 'arm', 'leg', 'hand', 'foot']
        previousLimb = ''
        
        for limbName in nameList:
            for limb in list:
                if limbName in limb:
                    if limbName+'_R' in previousLimb:
                        newList.insert(len(newList)-1, limb)
                    else:
                        newList.append(limb)
                    previousLimb = limb

        return newList
    
    def createRig(self, guideList):
        [biped_core.SETTINGS.append(item) for item in SETTINGS] # Pars UI Settings.
        [quadruped_core.SETTINGS.append(item) for item in SETTINGS] # Pars UI Settings.
        
        cleanList = self.orginizeInput(guideList)
        if len(cleanList) == 12:
            # Then all of the guides are for full biped.
            guideList = cleanList
        else:
            guideList = guideList
        
        if mc.objExists('ROOT_ctrl') is not True:
            rootCtrl, localCtrl = self.createRootRig()
        else:
            rootCtrl = 'ROOT_ctrl'
            localCtrl = 'local_ctrl'

        scale = self.getScale()    

        rootList = []
        spine = None
        neck = None
        shoulderL = None
        shoulderR = None
        armL = None
        armR = None
        legL = None
        legR = None
        handL = None
        handR = None
        footL = None
        footR = None
        for root in guideList:
            if 'spine' in root:
                rootSpine = self.biped.build_spine(root, scale)
                rootList.append(rootSpine)
                spine = True
            if 'neck' in root:
                rootneck = self.biped.build_head(root, scale)
                rootList.append(rootneck)
                neck = True
            if 'shoulder_L' in root:
                rootShoulderL = self.biped.build_shoulder(root, scale)
                rootList.append(rootShoulderL)
                shoulderL= True
            if 'shoulder_R' in root:
                rootShoulderR = self.biped.build_shoulder(root, scale)
                mc.setAttr(root+'.scaleZ', -1)
                rootList.append(rootShoulderR)
                shoulderR = True
            if 'arm_L' in root:
                rootArmL = self.biped.build_arm(root, scale)
                rootList.append(rootArmL)
                armL = True
            if 'arm_R' in root:
                rootArmR = self.biped.build_arm(root, scale)
                mc.setAttr('arm_R_ik_pVect_ctrl_orig.scaleX', -1)
                rootList.append(rootArmR)
                armR = True
            if 'leg_L' in root:
                rootLegL = self.biped.build_arm(root, scale)
                rootList.append(rootLegL) 
                legL = True
            if 'leg_R' in root:
                rootLegR = self.biped.build_arm(root, scale)
                mc.setAttr('leg_R_ik_pVect_ctrl_orig.scaleX', -1)
                rootList.append(rootLegR)
                legR = True
            if 'hand_L' in root:
                rootHandL = self.biped.build_hand(root, scale) 
                rootList.append(rootHandL)
                handL = True
            if 'hand_R' in root:
                rootHandR = self.biped.build_hand(root, scale)
                rootList.append(rootHandR)
                handR = True
            if 'foot_L' in root:
                rootFootL, fkOrigL, ikOrigL = self.biped.build_foot(root, scale)
                rootList.append(rootFootL)
                footL = True
            if 'foot_R' in root:
                rootFootR, fkOrigR, ikOrigR = self.biped.build_foot(root, scale)
                rootList.append(rootFootR)
                footR = True
                
            if 'qLeg_L' in root:
                rootLegL = self.quadruped.build_leg(root, scale)
                rootList.append(rootLegL)
                
        [mc.parent(root, localCtrl, a=True) for root in rootList]
        
        self.addControlColors()
        
        ### BIPED.
        # Attach neck to spine.
        if spine is True:
            pelvisCtrl = mc.listRelatives(self.getDriverNodes(rootSpine)[0], p=True)
            chestCtrl = mc.listRelatives(self.getDriverNodes(rootSpine)[-1], p=True)

        if spine is True and neck is True:
            mc.parentConstraint(chestCtrl, rootneck, mo=True)
            mc.scaleConstraint(chestCtrl, rootneck, mo=True)
            
        # Attach shoulder to spine.
        if spine is True and shoulderL is True:
            mc.parentConstraint(chestCtrl, rootShoulderL, mo=True)
            mc.scaleConstraint(chestCtrl, rootShoulderL, mo=True)
            if shoulderR is True:
                mc.parentConstraint(chestCtrl, rootShoulderR, mo=True)
                mc.scaleConstraint(chestCtrl, rootShoulderR, mo=True)
                               
        # Attach arm to shoulder.
        if shoulderL is True and armL is True:
            shoulderL_drv = self.getDriverNodes(rootShoulderL)
            shoulderR_drv = self.getDriverNodes(rootShoulderR)
            
            mc.parentConstraint(shoulderL_drv[0], rootArmL, mo=True)
            mc.scaleConstraint(shoulderL_drv[0], rootArmL, mo=True)
            if shoulderR is True and armR is True:
                mc.parentConstraint(shoulderR_drv[0], rootArmR, mo=True)
                mc.scaleConstraint(shoulderR_drv[0], rootArmR, mo=True)  
                
        # Attach leg to spine.
        if spine is True and legL is True:
            mc.parentConstraint(pelvisCtrl, rootLegL, mo=True)
            mc.scaleConstraint(pelvisCtrl, rootLegL, mo=True)
            if legR is True:
                mc.parentConstraint(pelvisCtrl, rootLegR, mo=True)
                mc.scaleConstraint(pelvisCtrl, rootLegR, mo=True)   
                       
        # Attach hand to arm.
        if armL is True and handL is True:
            armL_drv = self.getDriverNodes(rootArmL)
            armR_drv = self.getDriverNodes(rootArmR)
            
            mc.parentConstraint(armL_drv[-1], rootHandL, mo=True)
            mc.scaleConstraint(armL_drv[-1], rootHandL, mo=True)
            # Create twist for arm/foreArm. 
            twistGrpL = self.biped.twistJoints(armL_drv, reference=shoulderL_drv)
            mc.parent(twistGrpL, rootArmL, a=True)
            
            if armR is True and handR is True:
                mc.parentConstraint(armR_drv[-1], rootHandR, mo=True)
                mc.scaleConstraint(armR_drv[-1], rootHandR, mo=True)
                # Create twist for arm/foreArm. 
                twistGrpR = self.biped.twistJoints(armR_drv, reference=shoulderR_drv)
                mc.parent(twistGrpR, rootArmR, a=True)

        # Attach foot to leg.
        if legL is True and footL is True:
            legL_drv = self.getDriverNodes(rootLegL)
            legR_drv = self.getDriverNodes(rootLegR)
            legL_ctrls = self.getCtrlNodes(rootLegL)
            legR_ctrls = self.getCtrlNodes(rootLegR)
        
            mc.parent(fkOrigL, legL_ctrls[0], a=True)
            mc.parent(ikOrigL, legL_ctrls[9], a=True)
            
            twistGrpL = self.biped.twistJoints(legL_drv, reference=pelvisCtrl)
            mc.parent(twistGrpL, rootLegL, a=True)
            
            if legR is True and footR is True:
                mc.parent(fkOrigR, legR_ctrls[0], a=True)
                mc.parent(ikOrigR, legR_ctrls[9], a=True)
                
                twistGrpR = self.biped.twistJoints(legR_drv, reference=pelvisCtrl)
                mc.parent(twistGrpR, rootLegR, a=True) 
                
            handles = []
            [handles.append(item) for item in mc.listRelatives(rootLegL, ad=True, typ='transform') if 'handles_grp' in item]
            [handles.append(item) for item in mc.listRelatives(rootLegR, ad=True, typ='transform') if 'handles_grp' in item]
            handles.remove(handles[0])
            handles.remove(handles[1])
            
            #Undo pointConstr used for leg alone.
            for item in handles:
                constr = mc.listRelatives(item, typ='pointConstraint')
                mc.delete(constr)
        
            mc.pointConstraint(mc.listRelatives(rootFootL, ad=True, typ='joint')[0], handles[0], mo=True)
            mc.pointConstraint(mc.listRelatives(rootFootR, ad=True, typ='joint')[0], handles[1], mo=True)
        
            # Point Constr IK toe.
            ankleL_jnt = [node for node in mc.listRelatives(rootLegL, ad=1, typ='joint') if '_ik' in node][0]
            ankleR_jnt = [node for node in mc.listRelatives(rootLegR, ad=1, typ='joint') if '_ik' in node][0]           
            toeL_ref = [node for node in mc.listRelatives(rootFootL, ad=1, typ='transform') if '_ref' in node]
            toeR_ref = [node for node in mc.listRelatives(rootFootR, ad=1, typ='transform') if '_ref' in node]
        
            for item in [toeL_ref[0], toeR_ref[0]]:
                if '_L' in item:
                    ankle_jnt = ankleL_jnt
                else:
                    ankle_jnt = ankleR_jnt
                newRef = mc.group(n=item+'_1', empty=True)
                self.trans.snap(newRef, item)
                mc.parent(newRef, ankle_jnt)

        #self.finalize(rootCtrl)
        
        return
    
    def createRootRig(self, assetName=None):
        if assetName == None:
            assetName = ''
        ctrlGrp = mc.group(n=assetName+'controllers_grp', empty=True)
        rigGrp = mc.group(ctrlGrp, n=assetName+'RIG_GRP')
        
        mainCtrl = shapes.shpDico[str(6)]('ROOT_ctrl', radius=50)  # -Root shape.
        mc.parent(mainCtrl, ctrlGrp)

        localCtrl = shapes.shpDico[str(6)]('local_ctrl', radius=30)  # -Root shape.
        if mc.objExists('spine_root_ref') is True:
            self.trans.snap(localCtrl, 'spine_root_ref')
        mc.parent(localCtrl, mainCtrl,a=True)
        self.trans.orig_Sel(localCtrl)
            
        return mainCtrl, localCtrl
    
    def getScale(self):
        sel = mc.ls(geometry=True)
        zBox = mc.polyEvaluate(sel, b=True )[-1]
        value = zBox[-1]-zBox[0]
        scale = 100/value
        scale += 1
        
        return scale
    
    
    def addControlColors(self, centerPrefix='_C', leftSidePrefix='_L', rightSidePrefix='_R', controlSuffix='_ctrl'):
        """
        add colors to control shapes based on side
        """
        ctrls = []
        allControls = mc.ls('*' + controlSuffix)
        [ctrls.append(ctrl) for ctrl in allControls if ctrl.endswith(controlSuffix)]
        
        for ctrl in allControls:

            l_clrIndex = 6 # - Blue
            r_clrIndex = 13 # - Red
            c_clrIndex = 22 # - Yellow
            fk_clrIndex = 14 # - Green
            clrIndex = 0
            
            shapes = mc.listRelatives(ctrl, s=1)
            clrIndex = c_clrIndex
            if leftSidePrefix in ctrl:
                clrIndex = l_clrIndex
            
            elif rightSidePrefix in ctrl:
                clrIndex = r_clrIndex
                
            elif centerPrefix in ctrl:
                clrIndex = c_clrIndex
                
            if 'fk' in ctrl and centerPrefix in ctrl:
                clrIndex = fk_clrIndex
                
            if shapes is not None:
                for s in shapes:
                    mc.setAttr(s + '.ove', 1)
                    mc.setAttr(s + '.ovc', clrIndex)
            
    def getCtrlNodes(self, root):
        ctrlList = []
        children = mc.listRelatives(root, ad=True, typ='transform')
        [ctrlList.append(ctrl) for ctrl in children if '_ctrl' in ctrl]
        
        return ctrlList
    
    def getDriverNodes(self, root):
        driverList = []
        children = mc.listRelatives(root, ad=True)
        [driverList.append(driver) for driver in children if '_drv' in driver]
        
        return driverList
    
    def createSkeleton(self, rigRoots):
        mainGrp = mc.group(n='skeleton_grp', empty=True)
        
        allDrivers = []
        allJoints = []
        # Create and place joints.
        for root in rigRoots:
            drivers = []
            [drivers.append(driver) for driver in mc.listRelatives(root, ad=True) if '_drv' in driver]
            
            if 'hand' in root:
                drivers.reverse()
            [allDrivers.append(driver) for driver in drivers if '_drv' in driver]

            joints = []
            for driver in drivers:
                name = str(driver)
                newname = name.replace('_drv', '_jnt')
                
                jnt = mc.createNode('joint', n=newname)
                mc.parent(jnt, mainGrp)
                self.trans.snap(jnt, driver)
                joints.append(jnt)
                allJoints.append(jnt)

            [mc.parent(joints[i], joints[i-1]) for i in range(1, len(joints)) if len(joints) >= 2]
        
        if len(rigRoots) == 12:
            ## Attach limbs if full body count is found.
            # Orient/organize spine/neck/head joints.
            allJointRoot = mc.listRelatives(mainGrp, c=True)
            spine = mc.listRelatives(allJointRoot[0], ad=True)[0]
            mc.parent(allJointRoot[1], spine, a=True)

            spinehead = mc.listRelatives(allJointRoot[0], ad=True)
            spinehead.append(allJointRoot[0])
            spinehead.reverse()
            self.fonc.manual_orient_chain(spinehead)

            # Organize other joints.
            mc.parent(allJointRoot[2], allJointRoot[3], spine, a=True) # Shoulders.
            
            mc.parent(allJointRoot[4], allJointRoot[2], a=True) # L arm.
            mc.parent(allJointRoot[5], allJointRoot[3], a=True) # R arm.
    
            mc.parent(allJointRoot[6], allJointRoot[0], a=True) # L leg.
            mc.parent(allJointRoot[7], allJointRoot[0], a=True) # R leg.
            
            lHand = mc.listRelatives(allJointRoot[4], ad=True)[0]
            rHand = mc.listRelatives(allJointRoot[5], ad=True)[0]
            mc.parent(allJointRoot[8], lHand, a=True) # L hand.
            mc.parent(allJointRoot[9], rHand, a=True) # R hand.
            
            lAnkle = mc.listRelatives(allJointRoot[6], ad=True)[0]
            rAnkle = mc.listRelatives(allJointRoot[7], ad=True)[0]
            mc.parent(allJointRoot[10], lAnkle, a=True) # L foot.
            mc.parent(allJointRoot[11], rAnkle, a=True) # R foot.
            
            mc.makeIdentity(allJointRoot[2], apply=True, t=1, r=1, s=1, n=0, pn=1)
            mc.makeIdentity(allJointRoot[3], apply=True, t=1, r=1, s=1, n=0, pn=1)
            mc.makeIdentity(allJointRoot[6], apply=True, t=1, r=1, s=1, n=0, pn=1)
            mc.makeIdentity(allJointRoot[7], apply=True, t=1, r=1, s=1, n=0, pn=1)
            
            fingers = []
            [fingers.append(jnt) for jnt in mc.listRelatives(allJointRoot[8], ad=True) if '_0' in jnt]
            mc.parent(fingers[:-1], lHand, a=True)
            fingers = []
            [fingers.append(jnt) for jnt in mc.listRelatives(allJointRoot[9], ad=True) if '_0' in jnt]
            mc.parent(fingers[:-1], rHand, a=True)
            
        # Constraint all joint (matrix)
        [self.trans.snap(allDrivers[i], allJoints[i]) for i in range(0, len(allDrivers))]
        [self.matrix.matrixConstraint_old(str(allDrivers[i]), str(allJoints[i]), mo=False) for i in range(0, len(allDrivers))]

        mc.parent(mainGrp, 'RIG_GRP')
        
        return
    
    def finalize(self, *args):
        # Hide setup joints and ikHandles.
        if len(args) == 0:
            return
        else :
            for arg in args:
                joints = mc.listRelatives(arg, ad=True, typ='joint')
                handles = mc.listRelatives(arg, ad=True, typ='ikHandle')
        if joints is not None:
            [mc.setAttr(joint+'.drawStyle', 2) for joint in joints]
        if handles is not None:
            [mc.setAttr(handle+'.visibility', 0) for handle in handles]
        
        return
