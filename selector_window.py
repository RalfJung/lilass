#!/usr/bin/python
from PyQt4 import QtCore, QtGui

def makeLayout(parent, layout, widgets):
	for w in widgets:
		layout.addWidget(w)
	parent.setLayout(layout)

class PositionSelection(QtGui.QDialog):
	LEFT = 10
	RIGHT = 20
	EXTERNAL_ONLY = 30
	
	def __init__(self, externalResolutions):
		# set up main window
		super(PositionSelection, self).__init__()
		self.setWindowTitle('External screen setup')
		
		# first box: position selection
		posBox = QtGui.QGroupBox('Position of external screen', self)
		self.posLeft = QtGui.QRadioButton('Left of internal screen', posBox)
		self.posRight = QtGui.QRadioButton('Right of internal screen', posBox)
		self.posRight.setChecked(True)
		self.posRight.setFocus()
		self.extOnly = QtGui.QRadioButton('Use external screen exclusively', posBox)
		makeLayout(posBox, QtGui.QVBoxLayout(), [self.posLeft, self.posRight, self.extOnly])
		
		# second box: resolution selection
		resBox = QtGui.QGroupBox('Resolution of external screen', self)
		resLabel = QtGui.QLabel('Select the resolution of the external screen:', resBox)
		self.resolutions = QtGui.QComboBox(resBox)
		for res in externalResolutions:
			self.resolutions.addItem(res)
		self.resolutions.setCurrentIndex(0) # select first resolution
		makeLayout(resBox, QtGui.QHBoxLayout(), [resLabel, self.resolutions])
		
		# last row: buttons
		buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		
		# add them all to the window
		makeLayout(self, QtGui.QVBoxLayout(), [posBox, resBox, buttons])
	
	def accept(self):
		# store return values
		if self.posLeft.isChecked():
			self.position = PositionSelection.LEFT
		elif self.posRight.isChecked():
			self.position = PositionSelection.RIGHT
		else:
			self.position = PositionSelection.EXTERNAL_ONLY
		self.resolution = str(self.resolutions.currentText())
		# go on with default behaviour
		super(PositionSelection, self).accept()  
