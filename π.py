#!/usr/bin/env python
# encoding: utf-8


##############################################################################
# Unbounded Spigot Algorithms for the Digits of Pi
# http://web.comlab.ox.ac.uk/oucl/work/jeremy.gibbons/publications/spigot.pdf
# S. Rabinowitz and S. Wagon

# http://davidbau.com/archives/2010/03/14/python_pipy_spigot.html
def pi_decimal_generator():
  q, r, t, j = 1, 180, 60, 2
  while True:
    u, y = 3*(3*j+1)*(3*j+2), (q*(27*j-12)+5*r)//(5*t)
    yield str(y)
    q, r, t, j = 10*q*j*(2*j-1), 10*u*(q*(5*j-2)+r-y*t), t*u, j+1

## Usage:
# count = 0
# digits = pi_decimal_generator()
# while 1:
#   line = ''.join([digits.next() for j in xrange(50)])
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

COLS = 40
ROWS = 15

class PigrecoThread(Process):
    def __init__(self, queue):
        Process.__init__(self)

        self._queue = queue
        self._stop = Event()
        self._generator = pi_decimal_generator()

    def stop(self):
        self._stop.set()

    def run(self):
        count = 0

        self._generator.next()
        while 1:
            line = ''.join([self._generator.next() for j in range(COLS)])
            self._queue.put((count, line))
            count += COLS

            if self._stop.is_set():
                break

        print("DONE")


class PiWin(StandardWindow):
    def __init__(self, app):

        StandardWindow.__init__(self, "pigreco", "π", autodel=True)
        self.callback_delete_request_add(lambda o: app.quit())

        lb = Label(self, text="π", scale=15)
        self.resize_object_add(lb)
        lb.show()

        tg = TG(self)
        self.resize_object_add(tg)
        tg.show()

        self.tg = tg
        self.app = app
        self.show()


class TG(evas.Textgrid):
    def __init__(self, parent):
        evas.Textgrid.__init__(self, parent.evas,
                               size=(COLS, ROWS),
                               font=("Monospace", 15))

        self.palette_set(EVAS_TEXTGRID_PALETTE_STANDARD, 0, 0, 0, 0, 100)
        self.palette_set(EVAS_TEXTGRID_PALETTE_STANDARD, 1, 150, 150, 150, 255)

        pxw, pxh = self.cell_size
        self.size_hint_min = (pxw * COLS, pxh * ROWS)

        for row_count in range(ROWS):
            row = self.cellrow_get(row_count)
            for cell in row:
                cell.codepoint = ' '
                cell.fg = 1
                cell.bg = 0
            self.cellrow_set(row_count, row)

        self.lines = []

    def redraw(self, beg_line=None):
        if beg_line is None:
            beg_line = max(0, len(self.lines) - ROWS)

        for row_num in range(ROWS):
            if row_num >= len(self.lines):
                break
            row = self.cellrow_get(row_num)
            for i, cell in enumerate(row):
                cell.codepoint = self.lines[beg_line + row_num][i]
            self.cellrow_set(row_num, row)

        self.update_add(0, 0, COLS, ROWS)

    def line_append(self, line):
        self.lines.append(line)
        self.redraw()


class Pigreco(object):
    def __init__(self):
        self.win = PiWin(self)
        self.queue = Queue()
        self.thread = PigrecoThread(self.queue)
        self.thread.start()

        self.win.tg.lines.append('3.' + ' ' * (COLS-2))

        ecore.Timer(0.1, self._timer_cb)

    def _timer_cb(self):
        if self.queue.empty():
            return ecore.ECORE_CALLBACK_RENEW

        count, line = self.queue.get()
        print(self.queue.qsize(), count, line)

        self.win.tg.line_append(line)
        self.win.title = 'π  (calculated decimals: %d)' % count

        return ecore.ECORE_CALLBACK_RENEW

    def quit(self):
        self.thread.stop()
        self.thread.join()
        elementary.exit()


if __name__ == "__main__":
    elementary.init()

    Pigreco()

    elementary.run()
    elementary.shutdown()

