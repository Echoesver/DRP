#!/usr/bin/env python
import django
django.setup()
from sys import argv


fn1 = argv[1]
fn2 = argv[2]

with open(fn1) as f:
    h1 = set(f.readlines())

with open(fn2) as f:
    h2 = set(f.readlines())

h_intersect = h1.intersection(h2)
try:
    h_intersect.remove('\n')
except KeyError:
    pass

print ''.join(sorted(h_intersect, key=lambda x: x.lower())),
