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

from question_frontend import QuestionFrontend
from screen import processOutputIt

# Qt frontend
class QtFrontend:
    def __init__(self):
        from PyQt4 import QtGui
        self.app = QtGui.QApplication(sys.argv)
        print("Qt loaded")
    
    def error(self, message):
        from PyQt4 import QtGui
        QtGui.QMessageBox.critical(None, 'Fatal error', message)
    
    def setup(self, situation):
        from qt_dialogue import PositionSelection
        return PositionSelection(situation).run()
    
    @staticmethod
    def isAvailable():
        try:
            import PyQt4
            return True
        except ImportError:
            return False


# Zenity frontend
class ZenityFrontend(QuestionFrontend):
    def error(self, message):
        '''Displays a fatal error to the user'''
        subprocess.check_call(["zenity", "--error", "--text="+message])
    def userChoose (self, title, choices, returns, fallback):
        assert len(choices) == len(returns)
        args = ["zenity", "--list", "--text="+title, "--column="]+choices
        switch = dict (list(zip (choices,returns)))
        try:
            for line in processOutputIt(*args):
                return switch.get(line.strip(), fallback)
        except Exception:
            # on user cancel, the return code of zenity is nonzero
            return fallback
        # if the output was empty
        return fallback
    def isAvailable():
        try:
            processOutputIt("zenity", "--version")
            return True
        except FileNotFoundError:
            return False
        except PermissionError:
            return False

# CLI frontend
class CLIFrontend(QuestionFrontend):
    def error(self, message):
        print(message, file=sys.stderr)

    def userChoose (self, title, choices, returns, fallback):
        while True:
            # print question
            print(title)
            for i in range(len(choices)):
                print("%d. %s"%(i,choices[i]))
            print("Enter 'c' to cancel.")
            # handle input
            answer = input("> ")
            if answer == "c":
                return None
            #else
            try:
                answerint = int(answer)
                if answerint >= 0 and answerint < len(choices):
                    return returns[answerint]
            except ValueError:
                pass
            # if we are here something invalid was entered
            print("INVALID ANSWER: '%s'" % answer)

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
            else:
                raise Exception("Frontend %s not available" % name)
        # frontend not found
        raise Exception("Frontend %s not found" % name)
    # auto-detect
    for frontend in frontends.values():
        if frontend.isAvailable():
            return frontend() # call constructor
    raise Exception("No frontend is available - this should not happen")
