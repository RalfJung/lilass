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

# Check screen setup
internalName = "LVDS"
externalName = "CRT1"
connectors = getXrandrInformation()
internalResolutions = connectors[internalName] # there must be a screen assoicated to the internal connector
externalResolutions = connectors.get(externalName)

# Check what to do
if externalResolutions is not None: # we need to ask what to do
	extPosition = PositionSelection(map(res2user, internalResolutions), map(res2user, externalResolutions))
	extPosition.exec_()
	if not extPosition.result(): sys.exit(1) # the user canceled
	extResolution = res2xrandr(externalResolutions[extPosition.extResolutions.currentIndex()])
	intResolution = res2xrandr(internalResolutions[extPosition.intResolutions.currentIndex()])
	# build command-line
	externalArgs = ["--mode", extResolution] # we definitely want an external screen
	if extPosition.extOnly.isChecked():
		internalArgs = ["--off"]
		externalArgs += ["--primary"]
	else:
		# there are two screens
		internalArgs = ["--mode", intResolution]
		if extPosition.posLeft.isChecked():
			externalArgs += ["--left-of", internalName]
		else:
			externalArgs += ["--right-of", internalName]
		if extPosition.primExt.isChecked():
			externalArgs += ["--primary"]
		else:
			internalArgs += ["--primary"]
else:
	internalArgs = ["--mode", res2xrandr(internalResolutions[0]), "--primary"]
	externalArgs = ["--off"]
# and do it
call = ["xrandr", "--output", internalName] + internalArgs + ["--output", externalName] + externalArgs
print "Call that will be made:",call
subprocess.check_call(call)
