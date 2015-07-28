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

'''
This module implements two functions:

def error(message):
    This function displays the error message to the user in some appropriate fassion

def setup(internalResolutions, externalResolutions):
    Both arguments are lists of (width, height) tuples of resolutions. You can use dsl.res2user to obtain a user-readable representation of a resolution tuple.
    The user should be asked about his display setup preferences.
    The function returns None if the user cancelled, and an instance of dsl.ScreenSetup otherwise.
'''
import collections

from qt_frontend import QtFrontend
from cli_frontend import CLIFrontend
from zenity_frontend import ZenityFrontend


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
