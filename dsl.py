#!/usr/bin/python
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
# along with this program (gpl.txt); if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import os, re, subprocess
from selector_window import PositionSelection
import gui

# for auto-config: common names of internal connectors
commonInternalConnectorNames = ['LVDS', 'LVDS1']

# Load a section-less config file: maps parameter names to space-separated lists of strings (with shell quotation)
def loadConfigFile(file):
	import shlex
	result = {}
	if not os.path.exists(file):
		return result # no config file
	# read config file
	linenr = 0
	with open(file) as file:
		for line in file:
			linenr += 1
			line = line.strip()
			if not len(line) or line.startswith("#"): continue # skip empty and comment lines
			try:
				# parse line
				pos = line.index("=") # will raise exception when substring is not found
				curKey = line[:pos].strip()
				result[curKey] = shlex.split(line[pos+1:]) # shlex.split also strips
			except Exception:
				raise Exception("Invalid config, line %d: Error parsing line (quoting issue?)." % linenr)
	# add some convencience get functions
	return result

def getXrandrInformation():
	p = subprocess.Popen(["xrandr", "-q"], stdout=subprocess.PIPE)
	connectors = {} # map of connector names to a list of resolutions
	connector = None # current connector
	for line in p.stdout:
		# new connector?
		m = re.search(r'^([\w]+) (dis)?connected ', line)
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
	p.communicate()
	if p.returncode != 0: raise Exception("Querying xrandr for data failed.")
	return connectors

def res2xrandr(res):
	(w, h) = res
	return str(w)+'x'+str(h)

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

def findAvailableConnector(tryConnectors):
	for connector in tryConnectors:
		if connector in connectors and connectors[connector]: # if the connector exists and is active (i.e. there is a resolution)
			return connector
	return None

# the main function
def main():
	# load connectors and options
	connectors = getXrandrInformation()
	config = loadConfigFile(os.getenv('HOME') + '/.dsl.conf')
	# find internal connector
	if 'internalConnector' in config:
		if len(config['internalConnector']) != 1:
			raise Exception("You must specify exactly one internal connector.")
		internalConnector = config['internalConnector'][0]
		if not internalConnector in connectors:
			raise Exception("Connector %s does not exist, there is an error in your config file." % internalConnector)
	else:
		# auto-config
		internalConnector = findAvailableConnector(commonInternalConnectorNames)
		if internalConnector is None:
			raise Exception("Could not automatically find internal connector, please use ~/.dsl.conf to specify it manually.")
	# all the rest is external then, obviously - unless the user wants to do that manually
	if 'externalConnectors' in config:
		externalConnectors = config['externalConnectors']
		for connector in externalConnectors:
			if not connector in connectors:
				raise Exception("Connector %s does not exist, there is an error in your config file." % internalConnector)
	else:
		externalConnectors = connectors.keys()
		externalConnectors.remove(internalConnector)
	if not externalConnectors:
		raise Exception("No external connector found - either your config is wrong, or your machine has only one connector.")

	# default: screen off
	args = {} # maps connector names to xrand arguments
	for c in externalConnectors+[internalConnector]:
		args[c] = ["--off"]

	# Check what to do
	usedExternalConnector = findAvailableConnector(externalConnectors) # *the* external connector which is actually used
	if usedExternalConnector is not None: # there's an external screen connected, we need to ask what to do
		internalResolutions = connectors[internalConnector]
		externalResolutions = connectors[usedExternalConnector]
		extPosition = PositionSelection(usedExternalConnector, map(res2user, internalResolutions), map(res2user, externalResolutions))
		extPosition.exec_()
		if not extPosition.result(): sys.exit(1) # the user canceled
		extResolution = res2xrandr(externalResolutions[extPosition.extResolutions.currentIndex()])
		intResolution = res2xrandr(internalResolutions[extPosition.intResolutions.currentIndex()])
		# build command-line
		args[usedExternalConnector] = ["--mode", extResolution] # set external screen to desired resolution
		if extPosition.extOnly.isChecked():
			args[usedExternalConnector] += ["--primary"]
		else:
			# there are two screens
			args[internalConnector] = ["--mode", intResolution] # set internal screen to desired resolution
			# set position
			if extPosition.posLeft.isChecked():
				args[usedExternalConnector] += ["--left-of", internalConnector]
			else:
				args[usedExternalConnector] += ["--right-of", internalConnector]
			# set primary screen
			if extPosition.primExt.isChecked():
				args[usedExternalConnector] += ["--primary"]
			else:
				args[internalConnector] += ["--primary"]
	else:
		# use first resolution
		args[internalConnector] = ["--mode", res2xrandr(connectors[internalConnector][0]), "--primary"]
	# and do it
	call = ["xrandr"]
	for name in args:
		call += ["--output", name] + args[name]
	print "Call that will be made:",call
	subprocess.check_call(call)

# if we run top-level
if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		gui.error(str(e))
		raise
