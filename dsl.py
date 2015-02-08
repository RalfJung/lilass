#!/usr/bin/python3
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

import argparse, sys, os, re, subprocess
from enum import Enum
import gui, screen
frontend = gui.getFrontend("cli") # the fallback, until we got a proper frontend. This is guaranteed to be available.

# for auto-config: common names of internal connectors
commonInternalConnectorPrefixes = ['LVDS', 'eDP']
commonInternalConnectorSuffices = ['', '0', '1', '-0', '-1']
def commonInternalConnectorNames():
    for prefix in commonInternalConnectorPrefixes:
        for suffix in commonInternalConnectorSuffices:
            yield prefix+suffix


# Load a section-less config file: maps parameter names to space-separated lists of strings (with shell quotation)
def loadConfigFile(filename):
    import shlex
    result = {}
    if not os.path.exists(filename):
        return result # no config file
    # read config file
    linenr = 0
    with open(filename) as f:
        for line in f:
            linenr += 1
            line = line.strip()
            if not len(line) or line.startswith("#"): continue # skip empty and comment lines
            try:
                # parse line
                pos = line.index("=") # will raise exception when substring is not found
                curKey = line[:pos].strip()
                result[curKey] = shlex.split(line[pos+1:]) # shlex.split also strips
            except Exception:
                raise Exception("Invalid config, line %d: Error parsing line (may be a quoting issue)." % linenr)
    # add some convencience get functions
    return result


# Make sure the backlight is turned on
def turnOnBacklight():
    try:
        backlight = float(subprocess.check_output(["xbacklight", "-get"]).strip())
        if backlight == 0: # it's completely turned off, we better enable it
            subprocess.check_call(["xbacklight", "-set", "100"])
    except FileNotFoundError:
        print("xbacklight has not been found, unable to turn your laptop backlight on.")
    except subprocess.CalledProcessError:
        print("xbacklight returned an error while attempting to turn your laptop backlight on.")


# if we run top-level
if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser(description='easy Display Setup for Laptops')
    parser.add_argument("-f", "--frontend",
                        dest="frontend",
                        help="The frontend to be used for user interaction")
    parser.add_argument("-r", "--relative-position",
                        dest="rel_position", choices=list(map(str.lower, screen.RelativeScreenPosition.__members__.keys())),
                        help="Position of external screen relative to internal one")
    parser.add_argument("-i", "--internal-only",
                        dest="internal_only", action='store_true',
                        help="Enable internal screen, disable all the others (as if no external screen was connected")
    cmdArgs = parser.parse_args()
    
    # load frontend early (for error mssages)
    frontend = gui.getFrontend(cmdArgs.frontend)
    try:
        # see what situation we are in
        situation = screen.ScreenSituation(commonInternalConnectorNames())
        
        # construct the ScreenSetup
        setup = None
        if situation.externalResolutions() is not None:
            setup = frontend.setup(situation)
            if setup is None: sys.exit(1) # the user canceled
        else:
            # use first resolution of internal connector
            setup = ScreenSetup(intResolution = situation.internalResolutions()[0], extResolution = None)
        
        # call xrandr
        xrandrCall = situation.forXrandr(setup)
        print("Call that will be made:",xrandrCall)
        subprocess.check_call(xrandrCall)
        
        # make sure the internal screen is really, *really* turned on if there is no external screen
        if setup.extResolution is None:
            turnOnBacklight()
    except Exception as e:
        frontend.error(str(e))
        raise
