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

import re
import numpy
import PointSource

Header1 = [ (PointSource.Lon, 1.),
            (PointSource.Lat, 1.),
            (PointSource.Dep, 1.e3),
            (PointSource.Stk, 1.),
            (PointSource.Dip, 1.),
            (PointSource.Area, 1.e-4),
            (PointSource.Tinit, 1.), ('dt', 1.),
            (PointSource.Vs, 1.e-2),
            (PointSource.Den, 1000.)  ]
Header2 = [ (PointSource.Rake, 1.),
            (PointSource.Sl[0], 1.e-2),
            (PointSource.Nt[0], 1),
            (PointSource.Sl[1], 1.e-2),
            (PointSource.Nt[1], 1),
            (PointSource.Sl[2], 1.e-2),
            (PointSource.Nt[2], 1)  ]

def safereadline(f):
  line = f.readline()
  while line.startswith('#'):
    line = f.readline()
  if not line:
    raise RuntimeError('SRF parser expected a line but EOF is reached.')
  return line

def readPointSource(f):
  header1 = safereadline(f)
  header2 = safereadline(f)
  
  info1 = header1.split()
  info2 = header2.split()
  
  source = PointSource.PointSource()
  for i, info in enumerate(info1):
    source.info[ Header1[i][0] ] = Header1[i][1] * type(Header1[i][1])(info)
  for i, info in enumerate(info2):
    source.info[ Header2[i][0] ] = Header2[i][1] * type(Header2[i][1])(info)
  
  for i in range(3):
    nt = source.info[PointSource.Nt[i]]
    if nt > 0:
      samples = list()
      while len(samples) < nt:
        stf = safereadline(f)
        samples.extend([float(s) * 1.e-2 for s in stf.split()])

      if len(samples) != nt:
        raise RuntimeError('SRF parser expected {} samples but found {}.'.format(len(samples), nt))

      source.slipRates[i] = numpy.array(samples)    
  
  return source
  

def read(fileName):
  sources = list()

  points = re.compile('POINTS\s+([0-9]+)', flags=re.IGNORECASE)
  with open(fileName, 'r') as f:
    version = safereadline(f)
    line = f.readline()
    while line:
      block = points.match(line)
      if block != None:
        for i in range(int(block.group(1))):
          sources.append( readPointSource(f) )
      line = f.readline()

  return sources
