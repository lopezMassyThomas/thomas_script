'''
Created on Jun 1, 2017

@author: thomas
'''
import maya.cmds as mc
from thomas_script.maya.utils import riggingLib


reload(riggingLib)


import maya.api.OpenMaya as om


class Core(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.riggigLib = riggingLib.RiggingLib()

    def createJntChain(self, name, list, autoOrient=True):
        mc.select(clear=True)
        [mc.select(i, add=True) for i in list]
        skinChain = self.create_OrientedChain(baseName=name, name='Skin', autoOrient=autoOrient)

        return skinChain


    def getAllSkinjnts(self):
        #-get all skin joints
        skinJoints = []
        x = mc.listRelatives('skinJoints_GRP', ad=True)
        for i in x:
            skinJoints.append(str(i))
        skinJoints.reverse()
        return skinJoints


    #---------------------------------
    # Create Oriented chain of Joints.
    def create_OrientedChain(self, baseName, name, autoOrient=True):
        chain = self.create_chain_onSelected(baseName, name)
        # Orient joints chain
        if autoOrient is True:
            self.orient_chain(list_joints=chain)
        else:
            self.manual_orient_chain(list_joints=chain)
        return chain   
    
    
    #--------------------------------------------
    # Create chain of joints on selected objects.
    def create_chain_onSelected(self, baseName, name='Skin', radius=1) :      
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
            guide_position = mc.xform(guide[i], ws=True, translation=True, query=True )
            
            # - Define the joint name
            if baseName is None :
                jnt_name = '{}_{}_{}'.format(curName, name, 'jnt')
                if mc.objExists(jnt_name):
                    jnt_name = '{}_{}_{}'.format(curName, name, 'jnt01')
            else:
                jnt_name = '{}_{}_{}_{}'.format(baseName, curName, name, 'jnt')
                if mc.objExists(jnt_name) :
                    jnt_name = '{}_{}_{}_{}'.format(baseName, curName, name, 'jnt01')
                
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


    #--------------------------------------------------
    # Get Cross Direction. Produit en croix de matrice.
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


    # --------------------
    # Orient Joint Chain.
    def manual_orient_chain(self, list_joints):
        # at least 2 items selected
        if len(list_joints) < 1:
            print ('select at least 2 locators')
            # if <1 stop every thing in this function.
            return

        prevUp = om.MVector((0, 0, 0))  # upVector reset to 0

        for i in range(0, len(list_joints)):
            currentJoint = list_joints[i]
            parentJoint = ''
            if i != 0:
                parentJoint = list_joints[i - 1]

            # last joint (the one with no child)
            if i == len(list_joints) - 1:
                mc.orientConstraint(parentJoint, currentJoint, weight=1)
                mc.delete(currentJoint, cn=True)
                return

            childJoint = list_joints[i + 1]

            # Un-parent the child
            mc.parent(childJoint, w=True)

            upVect = (0, 0, 0)  # upVector courant reset to 0

            # Aim constraint
            mc.aimConstraint(childJoint,
                             currentJoint,
                             aim=(1.0, 0.0, 0.0),
                             upVector=(0.0, 1.0, 0.0),
                             worldUpType="vector",
                             worldUpVector=(0.0, 0.0, 1.0))

            # Delete constraint
            mc.delete(currentJoint, cn=True)

            curUp = om.MVector(upVect)
            curUp = curUp.normal()
            dotProd = curUp * om.MVector(prevUp)
            prevUp = upVect


            mc.joint(currentJoint, e=True, zso=True)
            mc.makeIdentity(currentJoint, apply=True)  # reset all.

            # re Parent objects
            mc.parent(childJoint, currentJoint)



    #--------------------
    # Orient Joint Chain.
    def orient_chain(self, list_joints, invert=False):
        '''
        '''
        # at least 2 items selected
        if len(list_joints) < 1:
            print ('select at least 2 locators')
            # if <1 stop every thing in this function.
            return
            
        prevUp = om.MVector((0, 0, 0)) # upVector reset to 0
        
        for i in range (0, len(list_joints)):
            currentJoint = list_joints[i]
            parentJoint = ''
            if i != 0:
                parentJoint = list_joints[i-1]
            
            # last joint (the one with no child)
            if i == len(list_joints)-1:

                mc.orientConstraint(parentJoint, currentJoint, weight=1)
                mc.delete(currentJoint, cn=True)
                return
    
            childJoint = list_joints[i+1]
            
            # Un-parent the child
            mc.parent(childJoint, w=True)
            
            upVect = (0, 0, 0)# upVector courant reset to 0
            
            # auto Guess direction
            if parentJoint != '':
                wUpVect = self.getCrossDir(parentJoint,
                                          currentJoint,
                                          childJoint)

            else:
                wUpVect = self.getCrossDir(currentJoint,
                                          childJoint,
                                          list_joints[i+2])
            # end auto Guess direction
            if invert is True:
                wUpVect = (wUpVect[0]*-1, wUpVect[1]*-1, wUpVect[2]*-1)
            # Aim constraint
            mc.aimConstraint(childJoint, 
                             currentJoint, 
                             aim=(1.0, 0.0, 0.0), 
                             upVector=(0.0, 0.0, 1.0),
                             worldUpType="vector", 
                             worldUpVector=wUpVect)
    
            # Delete constraint
            mc.delete(currentJoint, cn=True)
            
            curUp = om.MVector(wUpVect)
            curUp = curUp.normal()
            dotProd = curUp*om.MVector(prevUp)
            prevUp = wUpVect

            if(i > 0 and dotProd <= 0.0):
                mc.xform(currentJoint,
                         relative=True,
                         objectSpace=True,
                         rotateAxis=(0, 0, 180))
                prevUp = om.MVector(prevUp) * -1.0
                
            mc.joint(currentJoint, e=True, zso=True)
            mc.makeIdentity(currentJoint, apply=True)# reset all.
            
            # re Parent objects
            mc.parent(childJoint, currentJoint)


    #-------------------------------------
    # Parent constrain skinJoint on ik/fk.
    def parent_constraint(self, fk, ik, skin):   
        listConstraintsName = []
        listWeightFK = []
        listWieghtIK = []
        
        for i in range(0, len(skin)) :
            splitName = skin[i].split('_')

            objName = '{}_{}'.format(splitName[0], splitName[1]) #Redifine baseName.
            contraintName = mc.parentConstraint(fk[i], skin[i], n='{}_{}_{}'.format(objName, 'ParentConstraint', str(i+1))) #Contraint fk on skin.
            
            mc.parentConstraint(ik[i], skin[i], n = '{}_{}_{}'.format(objName, 'ParentConstraint', str(i+1))) #Contraint ik on skin.

            weight_FK, weight_IK = mc.parentConstraint(skin[i], q=True, wal=True) #Query.
            
            listConstraintsName.append(contraintName[0])
            listWeightFK.append(weight_FK)
            listWieghtIK.append(weight_IK)

        return (listWeightFK, listWieghtIK, listConstraintsName)    
    
    
    def constraint_switch(self, attrName, selection, indexNames=None, constrType='parent'):
        '''
        Create a switch of object constraint by two other.
        First select 2 objects as drivers.
        Then the node that will be constraint, the driven. 
        Last, the ctrl on which you want the attribute to appear.        
        '''
        
        driven = selection[-2]
        ctrl = selection[-1]
        drivers = selection[:-2]      
        
        if selection is None:
            selection = mc.ls(sl=True)
        else:
            pass   
           
        if indexNames is None:
            mc.addAttr(ctrl, ln=attrName, at="float", min=0, max=1, k=True, h=False, r=True, w=True)
               
        if len(indexNames) > 1:
            iNames = indexNames[0]
            iNames = ['{}:{}'.format(iNames, indexNames[i]) for i in range(1, len(indexNames))]
            mc.addAttr(ctrl, ln=attrName, at='enum', en=iNames[0], k=True)
            
        constrNode = mc.parentConstraint(drivers[0], driven, mo=True)   
        mc.parentConstraint(drivers[1], driven, mo=True)  
        
        invNode = mc.createNode('reverse', n='{}_{}'.format(attrName, 'invert'))
        mc.connectAttr('{}.{}'.format(ctrl, attrName), '{}.{}{}'.format(constrNode[0], drivers[0], 'W0'))
        mc.connectAttr('{}.{}'.format(ctrl, attrName), '{}.{}{}'.format(invNode, 'i', 'x'))
        mc.connectAttr('{}.{}{}'.format(invNode, 'o', 'x'), '{}.{}{}'.format(constrNode[0], drivers[1], 'W1'))

    
    def ikConstrSwitch(self, selection=None, objType='hand'):
        '''
        Create a switch of constraint (pelvis, shoulder, world )for ik hands or foots.
        First select 2 objects to constraint the ik ctrl to.
        Then the node that will be constraint. 
        Last, the ctrl on which you want the attribute to appear.
        '''
        
        #define if hand or foot.
        if objType == 'hand':
            constrAttr = 'pelvis:chest:world'
        if objType == 'foot':
            constrAttr = 'pelvis:chest:world'

        #define selections. 
        if selection is None:
            selection = mc.ls(sl=True)
        else:
            pass    
        targNode = selection[-2]
        ctrl = selection[-1]
        sourceNode = selection[:-2]
        constrNode = targNode+'_parentConstraint1'

        longName = 'localworldspace'
        niceName = 'local world space'

        #add attr.
        mc.addAttr(ctrl, ln=longName, nn=niceName, at='enum', en=constrAttr, k=True)
        
        #add constr.
        constrList = []
        for i in sourceNode:
            constr = mc.parentConstraint(i, targNode, mo=True)
            constrList.append(constr)

        #Create and set conditions nodes.
        x = mc.shadingNode('condition', n='{}_{}'.format(objType, 'condition1'), asUtility=True)
        mc.setAttr('{}.{}'.format(x, 'secondTerm'), 0)
        mc.setAttr('{}.{}'.format(x, 'colorIfTrueR'), 1)
        mc.setAttr('{}.{}'.format(x, 'colorIfFalseR'), 0)
        mc.setAttr('{}.{}'.format(x, 'colorIfTrueG'), 0)
        mc.setAttr('{}.{}'.format(x, 'colorIfFalseG'), 1)
        
        y = mc.shadingNode('condition', n='{}_{}'.format(objType, 'condition2'), asUtility=True)
        mc.setAttr('{}.{}'.format(y, 'secondTerm'), 1)
        mc.setAttr('{}.{}'.format(y, 'colorIfTrueR'), 1)
        mc.setAttr('{}.{}'.format(y, 'colorIfFalseR'), 0)
        
        mc.connectAttr('{}.{}'.format(ctrl, longName), '{}.{}'.format(x, 'firstTerm'))
        mc.connectAttr('{}.{}'.format(ctrl, longName), '{}.{}'.format(y, 'firstTerm') )

        mc.connectAttr('{}.{}'.format(x, 'outColorR'), '{}.{}{}'.format(constrNode, selection[0], 'W0'))
        mc.connectAttr('{}.{}'.format(y, 'outColorR'), '{}.{}{}'.format(constrNode, selection[1], 'W1'))

        mc.setAttr('{}.{}'.format(ctrl, longName), 2)


    def fkConstrSwitch(self, selection=None, objType='head'):
        '''
        Create a switch of constraint (pointConstr, parentConstr)for fk arm or neck.
        First select the object to constraint the fk ctrl to.
        Then the node that will be constraint.
        Last, the ctrl on which you want the attribute to appear.
        '''
        #define selections.
        if selection is None:
            selection = mc.ls(sl=True)
        else:
            pass

        sourceNode = selection[0]
        ctrl = selection[-1]
        targNode = selection[-2]
        parentNode = targNode + '_parentConstraint1'
        orientNode = targNode + '_orientConstraint1'

        #define if hand or foot.
        if objType == 'arm':
            constrAttr = 'world:shoulder'
        if objType == 'leg':
            constrAttr = 'world:pelvis'
        if objType == 'head':
            constrAttr = 'world:neck'
        if objType == 'eye':
            constrAttr = 'world:head'

        longName = 'localworldspace'
        niceName = 'local world space'

        # add attr.
        mc.addAttr(ctrl, ln=longName, nn=niceName, at='enum', en=constrAttr, k=True)

        #add constr.
        constrList = []
        constrTrans = mc.parentConstraint(sourceNode, targNode, sr=['x', 'y', 'z'], mo=True)
        constrOrient = mc.orientConstraint(sourceNode, targNode, mo=True)
        constrList.append(constrTrans)
        constrList.append(constrOrient)

        # Create and set conditions nodes.
        if objType == 'eye':
            mc.connectAttr('{}.{}'.format(ctrl, longName), '{}.{}{}'.format(parentNode, selection[0], 'W0'))
        mc.connectAttr('{}.{}'.format(ctrl, longName), '{}.{}{}'.format(orientNode, selection[0], 'W0'))

    def constrSwitch_poleVector(self, ctrl, poleVector, type='hand'):
        return
        
        
    #-----------------------
    # Create a switch ik fk.
    def switch_Ik_Fk(self, ctrl, attrName, FK_WO, IK_WO, constrNodes):
        attExist = mc.attributeQuery(attrName, node=ctrl, exists=True)
        if attExist is True:
            pass
        else:
            mc.addAttr(ctrl, ln=attrName, at="float", min=0, max=1, k=True, h=False, r=True, w=True)

        DIFname = '{}_{}'.format(attrName, 'DIF')
        DIFnode = mc.createNode('reverse', n=DIFname)
        
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
            attrCtrl = '{}.{}'.format(ctrl, attrName)
            
            #Connect fk.
            mc.connectAttr(attrCtrl, attrFK)
            
            #Connect Ik via Reverse. 0=Ik, 1=Fk.
            mc.connectAttr(attrCtrl, '{}.{}{}'.format(DIFnode, 'i', a))
            mc.connectAttr('{}.{}{}'.format(DIFnode, 'o', a), attrIK)
                
        return DIFnode
    
                    
    #----------------------------------------------
    # Create a symetry of the selected joint chain.
    def mirror_Jnt(self, jntList=None, mirrorBehev=True):
        # Get Current selection
        if jntList == None :
            selection = mc.ls(sl=True)
        if isinstance(jntList, list) is True :
            selection = jntList
        else:
            selection = [jntList]
              
        newTopNode = mc.mirrorJoint(selection[0], myz=True, mb=mirrorBehev, sr=('L_', 'R_'))
        
        children = mc.listRelatives(newTopNode, c=True)
        
        mc.select(newTopNode)
        mc.select(children, add=True)
        sel = mc.ls(sl=True)
        
        return sel #Return hierarchy.
    
                
    #-----------------------------
    #-Return topNode of hierarchy.        
    def getTopNode(self, selection):
        x = type(selection)
        if 'list' in str(x):
            selection = selection[0]  # ignore children.

        allParent = mc.listRelatives(selection, ap=True) #List all parents.

        if allParent is None :
            topNode = selection
        else :
            topNode = allParent[0]   
        return topNode


    #-----------------------------
    #-Return topNode of hierarchy.        
    def getLastNode(self, selection):
        x = type(selection)
        if 'list' in str(x):
            selection = selection[0]  # ignore children.
        
        allChildren = mc.listRelatives(selection, ad=True, typ='transform') #List all childen.
        if allChildren is None :
            lastNode = selection
        else :
            lastNode = allChildren[0]
        return lastNode
    
    
    #----------------------------------------------
    def duplicateJointChain(self, objName, idName):
        '''
        objName = baseName
        idName = newName
        '''
        sel = objName
        
        duplicata = mc.duplicate(sel, rc = True)
        newJntList = []

        for i in range(0, len(duplicata)) :
            
            splitName = duplicata[i].split('_')

            renamedObj = mc.rename(duplicata[i], '{}_{}_{}_{}'.format(splitName[0], 
                                                                      splitName[1], 
                                                                      idName, 
                                                                      'jnt'
                                                                      )
                                   )
            newJntList.append(renamedObj)    
                         
        return newJntList 
    
    
    #---------------------------------
    def freezeTransf_deleteHist(self, object):
        #mc.FreezeTransformations()
        mc.makeIdentity(object, apply=True, t=1, r=1, s=1, n=0, pn=1)
        mc.DeleteHistory()                 


    def getGuideRadius(self, guideList):
        newList = []
        valueList = []
        for i in guideList:
            if 'control' not in i:
                name = '{}_{}'.format(i, 'control')
                newList.append(name)
            else:
                newList.append(i)    
        for i in newList:
            x = mc.getAttr('{}.{}'.format(i, 'scaleY'))
            y = mc.getAttr('root_ctrl.scaleY')
            v = x*y
            valueList.append(v)
        return valueList
    
    
    def addControlColors(self, leftSidePrefix='L_', rightSidePrefix='R_', controlSuffix='_ctrl'):
        """
        add colors to control shapes based on side
        """

        allControls = mc.ls('*' + controlSuffix)

        for c in allControls:

            l_clrIndex = 6 # - Blue
            r_clrIndex = 13 # - Red
            c_clrIndex = 22 # - Yellow
            fk_clrIndex = 14 # - Green
            
            shapes = mc.listRelatives(c, s=1)

            if c.startswith(leftSidePrefix):
                clrIndex = l_clrIndex

            elif c.startswith(rightSidePrefix):
                clrIndex = r_clrIndex
                
            elif 'fk' in c:
                clrIndex = fk_clrIndex
            
            else:
                clrIndex = c_clrIndex

            for s in shapes:
                mc.setAttr(s + '.ove', 1)
                mc.setAttr(s + '.ovc', clrIndex)


    def connectModelAndSkeleton(self, selection=None):
        if selection is None :
            sel = mc.ls(sl=True)
        else :
            sel = selection     

        controlObj = sel[0]
        modelGrp = sel[1]
        skeletonGrp = sel[2]

        ats = ['geometryVis', 'geometryDispType', 'jointVis', 'jointDispType']

        try:

            mc.addAttr(controlObj, ln=ats[0], at='enum', enumName='off:on', k=1, dv=1)
            mc.addAttr(controlObj, ln=ats[1], at='enum', enumName='normal:template:reference', k=1, dv=2)
            mc.addAttr(controlObj, ln=ats[2], at='enum', enumName='off:on', k=1)
            mc.addAttr(controlObj, ln=ats[3], at='enum', enumName='Normal:Template:Reference', k=1, dv=2)

        except:
            pass

        for a in ats:
            mc.setAttr(controlObj + '.' + a, cb=1)

        # make groups

        [mc.group(n=g, em=1) for g in [modelGrp, skeletonGrp] if not mc.objExists(g)]

        # enable overrides

        mc.setAttr(modelGrp + '.ove', 1)
        mc.setAttr(skeletonGrp + '.ove', 1)

        # connect attributes

        mc.connectAttr(controlObj + '.' + ats[0], modelGrp + '.v')
        mc.connectAttr(controlObj + '.' + ats[1], modelGrp + '.ovdt')
        mc.connectAttr(controlObj + '.' + ats[2], skeletonGrp + '.v')
        mc.connectAttr(controlObj + '.' + ats[3], skeletonGrp + '.ovdt')
        
    def annote_arrow(self, source, target):
        ''' Create an annotation in an arrow shape, between two object. '''
        posSource = mc.xform(source, t=True, q=True, ws=True)
        print target
        note = mc.annotate(target, tx='', p=posSource)
        mc.parent(note, source, a=True)
        
        mc.setAttr('%s.overrideEnabled' % note, 1)
        mc.setAttr('%s.overrideDisplayType'  % note,  2)
        return