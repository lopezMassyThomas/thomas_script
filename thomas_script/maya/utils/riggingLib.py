'''
Created on Dec 12, 2016

@author: thomas
'''
#from common.utils import system
import maya.api.OpenMaya as om
import maya.cmds as mc
from __builtin__ import isinstance


class RiggingLib(object):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        pass



    # #######################=====================================================
    # #Snap Object to target.
    # #######################=====================================================
    # def snap(self, objName, target) :
    #
    #     #Constraint parent.
    #     constraint=mc.parentConstraint(target,
    #                                    objName,
    #                                    maintainOffset=False,
    #                                    name='TMP_cstr_TMP_snap')
    #     #Delete constraint.
    #     mc.delete(constraint[0])
    
    
    # ###############################=============================================
    # #Create grp and zeroOut target.
    # ###############################=============================================
    #
    # #Use Selection.
    # def orig_Sel(self, objList=None, preffix='_orig'):
    #     ''''''
    #     # Get Current selection
    #     if objList == None :
    #         selection = mc.ls(sl=True)
    #     if isinstance(objList, list) is True :
    #         selection = objList
    #     else :
    #         selection = [objList]
    #
    #     for i in selection:
    #         if i.startswith('|'):
    #             i = i[1:]
    #         # Get Parent
    #         sel_parent = mc.listRelatives( i, p= True )
    #         if str(sel_parent).startswith('|'):
    #             sel_parent = sel_parent[1:]
    #
    #         if sel_parent:
    #             sel_parent= sel_parent[0]
    #         # Get current Obj Transform
    #         pos_Sel = mc.xform( i, q=True, t=True, ws=True )
    #         rot_Sel = mc.xform( i, q=True, ro=True, ws=True )
    #         # Create a group
    #         grp = mc.group( em=True, name='{}{}'.format(i,preffix))
    #         # Set in place
    #         mc.xform( grp, a=True, t=pos_Sel, ro=rot_Sel, s=[1,1,1] )
    #         # Parent current to orig Group
    #         mc.parent( i, grp, relative= False )
    #         # reParent group to original parent
    #         if sel_parent:
    #             mc.parent( grp, sel_parent, relative= False )
    #     return grp
    #
    # # Use pre-defined List.
    # def orig_List(self, objectList):
    #     ''''''
    #     # Get Current selection
    #     selection = objectList
    #
    #     for i in selection:
    #         # Get Parent
    #         sel_parent = mc.listRelatives( i, p= True )
    #         if sel_parent:
    #             sel_parent= sel_parent[0]
    #         # Get current Obj Transform
    #         pos_Sel = mc.xform( i, q=True, t=True, ws=True )
    #         rot_Sel = mc.xform( i, q=True, ro=True, ws=True )
    #         # Create a group
    #         grp = mc.group( em=True, name= i[0] + '_orig' )
    #         # Set in place
    #         mc.xform( grp, a=True, t=pos_Sel, ro=rot_Sel, s=[1,1,1] )
    #         # Parent current to orig Group
    #         mc.parent( i, grp, relative= False )
    #         # reParent group to original parent
    #         if sel_parent:
    #             mc.parent( grp, sel_parent, relative= False )
    #     return grp
    
    # #######################################################################=====
    # # Add one joint between two others and move/rotate between them. (Skin)
    # #######################################################################=====
    #
    # def addBlendedJoint(self, sel):
    #
    #         #Get Parent of selection.
    #         parentSel = mc.listRelatives(sel, p=True)
    #         #Define and create jnt.
    #         jnt_name = '{}_{}'.format('blend', sel)
    #         jnt = mc.joint(n=jnt_name, r=1.5)
    #         #Set position of new jnt.
    #         pConstr = mc.pointConstraint(sel, jnt)
    #         mc.delete(pConstr)
    #         #Parent new jnt to the parent of selection.
    #         mc.parent(jnt, parentSel)
    #         #Create node to blend rotation of chainJnt.
    #         node = mc.createNode('pairBlend', n=sel+'_pairBlend')
    #         #Set attribute of pairBlend node.
    #         mc.setAttr(node+'.rotInterpolation', 1)
    #         mc.setAttr(node+'.weight', 0.5)
    #         #Connect selectedJnt to pairBlend.
    #         mc.connectAttr(sel+'.t', node+".inTranslate1")
    #         mc.connectAttr(sel+'.t', node+".inTranslate2")
    #         mc.connectAttr(sel+".r", node+".inRotate1")
    #         #Connect pairBlend to new Jnt.
    #         mc.connectAttr(node+".outRotateX", jnt+".rotateX")
    #         mc.connectAttr(node+".outRotateY", jnt+".rotateY")
    #         mc.connectAttr(node+".outRotateZ", jnt+".rotateZ")
    #
    #         mc.connectAttr(node+".outTranslateX", jnt+".translateX")
    #         mc.connectAttr(node+".outTranslateY", jnt+".translateY")
    #         mc.connectAttr(node+".outTranslateZ", jnt+".translateZ")
    #         #Connect scale of selected jnt and new Jnt.
    #         mc.connectAttr(sel+".scale", jnt+".scale")
    #
    #
    # ###################################################################=========
    # # Add one jnt on selected. Increment itself if used multiple times.
    # ###################################################################=========
    #
    # def addSupportJoint(self, objName=[]) :
    #     baseName = 'extraJnt'
    #
    #     for i in objName :
    #         children = mc.listRelatives(objName, c=True)
    #     if children is None :
    #         increment = 1
    #     else :
    #         increment = 1 + len(children)
    #
    #     if not objName:
    #         objName = mc.ls(sl=True)
    #
    #     for i in objName :
    #         jnt01 = mc.createNode('joint', n='{}{}_{}'.format(baseName, increment,  i))
    #         mc.setAttr(jnt01+'.radius', 1.5)
    #         mc.parent(jnt01, i, r=True)


    # ##############################################==============================
    # # Calculate average from list of int or float.
    # ##############################################==============================
    #
    # def averageValue(self, listValue):
    #
    #     total = sum(listValue)
    #     total = float(total)
    #
    #     return total / len(listValue)
    
    
    # ###############################################=============================
    # # Get the distance between two vector/position.
    # ###############################################=============================
    #
    # def getDistance(self, positionA, positionB):
    #     from math import sqrt
    #     a = positionA #data point 1
    #     b = positionB #data point 2
    #     result = sqrt(sum((a - b)**2 for a, b in zip(a, b)))
    #     return result
    
    # ####################################################################========
    # # Get the center of an object using the Bounding box Infos of xform.
    # ####################################################################========
    # def getGeoBBoxCenter(self, node):
    #
    #     #get raw boundingBox values of tagObject.
    #     bbInfo = mc.xform(node, q=True, bb =True)
    #
    #     #calculate average of each axis value.
    #     xValueList = [bbInfo[0],
    #                   bbInfo[3]]
    #     averageX = self.averageValue(xValueList)
    #     yValueList = [bbInfo[1],
    #                   bbInfo[4]]
    #     averageY = self.averageValue(yValueList)
    #     zValueList = [bbInfo[2],
    #                   bbInfo[5]]
    #     averageZ = self.averageValue(zValueList)
    #
    #     result = [averageX, averageY, averageZ]
    #
    #     return result
    
    #######################################################=====================
    # Get the index and weight value of a vertex selection.
    #######################################################=====================
    def softSelection(self):
        
        selection = om.MSelectionList()
        softSelection = om.MRichSelection()
        om.MGlobal.getRichSelection(softSelection)
        softSelection.getSelection(selection)
    
        dagPath = om.MDagPath()
        component = om.MObject()
    
        iter = om.MItSelectionList( selection,om.MFn.kMeshVertComponent )
        elements = []
        weights = []
        while not iter.isDone():
            iter.getDagPath( dagPath, component )
            dagPath.pop()
            node = dagPath.fullPathName()
            fnComp = om.MFnSingleIndexedComponent(component)
    
            for i in range(fnComp.elementCount()):
                #elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
                elements.append(fnComp.element(i))
                weights.append(fnComp.weight(i).influence())
            iter.next()
        return elements,weights 
    
    #######################################################=====================
    # Add shape to transform
    #######################################################=====================    
    
    def addShapeNode(self, nodeList, orient):
        for elem in nodeList:
            
            child = mc.listRelatives(elem, c=True)
            
            if child is None : #If end joint = stop
                continue
            else :                
                posChild = mc.getAttr('{}.{}'.format(child[0], 'tx'))    
                posShape = posChild/2 #find middle of the joint.(position ctrl)
            
                circle = mc.circle( nr=orient, 
                                    center = (posShape, 0, 0), 
                                    r=1 )
                
                cShape = mc.listRelatives(circle[0], s=True)
               
                mc.parent( cShape[0], elem, s=True, r=True )
                mc.rename( cShape[0], '%sShape' %(elem) )
                mc.delete( circle[0] ) #Parent shape ctrl on joint. 
    
#===============================================================================
# SKELETON RIG    
#===============================================================================
    def creatSkeletonLocGuide(self):
        legPartList = ['hip', 'shin', 'ankle', 'toe', 'toeTip', 'heel']
        spinePartList = ['pelvis', 'spine01', 'spine02', 'spine03', 'torso', 'neck', 'head', 'headEnd']
        armPartList = ['scapula', 'tensionMap', 'foreArm', 'wrist']
        grp = mc.group(n= 'humanRigGuide_grp', empty=True)
        
        for i in legPartList :
            mc.spaceLocator(n=i)
            mc.parent(i, grp, a=True)
            mc.setAttr('{}.{}'.format(i, 'tx'), 2)
        
        mc.setAttr('hip.ty', 12)
        mc.setAttr('shin.ty', 8)
        mc.setAttr('ankle.ty', 2)
        mc.setAttr('toe.tz', 1.5)
        mc.setAttr('toeTip.tz', 3)
        mc.setAttr('heel.tz', -1)
        
        for i in spinePartList :
            mc.spaceLocator(n=i)
            mc.parent(i, grp, a=True)
            
        mc.setAttr('pelvis.ty', 12)
        mc.setAttr('spine01.ty', 14)
        mc.setAttr('spine02.ty', 16)
        mc.setAttr('spine03.ty', 18)
        mc.setAttr('torso.ty', 20)
        mc.setAttr('neck.ty', 23)
        mc.setAttr('head.ty', 25)   
        mc.setAttr('headEnd.ty', 27)     
        
        for i in armPartList :
            mc.spaceLocator(n=i)
            mc.parent(i, grp, a=True)   
            mc.setAttr('{}.{}'.format(i, 'ty'), 22) 
        
        mc.setAttr('scapula.tx', 2)
        mc.setAttr('tensionMap.tx', 4)
        mc.setAttr('foreArm.tx', 8)
        mc.setAttr('wrist.tx', 12)   
        
                        
#===============================================================================
# IK/FK LEG    
#===============================================================================
    ####################################========================================
    # # Create Oriented chain of Joints.
    ####################################========================================
    
    def create_OrientedChain(self, baseName):
        chain = self.create_chain_onSelected(baseName)
        # Orient joints chain
        self.orient_chain(list_joints = chain)
        return chain
    
    ############################================================================
    # # Create_Oriented IK/FK Leg.   
    ############################================================================
    
    def create_Ik_Fk_Leg(self):
        
        skinChain = self.create_OrientedChain(baseName = 'L')
        mirrorChain = self.mirror_Jnt(skinChain)
        
        fkChain = self.create_FK(skinChain[0])
        ikChain = self.create_IK(skinChain[0])
        constraints = self.parent_constraint(fkChain, ikChain, skinChain)
        self.switch_Ik_Fk('L_Leg_Switch_Ik_Fk', constraints[0], constraints[1], constraints[2])
        
        mirrorfkChain = self.create_FK(mirrorChain[0])
        mirrorikChain = self.create_IK(mirrorChain[0])
        mirrorconstraints = self.parent_constraint(mirrorfkChain, mirrorikChain, mirrorChain)
        self.switch_Ik_Fk('R_Leg_Switch_Ik_Fk', mirrorconstraints[0], mirrorconstraints[1], mirrorconstraints[2])        
        

    #############################################===============================
    # Create chain of joints on selected objects.
    #############################################===============================
    
    def create_chain_onSelected(self, baseName, radius=1) :
            
        '''
        Create jnt based on locator Guide position
        
        baseName: string, The base name of my joints
        radius: float, Define the radius of joints
        '''
        # --- Get Guide element
        guide= mc.ls( sl= True )
        
        # --- Check current Selection
        if len(guide) < 1:
            print ' > select some object to build chain joints'
            return
            
        list_joints_created = []
        
        # --- Create joints:
        for i in range(0, len( guide)):
            
            curName = guide[i]
            
            # - Get the WS position
            guide_position= mc.xform( guide[i], ws=True, translation=True, query=True )
            
            # - Define the joint name
            jnt_name = '{}_{}_{}'.format(baseName, curName, 'jnt')
            
            # - Create joint
            jnt = mc.createNode( 'joint', n= jnt_name )
            
            # - Set the Radius jnt
            mc.setAttr( jnt + '.radius', radius )
            
            # - Set WS position
            mc.xform( jnt, ws= True, translation= guide_position )
            
            # - don't Parent the first joint
            if i != 0:
                # - Parent jnt to previous
                mc.parent(jnt, list_joints_created[i-1])
            
            # - reDefine previous jnt
            list_joints_created.append(jnt)
        return list_joints_created
        
    ###################################################=========================
    # Get Cross Direction. Produit en croix de matrice.
    ###################################################=========================
    
    def getCrossDir(self, objA, objB, objC):
        posA = mc.xform( objA, ws=True, rp=True, query=True )
        posB = mc.xform( objB, ws=True, rp=True, query=True )
        posC = mc.xform( objC, ws=True, rp=True, query=True )
        vect1 = (posA[0]-posB[0], posA[1]-posB[1], posA[2]-posB[2]) # (u1, u2, u3)
        vect2 = (posC[0]-posB[0], posC[1]-posB[1], posC[2]-posB[2]) # (v1, v2, v3)
        vect1 = om.MVector(vect1) # vect1 is now an MVector
        vect2 = om.MVector(vect2) # vect2 is now an MVector
        vectResult = vect1^vect2 # produit en croix
        vectResult = vectResult.normal()
        return (vectResult.x, vectResult.y, vectResult.z) # return the normal to the calculated vector

    #####################=======================================================
    # Orient Joint Chain.
    #####################=======================================================
    
    def orient_chain(self, list_joints, invert=False):

        # at least 2 items selected
        if len(list_joints) < 1:
            print ('select at least 2 locators')
            # if <1 stop every thing in this function(def)
            return
            
        prevUp = om.MVector((0, 0, 0)) # upVector reset to 0
        
        for i in range (0, len(list_joints)):
            currentJoint = list_joints[i]
            parentJoint = ''
            if i != 0:
                parentJoint = list_joints[i-1]
            
            # last joint (the one with no child)
            if i == len(list_joints )-1:

                mc.orientConstraint(parentJoint, currentJoint, weight=1)
                mc.delete(currentJoint, cn=True)
                return
    
            childJoint = list_joints[i+1]
            
            # Un-parent the child
            mc.parent(childJoint, w=True)
            
            upVect = (0, 0, 0)# upVector courant reset to 0
            
            # auto Guess direction
            if parentJoint != '':
                upVect = self.getCrossDir(parentJoint, 
                                          currentJoint, 
                                          childJoint)
            else:
                upVect = self.getCrossDir(currentJoint, 
                                          childJoint, 
                                          list_joints[i+2])
            # end auto Guess direction
            if invert is True :
                upVect = (upVect[0]*-1, upVect[1]*-1, upVect[2]*-1)
            # Aim constraint
            mc.aimConstraint(childJoint, 
                             currentJoint, 
                             aim=(1.0, 0.0, 0.0), 
                             upVector=(0.0, 0.0, 1.0), 
                             worldUpType="vector", 
                             worldUpVector=upVect)
    
            # Delete constraint
            mc.delete(currentJoint, cn=True)
            
            curUp = om.MVector(upVect)
            curUp = curUp.normal()
            dotProd = curUp*om.MVector(prevUp)
            prevUp = upVect
            
            if(i > 0 and dotProd <= 0.0):
                mc.xform(currentJoint, 
                         relative=True, 
                         objectSpace=True, 
                         rotateAxis=(0, 0, 180))
                prevUp = om.MVector(prevUp) * -1.0
                
            mc.joint(currentJoint, e=True, zso=True)
            mc.makeIdentity(currentJoint, apply=True) # reset all.
            
            # re Parent objects
            mc.parent(childJoint, currentJoint)
            
    #############################################===============================
    # Create fk chain from selected joint chain
    #############################################===============================
    
    def create_FK (self, objName):
        
        sel = objName
        
        duplicata = mc.duplicate(sel, rc = True)
        fkJntList = []

        for i in range(0, len(duplicata)) :
            
            splitName = duplicata[i].split('_')

            renamedObj = mc.rename(duplicata[i], '{}_{}_{}_{}'.format(splitName[0], 
                                                                      splitName[1], 
                                                                      'FK', 
                                                                      'jnt'
                                                                      )
                                   )
            fkJntList.append(renamedObj)       

        for i in fkJntList :
            mc.select(i)
            self.orig_Sel()
        
        for elem in fkJntList:
            
            child = mc.listRelatives(elem, c=True)
            
            if child is None :
                continue
            else :
                for i in range(0, 3) :
                    if i is 0 :
                        nr=(1, 0, 0)
                    if i is 1 :
                        nr=(0, 1, 0)
                    if i is 2 :
                        nr=(0, 0, 1) 
                           
                    posChild = mc.getAttr('{}.{}'.format(child[0], 'tx'))    
                    posShape = posChild/2
                
                    circle = mc.circle( nr=(nr[0], nr[1], nr[2]), 
                                        center = (posShape, 0, 0), 
                                        r=1 )
                    
                    cShape = mc.listRelatives(circle[0], s=True)
                   
                    mc.parent( cShape[0], elem, s=True, r=True )
                    mc.rename( cShape[0], '%sShape' %(elem) )
                    mc.delete( circle[0] )
                    
                
        return fkJntList
    
    ############################################================================
    # Create IK chain from selected joint chain.
    ############################################================================
    
    def create_IK (self, objName):

        sel = objName
        duplicata = mc.duplicate(sel, rc = True)
        
        ikJntList = []

        for i in range(0, len(duplicata)) :
            
            splitName = duplicata[i].split('_')

            renamedObj = mc.rename(duplicata[i], '{}_{}_{}_{}'.format(splitName[0], 
                                                                      splitName[1], 
                                                                      'IK', 
                                                                      'jnt'
                                                                      )
                                   )
            ikJntList.append(renamedObj)     
            
        #- Create Ikhandle    
        handleName = '{}_{}_{}'.format(splitName[0], splitName[1], 'IkHandle')
        poleVectorName = '{}_{}_{}'.format(splitName[0], 'KneeOrient', 'Ctrl')
        
        handle = mc.ikHandle( n= handleName, 
                              sj=ikJntList[0], 
                              ee=ikJntList[-1], 
                              sol= 'ikRPsolver', 
                              shf = False)
       
        
        poleVector= mc.circle ( n= poleVectorName, nr = (1,0,0), r=0.5 )   

        for i in range(0, 2) :

            if i is 0 :
                nr=(0, 1, 0)
            if i is 1 :
                nr=(0, 0, 1) 
            
            circle = mc.circle( nr=(nr[0], nr[1], nr[2]), 
                                r=0.5 )
            
            cShape = mc.listRelatives(circle[0], s=True)
            
            mc.parent( cShape, poleVector[0], s=True, r=True )
            mc.delete( circle[0] )
        
        #-- Vectors for PoleVector
        
        posA = om.MVector(mc.xform( ikJntList[0], ws=True, rp=True, query=True ))
        posB = om.MVector(mc.xform( ikJntList[1], ws=True, rp=True, query=True ))
        posC = om.MVector(mc.xform( ikJntList[2], ws=True, rp=True, query=True ))
        
        # -Get the vectors
        vectAB = posB - posA
        vectAC = posC - posA
        
        # - get the projection of B over AC
        dotProd = vectAC * vectAB
        proj = dotProd / vectAC.length()
        vectACNormalized = vectAC.normalize()
        
        finalV = vectACNormalized * proj
        finalV = vectAB - finalV
        finalV = finalV + posB
        
        
        #- align the polevector to the position found
        mc.xform( poleVector, ws=True, t=finalV)
        
        
        #- create an orig
        mc.select(poleVector[0])
        self.orig_Sel()
        
        #- create poleVector constraint
        mc.poleVectorConstraint (poleVector, handle[0])
        
        return ikJntList        

    ######################################======================================
    # Parent constrain skinJoint on ik/ik.
    ######################################======================================

    def parent_constraint(self, fk, ik, skin):
    
        listConstraintsName = []
        listWeightFK = []
        listWieghtIK = []
        
        for i in range(0, len(skin)) :
            
            splitName = skin[i].split('_')

            objName = '{}_{}'.format(splitName[0], splitName[1])        
        
        for i in range (0,3):
            contraintName = mc.parentConstraint(fk[i], skin[i], 
                                                n = '{}_{}_{}'.format(objName, 
                                                                      'ParentConstraint', 
                                                                      str(i+1)
                                                                      )
                                                )
            
            mc.parentConstraint(ik[i], skin[i], 
                                n = '{}_{}_{}'.format(objName, 
                                                      'ParentConstraint', 
                                                      str(i+1)
                                                      )
                                )
            
            weight_FK, weight_IK = mc.parentConstraint (skin[i],  
                                                        q= True, 
                                                        wal = True)
            
            listConstraintsName.append(contraintName[0])
            listWeightFK.append(weight_FK)
            listWieghtIK.append(weight_IK)

        return (listWeightFK, listWieghtIK, listConstraintsName)    
    
    ########################====================================================
    # Create a switch ik fk.
    ########################====================================================
    
    def switch_Ik_Fk(self, attrName, FK_WO, IK_WO, constrNodes):
        
        objExist = mc.objExists('Extra_Ctrl')
        
        # If exist do nothing else create ctrl.
        if objExist is False : 
            ctrl = mc.circle(n='Extra_Ctrl', d=1, s=6)
        else :
            mc.select('Extra_Ctrl')
            ctrl = mc.ls(sl=True)

        mc.addAttr(ctrl, ln=attrName, at="float", min=0, max=1, k=True, h=False, r=True, w=True)
        
        DIFname = '{}_{}'.format(attrName, 'DIF')
        mc.createNode('reverse', n=DIFname)
        
        # Loop for input/output x, y, z.
        for i in range(0, len(constrNodes)) :
            if i == 0 :
                a = 'x'
            if i == 1 :
                a = 'y'
            if i == 2 :
                a = 'z'        
            
            #def name obj.
            attrFK = '{}.{}'.format(constrNodes[i], FK_WO[i])
            attrIK = '{}.{}'.format(constrNodes[i], IK_WO[i])
            attrCtrl = '{}.{}'.format(ctrl[0], attrName)
            
            #Connect fk.
            mc.connectAttr(attrCtrl, attrFK)
            
            #Connect Ik via Reverse. 0=Ik, 1=Fk.
            mc.connectAttr(attrCtrl, '{}.{}{}'.format(DIFname, 'i', a))
            mc.connectAttr('{}.{}{}'.format(DIFname, 'o', a), attrIK)
    
    ###############################################=============================
    # Create a symetry of the selected joint chain.
    ###############################################=============================
    
    def mirror_Jnt(self, jntList):
        
        newTopNode = mc.mirrorJoint(jntList[0], myz=True, mb=True, sr=('L_', 'R_'))
        
        children = mc.listRelatives(newTopNode, c=True)
        
        mc.select(newTopNode)
        mc.select(children, add=True)
        sel = mc.ls(sl=True)
        
        return sel

#===============================================================================
# IK/FK LEG    //END\\
#===============================================================================

#===============================================================================
# IK/FK Foot with roll.
#===============================================================================
    
    def create_Ik_Fk_Foot(self, baseName):
        
        chain = self.create_chain_onSelected(baseName)
        # Orient joints chain
        self.orient_chain(list_joints = chain, invert=False)
        return chain
        
        
        
    #def createSkin_FootJointChain(self):
        
    