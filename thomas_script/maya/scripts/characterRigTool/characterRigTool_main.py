'''
Created on Jan 10, 2022

@author: thomas
'''
import sys
import maya.cmds as mc
import pymel.core as pm
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from thomas_script.maya.utils import pySideMaya

from thomas_script.maya.scripts.characterRigTool import characterRigTool
from thomas_script.maya.scripts.characterRigTool import characterRigTool_core
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

#ITEM_LIST = ['spine_hybrid', 'neck/head_fk', 'shoulder_fk', 'arm', 'hand', 'leg', 'foot']

ITEM_DICO = { '--Biped--': ['Simple Biped Rig', 'spine_hybrid', 'neck/head_fk', 'shoulder_fk', 'arm', 'hand', 'leg', 'foot'], 
             '--Quadruped--': ['frontLeg', 'BackLeg'], 
             '--Other--': ['Ribbon'],
             }


class Main(QtWidgets.QDialog):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(Main, self).__init__(parent)
        self.ui = characterRigTool.Ui_CharacterRigTool()
        self.ui.setupUi(self)
        self.guide = characterRigTool_core.Guide()
        self.rig = characterRigTool_core.Rig()
        self.initialize()
    
    def initialize(self):  
        self.resize(0,0)
        
        #Set visibility UI.
        self.ui.option_box.setHidden(True)
        
        #Set UI items.
        categories = ITEM_DICO.keys()
        categories.reverse()
        for c in categories:
            self.ui.listWidget.addItem(c)
            self.ui.listWidget.addItems(ITEM_DICO[c])

        #Set behavior.
        self.ui.listWidget.currentItemChanged.connect(self.setOptions)
        self.ui.draw_button.clicked.connect(self.drawGuide)
        self.ui.update_button.clicked.connect(self.updateGuide)
        self.ui.mirror_button.clicked.connect(self.mirrorGuide)
        self.ui.skeleton_button.clicked.connect(self.skeleton)
        self.ui.rig_button.clicked.connect(self.createRig)
        
        self.ui.RTB_button.clicked.connect(self.showRTB)
        self.ui.matConstr_button.clicked.connect(self.matrixConstraint)
        return

#===============================================================================
# Main.        
#===============================================================================
    ###
    # CHARACTER TAB.

    def setOptions(self):
        item = self.ui.listWidget.currentItem().text()
        if '--' in item:
            self.ui.option_box.setHidden(True)
        else:
            self.ui.option_box.setVisible(True)
        
        if 'Biped' in item:
            self.ui.section_count_spinBox.setVisible(False)
            self.ui.section_count_label.setVisible(False)
        else:
            self.ui.section_count_spinBox.setVisible(True)
            self.ui.section_count_label.setVisible(True)   
                   
        if 'spine' in item:
            self.ui.section_count_spinBox.setValue(4)
            self.ui.section_count_spinBox.setReadOnly(False)
        if 'head' in item:
            self.ui.section_count_spinBox.setValue(2)
            self.ui.section_count_spinBox.setReadOnly(False)
        if 'shoulder' in item:
            self.ui.section_count_spinBox.setValue(1)
            self.ui.section_count_spinBox.setReadOnly(True)
        if 'arm' in item or 'leg' in item:
            self.ui.section_count_spinBox.setValue(2)
            self.ui.section_count_spinBox.setReadOnly(True)
        if 'hand' in item:
            self.ui.section_count_spinBox.setValue(1)
            self.ui.section_count_spinBox.setReadOnly(True)      
        if 'foot' in item:
            self.ui.section_count_spinBox.setValue(3)
            self.ui.section_count_spinBox.setReadOnly(True)   
        if 'BackLeg' in item:
            self.ui.section_count_spinBox.setValue(4)
            self.ui.section_count_spinBox.setReadOnly(True) 
                                  
    def drawGuide(self):
        #Get current item selected.
        item = self.ui.listWidget.currentItem().text()
        
        name = item.split('_')
        name = name[0]
        print name
        #Get variables from UI.
        partNb = self.ui.section_count_spinBox.value()
        print partNb
        #Run command.
        if 'Biped' in item:
            self.guide.createBiped()
        else:
            self.guide.createGuide(name, partNb)

        return
    
    def updateGuide(self):
        item = self.ui.listWidget.currentItem().text()
        if 'spine' in item :
            mc.delete('spine_root_ref')
        if 'head' in item :
            mc.delete('neck_root_ref')
            
        self.drawGuide()
        return
    
    def mirrorGuide(self):
        #Get current item selected.
        item = self.ui.listWidget.currentItem().text()
        name = item.split('_')
        name = name[0]
        
        #Get variables from UI.
        partNb = self.ui.section_count_spinBox.value()
        
        #Run command.
        self.guide.mirrorGuide(name, partNb)
        return
    
    def skeleton(self):
        start = time.time()
        
        if mc.objExists('local_ctrl') is False:
            raise "No rig created"
        else:
            localGrp = 'local_ctrl'

        elems = mc.listRelatives(localGrp, c=True, typ='transform')
        
        self.rig.createSkeleton(elems)
        
        end = time.time()
        diff = end - start
        print 'Skeleton Completed: {0} {1}'.format(diff, 'seconds')
        return
    
    def createRig(self):
        start = time.time()
        
        self.getSettings()
        
        if mc.objExists('guide') is False:
            raise "No guide created"
        else:
            guideGrp = 'guide'
        elems = mc.listRelatives(guideGrp, c=True) 
        self.rig.createRig(elems)
        
        end = time.time()
        diff = end - start
        print 'Rig Completed: {0} {1}'.format(diff, 'seconds')
        
        return
    
    def getSettings(self):    
        #Get infos from option tab.
        settings =[]
        #qLabelsOption = self.ui.tabWidget.findChildren(QtWidgets.QLabel)
        qStringsOption = self.ui.tabWidget.findChildren(QtWidgets.QLineEdit)[0:-1]
        qColorsOption = self.ui.tabWidget.findChildren(QtWidgets.QComboBox)
        
        [settings.append(str(input.text())) for input in qStringsOption]
        [settings.append(str(input.currentText())) for input in qColorsOption]
        
        [characterRigTool_core.SETTINGS.append(item) for item in settings]

    ###
    # TOOLS TAB.

    def showRTB(self):
        from thomas_script.maya.scripts.rigToolKit import rigToolKit
        from thomas_script.maya.scripts.rigToolKit import rigToolKit_core
        from thomas_script.maya.scripts.rigToolKit import rigToolKit_main
        reload(rigToolKit)
        reload(rigToolKit_core)
        reload(rigToolKit_main)
        rigToolKit_main.show()
    
    def matrixConstraint(self):
        from thomas_script.maya.utils import matrix
        reload(matrix)
        matrix.showWindow()
        return
        
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