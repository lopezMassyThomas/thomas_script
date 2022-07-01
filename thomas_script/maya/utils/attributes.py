import maya.cmds as mc

def addControlColors(leftSidePrefix='L_', rightSidePrefix='R_', controlSuffix='_ctrl'):
    """
    add colors to control shapes based on side
    """

    allControls = mc.ls('*' + controlSuffix)

    for c in allControls:

        l_clrIndex = 6
        r_clrIndex = 13
        c_clrIndex = 22

        shapes = mc.listRelatives(c, s=1)

        if c.startswith(leftSidePrefix):

            clrIndex = l_clrIndex

        elif c.startswith(rightSidePrefix):

            clrIndex = r_clrIndex

        else:

            clrIndex = c_clrIndex

        for s in shapes:
            mc.setAttr(s + '.ove', 1)
            mc.setAttr(s + '.ovc', clrIndex)

def connectModelAndSkeleton(selection=None):
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

def labelJoints():
    """
    @param joints: list(str), list of joints to be labeled
    """
    joints = mc.ls(sl=True)

    for j in joints:

        # =======================================================================
        # get side
        # =======================================================================

        side = ''
        base = j

        if j.startswith('L_'):
            side = 'L'
            base = j.lstrip('L_')

        if j.startswith('R_'):
            side = 'R'
            base = j.lstrip('R_')

        # =======================================================================
        # set custom label
        # =======================================================================

        if side == '': mc.setAttr(j + '.side', 0)
        if side == 'L': mc.setAttr(j + '.side', 1)
        if side == 'R': mc.setAttr(j + '.side', 2)

        mc.setAttr(j + '.type', 18)
        mc.setAttr(j + '.otherType', base, typ='string')