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
import subprocess, collections

# Qt frontend
class QtFrontend:
    def __init__(self):
        from PyQt4 import QtGui
        self.app = QtGui.QApplication(sys.argv)
        print("Qt loaded")
    
    def error(self, message):
        from PyQt4 import QtGui
        QtGui.QMessageBox.critical(None, 'Fatal error', message)
    
    def setup(self, internalResolutions, externalResolutions, commonRes):
        from qt_dialogue import PositionSelection
        return PositionSelection(internalResolutions, externalResolutions, commonRes).run()
    
    @staticmethod
    def isAvailable():
        try:
            import PyQt4
            return True
        except ImportError:
            return False


# Zenity frontend
class ZenityFrontend:
    def error(message):
        '''Displays a fatal error to the user'''
        subprocess.check_call(["zenity", "--error", "--text="+message])
    
    def setup(self, internalResolutions, externalResolutions, commonRes):
        from zenity_dialogue import run
        return run(internalResolutions, externalResolutions)
    
    @staticmethod
    def isAvailable():
        try:
            from dsl import processOutputIt
            processOutputIt("zenity", "--version")
            return True
        except Exception:
            return False


# CLI frontend
class CLIFrontend:
    def error(self, message):
        print(message, file=sys.stderr)
    
    def setup(self, internalResolutions, externalResolutions, commonRes):
        raise Exception("Choosing the setup interactively is not supported with the CLI frontend")
    
    @staticmethod
    def isAvailable():
        return True

# list of available frontends
frontends = collections.OrderedDict()
frontends["qt"] = QtFrontend
frontends["zenity"] = ZenityFrontend
frontends["cli"] = CLIFrontend

# get a frontend
def getFrontend(name = None):
    # by name
    if name is not None:
        if name in frontends:
            if frontends[name].isAvailable():
                return frontends[name]() # call constructor
        # frontend not found or not available
        raise Exception("Frontend %s not found or not available" % name)
    # auto-detect
    for frontend in frontends.values():
        if frontend.isAvailable():
            return frontend() # call constructor
    raise Exception("No frontend is available - this should not happen")
