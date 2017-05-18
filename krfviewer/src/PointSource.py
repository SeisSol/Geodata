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

import numpy

Lon = u'Longitude'
Lat = u'Latitude'
Dep = u'Depth'
Stk = u'Strike'
Dip = u'Dip'
Area = u'Area'
Tinit = u'tᵢₙᵢₜ'
Dt = u'dt'
Vs = u'vₛ'
Den = u'Density'
Rake = u'Rake'
Sl = [u'Slip₁', u'Slip₂', u'Slip₃']
Nt = [u'nt₁', u'nt₂', u'nt₃']

Variables = { 'Geographic information': { Lon: u'°',
                              Lat: u'°',
                              Dep: u'm' },
              'Moment tensor': {  Stk: u'°',
                                  Dip: u'°',
                                  Rake: u'°',
                                  Area: u'm²',
                                  Sl[0]: u'm',
                                  Sl[1]: u'm',
                                  Sl[2]: u'm' },
              'Time discretisation': { Tinit: u's',
                        Dt: u's',
                        Nt[0]: u'',
                        Nt[1]: u'',
                        Nt[2]: u'' },
              'Material': { Vs: u'm/s',
                            Den: u'kg/m³' }
            }

class PointSource:  
  def __init__(self):
    self.info = dict()
    self.slipRates = [None] * 3
    
