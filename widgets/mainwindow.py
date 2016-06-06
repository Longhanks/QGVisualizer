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

import os
import math

from PyQt5 import uic
from PyQt5.QtCore import QRectF, QLineF, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene,\
    QGraphicsView, QGraphicsEllipseItem
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QBrush

from utilities import getResourcesPath


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'mainwindow.ui'),
                   self)
        self.actionExit.triggered.connect(QApplication.quit)
        self.actionLoad_G_Code.triggered.connect(self.loadGCode)

        self.scene = QGraphicsScene()
        self.scene.addRect(QRectF(0, 0, 200, 290))
        self.graphicsView.setScene(self.scene)
        self.graphicsView.scale(1, -1)

    def loadGCode(self):
        rawSteps = []
        # a step is tuple of str (command) and dict of arg -> value
        # eg ('G1', {'X': 0})
        with open(os.path.join(getResourcesPath(), 'gcode', 'gcode.txt')) as f:
            for line in f:
                if line.startswith(';'):
                    continue
                if line.endswith('\n'):
                    line = line[:-1]
                splitted = line.split(' ')
                cmd = splitted[0]
                packedArgs = splitted[1:]
                args = {}
                for arg in packedArgs:
                    args[arg[0]] = arg[1:]
                rawSteps.append((cmd, args))
        prevX = 0
        prevY = 0
        for rawStep in rawSteps:
            cmd = rawStep[0]
            args = rawStep[1]
            try:
                prevX = args['X']
            except:
                args['X'] = prevX
            try:
                prevY = args['Y']
            except:
                args['Y'] = prevY
            if cmd == 'G2' or cmd == 'G3':
                try:
                    args['I']
                except KeyError:
                    args['I'] = 0
                try:
                    args['J']
                except KeyError:
                    args['J'] = 0
        self.execGCode(rawSteps)

    def execGCode(self, codes):
        prevX = float(codes[0][1]['X'])
        prevY = float(codes[0][1]['Y'])
        for code in codes:
            cmd = code[0]
            args = code[1]
            x = float(args['X'])
            y = float(args['Y'])
            if cmd == 'G1':
                self.scene.addLine(QLineF(prevX, prevY, x, y))
            elif cmd == 'G2' or cmd == 'G3':
                # voodoo magic for drawing arcs.
                offsetX = float(args['I'])
                offsetY = float(args['J'])
                if args['I'] != 0:
                    radius = abs(offsetX)
                else:
                    radius = abs(offsetY)
                middleX = prevX + offsetX
                middleY = prevY + offsetY
                rectBottomLeftX = middleX - radius
                rectBottomLeftY = middleY - radius
                rectLength = 2 * radius
                arcLength = self.calcArc(prevX, prevY, middleX, middleY,
                                         x, y, radius)
                arcOffset = self.calcArc(prevX, prevY, middleX, middleY,
                                         middleX + radius, middleY, radius)
                if offsetY < 0:
                    arcOffset = 360 - arcOffset
                ellipse = Arc(rectBottomLeftX, rectBottomLeftY,
                              rectLength, rectLength)
                ellipse.setStartAngle(arcOffset)
                if cmd == 'G2':
                    ellipse.setSpanAngle(arcLength)
                else:
                    ellipse.setSpanAngle(-arcLength)
                self.scene.addItem(ellipse)
            prevX = x
            prevY = y

    def calcArc(self, p1x, p1y, mx, my, p2x, p2y, radius):
        # Vector from p1 to m
        vecp1m_x = mx - p1x
        vecp1m_y = my - p1y
        # Vector from m to p2
        vecmp2_x = p2x - mx
        vecmp2_y = p2y - my
        # Add to vectors -> vector from p1 to p2
        vecp1p2_x = vecp1m_x + vecmp2_x
        vecp1p2_y = vecp1m_y + vecmp2_y
        # Length of vector from p1 to p2
        vecp1p2_len = math.sqrt(vecp1p2_x ** 2 + vecp1p2_y ** 2)
        # Circular segment: Arc length in radians (formula from Wikipedia...)
        radians = 2 * math.asin(vecp1p2_len / (2 * radius))
        # Convert radians to degrees and be done with shit
        return math.degrees(radians)

    def wheelEvent(self, event):
        # Make scroll -> zoom in/out
        self.graphicsView.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse)
        scaleFactor = 1.15
        if event.angleDelta().y() > 0:
            self.graphicsView.scale(scaleFactor, scaleFactor)
        else:
            self.graphicsView.scale(1.0 / scaleFactor, 1.0 / scaleFactor)


class Arc(QGraphicsEllipseItem):
    # Need this class because ellipse would draw a "piece of pie" like circle,
    # we only need the arc
    def __init__(self, x, y, width, height, parent=None):
        super(Arc, self).__init__(x, y, width, height, parent)

    def setStartAngle(self, angle):
        # 5760? Yeah no Qt
        super(Arc, self).setStartAngle(angle * 16)
        
    def setSpanAngle(self, angle):
        # 0-360° convenience
        super(Arc, self).setSpanAngle(angle * 16)

    def paint(self, painter, styleoptionGraphicsItem, widget=None):
        painter.setPen(QPen())
        painter.setBrush(QBrush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())