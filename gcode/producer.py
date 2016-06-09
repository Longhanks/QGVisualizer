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
import math


sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..')))


from utilities import getResourcesPath

gcodeDir = os.path.join(getResourcesPath(), 'gcode')


steps = []


def move(x, y):
    steps.append('G0 X%f Y%f' % (x, y))


def cut(x, y):
    steps.append('G1 X%f Y%f' % (x, y))


def comment(cmt):
    steps.append('; ' + cmt)


def arc(x, y, i, j, clockwise=True):
    if clockwise:
        cmd = 'G2'
    else:
        cmd = 'G3'
    steps.append(cmd + ' X%f Y%f I%f J%f' % (x, y, i, j))


def arc_radius(x, y, r, clockwise=True):
    if clockwise:
        cmd = 'G2'
    else:
        cmd = 'G3'
    steps.append(cmd + ' X%f Y%f R%f' % (x, y, r))


def relative():
    steps.append('G91')


def absolute():
    steps.append('G90')


def squares():
    comment('Start bottom left square')
    move(0, 5)
    arc(5, 0, 5, 0, clockwise=False)
    cut(15, 0)
    arc(20, 5, 0, 5, clockwise=False)
    cut(20, 15)
    arc(15, 20, -5, 0, clockwise=False)
    cut(5, 20)
    arc(0, 15, 0, -5, clockwise=False)
    cut(0, 5)
    comment('Start top right square')
    move(20, 25)
    cut(20, 35)
    arc(25, 40, 5, 0)
    cut(35, 40)
    arc(40, 35, 0, -5)
    cut(40, 25)
    arc(35, 20, -5, 0)
    cut(25, 20)
    arc(20, 25, 0, 5)
    comment('Start inner circle for bottom left')
    move(5, 10)
    arc(10, 5, 5, 0, clockwise=False)
    arc(15, 10, 0, 5, clockwise=False)
    arc(10, 15, -5, 0, clockwise=False)
    arc(5, 10, 0, -5, clockwise=False)
    comment('Start inner circle for top right')
    move(25, 30)
    arc(30, 35, 5, 0, clockwise=False)
    arc(35, 30, 0, -5, clockwise=False)
    arc(30, 25, -5, 0, clockwise=False)
    arc(25, 30, 0, 5, clockwise=False)
    with open(os.path.join(gcodeDir, 'squares.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]


def front():
    HEIGHT = 200
    BOTTOM_HOLE_WIDTH = 5
    BOTTOM_HOLE_HEIGHT = 5
    MIDDLE_HOLE_WIDTH = 20
    MIDDLE_HOLE_HEIGHT = 4
    # motor = 12mm * 22mm
    MOTOR_HOLE_WIDTH = 23
    MOTOR_HOLE_HEIGHT = 13

    def cut_bottom_hole() -> None:
        """
        Starts in bottom left corner, moves right & up
        """
        # Cut a little over the edge
        move(-1, 0)
        cut(BOTTOM_HOLE_WIDTH + 1, 0)
        cut(0, BOTTOM_HOLE_HEIGHT)
        cut(-BOTTOM_HOLE_WIDTH - 1, 0)
        move(1, 0)

    def cut_middle_hole() -> None:
        """
        Starts in bottom left corner, moves right & up
        """
        cut(0, MIDDLE_HOLE_HEIGHT)
        cut(MIDDLE_HOLE_WIDTH, 0)
        cut(0, -MIDDLE_HOLE_HEIGHT)
        cut(-MIDDLE_HOLE_WIDTH, 0)

    def cut_motor_hole() -> None:
        """
        Starts in bottom left corner, moves right & up
        """
        cut(0, MOTOR_HOLE_HEIGHT)
        cut(MOTOR_HOLE_WIDTH, 0)
        cut(0, -MOTOR_HOLE_HEIGHT)
        cut(-MOTOR_HOLE_WIDTH, 0)

    # Start by cutting bottom holes @ 40% height start and 60% height stop
    relative()
    move(0, 80)
    cut_bottom_hole()
    move(0, 30)
    cut_bottom_hole()

    # Move to start point for cutting middle holes
    absolute()
    # 15 padding left, place holes on middle line and move cursor to top left
    move(15, HEIGHT / 2 - MIDDLE_HOLE_HEIGHT / 2)  # 15/98

    relative()
    for _ in range(6):
        # 290 width, 15 padding at each side -> 260 width,
        # that makes 6 segments of 20mm hole, 20mm whitespace and one last
        # hole (h-w-h-w-h-w-h-w-h-w-h-w-h)
        cut_middle_hole()
        move(40, 0)
    # The last missing hole (...-h)
    cut_middle_hole()
    # Move cursor on right end of hole
    move(20, 0)
    # Add final padding
    move(15, 0)

    # Cut motor holes
    absolute()
    move(240, 30)
    relative()
    cut_motor_hole()
    absolute()
    move(240, 170 - MOTOR_HOLE_HEIGHT)
    relative()
    cut_motor_hole()

    # Frame
    absolute()
    move(0, 0)
    cut(290, 0)
    cut(290, 200)
    cut(0, 200)
    cut(0, 0)

    # Done, write
    with open(os.path.join(gcodeDir, 'front.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]


def back():
    RASPI_WIDTH = 85
    RASPI_HEIGHT = 56
    RASPI_TOP_RIGHT = (225, 135)
    BOTTOM_BACK_STAND_HOLE = 8
    BOTTOM_BACK_STAND_BUMPER = 8
    BOTTOM_BACK_STAND_FLOORHOLE = 7

    def cut_hook():
        cut(0, 4)
        arc(4, 4, 4, 0, clockwise=True)
        cut(13, 0)
        arc(3, -3, 0, -3, clockwise=True)
        arc(-1, -1, -1, 0, clockwise=True)
        cut(-9, 0)
        cut(0, -4)

    relative()
    # 10mm off the left chart for nicer cut
    move(-10, 190)
    # Cut to 15mm padding
    cut(25, 0)
    # Same as above middle holes: 6x hook - 20mm, one time only hook
    for _ in range(6):
        cut_hook()
        cut(30, 0)
    # the "only hook"
    cut_hook()
    # 10mm to end of hook, 15mm padding, 10mm off the edge
    cut(35, 0)
    move(0, 10)
    # cut outline to bottom
    cut(-210, -210)
    move(10, 10)

    # cut outline back to top
    top_angle = math.atan(100 / 190)
    outer_top_angle = math.radians(90) - top_angle
    overcut_x = math.cos(outer_top_angle) * 10
    overcut_y = math.sin(outer_top_angle) * 10
    # cut a little over the bottom
    cut(overcut_x, -overcut_y)

    absolute()
    cut(0, 190)
    relative()

    # Cut a little over the top
    cut(-overcut_x, overcut_y)

    # Now cut bump at bottom of back so it fits into half moon stand
    absolute()
    move(0, 190)
    relative()
    offset_x = math.sin(top_angle) * BOTTOM_BACK_STAND_HOLE
    offset_y = math.sin(outer_top_angle) * BOTTOM_BACK_STAND_HOLE
    move(offset_x, -offset_y)
    offset_paper_x = math.cos(top_angle) * 4
    offset_paper_y = math.sin(top_angle) * 4
    cut(offset_paper_x, offset_paper_y)
    offset_bumber_x = math.sin(top_angle) * BOTTOM_BACK_STAND_BUMPER
    offset_bumper_y = math.sin(outer_top_angle) * BOTTOM_BACK_STAND_BUMPER
    cut(offset_bumber_x, -offset_bumper_y)
    cut(-offset_paper_x, -offset_paper_y)

    # Cut cable hole
    absolute()
    move(0, 190)
    relative()
    move(250, -20)
    arc(0, 0, 5, 5, clockwise=True)

    absolute()
    move(*RASPI_TOP_RIGHT)
    relative()

    # calculate triangle for rotated raspi rectangle
    width_offset = RASPI_WIDTH * math.sin(math.radians(45))
    height_offset = RASPI_HEIGHT * math.sin(math.radians(45))

    # Cut screw holes.
    # Center of screw hole is -3.5mm -3.5mm from edge
    move(-width_offset, -width_offset)
    move(0, 3.5)
    arc(0, 0, 0, 1.25)
    move((width_offset / RASPI_WIDTH) * 58, (width_offset / RASPI_WIDTH) * 58)
    arc(0, 0, 0, 1.25)
    move(0, -3.5)
    move(-(width_offset / RASPI_WIDTH) * 58,
         -(width_offset / RASPI_WIDTH) * 58)
    move(-height_offset, height_offset)
    move(3.5, 0)
    arc(0, 0, 1.25, 0)
    move((width_offset / RASPI_WIDTH) * 58, (width_offset / RASPI_WIDTH) * 58)
    arc(0, 0, 1.25, 0)

    # Now cut half moon stand plate
    absolute()
    move(220, 10)
    relative()
    cut(50, 0)
    cut(0, 5)
    cut(-5.25, 0)
    cut(0, 4)
    cut(5.25, 0)
    move(-50, -9)
    cut(0, 5)
    cut(5.25, 0)
    cut(0, 4)
    cut(-5.25, 0)
    # Bottom vase done, cut middle T piece
    move(9.75, 0)
    cut(0, -4)
    cut(30.5, 0)
    cut(0, 4)
    cut(-13.25, 0)
    cut(0, BOTTOM_BACK_STAND_HOLE)
    cut(-4, 0)
    cut(0, -BOTTOM_BACK_STAND_HOLE)
    cut(-13.25, 0)
    # cut hole at top
    _radius = BOTTOM_BACK_STAND_HOLE + BOTTOM_BACK_STAND_BUMPER +\
        BOTTOM_BACK_STAND_FLOORHOLE
    move(13.25, _radius)
    cut(0, -BOTTOM_BACK_STAND_FLOORHOLE)
    cut(4, 0)
    cut(0, BOTTOM_BACK_STAND_FLOORHOLE)
    # cut the two circles
    arc(_radius, -_radius, 0, -_radius)
    move(-(_radius + 4), _radius)
    arc(-_radius, -_radius, 0, -_radius, clockwise=False)

    with open(os.path.join(gcodeDir, 'back.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]


if __name__ == '__main__':
    squares()
    front()
    back()
