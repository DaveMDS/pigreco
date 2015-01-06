#!/usr/bin/env python
# encoding: utf-8


##############################################################################
# algoritmo "streaming" di Gibbons , Rabinowiz, Wagon,...
# http://web.comlab.ox.ac.uk/oucl/work/jeremy.gibbons/publications/spigot.pdf
# S. Rabinowitz and S. Wagon, A spigot algorithm for the digits of pi, Amer. Math. Monthly 102 (1995) 195–203.

# http://davidbau.com/archives/2010/03/14/python_pipy_spigot.html
def pi_decimal_digits():
  q, r, t, j = 1, 180, 60, 2
  while True:
    u, y = 3*(3*j+1)*(3*j+2), (q*(27*j-12)+5*r)//(5*t)
    yield y
    q, r, t, j = 10*q*j*(2*j-1), 10*u*(q*(5*j-2)+r-y*t), t*u, j+1

## Usage:
# count = 0
# digits = pi_decimal_digits()
# while 1:
#   line = ''.join([str(digits.next()) for j in xrange(50)])
#   print '%6d: %s' % (count, line)
#   count += 50

##############################################################################

from multiprocessing import Process, Queue, Event

from efl import ecore
from efl import evas
from efl.evas import EVAS_TEXTGRID_PALETTE_STANDARD, \
    EVAS_HINT_EXPAND, EXPAND_BOTH, EXPAND_HORIZ, EXPAND_VERT, \
    EVAS_HINT_FILL, FILL_BOTH, FILL_HORIZ, FILL_VERT

from efl import elementary
from efl.elementary.window import StandardWindow
from efl.elementary.label import Label
from efl.elementary.entry import Entry


class PigrecoThread(Process):
    def __init__(self, queue):
        Process.__init__(self)

        self._queue = queue
        self._stop = Event()
        self._digit_generator = pi_decimal_digits()

    def stop(self):
        self._stop.set()

    def run(self):
        count = 0

        while 1:
            line = ''.join([str(self._digit_generator.next()) for j in range(50)])
            self._queue.put((count, line))
            count += 50

            if self._stop.is_set():
                break

        print("DONE")



class PiWin(StandardWindow):
    def __init__(self, app):

        StandardWindow.__init__(self, "pigreco", "π", autodel=True, size=(500,500))
        self.callback_delete_request_add(lambda o: app.quit())

        lb = Label(self, text="π", scale=20, size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        self.resize_object_add(lb)
        lb.show()

        tg = TG(self)
        self.resize_object_add(tg)
        tg.show()


        self.tg = tg
        self.app = app
        self.show()


class TG(evas.Textgrid):
    width = 40
    height = 15
    def __init__(self, parent):

        self.lines = []
        evas.Textgrid.__init__(self, parent.evas,
                               size=(self.width, self.height),
                               font=("Courier", 24))

        self.palette_set(EVAS_TEXTGRID_PALETTE_STANDARD, 0, 0, 0, 0, 100)
        self.palette_set(EVAS_TEXTGRID_PALETTE_STANDARD, 1, 0, 255, 255, 255)

        pxw, pxh = self.cell_size
        self.size_hint_min=(pxw * self.width, pxh * self.height)

        self.fill()

    def fill(self):
        for row_count in range(self.height):
            row = self.cellrow_get(row_count)
            for cell in row:
                cell.codepoint = 'π'
                cell.fg = 1
                cell.bg = 0
            self.cellrow_set(row_count, row)


class Pigreco(object):
    def __init__(self):

        self.win = PiWin(self)
        self.queue = Queue()
        self.thread = PigrecoThread(self.queue)
        self.thread.start()

        ecore.Timer(0.1, self.timer_cb)

    def quit(self):
        self.thread.stop()
        self.thread.join()
        elementary.exit()
        
    def timer_cb(self):
        if self.queue.empty():
            return ecore.ECORE_CALLBACK_RENEW

        count, line = self.queue.get()
        print(self.queue.qsize(), count, line)

        return ecore.ECORE_CALLBACK_RENEW


if __name__ == "__main__":
    elementary.init()

    Pigreco()

    elementary.run()
    elementary.shutdown()

