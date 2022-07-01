'''
Created on Feb 21, 2018

@author: thomas
'''
from common.utils import system
import maya.api.OpenMaya as om
import maya.cmds as mc
import maya.mel as mm
import maya.api.OpenMaya as apiom
import pprint


class MayaMuscleLib(object):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        pass


    def mirrorMuscleControlPos(self, muscles=[], side='l'):

        """
        mirror middle muscle control translate values
        """

        if not muscles:
            muscles = self.getAllMusclesInScene()

        getOpposite = {'l': 'r', 'r': 'l'}

        for m in muscles:

            if not m[:2] in ['l_', 'r_']:
                continue

            opm = getOpposite[m[0]] + m[1:]

            startCtrl, midCtrl, endCtrl = self.getControlsFromMuscle(m)
            opStartCtrl, opMidCtrl, opEndCtrl = self.getControlsFromMuscle(opm)

            for ctrl, opctrl in zip([startCtrl, midCtrl, endCtrl], [opStartCtrl, opMidCtrl, opEndCtrl]):
                midCtrlTranslateVals = mc.getAttr(ctrl + '.t')[0]
                midCtrlRotateteVals = mc.getAttr(ctrl + '.r')[0]
                mc.setAttr(opctrl + '.t', -midCtrlTranslateVals[0], midCtrlTranslateVals[1], midCtrlTranslateVals[2])
                mc.setAttr(opctrl + '.r', midCtrlRotateteVals[0], -midCtrlRotateteVals[1], -midCtrlRotateteVals[2])

    def resetMuscleControlOffsets(self, muscles=[]):

        """
        Reset muscle controls offsets for start and end controls
        - that is zero values on control translate and rotate
        and match offset groups to the control transforms

        This script assumes default Maya Muscle setup on controls,
        no changes on control offset groups, otherwise script
        might not work
        """

        for m in muscles:

            ctrl1, ctrl2, ctrl3 = self.getControlsFromMuscle(m)

            for ctrl in [ctrl1, ctrl3]:
                ctrlParent = mc.listRelatives(ctrl, p=1)[0]

                # temporarily unparent control

                mc.parent(ctrl, w=1)

                #  disconnect from constraints

                pointConst = mc.listConnections(ctrlParent, type='pointConstraint', s=1, d=0)[0]
                orientConst = mc.listConnections(ctrlParent, type='orientConstraint', s=1, d=0)[0]

                pointTarget = mc.listConnections(pointConst + '.target[0].targetParentMatrix')[0]
                # orientTarget1 - same as pointTarget
                orientTarget2 = mc.listConnections(orientConst + '.target[1].targetParentMatrix')[0]
                targetsParent = mc.listRelatives(pointTarget, p=1)[0]

                # match control transform

                mc.delete(mc.parentConstraint(ctrl, targetsParent))
                mc.delete(mc.parentConstraint(ctrl, pointTarget))
                mc.delete(mc.pointConstraint(ctrl, orientTarget2))

                # parent control back

                mc.parent(ctrl, ctrlParent)

    def mirrorMuscleConstraints(self, muscles=[], side='l'):

        """
        mirror muscle constraints for selected muscle surfaces

        This is simplified, only creates one constraint for Translation
        and one for Rotation and always keeps Offset.
        Mirror will recreate disconnected constraint channels.
        """

        if not muscles:
            return

        opSideDt = {'l': 'r', 'r': 'l'}
        sideCap = side.capitalize()
        opSide = opSideDt[side]
        opSideCap = opSide.capitalize()

        for m in muscles:

            musControls = self.getControlsFromMuscle(m)

            for ctrl in musControls:

                constraints = []
                openAts = []

                for channel in ['t', 'r', 's']:

                    for axis in ['x', 'y', 'z']:

                        constRes = mc.listConnections(ctrl + '.' + channel + axis, type='constraint', s=1, d=0, p=0)

                        if constRes:

                            constraints.append(constRes[0])

                        else:

                            openAts.append(channel + axis)

                # clean duplicates
                constraints = list(set(constraints))

                mirCtrl = ctrl.replace(sideCap + '_', opSideCap + '_')

                # perform mirror control check

                if not mc.objExists(mirCtrl):
                    print '# PROBLEM - mirror control %s for %s not found, skipping this control' % (ctrl, mirCtrl)
                    continue

                # remove old constraints from mirror control

                for channel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:

                    constRes = mc.listConnections('%s.%s' % (mirCtrl, channel), type='constraint', s=1, d=0, p=0)

                    if constRes:
                        mc.delete(constRes)

                # make constraints

                for const in constraints:

                    constType = mc.nodeType(const)
                    targets = mc.listConnections(const + '.target[*].targetParentMatrix')

                    # mirror targets

                    mirTargets = []

                    for t in targets:

                        mirTarget = t

                        if t.startswith(side):

                            mirTarget = opSide + t.lstrip(side)

                        elif t.count(sideCap + '_'):

                            mirTarget = mirTarget.replace(sideCap + '_', opSideCap + '_')

                        mirTargets.append(mirTarget)

                    # make mirror constraint

                    mirTargetsStr = ' '.join(mirTargets)
                    constCommand = '%s -mo %s %s' % (constType, mirTargetsStr, mirCtrl)
                    mm.eval(constCommand)

                # open attributes

                for openAt in openAts:

                    ctrlPlug = mirCtrl + '.' + openAt
                    sourcePlug = mc.listConnections(ctrlPlug, s=1, d=0, p=1)

                    if not sourcePlug:
                        continue

                    mc.disconnectAttr(sourcePlug[0], ctrlPlug)

                # mirror transform limits

                self.mirrorMuscleControlLimits(ctrl, mirCtrl)

    def scaleMuscleControls(self, radius=1.0, muscles=[]):

        """
        scale muscle controls to given radius value
        based on distance from their pivot point
        """

        if not muscles:
            muscles = self.getAllMusclesInScene()

        for m in muscles:

            controls = self.getControlsFromMuscle(m)

            for ctrl in controls:

                centerPos = mc.xform(ctrl, q=1, t=1, ws=1)
                centerPosVt = apiom.MVector(centerPos[0], centerPos[1], centerPos[2])
                points = mc.ls(ctrl + '.cv[*]', fl=1)

                for p in points:
                    pointPos = mc.xform(p, q=1, t=1, ws=1)
                    pointPosVt = apiom.MVector(pointPos[0], pointPos[1], pointPos[2])

                    centerToPointVt = pointPosVt - centerPosVt
                    centerToPointScaledVt = centerToPointVt.normalize() * radius

                    newPointVt = centerToPointScaledVt + centerPosVt
                    mc.xform(p, t=[newPointVt[0], newPointVt[1], newPointVt[2]], ws=1)

    def mirrorMuscleControlLimits(self, refControl, oppositeControl):

        """
        mirror muscle control Transform Limits

        LIMITAIONS: this function only works with Translate channels
                    for purposes of the muscle setup
        """

        # reset limits on opposite control

        mc.transformLimits(oppositeControl, remove=1)

        # collect limits from reference control

        tx = mc.transformLimits(refControl, q=1, tx=1)
        ty = mc.transformLimits(refControl, q=1, ty=1)
        tz = mc.transformLimits(refControl, q=1, tz=1)
        etx = mc.transformLimits(refControl, q=1, etx=1)
        ety = mc.transformLimits(refControl, q=1, ety=1)
        etz = mc.transformLimits(refControl, q=1, etz=1)

        # set new limits to opposite control
        # X axis values need to be flipped - based on Maya Simple muscles setup

        mc.transformLimits(oppositeControl, tx=[-tx[1], -tx[0]], ty=ty, tz=tz,
                           etx=[etx[1], etx[0]], ety=ety, etz=etz)

    def getAllMusclesInScene(self):

        """
        return all Maya Muscle surface objects in scene
        """

        musclesRes = mc.ls('*_mus', type='transform')
        muscles = [m for m in musclesRes if mc.listRelatives(m, s=1, type='cMuscleObject')]

        return muscles

    def getControlsFromMuscle(self, muscleObject):

        """
        get controls from given muscle surface object
        """

        s = mc.listRelatives(muscleObject, s=1)[0]
        df = mc.listConnections(s, type='cMuscleSplineDeformer')[0]
        cmSpline = mc.listConnections(df, type='cMuscleSpline', sh=1)[0]

        ctrl1 = mc.listConnections(cmSpline + '.controlData[0].insertMatrix')[0]
        ctrl2 = mc.listConnections(cmSpline + '.controlData[1].insertMatrix')[0]
        ctrl3 = mc.listConnections(cmSpline + '.controlData[2].insertMatrix')[0]

        return [ctrl1, ctrl2, ctrl3]

    def getMiddleControlsFromMuscles(self, muscleObjects):

        middleControls = []

        for m in muscleObjects:
            controls = self.getControlsFromMuscle(m)
            middleControls.append(controls[1])

        return middleControls

    def setMuscleJiggleValues(self, muscleObjects, midX=0.2, midY=0.5, midZ=0.2):

        """
        set muscle controls jiggle values
        Currently setting values for middle control
        of each muscle in selection
        """

        for muscleObject in muscleObjects:
            ctrl1, ctrl2, ctrl3 = self.getControlsFromMuscle(muscleObject)

            mc.setAttr(ctrl2 + '.jiggleX', midX)
            mc.setAttr(ctrl2 + '.jiggleY', midY)
            mc.setAttr(ctrl2 + '.jiggleZ', midZ)

    def modifyMayaMuscles(self, muscleObjects):

        """
        modify Maya muscles for easier rigging
        """

        for muscleObject in muscleObjects:
            ctrl1, ctrl2, ctrl3 = self.getControlsFromMuscle(muscleObject)

            # add offset group to middle control

            ctrl2Offset = mc.group(n=ctrl2 + 'Offset', em=1, p=ctrl2)
            ctrl2Parent = mc.listRelatives(ctrl2, p=1)[0]
            mc.parent(ctrl2Offset, ctrl2Parent)
            mc.parent(ctrl2, ctrl2Offset)

            # set current stretch as default

            mc.select(muscleObject)
            mm.eval('cMBld_setSplineDefLength(0)')

    def unlockJiggleMuscleAttributes(self):

        """
        In case of using Muscle Master control, which hides
        all muscle jiggle attributes, this will unhide it again,
        so the values can be seen
        They cannot be changed because there is expression connection
        """

        allMuscles = self.getAllMusclesInScene()

        for m in allMuscles:
            middleCtrl = self.getControlsFromMuscle(m)[1]

            mc.setAttr(middleCtrl + '.jiggle', l=0, k=1)
            mc.setAttr(middleCtrl + '.cycle', l=0, k=1)
            mc.setAttr(middleCtrl + '.rest', l=0, k=1)

    def printMuscleAttachments(self, muscleObjects):

        """
        This is wrappet to printMuscleAttachmentsPerMuscle()
        to print attachent information about multiple muscles
        """

        for m in muscleObjects:
            self.printMuscleAttachmentsPerMuscle(m)

    def printMuscleAttachmentsPerMuscle(self, muscleObj):

        """
        Print muscle attachments - useful for quick analysis of muscle attachment
        This script is based on default Maya Simple muscle setup
        """

        muscleControls = self.getControlsFromMuscle(muscleObj)

        controlsData = [muscleObj]

        for i, c in enumerate(muscleControls):

            # get control attachment parent

            cParent = mc.listRelatives(c, p=1)[0]
            cParentPointConst = mc.listConnections(cParent, s=1, d=1, type='pointConstraint')[0]
            cParentTarget = mc.listConnections(cParentPointConst + '.target[0].targetParentMatrix')[0]
            cParentTargetOffsetGrp = mc.listRelatives(cParentTarget, p=1)[0]
            cAttachmentObj = mc.listRelatives(cParentTargetOffsetGrp, p=1)[0]

            # get control constraints

            constraints = mc.listConnections(c, s=1, d=0, type='constraint')
            targetsList = []

            if not constraints: constraints = []

            constraints = list(set(constraints))

            for const in constraints:
                targets = mc.listConnections(const + '.target[*].targetParentMatrix')
                targets = list(set(targets))
                targetsList.append(targets)

            constraintTypes = [mc.nodeType(const) for const in constraints]

            openChannels = []

            for channel in ['t', 'r']:

                for axis in ['x', 'y', 'z']:

                    connectedConst = mc.listConnections(c + '.' + channel + axis, s=1, d=0)

                    if not connectedConst:
                        openChannels.append(channel + axis)

            ctrlData = {'-': 'CONTROL %d' % (i + 1)}

            if not i == 1:
                ctrlData['attachObject'] = cAttachmentObj

            if constraints:
                ctrlData['constraints'] = constraintTypes
                ctrlData['targetsList'] = targetsList
                ctrlData['open'] = openChannels

            controlsData.append(ctrlData)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(controlsData)