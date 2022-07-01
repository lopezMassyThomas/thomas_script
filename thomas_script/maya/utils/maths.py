import maya.cmds as mc
import maya.OpenMaya as om

##############################################==============================
# Calculate average from list of int or float.
##############################################==============================

def averageValue(listValue):
    total = sum(listValue)
    total = float(total)

    return total / len(listValue)

###############################################=============================
# Get the distance between two vector/position.
###############################################=============================

def getDistance(positionA, positionB):
    from math import sqrt
    a = positionA  # data point 1
    b = positionB  # data point 2
    result = sqrt(sum((a - b) ** 2 for a, b in zip(a, b)))
    return result

####################################################################========
# Get the center of an object using the Bounding box Infos of xform.
####################################################################========

def getGeoBBoxCenter(node):
    # get raw boundingBox values of tagObject.
    bbInfo = mc.xform(node, q=True, bb=True)

    # calculate average of each axis value.
    xValueList = [bbInfo[0],
                  bbInfo[3]]
    averageX = averageValue(xValueList)
    yValueList = [bbInfo[1],
                  bbInfo[4]]
    averageY = averageValue(yValueList)
    zValueList = [bbInfo[2],
                  bbInfo[5]]
    averageZ = averageValue(zValueList)

    result = [averageX, averageY, averageZ]

    return result

def getMirrorPos():
    sel = mc.ls(sl=True)  # Get selection.
    mesh = str(sel[0]).split('.')
    mesh = mesh[0]
    posSel = mc.xform(sel, q=True, ws=True, t=True)  # Get position of selection.
    mirrorPos = posSel[0] * -1, posSel[1], posSel[2]

    mirrorSel, mirrorPos = getClosestPointOnGeo(mesh, mirrorPos)

    return mirrorSel

def getClosestPointOnGeo(geo, pos):
    nodeDagPath = om.MObject()
    try:
        selectionList = om.MSelectionList()
        selectionList.add(geo)
        nodeDagPath = om.MDagPath()
        selectionList.getDagPath(0, nodeDagPath)
    except:
        raise RuntimeError('OpenMaya.MDagPath() failed on %s' % geo)

    mfnMesh = om.MFnMesh(nodeDagPath)

    pointA = om.MPoint(pos[0], pos[1], pos[2])
    pointB = om.MPoint()
    space = om.MSpace.kWorld

    util = om.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()

    mfnMesh.getClosestPoint(pointA, pointB, space, idPointer)
    idx = om.MScriptUtil(idPointer).asInt()

    faceVerts = mc.ls(mc.polyListComponentConversion('{}.f[{}]'.format(geo, idx), fromFace=True, tv=True), fl=True)

    closestVert = None
    minLength = None
    maxPos = None
    for v in faceVerts:
        vPosi = mc.xform(v, ws=True, t=True, q=True)
        thisLength = getDistance(pos, vPosi)

        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v
            maxPos = vPosi
    return closestVert, maxPos




