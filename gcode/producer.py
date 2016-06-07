#!/usr/bin/env python3
#
# QGVisualizer. Created on 06.06.2016
# Copyright (c) 2015 Andreas Schulz
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import os


sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))
from utilities import getResourcesPath
gcodeDir = os.path.join(getResourcesPath(), 'gcode')


steps = []


def moveTo(x, y):
    steps.append('G0 X%f Y%f' % (x, y))

def cutTo(x, y):
    steps.append('G1 X%f Y%f' % (x, y))

def comment(comstr):
    steps.append('; ' + comstr)

def cutArcTo(x, y, offsetX, offsetY, clockwise=True):
    if clockwise:
        cmd = 'G2'
    else:
        cmd = 'G3'
    steps.append(cmd + ' X%f Y%f I%f J%F' % (x, y, offsetX, offsetY))


def squares():
    comment('Start bottom left square')
    moveTo(0, 5)
    cutArcTo(5, 0, 5, 0, clockwise=False)
    cutTo(15, 0)
    cutArcTo(20, 5, 0, 5, clockwise=False)
    cutTo(20, 15)
    cutArcTo(15, 20, -5, 0, clockwise=False)
    cutTo(5, 20)
    cutArcTo(0, 15, 0, -5, clockwise=False)
    cutTo(0, 5)
    comment('Start top right square')
    moveTo(20, 25)
    cutTo(0, 35)
    cutArcTo(25, 40, 5, 0)
    cutTo(35, 0)
    cutArcTo(40, 35, -5, 0)
    cutTo(0, 25)
    cutArcTo(35, 20, -5, 0)
    cutTo(25, 0)
    cutArcTo(20, 25, 5, 0)
    comment('Start inner circle for bottom left')
    moveTo(5, 10)
    cutArcTo(10, 5, 5, 0, clockwise=False)
    cutArcTo(15, 10, 0, 5, clockwise=False)
    cutArcTo(10, 15, -5, 0, clockwise=False)
    cutArcTo(5, 10, 0, -5, clockwise=False)
    comment('Start inner circle for top right')
    moveTo(25, 30)
    cutArcTo(30, 35, 5, 0, clockwise=False)
    cutArcTo(35, 30, 0, -5, clockwise=False)
    cutArcTo(30, 25, -5, 0, clockwise=False)
    cutArcTo(25, 30, 0, 5, clockwise=False)
    with open(os.path.join(gcodeDir, 'squares.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]

if __name__ == '__main__':
    squares()