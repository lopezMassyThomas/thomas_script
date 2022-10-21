'''
Created on Jun 1, 2020

@author: Thomas

name : Corrective blendshape workflow.
'''

import maya.cmds as mc
import maya.OpenMaya as om
import math

"""
DICO = {'shapeName01': ['time value 01'],
             'shapeName02': ['time value 02']}
"""
POSE_DICO = {'shoulder_up_100' : 1011,
             'shoulder_front_100': 1021,
             'shoulder_back_100': 1031,
             'arm_down_100': 1051,
             'arm_up_100': 1061,
             'shoulder_arm_up_100': 1071
             }
             
KEY_TIME = [] 
GROUP_NAME = ['correctiveBS_sculpt_grp', 'correctiveBS_BS_grp']
CTRL_NAME = 'L_shoulder_fk_ctrl'


def create_sculpt_from_dico():
    """Generate a duplicated mesh at each time value."""
    
    skinned_mesh = mc.ls(sl=True)[0]

    msh_grp = mc.group(n=GROUP_NAME[0], empty=True)
    
    for item in sorted(POSE_DICO.keys(), reverse=True): 
        time = POSE_DICO[item]
        mc.currentTime(time)
         
        new_mesh = copy_mesh(skinned_mesh, name=item)
        mc.parent(new_mesh, msh_grp, a=True)   
        
    return msh_grp


def all_invert_shape():
    selection = mc.ls(sl=True)
    
    if not selection or len(selection) > 2:
        raise RuntimeError('Select at least the skinned mesh to invert all, then select a specific sculpted mesh to invert only this node')

    elif len(selection) == 1:  # if true then try invert all.
        if mc.objExists(GROUP_NAME[0]):  # check for sculpt grp.
            sculpts = mc.listRelatives(GROUP_NAME[0], c=True)
            pos_info = len(POSE_DICO.items())
            
            for corrective in sculpts:
                if POSE_DICO.get(corrective):
                    mc.currentTime(POSE_DICO[corrective])
                    
                    if mc.objExists('%s_invertedShape' % corrective):
                        print '%s : update shape in BS_grp' % corrective
                        invert_shape(selection, corrective, update=True)
                        
                    else:
                        if not mc.objExists(GROUP_NAME[1]):  # then organize.
                            print 'BS_grp created.'
                            mc.group(n=GROUP_NAME[1], empty=True)
                        
                        print '%s : invert default and organized in BS_grp' % corrective
                        delta = invert_shape(selection, corrective, update=True)
                        mc.parent(delta, GROUP_NAME[1])
                else:
                    raise RuntimeWarning('Unable to invert shape %s. Pose information unknown.' % corrective)     
        else:
            raise RuntimeError('%s not found. Unable to invert all.' % GROUP_NAME[0])        
                
    else: # if == 2 then invert selected.
        base, corrective = selection
        
        if mc.objExists('%s_invertedShape' % corrective):
            print 'BS updated'
            invert_shape(base, corrective)
        else:
            print 'BS created'
            invert_shape(base, corrective)
    
    mc.currentTime(0)
    
def invert_shape(base=None, corrective=None, name=None, update=False):
    """Inverts a shape through the deformation chain."""
    
    # Check selection.
    if not base or not corrective:
        sel = mc.ls(sl=True)
        if not sel or len(sel) != 2:
            mc.undoInfo(closeChunk=True)
            raise RuntimeError, 'Select base then corrective'
        base, corrective = sel
    else:
        sel = [base, corrective]  
          
    if not name:
        name = '{}_{}'.format(corrective, 'inverted')
        
    # Get shapes.
    shape_list = []
    for i in range(0, len(sel)):
        shape = mc.listRelatives(sel[i], s=True)
        if not shape :
            raise RuntimeError, 'The selected object has no shape : %s' % sel[i]
        
        if mc.nodeType(shape[0]) != 'mesh':
            raise RuntimeError, '%s is not a mesh' % shape[0]
            
        if i == 0 and len(shape) > 1:
            # Check for skinCluster.
            skin = mc.listConnections(shape[0], type = 'skinCluster')
            # Check for blendShape node.
            bs = mc.listConnections(skin, c=True, type = 'DPK_bcs')
            delta = mc.objExists('%sShape' % name)
            
            if not skin:
                raise RuntimeError, '%s is not bind to a skin cluster' % sel[i]
            
            elif bs and delta:
                print 'connected to blendShape node'
                shape_list.append('%sShape' % name)
            else :
                if mc.getAttr(shape[1] + '.intermediateObject') is True:
                    shape_list.append(shape[1])
        
        shape_list.append(shape[0])
    orig_shape, base_shape, corrective_shape = shape_list

    # get points.
    orig_points = get_points(orig_shape)
    base_points = get_points(base_shape)
    corrective_points = get_points(corrective_shape)
    
    point_count = orig_points.length()
    extractPoints = om.MPointArray(orig_points)
    
    # Get list of vertice index that got corrected.
    pointList = []  
    for i in range(0, point_count):
        if base_points[i] != corrective_points[i]:
            pointList.append(i)
    
    if len(pointList) == 0:
        if update is False:
            raise RuntimeError, 'The selected two meshes are identical.'

    # Create the mesh that will recieve the delta.
    if delta:
        inverted_shape = name
    else:
        inverted_shape = mc.duplicate(base, name=name)[0]
    
    # Delete the unnessary shapes
    shapes = mc.listRelatives(inverted_shape, children=True, shapes=True, path=True)
    for s in shapes:
        if mc.getAttr('{}.{}'.format(s, 'intermediateObject')) is True:
            mc.delete(s)

    # Unlock the transformation attrs
    for attr in 'trs':
        for x in 'xyz':
            mc.setAttr('{}.{}{}'.format(inverted_shape, attr, x), lock=False)
    mc.setAttr('{}.{}'.format(inverted_shape, 'visibility'), 1)
    
    # Make new mesh match orig_shape.
    set_points(shapes[0], orig_points)
    
    # Calculate offset.
    xArray = om.MPointArray(orig_points)
    yArray = om.MPointArray(orig_points)
    zArray = om.MPointArray(orig_points)
    
    for i in pointList: # For each point moved.
        xArray.set(i, orig_points[i].x + 1.0, orig_points[i].y, orig_points[i].z)
        yArray.set(i, orig_points[i].x, orig_points[i].y + 1.0, orig_points[i].z)
        zArray.set(i, orig_points[i].x, orig_points[i].y, orig_points[i].z + 1.0)
    
    set_points(orig_shape, xArray)  # Apply offset x.
    xPointArray = get_points(base_shape)  # Get position base with offset x.
    
    for i in pointList:
        offX = xPointArray[i].x - base_points[i].x
        offY = xPointArray[i].y - base_points[i].y
        offZ = xPointArray[i].z - base_points[i].z
        xPointArray.set(i, offX, offY, offZ)  # set relative position x.
    
    set_points(orig_shape, yArray)  # Apply offset y.
    yPointArray = get_points(base_shape)  # Get position base with offset y.
    
    for i in pointList:
        offX = yPointArray[i].x - base_points[i].x
        offY = yPointArray[i].y - base_points[i].y
        offZ = yPointArray[i].z - base_points[i].z
        yPointArray.set(i, offX, offY, offZ)  # set relative position y.
    
    set_points(orig_shape, zArray)  # Apply offset z.
    zPointArray = get_points(base_shape)  # Get position base with offset z.
    
    for i in pointList:
        offX = zPointArray[i].x - base_points[i].x
        offY = zPointArray[i].y - base_points[i].y
        offZ = zPointArray[i].z - base_points[i].z
        zPointArray.set(i, offX, offY, offZ)  # set relative position z.
     
    # set the original points back
    set_points(orig_shape, orig_points)
    
    # Create matrix.
    for i in pointList:
        extractItems = [zPointArray[i].x, zPointArray[i].y, zPointArray[i].z, 0.0, 
                        xPointArray[i].x, xPointArray[i].y, xPointArray[i].z, 0.0, 
                        yPointArray[i].x, yPointArray[i].y, yPointArray[i].z, 0.0, 
                        base_points[i].x, base_points[i].y, base_points[i].z, 1.0]
        
        resultItems =  [0.0, 0.0, 1.0, 0.0, 
                        1.0, 0.0, 0.0, 0.0, 
                        0.0, 1.0, 0.0, 0.0, 
                        orig_points[i].x, orig_points[i].y, orig_points[i].z, 1.0]
        
        extractMatrix = om.MMatrix()
        om.MScriptUtil.createMatrixFromList(extractItems, extractMatrix)
        
        resultMatrix = om.MMatrix()
        om.MScriptUtil.createMatrixFromList(resultItems, resultMatrix)
        
        point = om.MPoint()
        point = corrective_points[i] * extractMatrix.inverse()
        point *= resultMatrix
        extractPoints.set(point, i)
    
    set_points(shapes[0], extractPoints) 
    
    return inverted_shape 

  
def copy_mesh(node, name=None):
    if not name:
        name = node
        
    new_mesh = mc.duplicate(node, n=name)[0]
    # Delete the unnessary shapes
    shapes = mc.listRelatives(new_mesh, children=True, shapes=True, path=True)
    for s in shapes:
        if mc.getAttr('{}.{}'.format(s, 'intermediateObject')) is True:
            mc.delete(s)

    # Unlock the transformation attrs
    for attr in 'trs':
        for x in 'xyz':
            mc.setAttr('{}.{}{}'.format(new_mesh, attr, x), lock=False)
    mc.setAttr('{}.{}'.format(new_mesh, 'visibility'), 1)

    return new_mesh


def get_points(node):
    """ Define API fonctions to get points positions of a single object"""

    mSel = om.MSelectionList()
    mSel.add(node)
    
    mObj = om.MObject()
    mSel.getDependNode(0, mObj)
        
    mfnMesh = om.MFnMesh()
    mfnMesh.setObject(mObj)
    
    mPointArray = om.MPointArray()
    mfnMesh.getPoints(mPointArray)
    
    return mPointArray


def set_points(node, point_list):
    """ Define API fonctions to set points positions of a single object"""
    
    mSel = om.MSelectionList()
    mSel.add(node)
    
    mObj = om.MObject()
    mSel.getDependNode(0, mObj)
        
    mfnMesh = om.MFnMesh()
    mfnMesh.setObject(mObj)

    mfnMesh.setPoints(point_list)  