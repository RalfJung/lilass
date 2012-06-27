#!/usr/bin/python
import sys, re, subprocess
from PyQt4 import QtGui
from selector_window import PositionSelection
app = QtGui.QApplication(sys.argv)

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

def res2str(res):
	(w, h) = res
	return str(w)+'x'+str(h)

# Check screen setup
internalName = "LVDS"
externalName = "CRT1"
connectors = getXrandrInformation()
internalResolutions = connectors[internalName] # there must be a screen assoicated to the internal connector
externalResolutions = connectors.get(externalName)

# Check what to do
internalArgs = ["--mode", res2str(internalResolutions[0])] # there must be a resolution for the internal screen
externalArgs = ["--off"]
if externalResolutions is not None: # we need to ask what to do
	extPosition = PositionSelection(map(res2str, externalResolutions))
	extPosition.exec_()
	if not extPosition.result(): sys.exit(1) # the user canceled
	# build command-line
	externalArgs = ["--mode", extPosition.resolution] # we definitely want an external screen
	if extPosition.position == PositionSelection.EXTERNAL_ONLY:
		internalArgs = ["--off"]
	elif extPosition.position == PositionSelection.LEFT:
		externalArgs += ["--left-of", internalName]
	else:
		externalArgs += ["--right-of", internalName]
# and do it
call = ["xrandr", "--output", internalName] + internalArgs + ["--output", externalName] + externalArgs
print "Call that will be made:",call
subprocess.check_call(call)
