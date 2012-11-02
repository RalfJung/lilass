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

'''
This module implements two functions:

def error(message):
	This function displays the error message to the user in some appropriate fassion

def setup(internalResolutions, externalResolutions):
	Both arguments are lists of (width, height) tuples of resolutions. You can use dsl.res2user to obtain a user-readable representation of a resolution tuple.
	The user should be asked about his display setup preferences.
	The function returns None if the user cancelled, and an instance of dsl.ScreenSetup otherwise.
'''

# frontend detectors
def qtAvailable():
	try:
		import PyQt4
		return True
	except ImportError:
		return False

def zenityAvailable():
	try:
		from dsl import processOutputIt
		processOutputIt("zenity", "--version")
		return True
	except Exception:
		return False

# actual frontends
if qtAvailable():
	from PyQt4 import QtGui
	from qt_dialogue import PositionSelection
	app = QtGui.QApplication(sys.argv)
	
	def error(message):
		QtGui.QMessageBox.critical(None, 'Fatal error', message)
	
	def setup(internalResolutions, externalResolutions):
		return PositionSelection(internalResolutions, externalResolutions).run()

elif zenityAvailable():
	import subprocess
	from zenity_dialogue import run as setup # this provides the setup function
	
	def error(message):
		'''Displays a fatal error to the user'''
		subprocess.check_call(["zenity", "--error", "--text="+message])

else:
	print >> sys.stderr, 'No GUI frontend available, please make sure PyQt4 or Zenity is installed'
