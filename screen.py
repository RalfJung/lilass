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

# for auto-config: common names of internal connectors
def commonInternalConnectorNames():
    commonInternalConnectorPrefixes = ['LVDS', 'eDP']
    commonInternalConnectorSuffices = ['', '0', '1', '-0', '-1']
    for prefix in commonInternalConnectorPrefixes:
        for suffix in commonInternalConnectorSuffices:
            yield prefix+suffix

## the classes

class RelativeScreenPosition(Enum):
    '''Represents the relative position of the external screen to the internal one'''
    LEFT      = ("left of")
    RIGHT     = ("right of")
    ABOVE     = ("above")
    BELOW     = ("below")
    MIRROR    = ("same as")
    def __init__(self, text):
        # auto numbering
        cls = self.__class__
        self._value_ = len(cls.__members__) + 1
        self.text = text
    def __str__(self):
        return self.text

class Resolution:
    '''Represents a resolution of a screen'''
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    @classmethod
    def fromDatabase(cls, dbstr):
        if dbstr is None:
            return None
        parts = dbstr.split("x")
        if len(parts) != 2:
            raise ValueError(xrandrstr)
        return Resolution(*map(int,parts))
    
    def forDatabase(self):
        return str(self.width)+'x'+str(self.height)
    
    def forXrandr(self):
        return self.forDatabase()
    
    def toTuple(self):
        return (self.width, self.height)
    
    def __eq__(self, other):
        if not isinstance(other, Resolution):
            return False
        return self.width == other.width and self.height == other.height
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(("Resolution",self.width,self.height))
    
    def __str__(self):
        # get ratio
        ratio = int(round(16.0*self.height/self.width))
        if ratio == 11: # 16:10.66 = 3:2
            strRatio = "3:2"
        elif ratio == 12: # 16:12 = 4:3
            strRatio = '4:3'
        elif ratio == 13: # 16:12.8 = 5:4
            strRatio = '5:4'
        else: # let's just hope this will never be 14 or more...
            strRatio = '16:%d' % ratio
        return '%dx%d (%s)' %(self.width, self.height, strRatio)
    
    def __repr__(self):
        return 'screen.Resolution('+self.forXrandr()+')'
    
    def pixelCount(self):
        return self.width * self.height


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
    
    def __str__(self):
        if self.intResolution is None:
            return "External display only, at "+str(self.extResolution)
        if self.extResolution is None:
            return "Internal display only, at "+str(self.intResolution)
        return "External display %s at %s %s internal display %s at %s" % ("(primary)" if self.extIsPrimary else "", str(self.extResolution), str(self.relPosition), "" if self.extIsPrimary else "(primary)", str(self.intResolution))

class Connector:
    def __init__(self, name=None):
        self.name = name # connector name, e.g. "HDMI1"
        self.edid = None # EDID string for the connector, or None if disconnected / unavailable
        self._resolutions = set() # set of Resolution objects, empty if disconnected
        self._preferredResolution = None
        self.previousResolution = None
        self.hasLastResolution = False
    
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return """<Connector "%s" EDID="%s" resolutions="%s">""" % (str(self.name), str(self.edid), ", ".join(str(r) for r in self.getResolutionList()))
    
    def isConnected(self):
        # It is very possible not to have an EDID even for a connected connector
        return len(self._resolutions) > 0
    
    def addResolution(self, resolution):
        assert isinstance(resolution, Resolution)
        self._resolutions.add(resolution)
    
    def appendToEdid(self, s):
        if self.edid is None:
            self.edid = s
        else:
            self.edid += s
    
    def setPreferredResolution(self, resolution):
        assert isinstance(resolution, Resolution) and resolution in self._resolutions
        self._preferredResolution = resolution
    
    def getPreferredResolution(self):
        if self._preferredResolution is not None:
            return self._preferredResolution
        return self.getResolutionList()[0] # prefer the largest resolution
    
    def getResolutionList(self):
        return sorted(self._resolutions, key=lambda r: -r.pixelCount())

class ScreenSituation:
    connectors = None # contains all the Connector objects
    internalConnector = None # the internal Connector object (will be an enabled one)
    externalConnector = None # the used external Connector object (an enabled one), or None
    previousSetup = None # None or the ScreenSetup used the last time this external screen was connected
    
    '''Represents the "screen situation" a machine can be in: Which connectors exist, which resolutions do they have, what are the names for the internal and external screen'''
    def __init__(self, internalConnectorNames, externalConnectorNames = None, xrandrSource = None):
        '''Both arguments are lists of connector names. The first one which exists and has a screen attached is chosen for that class. <externalConnectorNames> can be None to
           just choose any remaining connector.'''
        # which connectors are there?
        self.connectors = []
        self._getXrandrInformation(xrandrSource)
        # figure out which is the internal connector
        self.internalConnector = self._findAvailableConnector(internalConnectorNames)
        if self.internalConnector is None:
            raise Exception("Could not automatically find internal connector, please use (or fix) ~/.dsl.conf to specify it manually.")
        print("Detected internal connector:",self.internalConnector)
        # and the external one
        if externalConnectorNames is None:
            externalConnectorNames = map(lambda c: c.name, self.connectors)
            externalConnectorNames = set(filter(lambda name: name != self.internalConnector.name, externalConnectorNames))
        self.externalConnector = self._findAvailableConnector(externalConnectorNames)
        if self.internalConnector == self.externalConnector:
            raise Exception("Internal and external connector are the same. This must not happen. Please fix ~/.dsl.conf.");
        print("Detected external connector:",self.externalConnector)
    
    # Run xrandr and fill the dict of connector names mapped to lists of available resolutions.
    def _getXrandrInformation(self, xrandrSource = None):
        connector = None # current connector
        readingEdid = False
        if xrandrSource is None:
            xrandrSource = processOutputGen("xrandr", "-q", "--verbose")
        for line in xrandrSource:
            if readingEdid:
                m = re.match(r'^\s*([0-9a-f]+)\s*$', line)
                if m is not None:
                    connector.appendToEdid(m.group(1))
                    continue
                else:
                    readingEdid = False
                    # fallthrough to the rest of the loop for parsing of this line
            # screen?
            m = re.search(r'^Screen [0-9]+: ', line)
            if m is not None: # ignore this line
                connector = None
                continue
            # new connector?
            m = re.search(r'^([\w\-]+) (dis)?connected ', line)
            if m is not None:
                connector = Connector(m.group(1))
                assert not any(c.name == connector.name for c in self.connectors), "Duplicate connector {}".format(connector.name)
                if not connector.name.startswith("VIRTUAL"):
                    # skip "VIRTUAL" connectors
                    self.connectors.append(connector)
                continue
            # new resolution?
            m = re.search(r'^\s*([\d]+)x([\d]+)', line)
            if m is not None:
                resolution = Resolution(int(m.group(1)), int(m.group(2)))
                assert connector is not None
                connector.addResolution(resolution)
                if re.search(r' [+]preferred\b', line):
                    connector.setPreferredResolution(resolution)
                continue
            # EDID?
            m = re.search(r'^\s*EDID:\s*$', line)
            if m is not None:
                readingEdid = True
                continue
            # unknown line
            # not fatal, e.g. xrandr shows strange stuff when a display is enabled, but not connected; --verbose adds a whole lot of other weird stuff
    
    # return the first available connector from those listed in <tryConnectorNames>, skipping disabled connectors
    def _findAvailableConnector(self, tryConnectorNames):
        for c in filter(lambda c: c.name in tryConnectorNames and c.isConnected(), self.connectors):
            return c
        return None
    
    # return resolutions available for both internal and external screen
    def commonResolutions(self):
        assert self.externalConnector is not None, "Common resolutions may only be queried if there is an external screen connected."
        internalRes = self.internalConnector.getResolutionList()
        externalRes = self.externalConnector.getResolutionList()
        return sorted(set(externalRes).intersection(internalRes), key=lambda r: -r.pixelCount())
    
    # compute the xrandr call
    def forXrandr(self, setup):
        # turn all screens off
        connectorArgs = {} # maps connector names to xrand arguments
        for c in self.connectors:
            connectorArgs[c.name] = ["--off"]
        # set arguments for the relevant ones
        connectorArgs[self.internalConnector.name] = setup.getInternalArgs()
        if self.externalConnector is not None:
            connectorArgs[self.externalConnector.name] = setup.getExternalArgs(self.internalConnector.name)
        else:
            assert setup.extResolution is None, "There's no external screen to set a resolution for"
        # now compose the arguments
        call = ["xrandr"]
        for name in connectorArgs:
            call += ["--output", name] + connectorArgs[name]
        return call

    def fetchDBInfo(self, db):
        if self.externalConnector and self.externalConnector.edid:
            self.previousSetup = db.getConfig(self.externalConnector.edid) # may also return None
        else:
            self.previousSetup = None
        if self.previousSetup:
            print("Known screen, previous setup:", self.previousSetup)
            self.externalConnector.previousResolution = self.previousSetup.extResolution
            self.internalConnector.previousResolution = self.previousSetup.intResolution
    
    def putDBInfo(self, db, setup):
        if not self.externalConnector or not self.externalConnector.edid:
            return
        db.putConfig(self.externalConnector.edid, setup)
