# DSL - easy Display Setup for Laptops
# Copyright (C) 2012-2015 Ralf Jung <post@ralfj.de>
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
import sys, os
from screen import RelativeScreenPosition, ScreenSetup

try:
    # Be fine with PyQt4 not being installed
    from PyQt5 import QtCore, QtWidgets, uic

    class PositionSelection(QtWidgets.QDialog):
        def __init__(self, situation):
            # set up main window
            super(PositionSelection, self).__init__()
            self._situation = situation
            uifile = os.path.join(os.path.dirname(__file__), 'qt_dialogue.ui')
            uic.loadUi(uifile, self)
            
            # fill relative position box
            for pos in RelativeScreenPosition:
                self.relPos.addItem(pos.text, pos)
            
            # keep resolutions in sync when in mirror mode
            def syncIfMirror(source, target):
                def _slot(idx):
                    if self.isMirror:
                        target.setCurrentIndex(idx)
                source.currentIndexChanged.connect(_slot)
            syncIfMirror(self.intRes, self.extRes)
            syncIfMirror(self.extRes, self.intRes)

            # connect the update function, and make sure we are in a correct state
            self.intEnabled.toggled.connect(self.updateEnabledControls)
            self.extEnabled.toggled.connect(self.updateEnabledControls)
            self.relPos.currentIndexChanged.connect(self.updateEnabledControls)
            self.updateEnabledControls()
        
        def getRelativeScreenPosition(self):
            idx = self.relPos.currentIndex()
            return self.relPos.itemData(idx)
        
        def fillResolutionBox(self, box, resolutions):
            # if the count did not change, update in-place (this avoids flicker)
            if box.count() == len(resolutions):
                for idx, res in enumerate(resolutions):
                    box.setItemText(idx, str(res))
                    box.setItemData(idx, res)
            else:
                # first clear it
                while box.count() > 0:
                    box.removeItem(0)
                # then fill it
                for res in resolutions:
                    box.addItem(str(res), res)
        
        def updateEnabledControls(self):
            intEnabled = self.intEnabled.isChecked()
            extEnabled = self.extEnabled.isChecked()
            bothEnabled = intEnabled and extEnabled
            self.isMirror = bothEnabled and self.getRelativeScreenPosition() == RelativeScreenPosition.MIRROR # only if both are enabled, we can really mirror
            # configure screen controls
            self.intRes.setEnabled(intEnabled)
            self.intPrimary.setEnabled(intEnabled and not self.isMirror)
            self.extRes.setEnabled(extEnabled)
            self.extPrimary.setEnabled(extEnabled and not self.isMirror)
            if not intEnabled and extEnabled:
                self.extPrimary.setChecked(True)
            elif not extEnabled and intEnabled:
                self.intPrimary.setChecked(True)
            # which resolutions do we offer?
            if self.isMirror:
                commonRes = self._situation.commonResolutions()
                self.fillResolutionBox(self.intRes, commonRes)
                self.fillResolutionBox(self.extRes, commonRes)
                self.intRes.setCurrentIndex(self.extRes.currentIndex())
            else:
                self.fillResolutionBox(self.intRes, self._situation.internalResolutions())
                self.fillResolutionBox(self.extRes, self._situation.externalResolutions())
            # configure position control
            self.posGroup.setEnabled(bothEnabled)
            self.posLabel1.setEnabled(bothEnabled)
            self.posLabel2.setEnabled(bothEnabled)
            self.relPos.setEnabled(bothEnabled)
            # avoid having no screen
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(intEnabled or extEnabled)
        
        def run(self):
            self.exec_()
            if not self.result(): return None
            intRes = self.intRes.itemData(self.intRes.currentIndex()) if self.intEnabled.isChecked() else None
            extRes = self.extRes.itemData(self.extRes.currentIndex()) if self.extEnabled.isChecked() else None
            return ScreenSetup(intRes, extRes, self.getRelativeScreenPosition(), self.extPrimary.isChecked())
except ImportError:
    pass

# Qt frontend
class QtFrontend:
    def __init__(self):
        from PyQt5 import QtWidgets
        self.app = QtWidgets.QApplication(sys.argv)
        print("Qt loaded")
    
    def error(self, message):
        from PyQt5 import QtWidgets
        QtWidgets.QMessageBox.critical(None, 'Fatal error', message)
    
    def setup(self, situation):
        return PositionSelection(situation).run()
    
    @staticmethod
    def isAvailable():
        try:
            import PyQt5
            return True
        except ImportError:
            return False

