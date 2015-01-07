#!/usr/bin/env python
# encoding: utf-8

import sys


COLS = int(sys.argv[1]) if len(sys.argv) == 2 else 50


##############################################################################
# Unbounded Spigot Algorithms for the Digits of Pi
# http://web.comlab.ox.ac.uk/oucl/work/jeremy.gibbons/publications/spigot.pdf
# S. Rabinowitz and S. Wagon

# http://davidbau.com/archives/2010/03/14/python_pipy_spigot.html
##############################################################################

def pi_decimal_generator():
  q, r, t, j = 1, 180, 60, 2
  while True:
    u, y = 3*(3*j+1)*(3*j+2), (q*(27*j-12)+5*r)//(5*t)
    yield str(y)
    q, r, t, j = 10*q*j*(2*j-1), 10*u*(q*(5*j-2)+r-y*t), t*u, j+1


digits = pi_decimal_generator()
digits.next()
while 1:
    print(''.join([digits.next() for j in xrange(COLS)]))
    sys.stdout.flush()

