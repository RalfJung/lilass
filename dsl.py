#!/usr/bin/python3
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

import argparse, sys, os, re, subprocess
from gui import getFrontend
frontend = getFrontend("cli") # the fallback, until we got a proper frontend. This is guaranteed to be available.

# for auto-config: common names of internal connectors
commonInternalConnectorNames = ['LVDS', 'LVDS0', 'LVDS1', 'LVDS-0', 'LVDS-1']

# this is as close as one can get to an enum in Python
class RelativeScreenPosition:
	LEFT          = 0
	RIGHT         = 1
	EXTERNAL_ONLY = 2

# storing what's necessary for screen setup
class ScreenSetup:
	def __init__(self, relPosition, intResolution, extResolution, extIsPrimary = False):
		'''relPosition must be one of the RelativeScreenPosition members, the resolutions must be (width, height) pairs'''
		self.relPosition = relPosition
		self.intResolution = intResolution # value doesn't matter if the internal screen is disabled
		self.extResolution = extResolution
		self.extIsPrimary = extIsPrimary or self.relPosition == RelativeScreenPosition.EXTERNAL_ONLY # external is always primary if it is the only one
	
	def getInternalArgs(self):
		if self.relPosition == RelativeScreenPosition.EXTERNAL_ONLY:
			return ["--off"]
		args = ["--mode", res2xrandr(self.intResolution)] # set internal screen to desired resolution
		if not self.extIsPrimary:
			args.append('--primary')
		return args
	
	def getExternalArgs(self, intName):
		args = ["--mode", res2xrandr(self.extResolution)] # set external screen to desired resolution
		if self.extIsPrimary:
			args.append('--primary')
		if self.relPosition == RelativeScreenPosition.LEFT:
			args += ['--left-of', intName]
		elif self.relPosition == RelativeScreenPosition.RIGHT:
			args += ['--right-of', intName]
		return args

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

# helper function: execute a process, return output as iterator, throw exception if there was an error
# you *must* iterate to the end if you use this!
def processOutputGen(*args):
	with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
		for line in p.stdout:
			yield line.decode("utf-8")
	if p.returncode != 0:
		raise Exception("Error executing "+str(args))
def processOutputIt(*args):
	return list(processOutputGen(*args)) # list() iterates over the generator

# Run xrandr and return a dict of output names mapped to lists of available resolutions, each being a (width, height) pair.
# An empty list indicates that the connector is disabled.
def getXrandrInformation():
	connectors = {} # map of connector names to a list of resolutions
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
			assert connector not in connectors
			connectors[connector] = []
			continue
		# new resolution?
		m = re.search(r'^   ([\d]+)x([\d]+) +', line)
		if m is not None:
			assert connector is not None
			connectors[connector].append((int(m.groups()[0]), int(m.groups()[1])))
			continue
		# unknown line
		# not fatal as my xrandr shows strange stuff when a display is enabled, but not connected
		#raise Exception("Unknown line in xrandr output:\n"+line)
		print("Warning: Unknown xrandr line %s" % line)
	return connectors

# convert a (width, height) pair into a string accepted by xrandr as argument for --mode
def res2xrandr(res):
	(w, h) = res
	return str(w)+'x'+str(h)

# convert a (width, height) pair into a string to be displayed to the user
def res2user(res):
	(w, h) = res
	# get ratio
	ratio = int(round(16.0*h/w))
	if ratio == 12: # 16:12 = 4:3
		strRatio = '4:3'
	elif ratio == 13: # 16:12.8 = 5:4
		strRatio = '5:4'
	else: # let's just hope this will never be 14 or more...
		strRatio = '16:%d' % ratio
	return '%dx%d (%s)' %(w, h, strRatio)

# return the first available connector from those listed in tryConnectors, skipping disabled connectors
def findAvailableConnector(tryConnectors, allConnectors):
	for connector in tryConnectors:
		if connector in allConnectors and allConnectors[connector]: # if the connector exists and is active (i.e. there is a resolution)
			return connector
	return None

# Return a (internalConnector, externalConnectors) pair: The name of the internal connector, and a list of external connectors.
# Use the config file at ~/.dsl.conf and fall back to auto-detection
def classifyConnectors(allConnectors):
	config = loadConfigFile(os.getenv('HOME') + '/.dsl.conf')
	# find internal connector
	if 'internalConnector' in config:
		if len(config['internalConnector']) != 1:
			raise Exception("You must specify exactly one internal connector.")
		internalConnector = config['internalConnector'][0]
		if not internalConnector in allConnectors:
			raise Exception("Connector %s does not exist, there is an error in your config file." % internalConnector)
	else:
		# auto-config
		internalConnector = findAvailableConnector(commonInternalConnectorNames, allConnectors)
		if internalConnector is None:
			raise Exception("Could not automatically find internal connector, please use ~/.dsl.conf to specify it manually.")
	# all the rest is external then, obviously - unless the user wants to do that manually
	if 'externalConnectors' in config:
		externalConnectors = config['externalConnectors']
		for connector in externalConnectors:
			if not connector in allConnectors:
				raise Exception("Connector %s does not exist, there is an error in your config file." % connector)
			if connector == internalConnector:
				raise Exception("%s is both internal and external, that doesn't make sense." % connector)
	else:
		externalConnectors = list(allConnectors.keys())
		externalConnectors.remove(internalConnector)
	if not externalConnectors:
		raise Exception("No external connector found - either your config is wrong, or your machine has only one connector.")
	# done!
	return (internalConnector, externalConnectors)

# if we run top-level
if __name__ == "__main__":
	try:
		# parse command-line arguments
		parser = argparse.ArgumentParser(description='easy Display Setup for Laptops')
		parser.add_argument("-f", "--frontend",
							dest="frontend",
							help="The frontend to be used for user interaction")
		parser.add_argument("-r", "--relative-position",
							dest="rel_position", choices=('left', 'right', 'external-only'),
							help="Position of external screen relative to internal one")
		parser.add_argument("-i", "--internal-only",
							dest="internal_only", action='store_true',
							help="Enable internal screen, disable all the others (as if no external screen was connected")
		cmdArgs = parser.parse_args()
		
		# load frontend
		frontend = getFrontend(cmdArgs.frontend)
		
		# load connectors and classify them
		connectors = getXrandrInformation()
		(internalConnector, externalConnectors) = classifyConnectors(connectors)
		
		# default: screen off
		connectorArgs = {} # maps connector names to xrand arguments
		for c in externalConnectors+[internalConnector]:
			connectorArgs[c] = ["--off"]
		
		# check whether we got an external screen or not
		# Check what to do
		usedExternalConnector = findAvailableConnector(externalConnectors, connectors) # *the* external connector which is actually used
		if not cmdArgs.internal_only and usedExternalConnector is not None:
			# there's an external screen connected, we need to get a setup
			if cmdArgs.rel_position is not None:
				# use command-line arguments (can we do this relPosition stuff more elegant?)
				if cmdArgs.rel_position == 'left':
					relPosition = RelativeScreenPosition.LEFT
				elif cmdArgs.rel_position == 'right':
					relPosition = RelativeScreenPosition.RIGHT
				else:
					relPosition = RelativeScreenPosition.EXTERNAL_ONLY
				setup = ScreenSetup(relPosition, connectors[internalConnector][0], connectors[usedExternalConnector][0]) # use default resolutions
			else:
				# use GUI
				setup = frontend.setup(connectors[internalConnector], connectors[usedExternalConnector])
			if setup is None: sys.exit(1) # the user canceled
			# apply it
			connectorArgs[internalConnector] = setup.getInternalArgs()
			connectorArgs[usedExternalConnector] = setup.getExternalArgs(internalConnector)
		else:
			# use first resolution of internal connector
			connectorArgs[internalConnector] = ["--mode", res2xrandr(connectors[internalConnector][0]), "--primary"]
		
		# and do it
		call = ["xrandr"]
		for name in connectorArgs:
			call += ["--output", name] + connectorArgs[name]
		print("Call that will be made:",call)
		subprocess.check_call(call)
		
		# make sure the internal screen is really, *really* turned on if requested
		if cmdArgs.internal_only:
			backlight = float(subprocess.check_output(["xbacklight", "-get"]).strip())
			if backlight == 0: # it's completely turned off, we better enable it
				subprocess.check_call(["xbacklight", "-set", "100"])
	except Exception as e:
		frontend.error(str(e))
		raise
