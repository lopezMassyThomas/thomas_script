'''
Created on mar 25, 2019

@author: thomas
'''
import sys
import maya.cmds as mc
from Qt import QtCore
from Qt import QtWidgets

from thomas_script.maya.scripts.rigToolKit import rigToolKit
from thomas_script.maya.scripts.rigToolKit import rigToolKit_core
from thomas_script.maya.utils import shapes, rigging, attributes
from thomas_script.maya.scripts import shapeSculpting

reload(rigToolKit)
reload(rigToolKit_core)
reload(shapes)
reload(rigging)

from thomas_script.maya.utils import pySideMaya
#===============================================================================
# from common.utils import system
# from softwares.maya import common
#===============================================================================
import time

IS_IN_MAYA = True
#===============================================================================
# if system.isInMaya():
#     from softwares.maya.libs import pySideMaya
#     IS_IN_MAYA = True
#     
#===============================================================================

class Main(QtWidgets.QDialog):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(Main, self).__init__(parent)
        self.ui = rigToolKit.Ui_riggingToolKit()
        self.ui.setupUi(self)
        self.core = rigToolKit_core.Core()

        self.initialize()
    
    def initialize(self): 

        self.resize(0,0)
        self.hide_tab(starting=True)
        self.ui.categorie_box.currentIndexChanged.connect(self.set_tab)

        #blendshapes.
        self.ui.curveBS_BScreate_button.clicked.connect(self.create_BS)
        self.ui.curveBS_add_button.clicked.connect(self.add_BS)
        self.ui.BSconnect_Connect_Button.clicked.connect(self.connect_BS_to_Ctrl)
        self.ui.BSconnect_AddCtrl_Button.clicked.connect(self.addCtrl_UI)
        self.ui.BSconnect_ClearCtrl_Button.clicked.connect(self.clearCtrl_UI)
        self.ui.BSconnect_AddBS_Button.clicked.connect(self.addBS_UI)
        self.ui.BSconnect_ClearBS_Button.clicked.connect(self.clearBS_UI)
        #Controllers.
        self.ui.createCtrl_button.clicked.connect(self.create_ctrl)
        self.ui.jntOnVert_create_button.clicked.connect(self.ctrlJoint_onVertex)
        self.ui.curveBS_createJnt_button.clicked.connect(self.creatCtrlOnCurve)
        #Curves.
        self.ui.convEdge_Button.clicked.connect(self.convertEdge)
        #Clean up.
        self.ui.connectMod_button.clicked.connect(self.connectMod)
        self.ui.colorCtrl_button.clicked.connect(self.colorCtrl)
        #Setup.
        self.ui.blendLoc_button.clicked.connect(self.blendLoc)
        self.ui.blendJnt_button.clicked.connect(self.blendJnt)
        self.ui.supportJnt_button.clicked.connect(self.supposrtJnt)
        self.ui.twistJnt_button.clicked.connect(self.twistJnt)

#===============================================================================
# Main.        
#===============================================================================
    def hide_tab(self, starting=False):
        if starting is False:
            self.ui.BS_frame.hide()
        self.ui.CTRL_frame.hide()
        self.ui.curve_frame.hide()
        self.ui.cleanUp_frame.hide()
        self.ui.setup_frame.hide()

    def set_tab(self):
        self.hide_tab()
        #Check current index.
        index = self.ui.categorie_box.currentIndex()

        #Show related tab.
        if index is 0:
            self.ui.BS_frame.show()
        if index is 1:
            self.ui.CTRL_frame.show()
        if index is 2:
            self.ui.curve_frame.show()
        if index is 3:
            self.ui.cleanUp_frame.show()
        if index is 4:
            self.ui.setup_frame.show()

# ===============================================================================
# Blendshapes.
# ===============================================================================
    def create_BS(self):
        shapes.create_BS_Node()

    def add_BS(self):
        BSname = self.ui.curveBS_BSname_lineEdit.text()
        shapes.add_new_BS(BSname)

    def addCtrl_UI(self):
        sel = mc.ls(sl=True)

        for i in sel:
            exist = self.ui.BSconnect_Ctrl_listWidget.findItems(str(i), QtCore.Qt.MatchExactly)
            if len(exist) > 0:
                pass
            else:
                self.ui.BSconnect_Ctrl_listWidget.addItem(i)

    def clearCtrl_UI(self):
        x = self.ui.BSconnect_Ctrl_listWidget.count()
        for i in range(0, x):
            self.ui.BSconnect_Ctrl_listWidget.clear()

    def addBS_UI(self):
        listAttr = shapes.getBSListAttr()
        for i in listAttr:
            self.ui.BSconnect_BS_listWidget.addItem(i)

    def clearBS_UI(self):
        x = self.ui.BSconnect_BS_listWidget.count()
        for i in range(0, x):
            self.ui.BSconnect_BS_listWidget.clear()

    def connect_BS_to_Ctrl(self):
        curItemCtrl = self.ui.BSconnect_Ctrl_listWidget.currentItem()
        itemCtrl = curItemCtrl.text()

        curItemBS = self.ui.BSconnect_BS_listWidget.currentItem()
        indexBS = self.ui.BSconnect_BS_listWidget.currentRow()

        BS = curItemBS.text()
        x = BS.split('_')
        itemBS = '{}{}.{}_{}'.format(x[0], 'BS', x[0], x[1])

        X = self.ui.BSconnect_CtrlAxisX_checkBox.isChecked()
        Y = self.ui.BSconnect_CtrlAxisY_checkBox.isChecked()
        Z = self.ui.BSconnect_CtrlAxisZ_checkBox.isChecked()
        axisList = [X, Y, Z]
        axisList2 = ['tx', 'ty', 'tz']

        for i in range(0, len(axisList)):
            if axisList[i] is True:
                axis = axisList2[i]

        clamp, minimum, maximum = self.getClampInfo()
        MD, value, operation = self.getMDInfos()

        self.core.connectBStoCtrl(itemCtrl, itemBS, indexBS, axis, clamp, minimum, maximum, MD, value, operation)

    def getClampInfo(self):
        clamp = self.ui.BSconnect_clamp_checkBox.isChecked()
        minimum = self.ui.BSconnect_MinClamp_lineEdit.text()
        maximum = self.ui.BSconnect_MaxClamp_lineEdit.text()

        return clamp, minimum, maximum

    def getMDInfos(self):
        MD = self.ui.BSconnect_MD_checkBox.isChecked()
        value = self.ui.BSconnect_MDvalue_lineEdit.text()
        mult = self.ui.BSconnect_MDmult_checkBox.isChecked()
        div = self.ui.BSconnect_MDdiv_checkBox.isChecked()
        power = self.ui.BSconnect_MDpow_checkBox.isChecked()
        operation = 0

        if mult is True:
            operation = 1
            if div is True:
                operation = 2
                if power is True:
                    operation = 3
        return MD, value, operation

# ===============================================================================
# Controllers.
# ===============================================================================
    def getSel_createCtrl(self):
        stateList = [self.ui.circle_button.isChecked(),
                     self.ui.sphere_button.isChecked(),
                     self.ui.square_button.isChecked(),
                     self.ui.cube_button.isChecked(),
                     self.ui.cylinder_button.isChecked(),
                     self.ui.diamond_button.isChecked(),
                     self.ui.root_button.isChecked(),
                     self.ui.pushButton_5.isChecked()]

        if stateList.count(True) > 1:
            self.ui.warningTextEdit.setText('! - ERROR : More than one type of controller shape is selected.')
        if stateList.count(True) == 0:
            self.ui.warningTextEdit.setText('! - ERROR : Select at least one type of controller shape.')
        if stateList.count(True) == 1:
            self.ui.warningTextEdit.clear()
            index = stateList.index(True)
        return index

    def create_ctrl(self):
        name = self.ui.createCtrl_lineEdit.text()
        if len(name) == 0:
            self.ui.warningTextEdit.setText('! - ERROR : A name is required.')
        else:
            self.ui.warningTextEdit.clear()
            index = self.getSel_createCtrl()
            #self.core.create_ctrl(index, baseName=name)
            shapes.shpDico[str(index)](name=name)

    def ctrlJoint_onVertex(self):
        text = self.ui.jntOnVert_jntName_lineEdit.text()
        ctrlType = self.getSel_createCtrl()
        # Set condition if createJoint is checked, return bool.
        createJnt = self.ui.addJoint_checkBox.isChecked()
        
        if self.ui.ws_checkBox.isChecked() is True:
            space = 'world'
        else:
            space = 'local'   
        # Set condition if mirror is checked, return bool.
        mirror = self.ui.mirrorX_checkBox.isChecked()

        self.core.create_CtrlJointOnVert(baseName=text, createJnt=createJnt, mirror=mirror, ctrlType=ctrlType, space=space)

    def creatCtrlOnCurve(self):
        if self.ui.curveBS_followCurve_checkBox.isChecked():
            follow = True
        else:
            follow = False

        numJnt = self.ui.curveBS_jntNum_spineBox.value()
        ctrlType = self.getSel_createCtrl()
        
        rigging.ctrlJnt_onCurve(numJnt, follow, ctrlType)

# ===============================================================================
# Curves.
# ===============================================================================
    def convertEdge(self):
        rigging.edgeToCurve()

# ===============================================================================
# CleanUp.
# ===============================================================================
    def connectMod(self):
        attributes.connectModelAndSkeleton()

    def colorCtrl(self):
        attributes.addControlColors()

# ===============================================================================
# Setup.
# ===============================================================================
    def blendLoc(self):
        rigging.makeRotateBlendLocator()

    def blendJnt(self):
        rigging.addBlendedJoint()

    def supposrtJnt(self):
        rigging.addSupportJoint()

    def twistJnt(self):
        rigging.makeTwistJoints()


#===============================================================================
# Show window.
#===============================================================================
        
def show():
    if IS_IN_MAYA:
        mayaWindows = pySideMaya.getMayaWindow()
        toto = Main(mayaWindows)
        toto.show()
    else:
        app = QtCore.QCoreApplication.instance()
        if app is None:
            ok = True
            app = QtWidgets.QApplication(sys.argv)
        else:
            ok = False

        parent = QtWidgets.QApplication.activeWindow()

        toto = Main(parent)
        toto.show()

        app = QtCore.QCoreApplication.instance()
        if ok:
            sys.exit(app.exec_())

if __name__ == "__main__":
    show()             