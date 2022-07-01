import maya.cmds as mc


def add_new_BS(BSname):
    CvList = []
    sel = mc.ls(sl=True)
    CvList.append(sel)

    BlendName = sel[0] + 'BS'

    for i in CvList:

        NewShape = mc.duplicate(n=sel[0] + '_' + BSname)
        mc.move(0, 0, 10)
        mc.select(CvList[0])
        mc.select(i)
        queryWeights = mc.blendShape(i[0], q=True, w=1)

        if queryWeights < 1:
            mc.blendShape(BlendName, edit=True, t=(i[0], 1, NewShape[0], 1.0), w=[1, 1])
        else:
            numberOfBlendShapes = len(queryWeights)
            indexValue = numberOfBlendShapes + int(1)
            mc.blendShape(BlendName, edit=True, t=(i[0], indexValue, NewShape[0], 1.0), w=[indexValue, 1])


def create_BS_Node():
    CvList = []
    sel = mc.ls(sl=True)
    CvList.append(sel)

    blendNodeName = '{}{}'.format(sel[0], 'BS')
    for i in CvList:
        mc.blendShape(n=blendNodeName)
    return blendNodeName


def getBSListAttr():
    BS_list = []

    sel = mc.ls(sl=True)
    node = '{}{}'.format(sel[0], 'BS')

    name = '{}.{}'.format(node, 'weight')
    size = mc.listAttr(name, m=True)

    for i in range(0, len(size)):
        attrName = name + str([i])
        BS_list.append(size[i])

    return BS_list


#---------------------
#-controllers
#---------------------

def shp_circle(name='circle_ctrl', radius=1):
    ctrl = mc.circle(n=name, nr=(0, 1, 0))

    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name


def shp_sphere(name='sphere_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(0, 1, 0), (0, 0.92388, 0.382683), (0, 0.707107, 0.707107), (0, 0.382683, 0.92388), (0, 0, 1),
                       (0, -0.382683, 0.92388), (0, -0.707107, 0.707107), (0, -0.92388, 0.382683), (0, -1, 0),
                       (0, -0.92388, -0.382683), (0, -0.707107, -0.707107), (0, -0.382683, -0.92388), (0, 0, -1),
                       (0, 0.382683, -0.92388), (0, 0.707107, -0.707107), (0, 0.92388, -0.382683), (0, 1, 0),
                       (0.382683, 0.92388, 0), (0.707107, 0.707107, 0), (0.92388, 0.382683, 0), (1, 0, 0),
                       (0.92388, -0.382683, 0), (0.707107, -0.707107, 0), (0.382683, -0.92388, 0), (0, -1, 0),
                       (-0.382683, -0.92388, 0), (-0.707107, -0.707107, 0), (-0.92388, -0.382683, 0), (-1, 0, 0),
                       (-0.92388, 0.382683, 0), (-0.707107, 0.707107, 0), (-0.382683, 0.92388, 0), (0, 1, 0),
                       (0, 0.92388, -0.382683), (0, 0.707107, -0.707107), (0, 0.382683, -0.92388), (0, 0, -1),
                       (-0.382683, 0, -0.92388), (-0.707107, 0, -0.707107), (-0.92388, 0, -0.382683), (-1, 0, 0),
                       (-0.92388, 0, 0.382683), (-0.707107, 0, 0.707107), (-0.382683, 0, 0.92388), (0, 0, 1),
                       (0.382683, 0, 0.92388), (0.707107, 0, 0.707107), (0.92388, 0, 0.382683), (1, 0, 0),
                       (0.92388, 0, -0.382683), (0.707107, 0, -0.707107), (0.382683, 0, -0.92388), (0, 0, -1)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                       27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                       51, 52])
    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name


def shp_square(name='square_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(1, 0, 1), (-1, 0, 1), (-1, 0, -1), (1, 0, -1), (1, 0, 1)],
                    k=[0, 1, 2, 3, 4])

    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name


def shp_cube(name='cube_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(-1, 1, 1), (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1),
                       (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1),
                       (1, -1, -1), (-1, -1, -1)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name

def shp_cylinder(name='cylinder_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(1.002, -1.000, 0.000), (0.967, -1.000, -0.259), (0.867, -1.000, -0.501), (0.709, -1.000, -0.709),
                       (0.501, -1.000, -0.867), (0.259, -1.000, -0.967), (0.000, -1.000, -1.002), (0.000, 1.004, -1.002),
                       (0.259, 1.004, -0.967), (0.501, 1.004, -0.867), (0.709, 1.004, -0.709), (0.867, 1.004, -0.501),
                       (0.967, 1.004, -0.259), (1.002, 1.004, 0.000), (1.002, -1.000, 0.000), (0.967, -1.000, 0.259),
                       (0.867, -1.000, 0.501), (0.709, -1.000, 0.709), (0.501, -1.000, 0.867), (0.259, -1.000, 0.967),
                       (0.000, -1.000, 1.002), (-0.259, -1.000, 0.967), (-0.501, -1.000, 0.867), (-0.709, -1.000, 0.709), (-0.867, -1.000, 0.501),
                       (-0.967, -1.000, 0.259), (-1.002, -1.000, 0.000), (-1.002, 1.004, 0.000), (-0.967, 1.004, -0.259),
                       (-0.867, 1.004, -0.501), (-0.709, 1.004, -0.709), (-0.501, 1.004, -0.867), (-0.259, 1.004, -0.967),
                       (0.000, 1.004, -1.002), (0.000, -1.000, -1.002), (-0.259, -1.000, -0.967), (-0.501, -1.000, -0.867),
                       (-0.709, -1.000, -0.709), (-0.867, -1.000, -0.501), (-0.967, -1.000, -0.259), (-1.002, -1.000, 0.000),
                       (-1.002, 1.004, 0.000), (-0.967, 1.004, 0.259), (-0.867, 1.004, 0.501), (-0.709, 1.004, 0.709),
                       (-0.501, 1.004, 0.867), (-0.259, 1.004, 0.967), (0.000, 1.004, 1.002), (0.000, -1.000, 1.002),
                       (0.000, 1.004, 1.002), (0.259, 1.004, 0.967), (0.501, 1.004, 0.867), (0.709, 1.004, 0.709),
                       (0.867, 1.004, 0.501), (0.967, 1.004, 0.259), (1.002, 1.004, 0.000)],
                    k=[0.0, 1.565366, 3.130758, 4.696126, 6.261487, 7.826885, 9.392244, 15.392244, 16.957602, 18.523,
                       20.088361, 21.653729,
                       23.219121, 24.784487, 30.784487, 32.349852, 33.915246, 35.480611, 37.045976, 38.61137, 40.176735,
                       41.7421, 43.307494,
                       44.872859, 46.438224, 48.003618, 49.568983, 55.568983, 57.134349, 58.699741, 60.265109, 61.83047,
                       63.395868, 64.961226,
                       70.961226, 72.526584, 74.091982, 75.657343, 77.222712, 78.788104, 80.35347, 86.35347, 87.918834,
                       89.484229, 91.049594,
                       92.614959, 94.180353, 95.745718, 101.745718, 107.745718, 109.311083, 110.876477, 112.441842,
                       114.007207, 115.572601, 117.137966])

    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name

def shp_diamond(name='diamond_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(0, 0, 1), (0, 1, 0), (0, 0, -1), (0, -1, 0), (0, 0, 1), (1, 0, 0), (0, 1, 0), (-1, 0, 0),
                       (0, -1, 0), (1, 0, 0), (0, 0, -1), (-1, 0, 0), (0, 0, 1)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name

def shp_root(name='ROOT_ctrl', radius=1):
    ctrl = mc.circle(ch=1, o=1, nr=(0, 1, 0), r=1) #create main ctrl.
    mc.rename(ctrl[0], name)

    arrowList = [] #create first arrow ctrl.
    arrowName = name + 'arrow01'
    arrow = mc.curve(d=1,
                     p=[(-0.1, 0, 1.1), (0.1, 0, 1.1), (0.1, 0, 1.3), (0.2, 0, 1.3), (0, 0, 1.5), (-0.2, 0, 1.3),
                        (-0.1, 0, 1.3), (-0.1, 0, 1.1)],
                     k=[0, 1, 2, 3, 4, 5, 6, 7])
    mc.rename(arrow, arrowName)
    arrowList.append(arrowName)

    for v in range(1, 4): #duplicate and rotate arrows.
        degree = 90
        dup = mc.duplicate(arrowName)
        mc.rotate(0, 90 * v, 0, dup)
        mc.makeIdentity(dup, apply=True, t=1, r=1, s=1, n=0)
        arrowList.append(dup)

    shapesList = [] # parent each arrow shapes to main ctrl.
    for n in arrowList:
        s = mc.listRelatives(n, s=True)
        shapesList.append(s)

    [mc.parent(s, name, r=1, s=1) for s in shapesList]
    [mc.delete(n) for n in arrowList]

    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name

def shp_rotate(name='rotate_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(0.927709, 0.933166, 4.785622), (0.933166, 1.864716, 4.505818), (0.933166, 2.662429, 4.099688),
                       (0.933166, 3.410389, 3.51732), (0.933166, 4.011776, 2.84131), (2.7995, 4.011776, 2.84131),
                       (1.888188, 4.479274, 2.060603), (0.933166, 4.811788, 1.167227), (0, 4.964421, 0.248014),
                       (-0.91163, 4.81531, 1.146013), (-1.875934, 4.48556, 2.050105), (-2.7995, 4.011776, 2.84131),
                       (-0.933166, 4.011776, 2.84131), (-0.933166, 3.398044, 3.531197), (-0.933166, 2.654188, 4.106034),
                       (-0.933166, 1.822898, 4.526994), (-0.933166, 0.927709, 4.785622), (-1.914378, 0.933166, 4.480669),
                       (-2.64947, 0.933166, 4.108423), (-3.39244, 0.933166, 3.537496), (-4.011776, 0.933166, 2.84131),
                       (-4.011776, 2.7995, 2.84131), (-4.497041, 1.847291, 2.024032), (-4.811788, 0.933166, 1.167227),
                       (-4.964421, 0, 0.248014), (-4.811788, -0.933166, 1.167227), (-4.465589, -1.914864, 2.083456),
                       (-4.011776, -2.7995, 2.84131), (-4.011776, -0.933166, 2.84131), (-3.39244, -0.933166, 3.537496),
                       (-2.64924, -0.933166, 4.10854), (-1.818761, -0.933166, 4.528189), (-0.927709, -0.933166, 4.785622),
                       (-0.933166, -1.857022, 4.509714), (-0.933166, -2.671067, 4.093035), (-0.933166, -3.408494, 3.51945),
                       (-0.933166, -4.011776, 2.84131), (-2.7995, -4.011776, 2.84131), (-1.810282, -4.509784, 1.989343),
                       (-0.962033, -4.801849, 1.194284), (0, -4.964421, 0.248014), (0.938138, -4.810076, 1.171887),
                       (1.865788, -4.490673, 2.041369), (2.7995, -4.011776, 2.84131), (0.933166, -4.011776, 2.84131),
                       (0.933166, -3.354737, 3.566532), (0.933166, -2.646898, 4.109726), (0.933166, -1.830077, 4.523359),
                       (0.927709, -0.933166, 4.785622), (1.822898, -0.933166, 4.526994), (2.662097, -0.933166, 4.099943),
                       (3.313799, -0.933166, 3.598058), (4.011776, -0.933166, 2.84131), (4.011776, -2.7995, 2.84131),
                       (4.520404, -1.779439, 1.960435), (4.833797, -0.798609, 1.034682), (4.964421, 0, 0.248014),
                       (4.808417, 0.942957, 1.176404), (4.495671, 1.851272, 2.027764), (4.011776, 2.7995, 2.84131),
                       (4.011776, 0.933166, 2.84131), (3.381213, 0.933166, 3.546142), (2.655888, 0.933166, 4.104725),
                       (1.816633, 0.933166, 4.528804), (0.927709, 0.933166, 4.785622)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                    31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                    61, 62, 63, 64, 65])
    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name


def shp_loc(name='locator_ctrl', radius=1):
    ctrl = mc.curve(d=1,
                    p=[(0, 0, -1), (0, 0, 1), (0, 0, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 0), (0, 1, 0), (0, -1, 0)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7])
    mc.rename(ctrl, name)
    mc.xform(name, s=(radius, radius, radius), a=True)
    mc.makeIdentity(name, apply=True, t=1, r=1, s=1, n=0, pn=1)
    mc.delete(name, ch=1)

    return name

def shp_lolipop(name='lolipop_ctrl', radius=1):
    grp = mc.group(n=name, empty=True)
    
    ctrl1 = mc.circle(n=name+'1', nr=(0, 0, 1))

    #mc.xform(ctrl1, s=(radius, radius, radius), a=True)
    mc.xform(ctrl1, t=(0, 5, 0), a=True)
    mc.makeIdentity(ctrl1, apply=True, t=1, r=1, s=1, n=0, pn=1)
    #mc.delete(ctrl1, ch=1)

    ctrl2 = mc.curve(d=1,
                    p=[(0, 0, 0), (0, 5, 0)],
                    k=[0, 1])
    
    mc.xform(ctrl2, s=(radius, radius, radius), a=True)
    #mc.makeIdentity(ctrl2, apply=True, t=1, r=1, s=1, n=0, pn=1)
    #mc.delete(ctrl2, ch=1)

    mc.rename(ctrl2, name+'2')

    shape1 = mc.listRelatives(ctrl1[0], c=True, s=True)
    shape2 = mc.listRelatives(name+'2', c=True, s=True)
    mc.parent(shape1, shape2, grp, s=True, r=True)
    mc.delete(ctrl1[0], name+'2')
    
    return grp

shpDico = {'0': shp_circle,
           '1': shp_sphere,
           '2': shp_square,
           '3': shp_cube,
           '4': shp_cylinder,
           '5': shp_diamond,
           '6': shp_root,
           '7': shp_loc,
           '8': shp_lolipop
           }
