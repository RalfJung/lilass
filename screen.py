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
from fractions import Fraction

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
        ratio = Fraction(self.width, self.height) # automatically divides by the gcd
        strRatio = "%d:%d" % (ratio.numerator, ratio.denominator)
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

class Connector:
    def __init__(self, name=None):
        self.name = name # connector name, e.g. "HDMI1"
        self.edid = None # EDID string for the connector, or None if disconnected
        self._resolutions = set() # list of Resolution objects, empty if disconnected
        self.preferredResolution = None
        self.__lastResolution = None
        self.hasLastResolution = False
    
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return """<Connector "%s" EDID="%s" resolutions="%s">""" % (str(self.name), str(self.edid), ", ".join(str(r) for r in self.getResolutionList()))
    
    def __setLastRes(self, res):
        # res == None means this display was last switched off
        if res is not None and not res in self._resolutions:
            raise ValueError("Resolution "+res+" not available for "+self.name+".")
        self.__lastResolution = res
        self.hasLastResolution = True
    
    def __getLastRes(self):
        if not self.hasLastResolution:
            raise ValueError("Connector %s has no last known resolution." % self.name)
        return self.__lastResolution
    
    lastResolution = property(__getLastRes, __setLastRes)
    
    def isConnected(self):
        assert (self.edid is None) == (len(self._resolutions)==0)
        return self.edid is not None
    
    def addResolution(self, resolution):
        assert isinstance(resolution, Resolution)
        self._resolutions.add(resolution)
    
    def appendToEdid(self, s):
        if self.edid is None:
            self.edid = s
        else:
            self.edid += s
    
    def getResolutionList(self):
        return sorted(self._resolutions, key=lambda r: (0 if self.hasLastResolution and r==self.lastResolution else 1, 0 if r==self.preferredResolution else 1, -r.pixelCount()))

class ScreenSituation:
    connectors = [] # contains all the Connector objects
    internalConnector = None # the internal Connector object (will be an enabled one)
    externalConnector = None # the used external Connector object (an enabled one), or None
    
    '''Represents the "screen situation" a machine can be in: Which connectors exist, which resolutions do they have, what are the names for the internal and external screen'''
    def __init__(self, internalConnectorNames, externalConnectorNames = None):
        '''Both arguments are lists of connector names. The first one which exists and has a screen attached is chosen for that class. <externalConnectorNames> can be None to
           just choose any remaining connector.'''
        # which connectors are there?
        self._getXrandrInformation()
        for c in self.connectors:
            print(repr(c))
            print()
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
        # self.lastSetup is left uninitialized so you can't access it before trying a lookup in the database
    
    # Run xrandr and fill the dict of connector names mapped to lists of available resolutions.
    def _getXrandrInformation(self):
        connector = None # current connector
        readingEdid = False
        for line in processOutputGen("xrandr", "-q", "--verbose"):
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
                assert not any(c.name == connector.name for c in self.connectors)
                self.connectors.append(connector)
                continue
            # new resolution?
            m = re.search(r'^\s*([\d]+)x([\d]+)', line)
            if m is not None:
                resolution = Resolution(int(m.group(1)), int(m.group(2)))
                assert connector is not None
                connector.addResolution(resolution)
                if '+preferred' in line:
                    connector.preferredResolution = resolution
                continue
            # EDID?
            m = re.search(r'^\s*EDID:\s*$', line)
            if m is not None:
                readingEdid = True
                continue
            # unknown line
            # not fatal, e.g. xrandr shows strange stuff when a display is enabled, but not connected
            #print("Warning: Unknown xrandr line %s" % line)
    
    # return the first available connector from those listed in <tryConnectorNames>, skipping disabled connectors
    def _findAvailableConnector(self, tryConnectorNames):
        for c in filter(lambda c: c.name in tryConnectorNames and c.isConnected(), self.connectors):
            return c
        return None
    
    # return available internal resolutions
    def internalResolutions(self):
        return self.internalConnector.getResolutionList()
    
    # return available external resolutions (or None, if there is no external screen connected)
    def externalResolutions(self):
        if self.externalConnector is None:
            return None
        return self.externalConnector.getResolutionList()
    
    # return resolutions available for both internal and external screen
    def commonResolutions(self):
        internalRes = self.internalResolutions()
        externalRes = self.externalResolutions()
        assert externalRes is not None
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
            self.lastSetup = db.getConfig(self.externalConnector.edid) # may also return None
        else:
            self.lastSetup = None
        if self.lastSetup:
            print("SETUP FOUND", self.lastSetup)
            self.externalConnector.lastResolution = self.lastSetup.extResolution
            self.internalConnector.lastResolution = self.lastSetup.intResolution
        else:
            print("NO SETUP FOUND")
    
    def putDBInfo(self, db, setup):
        if not self.externalConnector or not self.externalConnector.edid:
            return
        db.putConfig(self.externalConnector.edid, setup)
