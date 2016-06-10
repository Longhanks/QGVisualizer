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


import os
import math

from utilities import getResourcesPath
from utilities.types import number


gcodeDir = os.path.join(getResourcesPath(), 'gcode')
steps = []


def move(x: number, y: number) -> None:
    steps.append('G0 X%f Y%f' % (x, y))


def cut(x: number, y: number) -> None:
    steps.append('G1 X%f Y%f' % (x, y))


def comment(cmt: str) -> None:
    steps.append('; ' + cmt)


def arc(x: number, y: number, i: number, j: number,
        clockwise: bool=True) -> None:
    if clockwise:
        cmd = 'G2'
    else:
        cmd = 'G3'
    steps.append(cmd + ' X%f Y%f I%f J%f' % (x, y, i, j))


def arc_radius(x: number, y: number, r: number, clockwise=True) -> None:
    if clockwise:
        cmd = 'G2'
    else:
        cmd = 'G3'
    steps.append(cmd + ' X%f Y%f R%f' % (x, y, r))


def relative() -> None:
    steps.append('G91')


def absolute() -> None:
    steps.append('G90')


def header() -> None:
    steps.append(';header')
    steps.append('G28 ;home')
    steps.append('G21 ;units in mm')
    steps.append('G90 ;abs coords')
    steps.append('M649 L1 P5 S100')
    steps.append('F1000 ;20mm/s')
    steps.append('M649 S100')


def footer() -> None:
    steps.append('; footer')
    steps.append('G90 ;abs coords')
    steps.append('G0 X0 Y230 ;pre-home')
    steps.append('M2')


class Raspi(object):
    width = 85
    height = 56
    screws_offset = 58
    screw_edge_offste = 3.5
    screw_radius = 1.375


class BackBottomHole(object):
    hole = 8
    bumper = 8
    floor_hole = 7


class Material(object):
    width = 290
    height = 200
    thickness = 3.8


class FrontBottomHole(object):
    width = 5
    height = 5


class FrontMiddleHole(object):
    width = 20
    height = Material.thickness


class MotorHole(object):
    width = 22
    height = 11.3
    edge_small_border = 4.5
    edge_long_border = 11
    screw_radius = 1


def squares() -> None:
    header()
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
    footer()
    with open(os.path.join(gcodeDir, 'squares.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]


def front() -> None:
    def cut_bottom_hole() -> None:
        """
        Starts in bottom left corner, moves right & up
        """
        cut(FrontBottomHole.width, 0)
        cut(0, -FrontBottomHole.height)
        cut(-FrontBottomHole.width, 0)

    def cut_middle_hole() -> None:
        """
        Starts in bottom left corner, moves right & up
        """
        cut(0, FrontMiddleHole.height)
        cut(FrontMiddleHole.width, 0)
        cut(0, -FrontMiddleHole.height)
        cut(-FrontMiddleHole.width, 0)

    def cut_motor_hole() -> None:
        """
        Starts in bottom left corner, moves right & up
        """
        move(-(MotorHole.edge_small_border / 2 - MotorHole.screw_radius / 2),
             MotorHole.edge_long_border / 2)
        arc(0, 0, -MotorHole.screw_radius, 0)
        move(MotorHole.edge_small_border / 2 - MotorHole.screw_radius / 2,
             -(MotorHole.edge_long_border / 2))
        cut(0, MotorHole.height)
        cut(MotorHole.width, 0)
        cut(0, -MotorHole.height)
        move(MotorHole.edge_small_border / 2 - MotorHole.screw_radius / 2,
             MotorHole.edge_long_border / 2)
        arc(0, 0, MotorHole.screw_radius, 0)
        move(-(MotorHole.edge_small_border / 2 - MotorHole.screw_radius / 2),
             -(MotorHole.edge_long_border / 2))
        cut(-MotorHole.width, 0)

    header()
    move(0, 120)
    # Start by cutting bottom holes @ 40% height start and 60% height stop
    relative()
    cut_bottom_hole()
    move(0, -30)
    cut_bottom_hole()

    # Move to start point for cutting middle holes
    absolute()
    # 15 padding left, place holes on middle line and move cursor to
    # bottom left
    move(9, Material.height / 2 - FrontMiddleHole.height / 2)  # 15/98
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
    move(240, 170 - MotorHole.height)
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
    footer()
    with open(os.path.join(gcodeDir, 'front.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]


def back():
    def cut_hook():
        cut(0, 3.8)
        arc(4, 4, 4, 0, clockwise=True)
        cut(13, 0)
        arc(3, -3, 0, -3, clockwise=True)
        arc(-1, -1, -1, 0, clockwise=True)
        cut(-5, 0)
        cut(0, -3.8)
        cut(6, 0)

    top_angle = math.atan(100 / 190)
    outer_top_angle = math.radians(90) - top_angle

    header()

    # Cut cable hole
    absolute()
    move(250, 170)
    relative()
    arc(0, 0, 5, 5, clockwise=True)

    absolute()
    move(225, 135)
    relative()

    # calculate triangle for rotated raspi rectangle
    width_offset = Raspi.width * math.sin(math.radians(45))
    height_offset = Raspi.height * math.sin(math.radians(45))

    # Cut screw holes.
    move(-width_offset, -width_offset)
    move(0, Raspi.screw_edge_offste)
    arc(0, 0, 0, Raspi.screw_radius)
    move((width_offset / Raspi.width) * Raspi.screws_offset,
         (width_offset / Raspi.width) * Raspi.screws_offset)
    arc(0, 0, 0, Raspi.screw_radius)
    move(0, -Raspi.screw_edge_offste)
    move(-(width_offset / Raspi.width) * Raspi.screws_offset,
         -(width_offset / Raspi.width) * Raspi.screws_offset)
    move(-height_offset, height_offset)
    move(Raspi.screw_edge_offste, 0)
    arc(0, 0, Raspi.screw_radius, 0)
    move((width_offset / Raspi.width) * Raspi.screws_offset,
         (width_offset / Raspi.width) * Raspi.screws_offset)
    arc(0, 0, Raspi.screw_radius, 0)

    # Now cut half moon stand plate
    absolute()
    move(20, 10)
    relative()
    cut(50, 0)
    cut(0, 5)
    cut(-5, 0)
    cut(0, Material.thickness)
    cut(5, 0)
    move(-50, -5 - Material.thickness)
    cut(0, 5)
    cut(5, 0)
    cut(0, Material.thickness)
    cut(-5, 0)
    # Bottom vase done, cut middle T piece
    move(10, 0)
    cut(0, -Material.thickness)
    cut(30, 0)
    cut(0, Material.thickness)
    cut(-(15 - Material.thickness / 2), 0)
    cut(0, BackBottomHole.hole)
    cut(-Material.thickness, 0)
    cut(0, -BackBottomHole.hole)
    cut(-(15 - Material.thickness / 2), 0)
    # cut hole at top
    _radius = BackBottomHole.hole + BackBottomHole.bumper + \
        BackBottomHole.floor_hole
    move(15 - Material.thickness / 2, _radius)
    cut(0, -BackBottomHole.floor_hole)
    cut(Material.thickness, 0)
    cut(0, BackBottomHole.floor_hole)
    # cut the two circles
    arc(_radius, -_radius, 0, -_radius)
    move(-(_radius + Material.thickness), _radius)
    arc(-_radius, -_radius, 0, -_radius, clockwise=False)

    # Now cut bump at bottom of back so it fits into half moon stand
    absolute()
    move(0, 190)
    relative()
    offset_x = math.sin(top_angle) * BackBottomHole.hole
    offset_y = math.sin(outer_top_angle) * BackBottomHole.hole
    move(offset_x, -offset_y)
    offset_paper_x = math.cos(top_angle) * Material.thickness
    offset_paper_y = math.sin(top_angle) * Material.thickness
    cut(offset_paper_x, offset_paper_y)
    offset_bumber_x = math.sin(top_angle) * BackBottomHole.bumper
    offset_bumper_y = math.sin(outer_top_angle) * BackBottomHole.bumper
    cut(offset_bumber_x, -offset_bumper_y)
    cut(-offset_paper_x, -offset_paper_y)

    # Start frame
    absolute()
    move(0, 190)
    relative()
    # Cut to 15mm padding
    cut(15, 0)
    # Same as middle holes: 6x hook - 20mm, one time only hook
    for _ in range(6):
        cut_hook()
        cut(20, 0)
    # the "only hook"
    cut_hook()
    # 10mm to end of hook, 15mm padding, 10mm off the edge
    cut(15, 0)
    # cut outline to bottom
    cut(-190, -190)

    # cut outline back to top
    absolute()
    cut(0, 190)
    relative()

    footer()
    with open(os.path.join(gcodeDir, 'back.gcode'), 'w') as gcode:
        gcode.write('\n'.join(steps))
    del steps[:]


if __name__ == '__main__':
    squares()
    front()
    back()
