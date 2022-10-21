'''
Created on Jul 2, 2018

@author: Thomas
'''

import maya.cmds as mc
import maya.mel as mm
from math import pow,sqrt
from thomas_script.maya.utils import shapes, transform

objList = mc.ls(sl=True)
BS = []
baseName = 'R_upperCheek_'

BASEGROUPLIST = ['ribbon_GRP', 
             'ribbon_control_grp', 
             'ribbon_noTransform_grp', 
             'ribbon_joints_grp']
NEWGROUPLIST = []


class Ribbon(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def ribbon(self, baseName=baseName, spanCount=7, ctrlCount=3, nurbSpanMult=1, skin=0, wire=1, twist=1, sine=1, bend=1, ikFk=1):
        if len(objList) < 2 or objList == None:
            print 'Select two objects as sources.'
            pass
        else:
            self.mainGroups()
 
            nurbSurf, posList = self.createNurbSurf(spanCount)
            listWeight = self.getWeights(spanCount)
            follicleList = self.createFollicles(nurbSurf, listWeight, spanCount) 
          
            wirePosList, ctrlGrpList = self.createMainCtrl(baseName, ctrlCount, posList, 2, ikFk, twist, sine, bend)
            constrList = self.createCtrlJoints(baseName, 2, ctrlGrpList, follicleList, ikFk)
            
            skinCluster = []
            if skin == 1:
                skinCluster = self.skinDeformer(baseName, nurbSurf, ctrlGrpList)
            if wire == 1:
                clusters = self.wireDeformer(baseName, nurbSurf, wirePosList)
                #PointConstr clusters to ctrlLoc.
                for i in range(0, len(ctrlGrpList)):
                    ctrl = mc.listRelatives(ctrlGrpList[i], ad=True, typ='transform')[1]
                    #mc.pointConstraint(ctrl, clusters[i], mo=True)
                    mc.connectAttr('{}.{}'.format(ctrl, 't'), '{}.{}'.format(clusters[i], 't')) 
            if twist == 1 :
                twistGrp = self.twistDeformer(baseName, nurbSurf, ctrlGrpList)
            if sine == 1 :
                sineGrp = self.sineDeformer(baseName, nurbSurf, ctrlGrpList)
            if bend == 1 :
                bendGrp = self.bendDeformer(baseName, nurbSurf, ctrlGrpList)
               
            self.createBlendShape(nurbSurf, skinCluster)      
            self.cleaning()
            self.snapToTarget()
        
    def getDistance(self, objA,objB):
        posA = mc.xform(objA, q=True, t=True, ws=True)
        posB = mc.xform(objB, q=True, t=True, ws=True)
        
        return sqrt(pow(posA[0]-posB[0], 2)+pow(posA[1]-posB[1], 2)+pow(posA[2]-posB[2], 2))
    
    def getWeights(self, spanCount):
        
        offsetConstr = 1.0 / (spanCount-1) #-Value spacing each weights.
        
        listWeight = [0] #-Store all weights.
        for i in range(0, spanCount) :
            print i
            value = offsetConstr * (i+1) #-Increment value.
            listWeight.append(value) #-Store weights.  
            
        return listWeight
        
    def mainGroups(self):
        for i in BASEGROUPLIST:
            i = baseName+i
            NEWGROUPLIST.append(i)

        [mc.group(n=grp, empty=True, w=True) for grp in NEWGROUPLIST]
        mc.setAttr('{}.{}'.format(NEWGROUPLIST[0], 'rotateOrder'), 2)
        [mc.parent(i, NEWGROUPLIST[0], a=True) for i in NEWGROUPLIST[1:]]
    
    def createNurbSurf(self, spanCount):
        
        lengh = self.getDistance(objList[0], objList[1])
        posStart = lengh/2
        posEnd = posStart*-1
        
        offset = lengh/(spanCount)
        
        valueList = []
        increment = posEnd
        for span in range(0, spanCount):
            increment = increment + offset
            valueList.append(increment)
        valueList.insert(0, posEnd)
        valueList.reverse()
        
        position_list = []
        for elem in valueList:
            position = [0, 0, elem]
            position_list.append(position)

        curve01 = mc.curve(n='curve01', d=1, p=position_list)
        mc.move(0.5,0,0)
        curve02 = mc.curve(n='curve02', d=1, p=position_list)
        mc.move(-0.5,0,0)            
        
#         mc.delete('{}.{}'.format(curve01, 'cv[10]'))
#         mc.delete('{}.{}'.format(curve01, 'cv[10]'))
        mc.rebuildCurve(curve01, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=spanCount-1, d=3, tol=0.01)
        mc.rebuildCurve(curve02, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=spanCount-1, d=3, tol=0.01)
        
        nurbSurf = mc.loft([curve01, curve02], n=baseName+'ribbon_nurbS',ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=True)
        mc.delete(nurbSurf, ch=True)
        mc.delete(curve01)
        mc.delete(curve02)
        
        mc.parent(nurbSurf[0], NEWGROUPLIST[0], a=True)
        
        return nurbSurf[0], position_list
            
    def createFollicles(self, nurbSurf, listWeight, spanCount):
        dif = listWeight[1]/2
        follicleList = []
        for i in range(0,spanCount) :
            folicle = mc.createNode("follicle")
            folicleTrans=mc.listRelatives(folicle,type='transform',p=True)
            mc.connectAttr('{}.{}'.format(folicle, "outRotate"), 
                           '{}.{}'.format(folicleTrans[0], "rotate"))
            mc.connectAttr('{}.{}'.format(folicle, "outTranslate"), 
                           '{}.{}'.format(folicleTrans[0], "translate"))
            mc.connectAttr('{}.{}'.format(nurbSurf, 'worldMatrix'), 
                           '{}.{}'.format(folicle, 'inputWorldMatrix'))
            mc.connectAttr('{}.{}'.format(nurbSurf, 'local'), 
                           '{}.{}'.format(folicle,'inputSurface'))
            mc.setAttr('{}.{}'.format(folicle, "simulationMethod"), 0)
             
            mc.setAttr('{}.{}'.format(folicle, 'parameterU'), listWeight[i])
            mc.setAttr('{}.{}'.format(folicle, 'parameterV'), 0.5)
            follicleList.append(folicleTrans)
         
        grp = mc.group(n=baseName+'ribbon_follicle_grp', empty=True, w=True) 
        [mc.parent(follicle, grp, a=True) for follicle in follicleList]
         
        mc.parent(grp, NEWGROUPLIST[2], a=True)
        
        return follicleList
    
    def createMainCtrl2(self, baseName, ctrlCount, posList, orientId, ikFk, twist, sine, bend):
#         if wire == 1 :
#             ctrlCount = 3
#             orientation = orientation[0]
#             ctrlAttr = ctrlList[1]
        
        orientation = [(0,0,0), (-90,0,0), (0,90,90)]
        name = baseName+'ribbon_ctrl'

        grpList = []
        ctrlList = []
        
        length = self.getDistance(objList[0], objList[1])
        offset = length / (ctrlCount-1)
        increment = offset
        
        for count in range(0, ctrlCount):
            mc.select(clear=True)
            grp = mc.group(n=name+str(count)+'_grp', empty=True, w=True)
            ctrl = shapes.shpDico[str(2)](name=name+str(count))
            mc.parent(ctrl, grp, a=True)
            jnt = mc.joint(n=name+str(count)+'_jnt', r=1)
            #mc.parent(jnt, ctrl, r=True)
            
            grpList.append(grp)
            ctrlList.append(ctrl)
            
            if count == 0 :
                mc.xform(grp, t=posList[0], ro=orientation[orientId])
                if twist == 1:
                    mc.addAttr(ctrl, ln='twistSep', nn='--------', at='enum', en='Twist', k=True)
                    mc.addAttr(ctrl, ln='twist', nn='Twist', at='float', k=True) 
            elif count == ctrlCount-1 :
                mc.xform(grp, t=posList[-1], ro=orientation[orientId])
                if twist == 1:
                    mc.addAttr(ctrl, ln='twistSep', nn='--------', at='enum', en='Twist', k=True)
                    mc.addAttr(ctrl, ln='twist', nn='Twist', at='float', k=True) 
            else:
                origin = posList[0]
                newpos = [origin[0], origin[1], origin[2]-increment]
                mc.xform(grp, t=newpos, ro=orientation[orientId])
                increment = increment+offset
            
        if bend == 1:
            name = baseName + BASEGROUPLIST[0]
            mc.addAttr(name, ln='rollSep', nn='--------', at='enum', en='Roll', k=True)
            mc.addAttr(name, ln='roll', nn='Roll', at='float', k=True)
            mc.addAttr(name, ln='rollOf', nn='Roll Offset', at='float', k=True)
            mc.addAttr(name, ln='rollScale', nn='Roll Scale', at='float', k=True, dv=1)
            mc.addAttr(name, ln='rollTwist', nn='Roll Twist', at='float', k=True)
        if sine == 1:
            name = baseName + BASEGROUPLIST[0]
            mc.addAttr(name, ln='sineSep', nn='--------', at='enum', en='Sine', k=True)
            mc.addAttr(name, ln='sine', nn='Sine', at='float', k=True)
            mc.addAttr(name, ln='sineOf', nn='Sine Offset', at='float', k=True)
            mc.addAttr(name, ln='sineTwist', nn='Sine Twist', at='float', k=True)
            mc.addAttr(name, ln='sineLength', nn='Sine Length', at='float', k=True, dv=2)
        if ikFk == 1:
            name = baseName + BASEGROUPLIST[0]
            mc.addAttr(name, ln='fkSwitchSep', nn='--------', at='enum', en='Fk Switch', k=True)
            mc.addAttr(name, ln='fkSwitch', nn='fk Switch', at='float', k=True, min=0, max=1)
            
        [mc.parent(ctrl, NEWGROUPLIST[1], a=True) for ctrl in grpList]    

        wirePosList = [posList[0], (0,0,0), posList[-1]]
        
        return wirePosList, grpList       
            
    def createMainCtrl(self, baseName, ctrlCount, posList, orientId, ikFk, twist, sine, bend):
        '''
        orient : 0 = world space, 1 = Y along plane, 2 = X along plane.
        '''

        orientation = [(0,0,0), (-90,0,0), (0,90,90)]
        name = baseName+'ribbon_ctrl'
        print posList
        
        newPosList = [posList[0], (0,0,0), posList[-1]]
        grpList = []
        ctrlList = []
        
        for i in range(0, len(newPosList)):
            mc.select(clear=True)
            grp = mc.group(n=name+str(i)+'_grp', empty=True, w=True)
            mc.xform(grp, t=newPosList[i], ro=orientation[0]) 
            
            ctrl = shapes.shpDico[str(2)](name=name+str(i))
            mc.parent(ctrl, grp, r=True)
            jnt = mc.joint(n=name+str(i)+'_jnt', r=1)
            #mc.parent(jnt, ctrl, r=True)
            
            grpList.append(grp)
            ctrlList.append(ctrl)
    
            if i == 1:
                if bend == 1:
                    mc.addAttr(ctrl, ln='rollSep', nn='--------', at='enum', en='Roll', k=True)
                    mc.addAttr(ctrl, ln='roll', nn='Roll', at='float', k=True)
                    mc.addAttr(ctrl, ln='rollOf', nn='Roll Offset', at='float', k=True)
                    mc.addAttr(ctrl, ln='rollScale', nn='Roll Scale', at='float', k=True, dv=1)
                    mc.addAttr(ctrl, ln='rollTwist', nn='Roll Twist', at='float', k=True)
                if sine == 1:
                    mc.addAttr(ctrl, ln='sineSep', nn='--------', at='enum', en='Sine', k=True)
                    mc.addAttr(ctrl, ln='sine', nn='Sine', at='float', k=True)
                    mc.addAttr(ctrl, ln='sineOf', nn='Sine Offset', at='float', k=True)
                    mc.addAttr(ctrl, ln='sineTwist', nn='Sine Twist', at='float', k=True)
                    mc.addAttr(ctrl, ln='sineLength', nn='Sine Length', at='float', k=True, dv=2)
                if ikFk == 1:
                    mc.addAttr(ctrl, ln='fkSwitchSep', nn='--------', at='enum', en='Fk Switch', k=True)
                    mc.addAttr(ctrl, ln='fkSwitch', nn='fk Switch', at='float', k=True, min=0, max=1)
            else :
                if twist == 1:
                    mc.addAttr(ctrl, ln='twistSep', nn='--------', at='enum', en='Twist', k=True)
                    mc.addAttr(ctrl, ln='twist', nn='Twist', at='float', k=True)        
                
        mc.pointConstraint(ctrlList[0], grpList[1], mo=True)
        mc.pointConstraint(ctrlList[2], grpList[1], mo=True)
        
        [mc.parent(ctrl, NEWGROUPLIST[1], a=True) for ctrl in grpList]
        
        return newPosList, grpList
    
    def createCtrlJoints(self, baseName, orientId, ctrlGrpList, follicleList, ikFk):
        orientation = [(0,0,0), (-90,0,0), (0,90,90)]
        
        ctrlList = []
        jntList = []
        constrList = []
        name=baseName+'ribbon_ctrlJnt'
        midCtrl = mc.listRelatives(ctrlGrpList[1], c=True)
        mainCtrl = baseName + BASEGROUPLIST[0]
        
        if ikFk == 1 :
            MD = mc.createNode('reverse', n=baseName+'fkSwith_rev')
            #mc.setAttr('{}.{}'.format(MD, 'input2X'), -1)
            mc.connectAttr('{}.{}'.format(midCtrl[0], 'fkSwitch'), '{}.{}'.format(MD, 'inputX'))
        
        for i in range(0, len(follicleList)):
            grp = mc.group(n=name+'_orig'+str(i), empty=True, w=True)
            ctrl = shapes.shpDico[str(1)](name=name+str(i))
            jnt = mc.joint(n=name+'_jnt'+str(i), r=1)
            
            mc.parent(ctrl, grp, a=True)
            
            transform.snap(grp, follicleList[i])
            mc.xform(grp, ro=orientation[orientId])
            constrNode = mc.parentConstraint(follicleList[i], grp, mo=True)
    
            mc.parent(grp, NEWGROUPLIST[-1], a=True)
            fol = follicleList[i]
            if len(ctrlList) > 0 and ikFk == 1:
                mc.parentConstraint(ctrlList[-1], grp, mo=True)
                mc.connectAttr('{}.{}'.format(MD, 'outputX'), '{}.{}{}'.format(constrNode[0], fol[0], 'W0'))
                               
                mc.connectAttr('{}.{}'.format(midCtrl[0], 'fkSwitch'), '{}.{}{}'.format(constrNode[0], ctrlList[-1], 'W1'))
    
            ctrlList.append(ctrl)
            jntList.append(jnt)

        return constrList  
    
    def skinDeformer(self, baseName, nurbSurf, ctrlList):
        jntList = []
        for item in ctrlList:
            ctrl = mc.listRelatives(item, c=True)
            jnt = mc.listRelatives(ctrl, c=True)
            jntList.append(jnt[-1])
            
        #mc.refresh()
        skinCluster = mc.skinCluster(nurbSurf, jntList, tsb=True, sm=2, bm=0, nw=1, mi=4, omi=True, dr=4, rui=True)
        
        mc.setAttr('{}.{}'.format(nurbSurf, 'inheritsTransform'), 0)
        
        return skinCluster
        
        
    def wireDeformer(self, baseName, nurbSurf, newPosList):
        wireCurve = mc.curve(n=baseName+'wire_curve', d=2, p=newPosList)
        wireNurb = mc.duplicate(nurbSurf, n=baseName+'ribbon_wire_NurbS')
        BS.append(wireNurb)
        mc.wire(wireNurb, w=wireCurve)
        mc.setAttr("wire1.dropoffDistance[0]", 20)
        
        #Create cluster on cv and place pivot.
        clust01 = mc.cluster('{}.{}'.format(wireCurve, 'cv[0]'))
        mc.xform('{}.{}'.format(clust01[1], 'scalePivot'), t=newPosList[0], a=True)
        mc.xform('{}.{}'.format(clust01[1], 'rotatePivot'), t=newPosList[0], a=True) 
        
        clust03 = mc.cluster('{}.{}'.format(wireCurve, 'cv[2]')) 
        mc.xform('{}.{}'.format(clust03[1], 'scalePivot'), t=newPosList[0], a=True)
        mc.xform('{}.{}'.format(clust03[1], 'rotatePivot'), t=newPosList[-1], a=True) 
        
        clust02 = mc.cluster('{}.{}'.format(wireCurve, 'cv[1]'))
        mc.setAttr('{}.{}'.format(clust02[0], 'envelope'), 2)
        
        wireList = []
        wireList.append(wireCurve)
        wireList.append(wireNurb)
        wireList.append(wireCurve+'BaseWire')
        wireList.append(clust01)
        wireList.append(clust02)
        wireList.append(clust03)
        
        #-Adjust weight of end cluster for middle cv.
        mc.percent(clust01[0], '{}.{}'.format(wireCurve,'cv[1]'), v=0.5)
        mc.percent(clust03[0], '{}.{}'.format(wireCurve,'cv[1]'), v=0.5)
        
        grp = mc.group(n=baseName+'ribbon_wireDeformer_grp', empty=True, w=True)
        [mc.parent(elem, grp, a=True) for elem in wireList]
        
        mc.parent(grp, NEWGROUPLIST[2], a=True)
        
        return [clust01[-1], clust02[-1], clust03[-1]]
        
    
    def twistDeformer(self, baseName, nurbSurf, ctrlGrpList):
        twistNurb = mc.duplicate(nurbSurf, n=baseName+'ribbon_twist_NurbS')
        twistDeform = mc.nonLinear(twistNurb, typ='twist')
        BS.append(twistNurb)
        mc.rotate(-90, 0, 0)
        
        grp = mc.group(n=baseName+'ribbon_twistDeformer_grp', empty=True, w=True)
        mc.parent(twistNurb, twistDeform, grp, a=True)
        
        for i in range(0, len(ctrlGrpList)):
            ctrl = mc.listRelatives(ctrlGrpList[i], c=True)
            if i == 0:
                mc.connectAttr('{}.{}'.format(ctrl[0], 'twist'), '{}.{}'.format(twistDeform[0], 'startAngle'))  
            if i > 0 and i < len(ctrlGrpList)-1:
                pass                   
            if i == len(ctrlGrpList)-1:
                mc.connectAttr('{}.{}'.format(ctrl[0], 'twist'), '{}.{}'.format(twistDeform[0], 'endAngle'))
            
        mc.parent(grp, NEWGROUPLIST[2], a=True)
    
    
    def sineDeformer(self, baseName, nurbSurf, ctrlGrpList):
        ctrl0 = mc.listRelatives(ctrlGrpList[0], c=True)
        pos=mc.xform(ctrl0, t=True, ws=True, q=True)
    
        sineNurb = mc.duplicate(nurbSurf, n=baseName+'ribbon_sine_NurbS')
        sineDeform = mc.nonLinear(sineNurb, typ='sine')
        BS.append(sineNurb)
        mc.rotate(90, 0, 90)
        mc.move(pos[0], pos[1], pos[2])
    
        grp = mc.group(n=baseName+'ribbon_sineDeformer_grp', empty=True, w=True)
        mc.parent(sineNurb, sineDeform, grp, a=True)
        
        ctrl = mc.listRelatives(ctrlGrpList[1], c=True)
        mc.connectAttr('{}.{}'.format(ctrl[0], 'sine'), '{}.{}'.format(sineDeform[0], 'amplitude'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'sineOf'), '{}.{}'.format(sineDeform[0], 'offset'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'sineTwist'), '{}.{}'.format(sineDeform[1], 'rotateZ'))
        mc.setAttr('{}.{}'.format(sineDeform[0], 'dropoff'), -1)
        mc.setAttr('{}.{}'.format(sineDeform[0], 'lowBound'), -10)
        mc.setAttr('{}.{}'.format(sineDeform[0], 'highBound'), 0)
        mc.connectAttr('{}.{}'.format(ctrl[0], 'sineLength'), '{}.{}'.format(sineDeform[0], 'wavelength'))
        
        mc.parent(grp, NEWGROUPLIST[2], a=True)
    
    def bendDeformer(self, baseName, nurbSurf, ctrlGrpList):
        bendNurb = mc.duplicate(nurbSurf, n=baseName+'ribbon_bend_NurbS')
        bendDeform = mc.nonLinear(bendNurb, typ='bend')
        BS.append(bendNurb)
        mc.rotate(-90, 0, 0)
        
        grp = mc.group(n=baseName+'ribbon_bendDeformer_grp', empty=True, w=True)
        mc.parent(bendNurb, bendDeform, grp, a=True)
    
        ctrl = mc.listRelatives(ctrlGrpList[1], c=True)
        mc.connectAttr('{}.{}'.format(ctrl[0], 'roll'), '{}.{}'.format(bendDeform[0], 'curvature'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'rollOf'), '{}.{}'.format(bendDeform[1], 'translateZ'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'rollScale'), '{}.{}'.format(bendDeform[1], 'scaleX'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'rollScale'), '{}.{}'.format(bendDeform[1], 'scaleY'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'rollScale'), '{}.{}'.format(bendDeform[1], 'scaleZ'))
        mc.connectAttr('{}.{}'.format(ctrl[0], 'rollTwist'), '{}.{}'.format(bendDeform[1], 'rotateZ'))
        mc.setAttr('{}.{}'.format(bendDeform[0], 'lowBound'), 0)
        mc.setAttr('{}.{}'.format(bendDeform[0], 'highBound'), 100)
                
        mc.parent(grp, NEWGROUPLIST[2], a=True)
    
    def createBlendShape(self, nurbSurf, skinCluster):
        mc.select(clear=True)
        for i in BS:
            mc.select(i, add=True)
        mc.select(nurbSurf, add=True)    
        bs = mc.blendShape(n='BS', w=[(0, 1), (1, 1), (2, 1), (3, 1)])    
        
        if len(skinCluster) > 0 :
            skinNode = skinCluster[0].encode('ascii','ignore')
            BsNode = bs[0].encode('ascii','ignore')
            
            mc.reorderDeformers(skinNode, BsNode, nurbSurf)
        
    def cleaning(self):
        mc.setAttr('{}.{}'.format(NEWGROUPLIST[2], 'inheritsTransform'), 0)
        mc.setAttr('{}.{}'.format(NEWGROUPLIST[2], 'visibility'), 0)
        
        
    def snapToTarget(self):
        lengh = self.getDistance(objList[0], objList[1])
        mainGrp = NEWGROUPLIST[0]
        
        for i in range(0, len(objList)) :
            constr = mc.pointConstraint(objList[i], mainGrp, mo=False)
        mc.delete(constr) 
        
        constr = mc.aimConstraint(objList[0], mainGrp, aim=(0,0,1), u=(0,1,0))
        mc.delete(constr)