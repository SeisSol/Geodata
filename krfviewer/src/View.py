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

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
try:
	from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
except ImportError:
	from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt

import Info
import Navigation
import PointSource

class View(QWidget):

  def __init__(self, parent = None):
    super(View, self).__init__(parent)

    self.figure = plt.figure()
    self.canvas = FigureCanvas(self.figure)
    self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.canvas.setMinimumHeight(200)    
    toolbar = NavigationToolbar(self.canvas, self)
    
    self.navigation = Navigation.Navigation(self)
    self.navigation.activeItemChanged.connect(self.updateVisualisation)
    self.navigation.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
    
    self.info = Info.Info(self)

    hLayout = QHBoxLayout()
    hLayout.addWidget(self.navigation)
    hLayout.addWidget(self.info)  
    
    layout = QVBoxLayout(self)
    layout.addLayout(hLayout)
    layout.addWidget(toolbar)
    layout.addWidget(self.canvas)

  def updateVisualisation(self):
    source = self.navigation.getActiveSource()
    self.info.update(source)
    
    numPlots = sum([1 if source.slipRates[i] != None else 0 for i in range(3)])

    self.figure.clear()
    for i in range(3):
      if source.slipRates[i] != None:
        p = self.figure.add_subplot(numPlots, 1, i+1)
        p.set_xlabel('t [s]')
        p.set_ylabel('u{} [m/s]'.format(i+1))
        time = [source.info[PointSource.Tinit] + j*source.info[PointSource.Dt] for j in range(len(source.slipRates[i]))]
        p.plot(time, source.slipRates[i])
    
    if numPlots > 0:
      self.figure.tight_layout()
    self.canvas.draw()
