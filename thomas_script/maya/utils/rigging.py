import maya.cmds as mc
from thomas_script.maya.utils import attributes, maths, shapes, transform

#######################################################################=====
# Add one joint between two others and move/rotate between them. (Skin)
#######################################################################=====

def addBlendedJoint():
    sel = mc.ls(sl=True)
    for i in sel:
        print i
        # Get Parent of selection.
        parentSel = mc.listRelatives(sel, p=True)
        # Define and create jnt.
        jnt_name = '{}_{}'.format('blend', i)
        jnt = mc.joint(n=jnt_name, r=1.5)
        # Set position of new jnt.
        pConstr = mc.pointConstraint(sel, jnt)
        mc.delete(pConstr)
        # Parent new jnt to the parent of selection.
        mc.parent(jnt, parentSel)
        # Create node to blend rotation of chainJnt.
        node = mc.createNode('pairBlend', n='{}_{}'.format(sel, 'pairBlend'))
        # Set attribute of pairBlend node.
        mc.setAttr('{}.{}'.format(node, 'rotInterpolation'), 1)
        mc.setAttr('{}.{}'.format(node, 'weight'), 0.5)
        # Connect selectedJnt to pairBlend.
        mc.connectAttr('{}.{}'.format(i, 't'), '{}.{}'.format(node, "inTranslate1"))
        mc.connectAttr('{}.{}'.format(i, 't'), '{}.{}'.format(node, "inTranslate2"))
        mc.connectAttr('{}.{}'.format(i, "r"), '{}.{}'.format(node, "inRotate1"))
        # Connect pairBlend to new Jnt.
        mc.connectAttr('{}.{}'.format(node, "outRotateX"), '{}.{}'.format(jnt, "rotateX"))
        mc.connectAttr('{}.{}'.format(node, "outRotateY"), '{}.{}'.format(jnt, "rotateY"))
        mc.connectAttr('{}.{}'.format(node, "outRotateZ"), '{}.{}'.format(jnt, "rotateZ"))

        mc.connectAttr('{}.{}'.format(node, "outTranslateX"), '{}.{}'.format(jnt, "translateX"))
        mc.connectAttr('{}.{}'.format(node, "outTranslateY"), '{}.{}'.format(jnt, "translateY"))
        mc.connectAttr('{}.{}'.format(node, "outTranslateZ"), '{}.{}'.format(jnt, "translateZ"))
        # Connect scale of selected jnt and new Jnt.
        mc.connectAttr('{}.{}'.format(i, "scale"), '{}.{}'.format(jnt, "scale"))


###################################################################=========
# Add one jnt on selected. Increment itself if used multiple times.
###################################################################=========

def addSupportJoint():
    sel = mc.ls(sl=True)
    for i in sel:
        baseName = 'extraJnt'
        objName = i
        children = mc.listRelatives(objName, c=True)
        if children is None:
            increment = 1
        else:
            increment = 1 + len(children)

        jnt01 = mc.createNode('joint', n='{}{}_{}'.format(baseName, increment, i))
        mc.setAttr(jnt01 + '.radius', 1.5)
        mc.parent(jnt01, i, r=True)


def ctrlJoint_onVertex(baseName, createJnt, ctrlType, mirror=False, space='local'):
    ctrlName = '{}_{}'.format(baseName, 'ctrl')
    ctrlShapeName = '{}{}'.format(ctrlName, 'Shape')

    sel = mc.ls(sl=True)  # Get selection.
    mesh = str(sel[0]).split('.')
    mesh = mesh[0]

    posSel = mc.xform(sel, q=True, ws=True, t=True)  # Get position of selection.

    # -----------------------------------------------------------------------
    # ---Create a controller with position and rotation of the selection---

    ctrl = mc.group(n=ctrlName, empty=True)  # Create controller.
    mc.xform(ctrl, t=posSel)  # Set position of ctrl.

    newCtrl = shapes.shpDico[str(ctrlType)]()  # Create controller shape.

    shape = mc.listRelatives(newCtrl, c=True)  # Get shape node.
    shape = mc.rename(shape, ctrlShapeName)  # Rename shape node.

    mc.parent(shape, ctrl, r=True, s=True)  # Parent shape to controller.
    mc.delete(newCtrl)  # Delete Nurbsphere node.
    
    if space is 'local':
        # Orient the controller using constraint and delete constraint.
        constr = mc.normalConstraint(sel,
                                     ctrl,
                                     aimVector=(0, 0, 1),
                                     worldUpType=0)
        mc.delete(constr)

    # mc.select(ctrl)
    orig = transform.orig_Sel(objList=ctrl)  # Create orig on controller.
    neg = transform.orig_Sel(objList=ctrl, preffix='_Neg')
    # mc.select(ctrl)
    offset = transform.orig_Sel(objList=ctrl, preffix='_offset')

    # -----------------------------------------------------------------------
    # ---Create a joint if check box is checked---

    if createJnt is True:
        mc.select(clear=True)
        jntName = '{}_{}'.format(baseName, 'Jnt')

        jnt = mc.joint(n=jntName, p=posSel, rad=0.5)
        RigConst_Grp = transform.orig_Sel(objList=jnt, preffix='_RigConstr')
        ctrlConst_Grp = transform.orig_Sel(objList=jnt, preffix='_CtrlConstr')
        
        if space is 'local':
            constr = mc.normalConstraint(sel,
                                         RigConst_Grp,
                                         aimVector=(0, 0, 1),
                                         worldUpType=0)
            mc.delete(constr)

        # -----------------------------------------------------------------------
        # ---Connect controller and joint---

        mc.connectAttr('{}.{}'.format(ctrl, 't'), '{}.{}'.format(ctrlConst_Grp, 't'))
        mc.connectAttr('{}.{}'.format(ctrl, 'r'), '{}.{}'.format(ctrlConst_Grp, 'r'))

        # -----------------------------------------------------------------------
        # ---Group and clean joint hierarchy---
        globalGrpName = '{}_{}'.format(baseName, 'Jnt_Grp')
        mc.group(RigConst_Grp, n=globalGrpName)

    # -----------------------------------------------------------------------
    # ---Connecting Neg node---
    MDname = '{}_{}'.format(ctrlName, 'NegMD')
    mc.createNode('multiplyDivide', n=MDname)
    mc.connectAttr('{}.{}'.format(ctrl, 't'), '{}.{}'.format(MDname, 'i1'))
    mc.setAttr('{}.{}'.format(MDname, 'i2x'), -1)
    mc.setAttr('{}.{}'.format(MDname, 'i2y'), -1)
    mc.setAttr('{}.{}'.format(MDname, 'i2z'), -1)
    mc.connectAttr('{}.{}'.format(MDname, 'o'), '{}.{}'.format(neg, 't'))

    # -----------------------------------------------------------------------
    # ---Create a follicle and constraint controller on it---

    closest = mc.createNode('closestPointOnMesh')
    mc.connectAttr('{}.{}'.format(mesh, 'outMesh'), '{}.{}'.format(closest, 'inMesh'))
    mc.setAttr('{}.{}'.format(closest, 'inPositionX'), posSel[0])
    mc.setAttr('{}.{}'.format(closest, 'inPositionY'), posSel[1])
    mc.setAttr('{}.{}'.format(closest, 'inPositionZ'), posSel[2])

    folicle = mc.createNode("follicle")
    folicleTrans = mc.listRelatives(folicle, type='transform', p=True)

    mc.connectAttr('{}.{}'.format(folicle, "outRotate"),
                   '{}.{}'.format(folicleTrans[0], "rotate"))
    mc.connectAttr('{}.{}'.format(folicle, "outTranslate"),
                   '{}.{}'.format(folicleTrans[0], "translate"))
    mc.connectAttr('{}.{}'.format(mesh, 'worldMatrix'),
                   '{}.{}'.format(folicle, 'inputWorldMatrix'))
    mc.connectAttr('{}.{}'.format(mesh, 'outMesh'),
                   '{}.{}'.format(folicle, 'inputMesh'))
    mc.setAttr('{}.{}'.format(folicle, "simulationMethod"), 0)
    u = mc.getAttr('{}.{}'.format(closest, 'result.parameterU'))
    v = mc.getAttr('{}.{}'.format(closest, 'result.parameterV'))
    mc.setAttr('{}.{}'.format(folicle, 'parameterU'), u)
    mc.setAttr('{}.{}'.format(folicle, 'parameterV'), v)

    mc.parentConstraint(folicleTrans[0], orig, mo=True)
    mc.delete(closest)

    # -----------------------------------------------------------------------
    # ---Group and clean control hierarchy---
    globalGrpName = '{}_{}'.format(baseName, 'Ctrl_Grp')
    globalGrp = mc.group(empty=True, n=globalGrpName)
    mc.parent(orig, globalGrp, a=True)
    mc.parent(folicleTrans, globalGrp, a=True)

    if createJnt is True:
        return jnt

def ctrlJnt_onCurve(numJnt, follow, ctrlType):
    LocatorList = []
    CvList = []
    JointList = []

    SelectedCVs = mc.ls(sl=True)[0]
    CvList.append(SelectedCVs)
    
    for i in range(0, numJnt, 1):
        LocName = '{}_{}{}'.format(CvList[0], 'Locator0', str(i + 1))
        JntName = '{}_{}{}'.format(CvList[0], 'Joint0', str(i + 1))
        OrigName = '{}_{}{}'.format(CvList[0], 'Orig0', str(i + 1))

        CreateLoc = mc.spaceLocator(name=LocName)
        LocatorList.append(CreateLoc)

        Uvalue = i / (numJnt - 1.0)

        mc.pathAnimation(SelectedCVs, CreateLoc, startU=Uvalue, follow=follow)

        CreateJoint = mc.joint(name=JntName)
        JointList.append(CreateJoint)

        mc.group(name=OrigName)

    for i in JointList:
        JntShpName = '{}{}'.format(JntName, 'Shape')
        newCtrl = shapes.shpDico[str(ctrlType)]()  # Create controller shape.
        
        shape = mc.listRelatives(newCtrl, c=True)  # Get shape node.
        shape = mc.rename(shape, JntShpName)  # Rename shape node.        
        mc.parent(shape, i, r=True, s=True)
        mc.delete(newCtrl)

def edgeToCurve():
    sel = mc.ls(sl=True)

    newCurve = mc.polyToCurve(form=0, degree=3)
    finalCurve = mc.rebuildCurve(newCurve, ch=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=0, d=3, tol=0.01)
    mc.delete(newCurve)

def makeTwistJoints(displayLocalAxis=False):
    # set variables
    sel = mc.ls(sl=True)
    baseJnt = sel[0]
    refJnt = sel[1]

    refJntRad = mc.getAttr(baseJnt + '.radius')
    numTwistJoints = 5

    # top group

    topGrp = 'twistJoints_grp'

    if not mc.objExists(topGrp):
        topGrp = mc.group(n=topGrp, em=1)

    # make prefix

    prefix = baseJnt.rstrip('_jnt')

    # main group

    mainGrp = mc.group(n=prefix + 'TwistJoints_grp', em=1, p=topGrp)

    mc.parentConstraint(baseJnt, mainGrp)

    # make twist ref joint

    baseJntChild = mc.listRelatives(baseJnt, c=1, typ='joint')[0]
    jntPos1 = mc.xform(baseJnt, q=1, t=1, ws=1)
    jntPos2 = mc.xform(baseJntChild, q=1, t=1, ws=1)

    mc.select(cl=1)
    twistRefJnt1 = mc.joint(n=prefix + 'TwistRef1_jnt', radius=refJntRad * 2, p=jntPos1)
    twistRefJnt2 = mc.joint(n=prefix + 'TwistRef2_jnt', radius=refJntRad * 2, p=jntPos2)
    mc.joint(twistRefJnt1, e=1, zso=1, oj='xyz', sao='yup')
    mc.parent(twistRefJnt1, mainGrp)

    refIk = mc.ikHandle(n=prefix + 'TwistRef_ikh', sol='ikSCsolver', sj=twistRefJnt1, ee=twistRefJnt2)[0]
    mc.parent(refIk, mainGrp)
    mc.hide(twistRefJnt1, refIk)
    mc.orientConstraint(refJnt, refIk, mo=1)

    # make twist joints

    mc.select(mainGrp)
    creatorTwistJnt = mc.joint(n=prefix + 'TwistCreator_jnt', radius=refJntRad * 2)
    mc.color(creatorTwistJnt, ud=8)
    target1 = baseJnt
    target2 = baseJntChild

    if baseJntChild == refJnt:
        target1 = baseJntChild
        target2 = baseJnt

    twistJntPointConst = mc.pointConstraint(target1, target2, creatorTwistJnt)[0]
    twistJntPointConstAts = mc.pointConstraint(twistJntPointConst, q=1, weightAliasList=1)
    offsetIncrement = 1.0 / (numTwistJoints - 1)

    twistJoints = []

    for i in range(numTwistJoints):
        mc.setAttr(twistJntPointConst + '.' + twistJntPointConstAts[0], i * offsetIncrement)
        mc.setAttr(twistJntPointConst + '.' + twistJntPointConstAts[1], 1 - (i * offsetIncrement))
        twistJnt = mc.duplicate(creatorTwistJnt, n=prefix + 'TwistPart%d_jnt' % (i + 1), parentOnly=1)[0]
        twistJntPos = mc.getAttr(creatorTwistJnt + '.t')[0]
        mc.setAttr(twistJnt + '.t', twistJntPos[0], twistJntPos[1], twistJntPos[2])
        multiRotNode = mc.createNode('multDoubleLinear', n=prefix + 'TwistPart%d_mdl' % (i + 1))
        mc.connectAttr(twistRefJnt1 + '.rx', multiRotNode + '.i1')
        mc.setAttr(multiRotNode + '.i2', i * offsetIncrement)
        mc.connectAttr(multiRotNode + '.o', twistJnt + '.rx')

        mc.setAttr(twistJnt + '.displayLocalAxis', displayLocalAxis)

    mc.delete(creatorTwistJnt)

    return twistJoints


def makeRotateBlendLocator():
    """
    make locator which rotates half of rotation of parent and child joint
    Useful for shoulders, knees and other joints for interpolation of weights
    and for attachment of muscles
    """

    sel = mc.ls(sl=True)
    parentJnt = sel[0]
    childJnt = sel[1]

    topRotateBlendGrp = 'rotateBlendLocators_grp'

    if not mc.objExists(topRotateBlendGrp):
        topRotateBlendGrp = mc.group(n=topRotateBlendGrp, em=1)

    prefix = parentJnt.rstrip('_jnt') + '_' + childJnt.rstrip('_jnt') + '_rotblend'
    locGrp = mc.group(n=prefix + '_grp', em=1, p=topRotateBlendGrp)
    loc = mc.spaceLocator(n=prefix + '_loc')[0]
    mc.color(loc, ud=4)
    mc.parent(loc, locGrp, r=1)

    mc.parentConstraint(childJnt, locGrp)
    locConst = mc.parentConstraint(parentJnt, childJnt, loc, st=['x', 'y', 'z'])[0]

    mc.setAttr(locConst + '.interpType', 2)  # interpolation type - shortest

    return loc