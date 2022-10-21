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

####### JOINTS #######
    
    def create_oriented_jointChain(self, selection, baseName, tag, invertUp=True, invertAim=False, rotateUp=False):
        
        mc.select(clear=True)
        [mc.select(jnt, add=True) for jnt in selection]
        
        jointChain = self.create_chain_onSelected(baseName, tag)
        
        if len(selection) > 3:
            self.orient_chain2(jointChain, invertUp, invertAim, rotateUp)
        else:
            self.orient_chain(jointChain, invertUp, invertAim)            
        return jointChain
    
    #--------------------------------------------
    # Create chain of joints on selected objects.
    def create_chain_onSelected(self, baseName=None, tag='skin', radius=1) :      
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
                jnt_name = '{}_{}_{}_{}'.format(curName, str(i), tag, 'jnt')
                if mc.objExists(jnt_name):
                    jnt_name = '{}_{}_{}_{}'.format(curName, str(i), tag, 'jnt01')
            else:
                jnt_name = '{}_{}_{}_{}'.format(baseName, str(i), tag, 'jnt')
                if mc.objExists(jnt_name) :
                    jnt_name = '{}_{}_{}_{}'.format(baseName, str(i), tag, 'jnt01')
                
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

    #--------------------
    # Orient Joint Chain.
    
    def orient_chain2(self, list_joints, invertUp=False, invertAim=False, rotateUp=False):
        aimAxis = [1,0,0]
        upAxis = [0,1,0]
        upDir = [0,0,1]
        
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
            if len(list_joints) > 2:
                if parentJoint != '':
                    upVect = self.getCrossDir(parentJoint,
                                              currentJoint,
                                              childJoint)
                else:
                    upVect = self.getCrossDir(currentJoint,
                                              childJoint,
                                              list_joints[i+2])
            # end auto Guess direction
            if invertUp is True:
                #aimAxis = (aimAxis[0]*-1, aimAxis[1]*-1, aimAxis[2]*-1)
                upVect = (upVect[0]*-1, upVect[1]*-1, upVect[2]*-1)
            
            if rotateUp is True:
                upVect = (-upVect[2], upVect[1], upVect[0])
                
            if invertAim is True:
                aimAxis = (aimAxis[0]*-1, aimAxis[1]*-1, aimAxis[2]*-1) 
                  
            # Aim constraint
            mc.aimConstraint(childJoint, 
                             currentJoint, 
                             aim=(aimAxis[0], aimAxis[1], aimAxis[2]), 
                             upVector=(upAxis[0], upAxis[1], upAxis[2]),
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
                         rotateAxis=(aimAxis[0]*180, aimAxis[1]*180, aimAxis[2]*180))
                prevUp = om.MVector(prevUp) * -1.0
                
            mc.joint(currentJoint, e=True, zso=True)
            mc.makeIdentity(currentJoint, apply=True)# reset all.
            
            # re Parent objects
            mc.parent(childJoint, currentJoint)            
            
    def orient_chain(self, list_joints, invertUp=False, invertAim=False):
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
            wUpVect = (0, 1, 0)
            if len(list_joints) > 2:
                if parentJoint != '':
                    wUpVect = self.getCrossDir(parentJoint,
                                              currentJoint,
                                              childJoint)
                else:
                    wUpVect = self.getCrossDir(currentJoint,
                                              childJoint,
                                              list_joints[i+2])
            # end auto Guess direction
            if invertUp is True:
                wUpVect = (wUpVect[0]*-1, wUpVect[1]*-1, wUpVect[2]*-1)
            aimDir = 1.0
            if invertAim is True:
                aimDir = -1.0    
            # Aim constraint
            mc.aimConstraint(childJoint, 
                             currentJoint, 
                             aim=(aimDir, 0.0, 0.0), 
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
    
    
    def getPoleVectorPosition(self, joints, distance=1):
        if len(joints) != 3:
            raise 'Select a joint chain of 3 joints'
            return
        start = mc.xform(joints[0], q=True, ws=True, t=True)
        mid = mc.xform(joints[1], q=True, ws=True, t=True)
        end = mc.xform(joints[2], q=True, ws=True, t=True)
        
        startV = om.MVector(start[0], start[1], start[2])
        midV = om.MVector(mid[0], mid[1], mid[2])
        endV = om.MVector(end[0], end[1], end[2])
        
        startEndV = endV - startV
        startMidV = midV - startV
        
        dotP = startMidV * startEndV
        
        proj = float(dotP) / float(startEndV.length())
        
        startEndN = startEndV.normal()
        
        projV = startEndN * proj
        
        arrowV = startMidV - projV
        
        arrowV *= distance
        
        finalV = arrowV + midV

        return finalV

    def ikFk_switch(self, fk, ik, skin):
        count = len(skin)
        if len(skin) != count or len(skin) != count:
            raise 'fk/ik/skin have different amout of elements'
            return
        pBlendList = []
        for i in range(0, len(skin)):
            #Create nodes.
            pBlend = mc.createNode('pairBlend')
            mc.setAttr(pBlend+'.rotInterpolation', 1)
            dMat_fk = mc.createNode('decomposeMatrix')
            dMat_ik = mc.createNode('decomposeMatrix')
            
            #Connect fk.
            mc.connectAttr(fk[i]+'.worldMatrix', dMat_fk+'.inputMatrix')
            mc.connectAttr(dMat_fk+'.outputRotate', pBlend+'.inRotate1')
            mc.connectAttr(dMat_fk+'.outputTranslate', pBlend+'.inTranslate1')            
            mc.connectAttr(dMat_fk+'.outputScale', skin[i]+'.scale')
            
            #Connect ik.
            mc.connectAttr(ik[i]+'.worldMatrix', dMat_ik+'.inputMatrix')
            mc.connectAttr(dMat_ik+'.outputRotate', pBlend+'.inRotate2')
            mc.connectAttr(dMat_ik+'.outputTranslate', pBlend+'.inTranslate2')            
            #mc.connectAttr(dMat_ik+'.outputScale', skin[i]+'.scale')            
            
            #Connect pairBlend.
            mc.connectAttr(pBlend+'.outTranslate', skin[i]+'.translate') 
            mc.connectAttr(pBlend+'.outRotate', skin[i]+'.rotate') 

            pBlendList.append(pBlend)
            
        return pBlendList
    
    def getAllSkinjnts(self):
        #-get all skin joints
        skinJoints = []
        x = mc.listRelatives('skinJoints_GRP', ad=True)
        for i in x:
            skinJoints.append(str(i))
        skinJoints.reverse()
        return skinJoints
    
    def rename_searchReplace(self, name, search, replace):
        newName = ''
        splitName = name.split('_')
        
        for i in splitName :
            print search[1:]
            if search[1:] in i:
                print splitName.index(i)
                
                
        mc.rename(name, newName)
        
        return newName
        
        