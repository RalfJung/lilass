#!/usr/bin/python
from PyQt4 import QtCore, QtGui

def makeLayout(layout, members):
	for m in members:
		if isinstance(m, QtGui.QLayout):
			layout.addLayout(m)
		else:
			layout.addWidget(m)
	return layout

class PositionSelection(QtGui.QDialog):
	LEFT = 10
	RIGHT = 20
	EXTERNAL_ONLY = 30
	
	def __init__(self, externalName, internalResolutions, externalResolutions):
		# set up main window
		super(PositionSelection, self).__init__()
		self.setWindowTitle('External screen setup (connector: %s)' % externalName)
		
		# position selection
		posBox = QtGui.QGroupBox('Position of external screen', self)
		self.posLeft = QtGui.QRadioButton('Left of internal screen', posBox)
		self.posRight = QtGui.QRadioButton('Right of internal screen', posBox)
		self.posRight.setChecked(True)
		self.posRight.setFocus()
		self.extOnly = QtGui.QRadioButton('Use external screen exclusively', posBox)
		posBox.setLayout(makeLayout(QtGui.QVBoxLayout(), [self.posLeft, self.posRight, self.extOnly]))
		
		# primary screen
		primBox = QtGui.QGroupBox('Which should be the primary screen?', self)
		self.extOnly.toggled.connect(primBox.setDisabled) # disable the box if there's just one screen in use
		self.primExt = QtGui.QRadioButton('The external screen', primBox)
		self.primInt = QtGui.QRadioButton('The internal screen', primBox)
		self.primInt.setChecked(True)
		primBox.setLayout(makeLayout(QtGui.QVBoxLayout(), [self.primExt, self.primInt]))
		
		# resolution selection
		resBox = QtGui.QGroupBox('Screen resolutions', self)
		extResLabel = QtGui.QLabel('Resolution of external screen:', resBox)
		self.extResolutions = QtGui.QComboBox(resBox)
		for res in externalResolutions:
			self.extResolutions.addItem(res)
		self.extResolutions.setCurrentIndex(0) # select first resolution
		extRow = makeLayout(QtGui.QHBoxLayout(), [extResLabel, self.extResolutions])
		intResLabel = QtGui.QLabel('Resolution of internal screen:', resBox)
		self.extOnly.toggled.connect(intResLabel.setDisabled) # disable the label if there's just one screen in use
		self.intResolutions = QtGui.QComboBox(resBox)
		for res in internalResolutions:
			self.intResolutions.addItem(res)
		self.intResolutions.setCurrentIndex(0) # select first resolution
		self.extOnly.toggled.connect(self.intResolutions.setDisabled) # disable the box if there's just one screen in use
		intRow = makeLayout(QtGui.QHBoxLayout(), [intResLabel, self.intResolutions])
		resBox.setLayout(makeLayout(QtGui.QVBoxLayout(), [extRow, intRow]))
		
		# last row: buttons
		buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		
		# add them all to the window
		self.setLayout(makeLayout(QtGui.QVBoxLayout(), [posBox, primBox, resBox, buttons]))
