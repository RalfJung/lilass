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

import re, subprocess
from enum import Enum

## utility functions

# execute a process, return output as iterator, throw exception if there was an error
# you *must* iterate to the end if you use this!
def processOutputGen(*args):
    with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
        for line in p.stdout:
            yield line.decode("utf-8")
    if p.returncode != 0:
        raise Exception("Error executing "+str(args))
def processOutputIt(*args):
    return list(processOutputGen(*args)) # list() iterates over the generator

## the classes

class RelativeScreenPosition(Enum):
    '''Represents the relative position of the external screen to the internal one'''
    LEFT      = 0
    RIGHT     = 1
    ABOVE     = 2
    BELOW     = 3
    MIRROR    = 4


class Resolution:
    '''Represents a resolution of a screen'''
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def __eq__(self, other):
        if not isinstance(other, Resolution):
            return False
        return self.width == other.width and self.height == other.height
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        # get ratio
        ratio = int(round(16.0*self.height/self.width))
        if ratio == 12: # 16:12 = 4:3
            strRatio = '4:3'
        elif ratio == 13: # 16:12.8 = 5:4
            strRatio = '5:4'
        else: # let's just hope this will never be 14 or more...
            strRatio = '16:%d' % ratio
        return '%dx%d (%s)' %(self.width, self.height, strRatio)
    
    def __repr__(self):
        return 'screen.Resolution('+self.forXrandr()+')'
    
    def forXrandr(self):
        return str(self.width)+'x'+str(self.height)


class ScreenSetup:
    '''Represents a screen configuration (relative to some notion of an "internal" and an "external" screen): Which screens are enabled with which resolution, how
       are they positioned, which is the primary screen.'''
    def __init__(self, intResolution, extResolution, relPosition = None, extIsPrimary = True):
        '''The resolutions can be None to disable the screen, instances of Resolution. The last two arguments only matter if both screens are enabled.'''
        assert intResolution is None or isinstance(intResolution, Resolution)
        assert extResolution is None or isinstance(extResolution, Resolution)
        
        self.intResolution = intResolution
        self.extResolution = extResolution
        self.relPosition = relPosition
        self.extIsPrimary = extIsPrimary or self.intResolution is None # external is always primary if it is the only one
    
    def getInternalArgs(self):
        if self.intResolution is None:
            return ["--off"]
        args = ["--mode", self.intResolution.forXrandr()] # set internal screen to desired resolution
        if not self.extIsPrimary:
            args.append('--primary')
        return args
    
    def getExternalArgs(self, intName):
        if self.extResolution is None:
            return ["--off"]
        args = ["--mode", self.extResolution.forXrandr()] # set external screen to desired resolution
        if self.extIsPrimary:
            args.append('--primary')
        if self.intResolution is None:
            return args
        # set position
        args += [{
                RelativeScreenPosition.LEFT  : '--left-of',
                RelativeScreenPosition.RIGHT : '--right-of',
                RelativeScreenPosition.ABOVE : '--above',
                RelativeScreenPosition.BELOW : '--below',
                RelativeScreenPosition.MIRROR: '--same-as',
            }[self.relPosition], intName]
        return args


class ScreenSituation:
    connectors = {} # maps connector names to lists of Resolution (empty list -> disabled connector)
    internalConnector = None # name of the internal connector (will be an enabled one)
    externalConnector = None # name of the used external connector (an enabled one), or None
    
    '''Represents the "screen situation" a machine can be in: Which connectors exist, which resolutions do they have, what are the names for the internal and external screen'''
    def __init__(self, internalConnectorNames, externalConnectorNames = None):
        '''Both arguments are lists of connector names. The first one which exists and has a screen attached is chosen for that class. <externalConnectorNames> can be None to
           just choose any remaining connector.'''
        # which connectors are there?
        self._getXrandrInformation()
        print(self.connectors)
        # figure out which is the internal connector
        self.internalConnector = self._findAvailableConnector(internalConnectorNames)
        if self.internalConnector is None:
            raise Exception("Could not automatically find internal connector, please use ~/.dsl.conf to specify it manually.")
        print(self.internalConnector)
        # and the external one
        if externalConnectorNames is None:
            externalConnectorNames = list(self.connectors.keys())
            externalConnectorNames.remove(self.internalConnector)
        self.externalConnector = self._findAvailableConnector(externalConnectorNames)
        print(self.externalConnector)
    
    # Run xrandr and fill the dict of connector names mapped to lists of available resolutions.
    def _getXrandrInformation(self):
        connector = None # current connector
        for line in processOutputGen("xrandr", "-q"):
            # screen?
            m = re.search(r'^Screen [0-9]+: ', line)
            if m is not None: # ignore this line
                connector = None
                continue
            # new connector?
            m = re.search(r'^([\w\-]+) (dis)?connected ', line)
            if m is not None:
                connector = m.groups()[0]
                assert connector not in self.connectors
                self.connectors[connector] = []
                continue
            # new resolution?
            m = re.search(r'^   ([\d]+)x([\d]+) +', line)
            if m is not None:
                resolution = Resolution(int(m.groups()[0]), int(m.groups()[1]))
                assert connector is not None
                self.connectors[connector].append(resolution)
                continue
            # unknown line
            # not fatal, e.g. xrandr shows strange stuff when a display is enabled, but not connected
            print("Warning: Unknown xrandr line %s" % line)
    
    # return the first available connector from those listed in <tryConnectors>, skipping disabled connectors
    def _findAvailableConnector(self, tryConnectors):
        for connector in tryConnectors:
            if connector in self.connectors and len(self.connectors[connector]): # if the connector exists and is active (i.e. there is a resolution)
                return connector
        return None
    
    # return available internal resolutions
    def internalResolutions(self):
        return self.connectors[self.internalConnector]
    
    # return available external resolutions (or None, if there is no external screen connected)
    def externalResolutions(self):
        if self.externalConnector is None:
            return None
        return self.connectors[self.externalConnector]
    
    # return resolutions available for both internal and external screen
    def commonResolutions(self):
        internalRes = self.internalResolutions()
        externalRes = self.externalResolutions()
        assert externalRes is not None
        return [res for res in externalRes if res in internalRes]
    
    # compute the xrandr call
    def forXrandr(self, setup):
        # turn all screens off
        connectorArgs = {} # maps connector names to xrand arguments
        for c in self.connectors.keys():
            connectorArgs[c] = ["--off"]
        # set arguments for the relevant ones
        connectorArgs[self.internalConnector] = setup.getInternalArgs()
        if self.externalConnector is not None:
            connectorArgs[self.externalConnector] = setup.getExternalArgs(self.internalConnector)
        else:
            assert setup.extResolution is None, "There's no external screen to set a resolution for"
        # now compose the arguments
        call = ["xrandr"]
        for name in connectorArgs:
            call += ["--output", name] + connectorArgs[name]
        return call

