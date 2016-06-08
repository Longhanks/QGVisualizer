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


from PyQt5.QtWidgets import QGraphicsEllipseItem, QWidget,\
    QStyleOptionGraphicsItem
from PyQt5.QtGui import QPainter, QBrush

from widgets.penwidthsettable import PenWidthSettable
from utilities.types import number


# because Qt:
# noinspection PyPep8Naming
class QGraphicsArcItem(QGraphicsEllipseItem, PenWidthSettable):
    # Need this class because ellipse would draw a "piece of pie" like circle,
    # we only need the arc
    def __init__(self, x: number, y: number, width: number, height: number,
                 penWidth: float = 1, parent: QWidget=None) -> None:
        super(QGraphicsArcItem, self).__init__(x, y, width, height, parent)
        self._pen.setWidthF(penWidth)

    def setStartAngle(self, angle: number) -> None:
        # 5760? Yeah no Qt
        super(QGraphicsArcItem, self).setStartAngle(angle * 16)

    def setSpanAngle(self, angle: number) -> None:
        # 0-360° convenience
        super(QGraphicsArcItem, self).setSpanAngle(angle * 16)

    def paint(self, painter: QPainter,
              styleOptionGraphicsItem: QStyleOptionGraphicsItem,
              widget: QWidget=None):
        painter.setPen(self._pen)
        painter.setBrush(QBrush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())
