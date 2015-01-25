# DSL - easy Display Setup for Laptops
# Copyright (C) 2012 Ralf Jung <post@ralfj.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
from dsl import RelativeScreenPosition, ScreenSetup, res2user
from PyQt4 import QtCore, QtGui

def makeLayout(layout, members):
    for m in members:
        if isinstance(m, QtGui.QLayout):
            layout.addLayout(m)
        else:
            layout.addWidget(m)
    return layout

class PositionSelection(QtGui.QDialog):
    def __init__(self, internalResolutions, externalResolutions, commonResolutions):
        # set up main window
        super(PositionSelection, self).__init__()
        self.setWindowTitle('DSL - easy Display Setup for Laptops')
        
        ## position selection
        posBox = QtGui.QGroupBox('Position of external screen', self)
        self.posLeft = QtGui.QRadioButton('Left of internal screen', posBox)
        self.posRight = QtGui.QRadioButton('Right of internal screen', posBox)
        self.posRight.setChecked(True)
        self.posRight.setFocus()
        self.extOnly = QtGui.QRadioButton('Use external screen exclusively', posBox)
        self.mirror = QtGui.QRadioButton('Mirror internal screen', posBox)
        positions = [self.posLeft, self.posRight, self.extOnly, self.mirror]
        posBox.setLayout(makeLayout(QtGui.QVBoxLayout(), positions))
        for pos in positions:
            pos.toggled.connect(self.updateForm)
        
        ## primary screen
        self.primBox = QtGui.QGroupBox('Which should be the primary screen?', self)
        self.primExt = QtGui.QRadioButton('The external screen', self.primBox)
        self.primInt = QtGui.QRadioButton('The internal screen', self.primBox)
        self.primInt.setChecked(True)
        self.primBox.setLayout(makeLayout(QtGui.QVBoxLayout(), [self.primExt, self.primInt]))
        
        ## resolution selection
        resBox = QtGui.QGroupBox('Screen resolutions', self)
        # external screen
        self.extResLabel = QtGui.QLabel('Resolution of external screen:', resBox)
        self.extResolutions = externalResolutions
        self.extResolutionsBox = QtGui.QComboBox(resBox)
        for res in externalResolutions:
            self.extResolutionsBox.addItem(res2user(res))
        self.extResolutionsBox.setCurrentIndex(0) # select first resolution
        self.extRow = makeLayout(QtGui.QHBoxLayout(), [self.extResLabel, self.extResolutionsBox])
        # internal screen
        self.intResLabel = QtGui.QLabel('Resolution of internal screen:', resBox)
        self.intResolutions = internalResolutions
        self.intResolutionsBox = QtGui.QComboBox(resBox)
        for res in internalResolutions:
            self.intResolutionsBox.addItem(res2user(res))
        self.intResolutionsBox.setCurrentIndex(0) # select first resolution
        self.intRow = makeLayout(QtGui.QHBoxLayout(), [self.intResLabel, self.intResolutionsBox])
        # both screens
        self.mirrorResLabel = QtGui.QLabel('Resolution of both screens:', resBox)
        self.mirrorResolutions = commonResolutions
        self.mirrorResolutionsBox = QtGui.QComboBox(resBox)
        for res in commonResolutions:
            self.mirrorResolutionsBox.addItem(res2user(res))
        self.mirrorResolutionsBox.setCurrentIndex(0) # select first resolution
        self.mirrorRow = makeLayout(QtGui.QHBoxLayout(), [self.mirrorResLabel, self.mirrorResolutionsBox])
        # show them all
        resBox.setLayout(makeLayout(QtGui.QVBoxLayout(), [self.extRow, self.intRow, self.mirrorRow]))
        
        # last row: buttons
        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # add them all to the window
        self.setLayout(makeLayout(QtGui.QVBoxLayout(), [posBox, self.primBox, resBox, buttons]))
        
        # make sure we are consistent
        self.updateForm()
    
    def updateForm(self):
        self.primBox.setEnabled(self.posLeft.isChecked() or self.posRight.isChecked())
        self.extResolutionsBox.setEnabled(not self.mirror.isChecked())
        self.extResLabel.setEnabled(not self.mirror.isChecked())
        self.intResolutionsBox.setEnabled(self.posLeft.isChecked() or self.posRight.isChecked())
        self.intResLabel.setEnabled(self.posLeft.isChecked() or self.posRight.isChecked())
        self.mirrorResolutionsBox.setEnabled(self.mirror.isChecked())
        self.mirrorResLabel.setEnabled(self.mirror.isChecked())
    
    def run(self):
        self.exec_()
        if not self.result(): return None
        if self.mirror.isChecked():
            return ScreenSetup(RelativeScreenPosition.MIRROR,
                self.mirrorResolutions[self.mirrorResolutionsBox.currentIndex()],
                self.mirrorResolutions[self.mirrorResolutionsBox.currentIndex()],
                extIsPrimary = True)
        else:
            return ScreenSetup(self.getRelativeScreenPosition(),
                self.intResolutions[self.intResolutionsBox.currentIndex()],
                self.extResolutions[self.extResolutionsBox.currentIndex()],
                self.primExt.isChecked())
    
    def getRelativeScreenPosition(self):
        if self.posLeft.isChecked():
            return RelativeScreenPosition.LEFT
        elif self.posRight.isChecked():
            return RelativeScreenPosition.RIGHT
        elif self.extOnly.isChecked():
            return RelativeScreenPosition.EXTERNAL_ONLY
        else:
            raise Exception("Nothing is checked?")
