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
# along with this program (gpl.txt); if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# This file bstracts GUI stuff away, so that the actual dsl.py does not have to deal with it
import sys
from PyQt4 import QtGui
from qt_dialogue import PositionSelection
app = QtGui.QApplication(sys.argv)

def error(message):
	'''Displays a fatal error to the user'''
	QtGui.QMessageBox.critical(None, 'Fatal error', message)

def getDialogue(internalResolutions, externalResolutions):
	'''Returns a class implementing a function run() which returns a ScreenSetup instance, or None if the user canceled'''
	return PositionSelection(internalResolutions, externalResolutions)
