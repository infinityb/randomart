#!/usr/bin/python

# Copyright (c) 2010, Andrej Bauer, http://andrej.com/
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
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

######################################################################
# SIMPLE RANDOM ART IN PYTHON
#
# Version 2010-04-21
#
# I get asked every so often to release the source code for my random art
# project at http://www.random-art.org/. The original source is written in
# Ocaml and is not publicly available, but here is a simple example of how
# you can get random art going in python in 250 lines of code.
#
# The idea is to generate expression trees that describe an image. For each
# point (x,y) of the image we evaluate the expression and get a color. A color
# is represented as a triple (r,g,b) where the red, green, blue components are
# numbers between -1 and 1. In computer graphics it is more usual to use the
# range [0,1], but since many operations are symmetric with respect to the
# origin it is more convenient to use the interval [-1,1].
#
# I kept the program as simple as possible, and independent of any non-standard
# Python libraries. Consequently, a number of improvements and further
# experiments are possible:
#
#   * The most pressing problem right now is that the image is displayed as a
#     large number of rectangles of size 1x1 on the tkinter Canvas, which
#     consumes a great deal of memory. You will not be able to draw large
#     images this way. An improved version would use the Python imagining
#     library (PIL) instead.
#
#   * The program uses a simple RGB (Red Green Blue) color model. We could also
#     use the HSV model (Hue Saturation Value), and others. One possibility is
#     to generate a palette of colors and use only colors that are combinations
#     of those from the palette.
#
#   * Of course, you can experiment by introducing new operators. If you are
#     going to play with the source, your first exercise should be a new
#     operator.
#
#   * The program uses cartesian coordinates. You could experiment with polar
#     coordinates.
#
# For more information and further discussion,
# see http://math.andrej.com/category/random-art/

## before
## 1400093876.27: out/out00000000.png written
## 1400093948.94: out/out00000001.png written
## 1400094129.59: out/out00000002.png written
## 1400094329.24: out/out00000003.png written
## 1400094527.72: out/out00000004.png written
## 1400094587.85: out/out00000005.png written
## 1400094637.49: out/out00000006.png written
## 1400094718.03: out/out00000007.png written
## 1400094823.81: out/out00000008.png written

import math
import random
import cPickle as pickle
from .formats import qcolor
from . import formats
from .transforms import (
    average_impl, tent_impl,
    well_impl, prod_impl,
    mod_impl, sin_impl,
    level_impl)


# We next define classes that represent expression trees.

# Each object that reprents and expression should be a callable which
# computes the value of the expression at (x,y). The __init__ should
# accept the objects representing its subexpressions. The class definition
# should contain the arity attribute which tells how many subexpressions should
# be passed to the __init__ constructor.

class VariableX(object):
    arity = 0

    def __init__(self):
        pass

    def __repr__(self):
        return "x"

    def reify(self):
        return formats.ra_variable_x()

    def eval(self, x, y):
        return formats.ra_variable_x()(x, y)


class VariableY(object):
    arity = 0

    def __init__(self):
        pass

    def __repr__(self):
        return "y"

    def reify(self):
        return formats.ra_variable_y()

    def eval(self, x, y):
        return qcolor(y, y, y)


class Constant(object):
    arity = 0

    def __init__(self, xargs=None):
        if xargs is None:
            xargs = qcolor(
                random.uniform(0, 1),
                random.uniform(0, 1),
                random.uniform(0, 1)
            )
        self.c = xargs

    def __repr__(self):
        return 'Constant(%r)' % (self.c, )

    def reify(self):
        return formats.ra_constant(
            self.c.r, self.c.g, self.c.b)

    def eval(self, x, y):
        return self.c


class Sum(object):
    arity = 2

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Sum(%s, %s)' % (self.e1, self.e2)

    def reify(self):
        return formats.ra_sum(self.e1.reify(), self.e2.reify())

    def eval(self, x, y):
        out = qcolor()
        average_impl(
            self.e1.eval(x, y),
            self.e2.eval(x, y),
            0.5, out)
        return out


class Product(object):
    arity = 2

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Product(%s, %s)' % (self.e1, self.e2)

    def reify(self):
        return formats.ra_product(self.e1.reify(), self.e2.reify())

    def eval(self, x, y):
        out = qcolor()
        prod_impl(self.e1.eval(x, y), self.e2.eval(x, y), out)
        return out


class Mod(object):
    arity = 2

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Mod(%s, %s)' % (self.e1, self.e2)

    def reify(self):
        return formats.ra_mod(self.e1.reify(), self.e2.reify())

    def eval(self, x, y):
        out = qcolor()
        c2 = self.e1.eval(x, y)
        if 0.0 not in (c2.r, c2.g, c2.b):
            mod_impl(self.e1.eval(x, y), c2, out)
        return out


class Well(object):
    arity = 1

    def __init__(self, e):
        self.e = e

    def __repr__(self):
        return 'Well(%s)' % self.e

    def reify(self):
        return formats.ra_well(self.e.reify())

    def eval(self, x, y):
        out = qcolor()
        well_impl(self.e.eval(x, y), out)
        return out


class Tent(object):
    arity = 1

    def __init__(self, e):
        self.e = e

    def __repr__(self):
        return 'Tent(%s)' % self.e

    def reify(self):
        return formats.ra_tent(self.e.reify())

    def eval(self, x, y):
        out = qcolor()
        tent_impl(self.e.eval(x, y), out)
        return out


class Sin(object):
    arity = 1

    def __init__(self, e):
        self.e = e
        self.phase = random.uniform(0, math.pi)
        self.freq = random.uniform(1.0, 6.0)

    def __repr__(self):
        return 'Sin(%g + %g * %s)' % (self.phase, self.freq, self.e)

    def reify(self):
        return formats.ra_sin(self.phase, self.freq, self.e.reify())

    def eval(self, x, y):
        out = qcolor()
        sin_impl(self.e.eval(x, y), self.phase, self.freq, out)
        return out


class Level(object):
    arity = 3

    def __init__(self, level, e1, e2):
        self.treshold = random.uniform(-1.0, 1.0)
        self.level = level
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Level({0.treshold:g}, {0.level}, {0.e1}, {0.e2})'.format(self)

    def reify(self):
        return formats.ra_level(
            self.treshold,
            self.level.reify(),
            self.e1.reify(),
            self.e2.reify())

    def eval(self, x, y):
        out = qcolor()
        level_impl(
            self.treshold, self.level.eval(x, y),
            self.e1.eval(x, y), self.e2.eval(x, y), out)
        return out


class Mix(object):
    arity = 3

    def __init__(self, w, e1, e2):
        self.w = w
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return 'Mix(%s, %s, %s)' % (self.w, self.e1, self.e2)

    def reify(self):
        return formats.ra_mix(
            self.w.reify(),
            self.e1.reify(),
            self.e2.reify())

    def eval(self, x, y):
        w = 0.5 * (self.w.eval(x, y).r + 1.0)
        out = qcolor()
        average_impl(
            self.e1.eval(x, y),
            self.e2.eval(x, y),
            w, out)
        return out


# The following list of all classes that are used for generation of expressions
# is used by the generate function below.
operators = (
    VariableX, VariableY, Constant, Sum,
    Product, Sin, Level, Mix, Mod,
    Well, Tent
)

# We precompute those operators that have arity 0 and arity > 0
operators0 = [op for op in operators if op.arity == 0]
operators1 = [op for op in operators if op.arity > 0]


def generate(k=50):
    '''Randonly generate an expession of a given size.'''
    if k <= 0:
        # We used up available size, generate a leaf of the expression tree
        op = random.choice(operators0)
        return op()
    else:
        # randomly pick an operator whose arity > 0
        op = random.choice(operators1)
        # generate subexpressions
        i = 0  # the amount of available size used up so far
        args = []  # the list of generated subexpression
        for j in sorted([random.randrange(k) for l in range(op.arity - 1)]):
            args.append(generate(j - i))
            i = j
        args.append(generate(k - 1 - i))
        return op(*args)


class BaseArt(object):
    initial_square_size = 1

    def __init__(self, size):
        self.size = size
        self.d = self.initial_square_size  # current square size
        self.y = 0  # current row

    def setup_art(self):
        self.set_art(generate(random.randrange(20, 150)))
        # self.set_art(generate(random.randrange(5, 15)))

    def set_art(self, art):
        self.art = art
        self.art_reified = None

    def reify(self):
        self.art_reified = self.art.reify()

    def redraw(self):
        for _ in self._do_draw_rounds():
            pass

    def get_pixel(self, (x, y), d):
        u = 2 * float(x + d / 2) / self.size - 1.0
        v = 2 * float(y + d / 2) / self.size - 1.0
        if self.art_reified is not None:
            return self.art_reified.eval(u, v)
        else:
            return self.art.eval(u, v)

    def _do_draw_rounds(self, inv_resolution=1):
        # for x in range(0, self.size, inv_resolution):
        #     for y in range(0, self.size, inv_resolution):
        #         get_pixel(x, y)
        d = 1
        for x in range(0, self.size):
            for y in range(0, self.size):
                px_color = self.get_pixel((x, y), d)
                self._draw_rectangle(
                    ((x, y), (x + d, y + d)),
                    fill=px_color.to_color())
            yield


class _PILArt(BaseArt):
    def __init__(self, target):
        from PIL import ImageDraw
        (side_length_x, side_length_y) = target.size
        if side_length_y != side_length_x:
            raise TypeError("side lengths must be equal")
        super(_PILArt, self).__init__(side_length_x)
        self.target_drawable = ImageDraw.Draw(target)

    def _draw_rectangle(self, location, fill):
        self.target_drawable.rectangle(
            location, fill=fill.to_tuple(), outline=None)


import struct
from array import array
from itertools import repeat


class MemorySlabArt(BaseArt):
    def __init__(self, size):
        super(MemorySlabArt, self).__init__(size)
        self.target = array('i', repeat(0, size * size))

    def set_pixel(self, (x, y), fill):
        self.target[x * self.size + y] = fill.pack_rgb()

    def _draw_rectangle(self, location, fill):
        ((x_i, y_i), (x_f, y_f)) = location
        for x in range(x_i, x_f):
            for y in range(y_i, y_f):
                self.set_pixel((x, y), fill)

    def save(self, outfh):
        outfh.write(struct.pack('!I', self.size))
        outfh.write(struct.pack('!I', self.size))
        for i in xrange(self.size * self.size):
            outfh.write(struct.pack('!I', self.target[i]))


def pil_create_image(side_length, artfh=None):
    from PIL import Image
    image = Image.new("RGB", (side_length, side_length))
    art_impl = _PILArt(image)
    if artfh is not None:
        art_impl.set_art(pickle.load(artfh))
    else:
        art_impl.setup_art()
    art_impl.redraw()
    return image


def memoryslab_create_image(side_length, artfh=None):
    art_impl = MemorySlabArt(side_length)
    if artfh is not None:
        art_impl.set_art(pickle.load(artfh))
    else:
        art_impl.setup_art()
    art_impl.redraw()
    return art_impl


# class TkArt(BaseArt):
#     """A simple graphical user interface for random art. It displays the
#     image, and the 'Again!' button."""
#     initial_square_size = 64

#     def __init__(self, master, size=256):
#         super(TkArt, self).__init__(size=size)
#         master.title('Random art')
#         self.canvas = Canvas(master, width=size, height=size)
#         self.canvas.grid(row=0, column=0)
#         b = Button(master, text='Again!', command=self.redraw)
#         b.grid(row=1, column=0)
#         self.draw_alarm = None
#         self.redraw()

#     def _draw_rectangle(self, location, width, fill):
#         ((x_i, y_i), (x_f, y_f)) = location
#         self.canvas.create_rectangle(
#             x_i, y_i, x_f, y_f,
#             fill=fill)

#     def redraw(self):
#         self.setup_art()
#         if self.draw_alarm:
#             self.canvas.after_cancel(self.draw_alarm)
#         self.canvas.delete(ALL)
#         coroutine = self._do_draw_rounds()
#         self.draw_alarm = self.canvas.after(1, partial(next, coroutine))


# from Tkinter import Canvas, Tk, Button, ALL
# # Main program
# win = Tk()
# arg = TkArt(win)
# win.mainloop()
