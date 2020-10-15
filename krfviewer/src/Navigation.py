##
# @file
# This file is part of SeisSol.
#
# @author Carsten Uphoff (c.uphoff AT tum.de, http://www5.in.tum.de/wiki/index.php/Carsten_Uphoff,_M.Sc.)
#
# @section LICENSE
# Copyright (c) 2017, SeisSol Group
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# @section DESCRIPTION
#

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os.path
import copy

import SRFReader

class Navigation(QWidget):
  activeItemChanged = pyqtSignal(name='activeItemChanged')

  def __init__(self, parent = None):
    super(Navigation, self).__init__(parent)
    
    self.currentFile = ''

    openIcon = QIcon.fromTheme('folder-open')
    openButton = QPushButton(openIcon, '', self)
    openButton.clicked.connect(self.selectFile)
    refreshIcon = QIcon.fromTheme('view-refresh')
    refreshButton = QPushButton(refreshIcon, '', self)
    refreshButton.clicked.connect(self.refreshFile)
    
    self.sourceList = QListView(self)
    self.model = QStandardItemModel()
    self.sourceList.setModel(self.model)
    self.sourceList.clicked.connect(self.activeItemChanged)
    
    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(openButton)
    buttonLayout.addWidget(refreshButton)
    buttonLayout.addStretch()

    layout = QVBoxLayout(self)
    layout.addLayout(buttonLayout)
    layout.addWidget(self.sourceList)
      
  def selectFile(self):
    rfFilter = 'Standard rupture format (*.srf)'
    fileName = QFileDialog.getOpenFileName(self, 'Open kinematic rupture file', QFileInfo(self.currentFile).dir().path(), rfFilter)
    self.currentFile = fileName
    self.readFile(fileName)
      
  def readFile(self, fileName):
    if len(fileName) != 0:
      sources = list()
      suffix = QFileInfo(fileName).suffix()
      if suffix == 'srf':
        sources = SRFReader.read(fileName)
      else:
        raise ValueError('Unknown file type {}.'.format(suffix))
      currentIndex = self.sourceList.currentIndex()
      self.model.clear()
      
      for i, source in enumerate(sources):
        item = QStandardItem('Source {}'.format(i+1))
        item.setData(source)
        self.model.appendRow(item)

      if currentIndex.row() >= 0 and len(sources) > currentIndex.row():
        newIndex = self.model.index(currentIndex.row(), currentIndex.column())
        self.sourceList.setCurrentIndex(newIndex)
        self.activeItemChanged.emit()
    
  def getActiveSource(self):      
    source = None
    for index in self.sourceList.selectedIndexes():
      source = self.model.itemFromIndex(index).data().toPyObject()
    return source
    
  def refreshFile(self):
    self.readFile(self.currentFile)
    if not self.sourceList.selectionModel().hasSelection():
      self.activeItemChanged.emit()
    


