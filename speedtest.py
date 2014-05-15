#!/usr/bin/python
from itertools import count
from randomart import memoryslab_create_image
from cStringIO import StringIO


with open('testspeed.art.pickle', 'rb') as artfh:
    with open('/dev/null', 'w+') as fh:
        out = StringIO()
        memoryslab_create_image(1024, artfh).save(out)
        print("len = %d" % out.tell())

