from ctypes import (
    Structure, POINTER, CFUNCTYPE, CDLL, pointer,
    c_int, c_ubyte, c_double, c_size_t, c_char_p,
    c_char
)


class color(Structure):
    _fields_ = [
        ('r', c_ubyte),
        ('g', c_ubyte),
        ('b', c_ubyte),
    ]

    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def to_tuple(self):
        return (self.r, self.g, self.b)

    def to_html(self):
        return "#{s.r:02x}{s.g:02x}{s.b:02x}".format(s=self)

    def pack_rgba(self):
        acc = 0
        acc += self.r << 24
        acc += self.g << 16
        acc += self.b << 8
        return acc

    def pack_rgb(self):
        acc = 0
        acc += self.r << 16
        acc += self.g << 8
        acc += self.b
        return acc


class qcolor(Structure):
    _fields_ = [
        ('r', c_double),
        ('g', c_double),
        ('b', c_double),
    ]

    def __init__(self, r=0.0, g=0.0, b=0.0):
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    def _color_quantize(val):
        return max(0, min(255, int(128 * (val + 1))))

    def to_color(self):
        out = color()
        out.r = qcolor._color_quantize(self.r)
        out.g = qcolor._color_quantize(self.g)
        out.b = qcolor._color_quantize(self.b)
        return out

    def to_tuple(self):
        return (self.r, self.g, self.b)

    def apply_filter(self, func):
        out = qcolor()
        out.r = func(self.r)
        out.g = func(self.g)
        out.b = func(self.b)
        return out

    def __repr__(self):
        return "qcolor(%g, %g, %g)" % (self.r, self.g, self.b)


class transforminfo(Structure):

    def __call__(self, x, y):
        return self.eval(x, y)


transforminfo_apply = CFUNCTYPE(
    qcolor, POINTER(transforminfo), c_double, c_double)

transforminfo_inspect = CFUNCTYPE(
    c_int, POINTER(transforminfo), c_char_p, c_size_t)

transforminfo._fields_ = [
    ('apply', transforminfo_apply),
    ('inspect', transforminfo_inspect),
    ('subslots', POINTER(transforminfo) * 4),
    ('data', c_char * 80)
]


try:
    librandomart = CDLL('./librandomart.so')
except OSError:
    librandomart = None


_transformer_func = [POINTER(transforminfo), c_double, c_double]


librandomart.ra_variable_x_init.restype = None
librandomart.ra_variable_x_init.argtypes = [POINTER(transforminfo)]
librandomart.ra_variable_x.restype = qcolor
librandomart.ra_variable_x.argtypes = _transformer_func


class ra_variable_x(transforminfo):
    def __init__(self):
        transforminfo.__init__(self)
        librandomart.ra_variable_x_init(pointer(self))

    def eval(self, x, y):
        return librandomart.ra_variable_x(self, x, y)


librandomart.ra_variable_y_init.restype = None
librandomart.ra_variable_y_init.argtypes = [POINTER(transforminfo)]
librandomart.ra_variable_y.restype = qcolor
librandomart.ra_variable_y.argtypes = _transformer_func


class ra_variable_y(transforminfo):
    def __init__(self):
        transforminfo.__init__(self)
        librandomart.ra_variable_y_init(pointer(self))

    def eval(self, x, y):
        return librandomart.ra_variable_y(pointer(self), x, y)


librandomart.ra_constant_init.restype = None
librandomart.ra_constant_init.argtypes = [
    POINTER(transforminfo), c_double, c_double, c_double]
librandomart.ra_constant.restype = qcolor
librandomart.ra_constant.argtypes = _transformer_func


class ra_constant(transforminfo):
    def __init__(self, r, g, b):
        transforminfo.__init__(self)
        librandomart.ra_constant_init(pointer(self), r, g, b)

    def eval(self, x, y):
        return librandomart.ra_constant(pointer(self), x, y)


librandomart.ra_sum_init.restype = None
librandomart.ra_sum_init.argtypes = [
    POINTER(transforminfo),
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_sum.restype = qcolor
librandomart.ra_sum.argtypes = _transformer_func


class ra_sum(transforminfo):
    def __init__(self, e1, e2):
        assert isinstance(e1, transforminfo)
        assert isinstance(e2, transforminfo)
        self._pins = (e1, e2)  # pin to avoid garbage collection
        librandomart.ra_sum_init(
            pointer(self), pointer(e1), pointer(e2))

    def eval(self, x, y):
        return librandomart.ra_sum(pointer(self), x, y)


librandomart.ra_product_init.restype = None
librandomart.ra_product_init.argtypes = [
    POINTER(transforminfo),
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_product.restype = qcolor
librandomart.ra_product.argtypes = _transformer_func


class ra_product(transforminfo):
    def __init__(self, e1, e2):
        assert isinstance(e1, transforminfo)
        assert isinstance(e2, transforminfo)
        self._pins = (e1, e2)  # pin to avoid garbage collection
        librandomart.ra_product_init(
            pointer(self), pointer(e1), pointer(e2))

    def eval(self, x, y):
        return librandomart.ra_product(pointer(self), x, y)


librandomart.ra_mod_init.restype = None
librandomart.ra_mod_init.argtypes = [
    POINTER(transforminfo),
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_mod.restype = qcolor
librandomart.ra_mod.argtypes = _transformer_func


class ra_mod(transforminfo):
    def __init__(self, e1, e2):
        assert isinstance(e1, transforminfo)
        assert isinstance(e2, transforminfo)
        self._pins = (e1, e2)  # pin to avoid garbage collection
        librandomart.ra_mod_init(
            pointer(self), pointer(e1), pointer(e2))

    def eval(self, x, y):
        return librandomart.ra_mod(pointer(self), x, y)


librandomart.ra_well_init.restype = None
librandomart.ra_well_init.argtypes = [
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_well.restype = qcolor
librandomart.ra_well.argtypes = _transformer_func


class ra_well(transforminfo):
    def __init__(self, e1):
        assert isinstance(e1, transforminfo)
        self._pins = (e1, )  # pin to avoid garbage collection
        librandomart.ra_well_init(
            pointer(self), pointer(e1))

    def eval(self, x, y):
        return librandomart.ra_well(pointer(self), x, y)


librandomart.ra_tent_init.restype = None
librandomart.ra_tent_init.argtypes = [
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_tent.restype = qcolor
librandomart.ra_tent.argtypes = _transformer_func


class ra_tent(transforminfo):
    def __init__(self, e1):
        assert isinstance(e1, transforminfo)
        self._pins = (e1, )  # pin to avoid garbage collection
        librandomart.ra_tent_init(
            pointer(self), pointer(e1))

    def eval(self, x, y):
        return librandomart.ra_tent(pointer(self), x, y)


librandomart.ra_sin_init.restype = None
librandomart.ra_sin_init.argtypes = [
    POINTER(transforminfo),
    c_double, c_double,
    POINTER(transforminfo)
]
librandomart.ra_sin.restype = qcolor
librandomart.ra_sin.argtypes = _transformer_func


class ra_sin(transforminfo):
    def __init__(self, phase, freq, e1):
        assert isinstance(e1, transforminfo)
        self._pins = (e1, )  # pin to avoid garbage collection
        librandomart.ra_sin_init(
            pointer(self), phase, freq, pointer(e1))

    def eval(self, x, y):
        return librandomart.ra_sin(pointer(self), x, y)


librandomart.ra_level_init.restype = None
librandomart.ra_level_init.argtypes = [
    POINTER(transforminfo),
    c_double,
    POINTER(transforminfo),
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_level.restype = qcolor
librandomart.ra_level.argtypes = _transformer_func


class ra_level(transforminfo):
    def __init__(self, threshold, level, e1, e2):
        assert isinstance(e1, transforminfo)
        self._pins = (level, e1, e2, )  # pin to avoid garbage collection
        librandomart.ra_level_init(
            pointer(self), threshold, pointer(level),
            pointer(e1), pointer(e2))

    def eval(self, x, y):
        return librandomart.ra_level(pointer(self), x, y)


librandomart.ra_mix_init.restype = None
librandomart.ra_mix_init.argtypes = [
    POINTER(transforminfo),
    POINTER(transforminfo),
    POINTER(transforminfo),
    POINTER(transforminfo)
]
librandomart.ra_mix.restype = qcolor
librandomart.ra_mix.argtypes = _transformer_func


class ra_mix(transforminfo):
    def __init__(self, level, e1, e2):
        assert isinstance(e1, transforminfo)
        self._pins = (level, e1, e2, )  # pin to avoid garbage collection
        librandomart.ra_mix_init(
            pointer(self), pointer(level),
            pointer(e1), pointer(e2))

    def eval(self, x, y):
        return librandomart.ra_mix(pointer(self), x, y)

