import maya.cmds as mc

###############################=============================================
# Create grp and zeroOut target.
###############################=============================================

# Use Selection.
def orig_Sel(objList=None, preffix='_orig'):
    ''''''
    # Get Current selection
    if objList == None:
        selection = mc.ls(sl=True)
    if isinstance(objList, list) is True:
        selection = objList
    else:
        selection = [objList]

    for i in selection:
        if i.startswith('|'):
            i = i[1:]
        # Get Parent
        sel_parent = mc.listRelatives(i, p=True)
        if str(sel_parent).startswith('|'):
            sel_parent = sel_parent[1:]

        if sel_parent:
            sel_parent = sel_parent[0]
        # Get current Obj Transform
        pos_Sel = mc.xform(i, q=True, t=True, ws=True)
        rot_Sel = mc.xform(i, q=True, ro=True, ws=True)
        # Create a group
        grp = mc.group(em=True, name='{}{}'.format(i, preffix))
        # Set in place
        mc.xform(grp, a=True, t=pos_Sel, ro=rot_Sel, s=[1, 1, 1])
        # Parent current to orig Group
        mc.parent(i, grp, relative=False)
        # reParent group to original parent
        if sel_parent:
            mc.parent(grp, sel_parent, relative=False)
    return grp

# Use pre-defined List.
def orig_List(objectList):
    ''''''
    # Get Current selection
    #selection = objectList
    origList = []
    for item in objectList:
        # Get Parent
        sel_parent = mc.listRelatives(item, p=True)
        if sel_parent:
            sel_parent = sel_parent[0]
        # Get current Obj Transform
        pos_Sel = mc.xform(item, q=True, t=True, ws=True)
        rot_Sel = mc.xform(item, q=True, ro=True, ws=True)
        # Create a group
        grp = mc.group(em=True, name=item + '_orig')
        origList.append(grp)
        # Set in place
        mc.xform(grp, a=True, t=pos_Sel, ro=rot_Sel, s=[1, 1, 1])
        # Parent current to orig Group
        mc.parent(item, grp, relative=False)
        # reParent group to original parent
        if sel_parent:
            mc.parent(grp, sel_parent, relative=False)
    return origList

#######################=====================================================
#Snap Object to target.
#######################=====================================================
def snap(objName, target) :

    #Constraint parent.
    constraint=mc.parentConstraint(target,
                                   objName,
                                   maintainOffset=False,
                                   name='TMP_cstr_TMP_snap')
    #Delete constraint.
    mc.delete(constraint[0])