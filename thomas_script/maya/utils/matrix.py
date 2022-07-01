'''
Created on Feb 18, 2021

@author: Thomas
'''
import maya.cmds as mc
import maya.OpenMaya as om

        
def getDagPath(node=None):
    sel = om.MSelectionList()
    print node
    sel.add(node)
    dag = om.MDagPath()
    sel.getDagPath(0, dag)
    return dag

def getLocalOffset(parent, child):
    parentWorldMatrix = getDagPath(parent).inclusiveMatrix()
    childWorldMatrix = getDagPath(child).inclusiveMatrix()
    return childWorldMatrix * parentWorldMatrix.inverse()

def renameNodes():
    pass

def matrixConstraint(parent, child, mo=True, t=True, ro=True, s=True):
    decompose = mc.createNode('decomposeMatrix')
    if mo is True:
        mult = mc.createNode('multMatrix')
        localOffset = getLocalOffset(parent, child)
        mc.setAttr('{}.matrixIn[0]'.format(mult), [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
        
        # -connect matrices to multMatrix.
        mc.connectAttr('{}.worldMatrix[0]'.format(parent), '{}.matrixIn[1]'.format(mult))
        mc.connectAttr('{}.parentInverseMatrix[0]'.format(child), '{}.matrixIn[2]'.format(mult))
        
        # -Connect multMatrix to decomposeMatrix.
        mc.connectAttr('{}.matrixSum'.format(mult), '{}.inputMatrix'.format(decompose))
    else:
        # -Connect parent to decomposeMatrix.
        mc.connectAttr('{}.worldMatrix[0]'.format(parent), '{}.inputMatrix'.format(decompose))  
                 
    # -Connect decomposeMarix to driven.
    if t is True:
        mc.connectAttr('{}.outputTranslate'.format(decompose), '{}.translate'.format(child))
    if ro is True:
        mc.connectAttr('{}.outputRotate'.format(decompose), '{}.rotate'.format(child))
    if s is True:
        mc.connectAttr('{}.outputScale'.format(decompose), '{}.scale'.format(child)) 
               
def matrixConstraint_old(parent, child, mo=True, t=True, ro=True, s=True):
    # -Create matrix math nodes.
    mult = mc.createNode('multMatrix')
    decompose = mc.createNode('decomposeMatrix')

    # -Set local offset for MaintainOffset.
    if mo is True:
        localOffset = getLocalOffset(parent, child)
        mc.setAttr('{}.matrixIn[0]'.format(mult), [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
        
    # -connect matrices to multMatrix.
    mc.connectAttr('{}.worldMatrix[0]'.format(parent), '{}.matrixIn[1]'.format(mult))
    mc.connectAttr('{}.parentInverseMatrix[0]'.format(child), '{}.matrixIn[2]'.format(mult))
    
    # -Connect multMatrix to decomposeMatrix.
    mc.connectAttr('{}.matrixSum'.format(mult), '{}.inputMatrix'.format(decompose))
    
    # -Connect decomposeMarix to driven.
    if t is True:
        mc.connectAttr('{}.outputTranslate'.format(decompose), '{}.translate'.format(child))
    if ro is True:
        mc.connectAttr('{}.outputRotate'.format(decompose), '{}.rotate'.format(child))
    if s is True:
        scale = mc.createNode('decomposeMatrix')
        mc.connectAttr('{}.worldMatrix[0]'.format(parent), '{}.inputMatrix'.format(scale))
        mc.connectAttr('{}.outputScale'.format(scale), '{}.scale'.format(child))
      
    # -Fix jointOrient if child is a joint.
    if mc.objectType(child) == 'joint':
        #previous = mc.listRelatives(child)
        # -Create matrix math nodes.
        compose = mc.createNode('composeMatrix')
        multJO_0 = mc.createNode('multMatrix')
        invert = mc.createNode('inverseMatrix')
        multJO_1 = mc.createNode('multMatrix')          
        decomposeJO = mc.createNode('decomposeMatrix')
          
        # -Set jointOrient offset to composeMatrix.
        '''
        mc.setAttr('{}.jointOrient'.format(child), '{}.inputRotate'.format(compose))  
        '''
        joX = mc.getAttr('{}.jointOrientX'.format(child))
        joY = mc.getAttr('{}.jointOrientY'.format(child))
        joZ = mc.getAttr('{}.jointOrientZ'.format(child))
        mc.setAttr('{}.inputRotateX'.format(compose), joX)
        mc.setAttr('{}.inputRotateY'.format(compose), joY)
        mc.setAttr('{}.inputRotateZ'.format(compose), joZ)
          
        # -Connect composeMatrix and parent matrix to mult1.
        drivenParent = mc.listRelatives(child, p=True)[0]
        mc.connectAttr('{}.outputMatrix'.format(compose), '{}.matrixIn[0]'.format(multJO_0))
        mc.connectAttr('{}.worldMatrix[0]'.format(drivenParent), '{}.matrixIn[1]'.format(multJO_0))        
          
        # -Reverse matrix.
        mc.connectAttr('{}.matrixSum'.format(multJO_0), '{}.inputMatrix'.format(invert))
          
        # -Connect 
        mc.connectAttr('{}.worldMatrix[0]'.format(parent), '{}.matrixIn[0]'.format(multJO_1))
        mc.connectAttr('{}.outputMatrix'.format(invert), '{}.matrixIn[1]'.format(multJO_1))
          
        mc.connectAttr('{}.matrixSum'.format(multJO_1), '{}.inputMatrix'.format(decomposeJO))
          
        mc.disconnectAttr('{}.outputRotate'.format(decompose), '{}.rotate'.format(child))
        mc.connectAttr('{}.outputRotate'.format(decomposeJO), '{}.rotate'.format(child))   
