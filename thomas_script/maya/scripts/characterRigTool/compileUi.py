'''
Compiles *.ui and *.qrc files in the directory that this script is in.
Compiles using PySide2 then replaces the PySide2 imports with Qt.py imports for 
backwards compatability.
If you don't have PySide2, you can add PySide2 to your PYTHONPATH from an 
application that comes with it such as Maya 2017 or greater. 
'''

import os
import io
import glob
import subprocess

import pysideuic

def main():
    uiDir = os.path.dirname(__file__)
    pysideuic.compileUiDir(uiDir)
    
    uiGlob = os.path.join(uiDir, '*.ui')
    for uiPath in glob.iglob(uiGlob):
        compiledPath = os.path.splitext(uiPath)[0] + '.py'
        
        with io.open(compiledPath, 'r', encoding='utf8') as f:
            text = f.read()
        
        text = text.replace(u'from PySide2 import', u'import Qt\nfrom Qt import')
        text = text.replace(u'from PySide import', u'import Qt\nfrom Qt import')
        text = text.replace(u'QtWidgets.QApplication.translate', u'Qt.QtCompat.translate')
        
        with io.open(compiledPath, 'w', encoding='utf8') as f:
            f.write(text)
    
    qtResourceGlob = os.path.join(uiDir, '*.qrc')
    for path in glob.iglob(qtResourceGlob):
        fileNameIn = os.path.basename(path)
        fileNameOut = os.path.splitext(fileNameIn)[0]
        fileNameOut = '{0}_rc.py'.format(fileNameOut)
        args = ['pyside-rcc', '-o', fileNameOut, fileNameIn]
        proc = subprocess.Popen(args, cwd=uiDir)
        proc.wait()
        
        with io.open(fileNameOut, 'r', encoding='utf8') as f:
            text = f.read()
        
        text = text.replace(u'PySide2', u'Qt')
        text = text.replace(u'PySide', u'Qt')
        
        with io.open(fileNameOut, 'w', encoding='utf8') as f:
            f.write(text)
        
    print 'UI compiled! Success!'

if __name__ == '__main__':
    main()
