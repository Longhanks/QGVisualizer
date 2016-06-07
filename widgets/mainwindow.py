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
from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene,\
    QGraphicsEllipseItem, QFileDialog, QGraphicsLineItem, QMessageBox, \
    QInputDialog
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt

from utilities import getResourcesPath


RESOLUTION = 1


def setResolution(res):
    global RESOLUTION
    RESOLUTION = res


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'mainwindow.ui'),
                   self)
        self.actionExit.triggered.connect(QApplication.quit)
        self.actionLoad_G_Code.triggered.connect(self.askGCodeFile)
        self.actionClear.triggered.connect(self.askClearScene)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionResetZoom.triggered.connect(self.resetZoom)
        self.actionSetResolution.triggered.connect(self.askResolution)

        self.zoomFactor = 1
        self.scene = QGraphicsScene()
        self.scene.addRect(QRectF(0, 0, 290 * RESOLUTION, 200 * RESOLUTION))
        self.graphicsView.setScene(self.scene)
        self.graphicsView.scale(1, -1)
        self.updateStatusBar()

    def updateStatusBar(self):
        self.statusBar.showMessage('Current resolution scale: %d' % RESOLUTION)

    def askResolution(self):
        if self.askClearScene():
            res = QInputDialog.getDouble(self, 'Change resolution',
                                         'Enter a new resolution:',
                                         RESOLUTION, 1)
            if res[1]:
                setResolution(res[0])
                self.updateStatusBar()
                self.clearScene()

    def askClearScene(self):
        msgbox = QMessageBox()
        msgbox.setText('This will clear the area.')
        msgbox.setInformativeText('Are you sure you want to continue?')
        msgbox.setStandardButtons(
            QMessageBox.Cancel | QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        ret = msgbox.exec()
        if ret == QMessageBox.Ok:
            setResolution(1)
            self.updateStatusBar()
            self.clearScene()
            return True
        return False

    def clearScene(self):
        self.scene.clear()
        self.scene.addRect(QRectF(0, 0, 290 * RESOLUTION, 200 * RESOLUTION))


    def askGCodeFile(self):
        filetuple = QFileDialog.getOpenFileName(self,
                                                'Select G Code file',
                                                getResourcesPath(),
                                                'G Code files (*.gcode);;'
                                                'Text files (*.txt)')
        if filetuple:
            self.loadGCode(filetuple[0])

    def zoomIn(self):
        self.graphicsView.scale(1.15, 1.15)
        self.zoomFactor *= 1.15

    def zoomOut(self):
        self.graphicsView.scale(1.0 / 1.15, 1.0 / 1.15)
        self.zoomFactor /= 1.15

    def resetZoom(self):
        self.graphicsView.scale(1.0 / self.zoomFactor, 1.0 / self.zoomFactor)
        self.zoomFactor = 1

    def loadGCode(self, filename):
        rawSteps = []
        # a step is tuple of str (command) and dict of arg -> value
        # eg ('G1', {'X': 0})
        with open(filename) as f:
            for line in f:
                line = line.split(';',1)[0]
                if line.endswith('\n'):
                    line = line[:-1]
                if not line:
                    continue
                splitted = line.split(' ')
                cmd = splitted[0]
                packedArgs = splitted[1:]
                args = {}
                for arg in packedArgs:
                    args[arg[0]] = arg[1:]
                rawSteps.append((cmd, args))
        for rawStep in rawSteps:
            cmd = rawStep[0]
            args = rawStep[1]
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
        relative_mode = False
        prevX = 0
        prevY = 0
        for code in codes:
            cmd = code[0]
            args = code[1]
            if 'X' in args:
                x = (RESOLUTION * float(args['X'])) + \
                    (prevX if relative_mode else 0)
            else:
                x = prevX
            if 'Y' in args:
                y = (RESOLUTION * float(args['Y'])) + \
                    (prevY if relative_mode else 0)
            else:
                y = prevY
            if cmd == 'G0':
                line = QColoredGraphicsLineItem(QLineF(prevX, prevY, x, y),
                                                Qt.green)
                self.scene.addItem(line)
            elif cmd == 'G1':
                self.scene.addLine(QLineF(prevX, prevY, x, y))
            elif cmd == 'G2' or cmd == 'G3':
                offsetX = RESOLUTION * float(args['I'])
                offsetY = RESOLUTION * float(args['J'])
                radius = math.sqrt(offsetX ** 2 + offsetY ** 2)
                middleX = prevX + offsetX
                middleY = prevY + offsetY
                rectBottomLeftX = middleX - radius
                rectBottomLeftY = middleY - radius
                rectLength = 2 * radius
                alpha = math.degrees(math.atan2(prevY - middleY,
                                                prevX - middleX))
                beta = math.degrees(math.atan2(y - middleY, x - middleX))
                if beta == 180:
                    beta = -180
                if alpha * beta < 0:
                    if alpha < 0:
                        alpha += 360
                    elif beta < 0:
                        beta += 360

                delta = beta - alpha
                if delta == 0:
                    delta = 360
                ellipse = Arc(rectBottomLeftX, rectBottomLeftY,
                              rectLength, rectLength)
                ellipse.setStartAngle(-max(alpha, beta))
                ellipse.setSpanAngle(abs(delta))
                self.scene.addItem(ellipse)
            elif cmd =='G91':
                relative_mode = True
            elif cmd == 'G90':
                relative_mode = False
            elif cmd == 'G28':
                # reference drive + general init
                relative_mode = False
                x = -0.9
                y = 242.3
            prevX = x
            prevY = y


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


class QColoredGraphicsLineItem(QGraphicsLineItem):
    def __init__(self, line, color, parent=None):
        super(QColoredGraphicsLineItem, self).__init__(line, parent)
        self.color = color

    def paint(self, painter, styleoptionGraphicsItem, widget=None):
        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush())
        painter.drawLine(self.line())
