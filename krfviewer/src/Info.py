# -*- coding: utf-8 -*-
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy
import math
import re
import PointSource

HasPyproj = False
try:
  import pyproj
except ImportError:
  print('Could not find pyproj module. Projections are not available.')
else:
  HasPyproj = True

MeshPosition = 'Position in mesh'
X = u'x'
Y = u'y'
Z = u'z'

FaultGeometry = 'Fault geometry'
AxDef = u'Ax. Def.'
AxDefDefault = 'enu'
FaultAxes = [u'u₁', u'u₂', u'u₃']

InferredSlip = 'Slip from STF'
ISl = [u'int SR₁', u'int SR₂', u'int SR₃']

InferredVariables = { MeshPosition: { X: u'm',
                                      Y: u'm',
                                      Z: u'm' },
                      FaultGeometry: {  AxDef: u'',
                                        FaultAxes[0]: u'm',
                                        FaultAxes[1]: u'm',
                                        FaultAxes[2]: u'm' },
                      InferredSlip: { ISl[0]: u'm',
                                      ISl[1]: u'm',
                                      ISl[2]: u'm' }
                    }

class Info(QWidget):
  NumberOfRows = 3

  def __init__(self, parent = None):
    super(Info, self).__init__(parent)
    
    self.source = None
    self.axdef = AxDefDefault
    self.axdefRe = re.compile('\+axis=([ewsnud]{3})')
    layout = QVBoxLayout(self)
    
    if HasPyproj:
      self.lonlat = pyproj.Proj('+proj=lonlat +datum=WGS84 +units=km +no_defs')
      projLabel = QLabel('Projection:', self)
      self.proj = QLineEdit(self)
      self.proj.setText('+proj=geocent +datum=WGS84 +units=m +no_defs')
      self.proj.textChanged.connect(self.updateInferredValues)
      self.projError = QLabel(self)
      self.projError.setStyleSheet('QLabel { font: italic; }')
      projLayout = QGridLayout()
      projLayout.addWidget(projLabel, 0, 0)
      projLayout.addWidget(self.proj, 0, 1)
      projLayout.addWidget(self.projError, 1, 1)
      layout.addLayout(projLayout)
      
    variables = PointSource.Variables.copy()
    variables.update(InferredVariables)
      
    infoLayout = QGridLayout()    
    self.widgets = dict()
    for groupNr,group in enumerate(variables):
      groupWidget = QGroupBox(group)
      groupLayout = QFormLayout(groupWidget)
      infoLayout.addWidget(groupWidget, groupNr%self.NumberOfRows, groupNr/self.NumberOfRows)
      for key in sorted(variables[group].iterkeys()):
        self.widgets[key] = QLabel(self)
        groupLayout.addRow(key, self.widgets[key])
    
    layout.addLayout(infoLayout)
    layout.addStretch()

  def update(self, source):
    self.source = source
    for group, variables in PointSource.Variables.iteritems():
      self.updateLabels(self.source.info, variables)

    self.updateInferredValues()
    
  def updateInferredValues(self):
    if self.source != None:
      # Position in mesh
      data = dict()
      if HasPyproj:
        try:
          projection = pyproj.Proj(str(self.proj.text()))
        except RuntimeError as err:
          self.proj.setStyleSheet('QLineEdit { background: rgb(255, 0, 0); }')
          self.projError.setText(str(err))
        else:
          try:
            x, y, z = pyproj.transform(self.lonlat, projection, self.source.info[PointSource.Lon], self.source.info[PointSource.Lat], -self.source.info[PointSource.Dep], radians=False)
          except RuntimeError as err:
            self.proj.setStyleSheet('QLineEdit { background: rgb(255, 0, 0); }')
            self.projError.setText(str(err))
          else:
            data = {X: x, Y: y, Z: z}
            self.projError.setText('')
            self.proj.setStyleSheet('')
      self.updateLabels(data, InferredVariables[MeshPosition])

      # Fault geometry
      data = dict()
      if HasPyproj:
        axdef = self.axdefRe.search(str(self.proj.text()))
        if axdef != None:
          self.axdef = axdef.group(1)
        else:
          self.axdef = AxDefDefault
      data[AxDef] = self.axdef
      for i in range(3):
        axis = self.toMCS(  math.radians(self.source.info[PointSource.Stk]),
                            math.radians(self.source.info[PointSource.Dip]),
                            math.radians(self.source.info[PointSource.Rake]),
                            1.0 if i==0 else 0.0,
                            1.0 if i==1 else 0.0,
                            1.0 if i==2 else 0.0  )
        data[ FaultAxes[i] ] = [round(x, 2) for x in axis]
      self.updateLabels(data, InferredVariables[FaultGeometry])
      
      # Inferred slip
      data = dict()
      for i in range(3):
        slip = self.computeSlip(self.source.slipRates[i])
        if not math.isnan(slip):
          data[ ISl[i] ] = slip
      self.updateLabels(data, InferredVariables[InferredSlip])
  
  def updateLabels(self, data, variables):
    for key, unit in variables.iteritems():
      if data.has_key(key):
        self.widgets[key].setText(u'{} {}'.format(data[key], unit))
      else:
        self.widgets[key].setText(u'N/A')
        
  def computeSlip(self, slipRate):
    if slipRate == None or slipRate.size < 2:
      return float('nan')
    # Area of piecewise linear function
    return 0.5 * self.source.info[PointSource.Dt] * numpy.sum(slipRate[0:-1] + slipRate[1:])

  def adjustAxes(self, u1, u2, u3):
    x = [0.0] * 3
    axes = {'e': u2, 'w': -u2, 'n': u1, 's': -u1, 'd': u3, 'u': -u3}
    return [axes[ self.axdef[i] ] for i in range(3)]

  def toMCS(self, strike, dip, rake, u1, u2, u3):
    x1 = u1*(math.sin(rake)*math.sin(strike)*math.cos(dip) + math.cos(rake)*math.cos(strike)) + u2*(-math.sin(rake)*math.cos(strike) + math.sin(strike)*math.cos(dip)*math.cos(rake)) - u3*math.sin(dip)*math.sin(strike);
    x2 = u1*(-math.sin(rake)*math.cos(dip)*math.cos(strike) + math.sin(strike)*math.cos(rake)) + u2*(-math.sin(rake)*math.sin(strike) - math.cos(dip)*math.cos(rake)*math.cos(strike)) + u3*math.sin(dip)*math.cos(strike);
    x3 = -u1*math.sin(dip)*math.sin(rake) - u2*math.sin(dip)*math.cos(rake) - u3*math.cos(dip)
    return self.adjustAxes(x1, x2, x3)
