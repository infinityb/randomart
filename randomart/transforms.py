import ctypes
import os
import math

from .formats import qcolor


# Shared library loader

try:
    librandomart = ctypes.CDLL('./librandomart.so')
except OSError:
    librandomart = None


blacklist_natives = set([])


def _compare_factory(pyfunc, natfunc):
    print "_compare_factory contructed"

    def decorated(*args):
        out_b = qcolor()
        pyfunc(*args)
        natfunc(*(args[:-1] + (out_b, )))
        if not args[-1] == out_b:
            raise ValueError("{!r} != {!r} @ {!r} for {!r}".format(
                args[-1], out_b, pyfunc, args))
    return decorated


def _ll_loadcomonent(symbol_name, argtypes):
    try:
        impl = getattr(librandomart, symbol_name)
    except AttributeError:
        return None
    impl.restype = None
    impl.argtypes = argtypes
    return impl


def _loadcomponent(python_function, symbol_name, argtypes):
    if bool(int(os.environ.get('RA_NONATIVE', '0'))):
        return python_function
    if symbol_name in blacklist_natives:
        return python_function
    impl = _ll_loadcomonent(symbol_name, argtypes)
    if impl is None:
        return python_function
    if bool(int(os.environ.get('RA_COMPARE', '0'))):
        return _compare_factory(python_function, impl)
    return impl


# Utility functions

def _well(x):
    '''A function which looks a bit like a well.'''
    return 1 - 2 / (1 + x * x) ** 8


def _tent(x):
    '''A function that looks a bit like a tent.'''
    return 1 - 2 * abs(x)


def _py_average_impl(c1, c2, weight, out):
    '''Compute the weighted average of two colors. With w = 0.5 we get the
    average.'''
    out.r = weight * c1.r + (1 - weight) * c2.r
    out.g = weight * c1.g + (1 - weight) * c2.g
    out.b = weight * c1.b + (1 - weight) * c2.b


average_impl = _loadcomponent(
    _py_average_impl,
    'qcolor_average', (
        qcolor, qcolor,
        ctypes.c_double,
        ctypes.POINTER(qcolor)
    ))


def _py_tent_impl(c1, out):
    out.r = _tent(c1.r)
    out.g = _tent(c1.g)
    out.b = _tent(c1.b)


tent_impl = _loadcomponent(
    _py_tent_impl,
    'qcolor_tent', (
        qcolor, ctypes.POINTER(qcolor)
    ))


def _py_well_impl(c1, out):
    out.r = _well(c1.r)
    out.g = _well(c1.g)
    out.b = _well(c1.b)


well_impl = _loadcomponent(
    _py_well_impl,
    'qcolor_well', (
        qcolor, ctypes.POINTER(qcolor)
    ))


def _py_prod_impl(c1, c2, output):
    output.r = c1.r * c2.r
    output.g = c1.g * c2.g
    output.b = c1.b * c2.b


prod_impl = _loadcomponent(
    _py_prod_impl,
    'qcolor_product', (
        qcolor, qcolor,
        ctypes.POINTER(qcolor)
    ))


def _py_mod_impl(c1, c2, out):
    out.r = c1.r % c2.r
    out.g = c1.g % c2.g
    out.b = c1.b % c2.b


mod_impl = _loadcomponent(
    _py_mod_impl,
    'qcolor_mod', (
        qcolor, qcolor,
        ctypes.POINTER(qcolor)
    ))


def _py_sin_impl(c, phase, freq, out):
    out.r = math.sin(phase + freq * c.r)
    out.g = math.sin(phase + freq * c.g)
    out.b = math.sin(phase + freq * c.b)


sin_impl = _loadcomponent(
    _py_sin_impl,
    'qcolor_sin', (
        qcolor, ctypes.c_double, ctypes.c_double,
        ctypes.POINTER(qcolor)
    ))


def _py_level_impl(threshold, c1, c2, c3, out):
    out.r = c2.r if c1.r < threshold else c3.r
    out.g = c2.g if c1.g < threshold else c3.g
    out.b = c2.b if c1.b < threshold else c3.b


level_impl = _loadcomponent(
    _py_level_impl,
    'qcolor_level', (
        ctypes.c_double,
        qcolor, qcolor, qcolor,
        ctypes.POINTER(qcolor)
    ))


__all__ = """
    average_impl tent_impl well_impl prod_impl mod_impl
    sin_impl level_impl
""".split()
