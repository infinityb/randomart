#!/usr/bin/python
import sys
from time import time
from itertools import count
import random

from PIL import Image
from randomart import _PILArt, generate


initial_count = 0
if sys.argv[1:]:
    initial_count = int(sys.argv[1], 16)


def create_image(art_def, use_native, side_len):
    image = Image.new("RGB", (side_len, side_len))
    art_impl = _PILArt(image)
    art_impl.set_art(art_def)
    if use_native:
        art_impl.reify()
    art_impl.redraw()
    return image


for i in count(initial_count):
    art_definition = generate(random.randrange(20, 150))
    # print("processing %r" % art_definition)
    # create_image(art_definition, False, 256).save('out/out%08x_p.png' % i)
    # print('   out/out%08x_p.png written' % i)

    t_i = time()
    img = create_image(art_definition, True, 512)
    t_f = time()
    img.save('out/out%08x_n.png' % i)
    print('   out/out%08x_n.png written (rendered in %gs)' % (i, t_f - t_i))
