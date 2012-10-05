#!/usr/bin/python
# DSL - easy Display Setup for Laptops

import os, sys, re, subprocess
from PyQt4 import QtGui
from selector_window import PositionSelection
app = QtGui.QApplication(sys.argv)

# Load a section-less config file: maps parameter names to space-separated lists of strings (with shell quotation)
def loadConfigFile(file):
	import shlex
	# read config file
	linenr = 0
	with open(file) as file:
		result = {}
		for line in file:
			linenr += 1
			line = line.strip()
			if not len(line) or line.startswith("#"): continue # skip empty and comment lines
			try:
				# parse line
				pos = line.index("=") # will raise exception when substring is not found
				curKey = line[:pos].strip()
				value = line[pos+1:]
				result[curKey] = shlex.split(value)
			except Exception:
				raise Exception("Invalid config, line %d: Error parsing line (quoting issue?)" % linenr)
	# add some convencience get functions
	return result

def getXrandrInformation():
	p = subprocess.Popen(["xrandr", "-q"], stdout=subprocess.PIPE)
	connectors = {} # map of connector names to a list of resolutions
	connector = None # current connector
	for line in p.stdout:
		# new connector?
		m = re.search(r'^([\w]+) connected ', line)
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
	if p.returncode != 0: raise Exception("Querying xrandr for data failed")
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

def findAvailableConnector(tryConnectors, availableConnectors):
	for connector in tryConnectors:
		if connector in availableConnectors: return connector
	return None

# load options
config = loadConfigFile(os.getenv('HOME') + '/.dsl.conf')
if len(config['internalConnector']) != 1:
	raise Exception("You must specify exactly one internal connector")
if len(config['externalConnectors']) < 1:
	raise Exception("You must specify at least one external connector")
# use options
internalConnector = config['internalConnector'][0]
externalConnectors = config['externalConnectors']
connectors = getXrandrInformation()
usedExternalConnector = findAvailableConnector(externalConnectors, connectors) # *the* external connector which is actually used

# default: screen off
args = {} # maps connector names to xrand arguments
for c in externalConnectors+[internalConnector]:
	args[c] = ["--off"]

# Check what to do
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
