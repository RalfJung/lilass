#!/usr/bin/python
from PyQt4 import QtGui

class PositionSelection(QtGui.QDialog):
	LEFT = 10
	RIGHT = 20
	EXTERNAL_ONLY = 30
	
	def __init__(self, resolutions):
		super(PositionSelection, self).__init__()   
		
		mainBox = QtGui.QVBoxLayout()
		posBox = QtGui.QHBoxLayout()
		resBox = QtGui.QHBoxLayout()
		
		# First row: Resolution selection
		mainBox.addLayout(resBox)
		resBox.addWidget(QtGui.QLabel('Select the resolution of the external screen:'))
		self.resolutions = QtGui.QComboBox(self)
		for res in resolutions:
			self.resolutions.addItem(res)
		self.resolutions.setCurrentIndex(0) # select first resolution
		resBox.addWidget(self.resolutions)
		
		# Next two rows: Position selection
		mainBox.addWidget(QtGui.QLabel('Select the position of the external screen relative to the internal one:'))
		mainBox.addLayout(posBox)

		btn = QtGui.QPushButton('Left', self)
		btn.clicked.connect(self.left)
		posBox.addWidget(btn)

		btn = QtGui.QPushButton('Right', self)
		btn.clicked.connect(self.right)
		btn.setFocus()
		posBox.addWidget(btn)

		btn = QtGui.QPushButton('External only', self)
		btn.clicked.connect(self.externalOnly)
		posBox.addWidget(btn)

		# Finalization
		self.setLayout(mainBox)
		self.setWindowTitle('External screen setup')
	
	def accept(self):
		self.resolution = str(self.resolutions.currentText())
		super(PositionSelection, self).accept()  
	
	def left(self):
		self.position = PositionSelection.LEFT
		self.accept()
	
	def right(self):
		self.position = PositionSelection.RIGHT
		self.accept()
	
	def externalOnly(self):
		self.position = PositionSelection.EXTERNAL_ONLY
		self.accept()
