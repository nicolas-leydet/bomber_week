from game1 import intersect
from collections import namedtuple



BB = namedtuple('BB', ['x', 'y', 'rx', 'ry'])

a = BB(4, 5, 1, 1)
b = BB(4, 5, 2, 3)
c = BB(7.5, 2, 6.5, 1)
d = BB(12, 3.5, 1, 1.5)
e = BB(10, 5, 2, 1)

import pdb; pdb.set_trace()  # XXX BREAKPOINT

assert(intersect(a, b))
assert(intersect(b, c))
assert(intersect(c, d))
assert(intersect(d, e))


