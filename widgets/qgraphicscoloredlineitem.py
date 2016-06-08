# QGVisualizer. Created on 08.06.2016
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


from PyQt5.QtWidgets import QGraphicsLineItem, QStyleOptionGraphicsItem,\
    QWidget
from PyQt5.QtGui import QColor, QPainter, QBrush
from PyQt5.QtCore import QLineF, Qt

from widgets.penwidthsettable import PenWidthSettable


# because Qt:
# noinspection PyPep8Naming
class QGraphicsColoredLineItem(QGraphicsLineItem, PenWidthSettable):
    def __init__(self, line: QLineF, color: QColor=Qt.black,
                 penWidth: float=1, parent: QWidget=None) -> None:
        super(QGraphicsColoredLineItem, self).__init__(line, parent)
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
