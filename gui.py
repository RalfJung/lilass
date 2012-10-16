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

# This file abstracts GUI stuff away, so that the actual dsl.py does not have to deal with it
import sys

qt_available = True
try:
	from PyQt4 import QtGui
	from qt_dialogue import PositionSelection
	app = QtGui.QApplication(sys.argv)
except Exception, e:
	import subprocess
	from zenity_dialogue import run as zenity_run
	qt_available = False

def error(message):
	'''Displays a fatal error to the user'''
	if qt_available:
		QtGui.QMessageBox.critical(None, 'Fatal error', message)
	else:
		subprocess.Popen(["zenity", "--error", "--text="+message], stdout=subprocess.PIPE)

def setup(internalResolutions, externalResolutions):
	'''Returns a ScreenSetup instance, or None if the user canceled'''
	if qt_available:
		return PositionSelection(internalResolutions, externalResolutions).run()
	else:
		return zenity_run(internalResolutions, externalResolutions)
