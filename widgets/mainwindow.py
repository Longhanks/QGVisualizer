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
from typing import Union, List, Tuple, Dict

from PyQt5 import uic
from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene,\
    QGraphicsEllipseItem, QFileDialog, QGraphicsLineItem, QMessageBox, \
    QInputDialog, QWidget, QStyleOptionGraphicsItem, QGraphicsItem,\
    QCheckBox, QColorDialog
from PyQt5.QtGui import QPen, QColor, QPainter
from PyQt5.QtGui import QBrush
from PyQt5.QtCore import Qt

from utilities import getResourcesPath


# number type
number = Union[int, float]
GCode = Tuple[str, Dict[str, number]]


# because Qt:
# noinspection PyPep8Naming
class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget=None) -> None:
        super(MainWindow, self).__init__(parent)
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'mainwindow.ui'),
                   self)
        self.actionExit.triggered.connect(QApplication.quit)
        self.actionLoad_G_Code.triggered.connect(self.askGCodeFile)
        self.actionClear.triggered.connect(self.actionClearSlot)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionResetZoom.triggered.connect(self.resetZoom)
        self.actionSetPenWidth.triggered.connect(self.askPenWidth)
        self.actionShowMovement.toggled.connect(self.actionShowMovementSlot)
        self.checkBoxActionShowMovement = QCheckBox(
            self.actionShowMovement.text(), self.toolBar)
        self.checkBoxActionShowMovement.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.checkBoxActionShowMovement.toggled.connect(
            self.actionShowMovementSlot)
        self.toolBar.insertWidget(self.actionSetMoveLineColor,
                                  self.checkBoxActionShowMovement)
        self.actionSetMoveLineColor.triggered.connect(
            self.actionSetMoveLineColorSlot)

        self.zoomFactor = 1
        self._precision = 1
        self._moveLineColor = Qt.green
        self.scene = QGraphicsScene()
        self.scene.addRect(QRectF(0, 0, 290, 200))
        self.graphicsView.setScene(self.scene)
        self.graphicsView.scale(1, -1)
        self.updateStatusBar()

    @property
    def moveLineColor(self) -> QColor:
        return self._moveLineColor

    @moveLineColor.setter
    def moveLineColor(self, new_color: QColor) -> None:
        self._moveLineColor = new_color
        for item in self.scene.items():
            if isinstance(item, MoveOnlyLine):
                item.color = self.moveLineColor

    @property
    def precision(self) -> number:
        return self._precision

    @precision.setter
    def precision(self, new_precision: number) -> None:
        self._precision = new_precision
        for item in self.scene.items():
            if isinstance(item, PenWidthSettable) and\
                    isinstance(item, QGraphicsItem):
                item.penWidth = self.precision
        self.updateStatusBar()

    def updateStatusBar(self) -> None:
        # noinspection PyUnresolvedReferences
        self.statusBar.showMessage('Current pen width: %.3f' % self._precision)

    def actionShowMovementSlot(self, toggle: bool) -> None:
        self.checkBoxActionShowMovement.setChecked(toggle)
        self.actionShowMovement.setChecked(toggle)
        for item in self.scene.items():
            if isinstance(item, MoveOnlyLine):
                item.setVisible(toggle)

    def askPenWidth(self) -> None:
        # noinspection PyCallByClass, PyTypeChecker
        res = QInputDialog.getDouble(self, 'Change pen width',
                                     'Enter new pen width:',
                                     self.precision, -10000, 10000, 3)
        if res[1]:
            self.precision = res[0]

    def actionClearSlot(self) -> None:
        if self.askClearScene():
            self.clearScene()

    def actionSetMoveLineColorSlot(self) -> None:
        # Inspector doesn't understand Qt's static methods
        # noinspection PyCallByClass,PyTypeChecker
        color = QColorDialog.getColor(self.moveLineColor, self,
                                      'Select new move line color')
        if QColor.isValid(color):
            self.moveLineColor = color

    def askClearScene(self) -> bool:
        msgbox = QMessageBox(self)
        msgbox.setText('This will clear the area.')
        msgbox.setInformativeText('Are you sure you want to continue?')
        msgbox.setStandardButtons(
            QMessageBox.Cancel | QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        ret = msgbox.exec()
        if ret == QMessageBox.Ok:
            return True
        return False

    def clearScene(self) -> None:
        self.scene.clear()
        self.precision = 1
        self.updateStatusBar()
        self.scene.addRect(QRectF(0, 0, 290, 200))

    def askGCodeFile(self) -> None:
        # noinspection PyCallByClass, PyTypeChecker
        filetuple = QFileDialog.getOpenFileName(self,
                                                'Select G Code file',
                                                getResourcesPath(),
                                                'G Code files (*.gcode);;'
                                                'Text files (*.txt);;'
                                                'All Files (*.*)')
        if filetuple:
            if os.path.isfile(filetuple[0]):
                self.loadGCode(filetuple[0])

    def zoomIn(self) -> None:
        self.graphicsView.scale(1.15, 1.15)
        self.zoomFactor *= 1.15

    def zoomOut(self) -> None:
        self.graphicsView.scale(1.0 / 1.15, 1.0 / 1.15)
        self.zoomFactor /= 1.15

    def resetZoom(self) -> None:
        self.graphicsView.scale(1.0 / self.zoomFactor, 1.0 / self.zoomFactor)
        self.zoomFactor = 1

    def loadGCode(self, filename: str) -> None:
        rawSteps = []
        # a step is tuple of str (command) and dict of arg -> value
        # eg ('G1', {'X': 0})
        with open(filename) as f:
            for index, line in enumerate(f):
                line = line.split(';', 1)[0]
                if not line:
                    continue
                splitted = line.strip().split(' ')
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

    def execGCode(self, codes: List[GCode]) -> None:
        relative_mode = False
        prevX = 0
        prevY = 0
        for code in codes:
            cmd = code[0]
            args = code[1]
            if 'X' in args:
                x = float(args['X']) + (prevX if relative_mode else 0)
            else:
                x = prevX
            if 'Y' in args:
                y = float(args['Y']) + (prevY if relative_mode else 0)
            else:
                y = prevY
            if cmd == 'G0':
                line = MoveOnlyLine(
                    line=QLineF(prevX, prevY, x, y),
                    color=self._moveLineColor,
                    penWidth=self.precision)
                self.scene.addItem(line)
            elif cmd == 'G1':
                self.scene.addItem(
                    QColoredGraphicsLineItem(
                        line=QLineF(prevX, prevY, x, y),
                        penWidth=self.precision))
            elif cmd == 'G2' or cmd == 'G3':
                offsetX = float(args['I'])
                offsetY = float(args['J'])
                if offsetX == 0 and offsetY == 0:
                    # only R given
                    radius = float(args['R'])
                    dx = x - prevX
                    dy = y - prevY
                    dist = math.sqrt(dx ** 2 + dy ** 2)
                    h = math.sqrt((radius ** 2) - ((dist ** 2) / 4))
                    tmpx = dy * h / dist
                    tmpy = -dx * h / dist
                    ccw = (cmd == 'G3')
                    if (ccw and radius > 0) or ((not ccw) and radius < 0):
                        tmpx = -tmpx
                        tmpy = -tmpy
                    middleX = tmpx + (2 * x - dx) / 2
                    middleY = tmpy + (2 * y - dy) / 2
                else:
                    radius = math.sqrt(offsetX ** 2 + offsetY ** 2)
                    middleX = prevX + offsetX
                    middleY = prevY + offsetY
                rectBottomLeftX = middleX - radius
                rectBottomLeftY = middleY - radius
                rectLength = 2 * radius
                alpha = math.degrees(math.atan2(prevY - middleY,
                                                prevX - middleX))
                beta = math.degrees(math.atan2(y - middleY, x - middleX))
                if cmd == 'G2':
                    if beta > alpha:
                        if beta >= 180:
                            beta -= 360
                        else:
                            alpha += 360
                elif cmd == 'G3':
                    if beta < alpha:
                        if alpha > 180:
                            alpha -= 360
                        else:
                            beta += 360
                delta = alpha - beta
                if delta == 0:
                    delta = 360
                ellipse = Arc(rectBottomLeftX, rectBottomLeftY,
                              rectLength, rectLength, penWidth=self.precision)
                ellipse.setStartAngle(-alpha)
                ellipse.setSpanAngle(delta)
                self.scene.addItem(ellipse)
            elif cmd == 'G91':
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


# because Qt:
# noinspection PyPep8Naming
class PenWidthSettable(object):
    def __init__(self):
        self._pen = QPen()

    @property
    def penWidth(self) -> float:
        return self._pen.widthF()

    @penWidth.setter
    def penWidth(self, newWidth: number) -> None:
        self._pen.setWidthF(newWidth)


# because Qt:
# noinspection PyPep8Naming
class Arc(QGraphicsEllipseItem, PenWidthSettable):
    # Need this class because ellipse would draw a "piece of pie" like circle,
    # we only need the arc
    def __init__(self, x: number, y: number, width: number, height: number,
                 penWidth: float=1, parent: QWidget=None) -> None:
        super(Arc, self).__init__(x, y, width, height, parent)
        self._pen.setWidthF(penWidth)

    def setStartAngle(self, angle: number) -> None:
        # 5760? Yeah no Qt
        super(Arc, self).setStartAngle(angle * 16)
        
    def setSpanAngle(self, angle: number) -> None:
        # 0-360° convenience
        super(Arc, self).setSpanAngle(angle * 16)

    def paint(self, painter: QPainter,
              styleOptionGraphicsItem: QStyleOptionGraphicsItem,
              widget: QWidget=None):
        painter.setPen(self._pen)
        painter.setBrush(QBrush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())


# because Qt:
# noinspection PyPep8Naming
class QColoredGraphicsLineItem(QGraphicsLineItem, PenWidthSettable):
    def __init__(self, line: QLineF, color: QColor=Qt.black,
                 penWidth: float=1, parent: QWidget=None) -> None:
        super(QColoredGraphicsLineItem, self).__init__(line, parent)
        self._pen.setColor(color)
        self._pen.setWidthF(penWidth)

    @property
    def color(self) -> QColor:
        return self._pen.color()

    @color.setter
    def color(self, newColor: QColor) -> None:
        self._pen.setColor(newColor)

    def paint(self, painter: QPainter,
              styleOptionGraphicsItem: QStyleOptionGraphicsItem,
              widget: QWidget=None):
        painter.setPen(self._pen)
        painter.setBrush(QBrush())
        painter.drawLine(self.line())


# because Qt:
# noinspection PyPep8Naming
class MoveOnlyLine(QColoredGraphicsLineItem):
    def __init__(self, line: QLineF, color: QColor,
                 penWidth: float=1, parent: QWidget=None):
        super(MoveOnlyLine, self).__init__(line, color, penWidth, parent)
