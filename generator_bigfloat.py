#!/usr/bin/env python
# encoding: utf-8


# NOTE: this generator do not work yet
#       need to increase the precision in steps
#       and maybe find a standard lib instead of bigfloat


# http://www.eveandersson.com/pi/
# http://www.angio.net/pi/piquery
# http://rosettacode.org/wiki/Pi#Python
# ftp://pi.super-computing.org/
# http://piworld.calico.jp/estart.html
# http://www.joyofpi.com/pilinks.html

# https://pythonadventures.wordpress.com/tag/gibbons-spigot-algorithm-for-pi/

from bigfloat import precision
import bigfloat
 
s = str(bigfloat.atan2(+0.0,-0.0,precision(100000000)))
print(len(s))
