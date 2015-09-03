#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
import time
import argparse

from efl import evas
from efl import ecore
from efl import edje
from efl import elementary
from efl.elementary.window import StandardWindow
from efl.elementary.layout import Layout
from efl.elementary.slider import Slider

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, \
    EVAS_TEXTGRID_PALETTE_STANDARD as PALETTE



parser = argparse.ArgumentParser(prog='pigreco',
                                 description='Fancy pi digits calculator.')
parser.add_argument('-g', dest='generator',  type=str,
                    default='generator_spigot.py',
                    help='Script to use for digits calculation')
parser.add_argument('-c', dest='cols', type=int, default=50,
                    help='Number of columns')
parser.add_argument('-r', dest='rows', type=int, default=20,
                    help='Number of rows')
parser.add_argument('-t', dest='theme', type=str, default='theme.edj',
                    help='Edje theme file (default: theme.edj)')

args = parser.parse_args()
COLS = args.cols
ROWS = args.rows



intervals = (
    ('day', 'days',  60 * 60 * 24),
    ('hour','hours', 60 * 60),
    ('min', 'mins',  60),
    ('sec', 'secs',  1),
)

def format_seconds(seconds):
    L = list()
    for sing, plur, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            L.append('{:.0f} {}'.format(value, plur if value > 1 else sing))
    return ', '.join(L)


class PiWin(StandardWindow):
    def __init__(self, app):

        StandardWindow.__init__(self, 'pigreco', 'π', autodel=True)
        self.callback_delete_request_add(lambda o: app.quit())

        ly = Layout(self, file=(args.theme, 'pigreco/layout'))
        ly.signal_callback_add('autoscroll,toggle', '',
                               lambda a,s,d: self.autoscroll_toggle())
        self.resize_object_add(ly)
        ly.show()

        digits_color = ly.data_get('digits_color')
        digits_color = map(int, digits_color.split())

        tg = TG(self, app.lines, digits_color)
        ly.part_content_set('textgrid.swallow', tg)
        tg.show()

        self.tg = tg
        self.layout = ly
        self.app = app
        self.show()

        self.scroll_slider = ly.edje.part_external_object_get('scroll.slider')
        self.scroll_slider.callback_changed_add(self._scroll_slider_changed)
        self.scroll_slider.callback_slider_drag_start_add(self._scroll_drag_start)
        self.scroll_slider.callback_slider_drag_stop_add(self._scroll_drag_stop)

        self._scroll_timer = ecore.Timer(1.0, self._scroll_timer_cb)
        self.autoscroll_paused = False

    def shutdown(self):
        self._scroll_timer.delete()
        self.delete()
        
    def _scroll_timer_cb(self):
        self.scroll_slider.min_max = (1, len(self.app.lines))
        self.scroll_slider.value = self.tg.scroll_pos

        if self._scroll_timer.interval > 0.1:
            self._scroll_timer.interval -= 0.05

        if not self.autoscroll_paused:
            self.tg.scroll_rel(+1)
            self.tg.redraw()

        return ecore.ECORE_CALLBACK_RENEW

    def _scroll_drag_start(self, sl):
        self._scroll_timer.freeze()

    def _scroll_drag_stop(self, sl):
        self._scroll_timer.thaw()
        
    def _scroll_slider_changed(self, sl):
        self.tg.scroll_to(int(sl.value))
        self.tg.redraw()

    def autoscroll_toggle(self):
        if self.autoscroll_paused is True:
            self.autoscroll_paused = False
            self.layout.signal_emit('autoscroll,play,set', '')
        else:
            self.autoscroll_paused = True
            self.layout.signal_emit('autoscroll,pause,set', '')


class TG(evas.Textgrid):
    def __init__(self, parent, lines, color):
        evas.Textgrid.__init__(self, parent.evas,
                               size=(COLS, ROWS),
                               font=('Sans', 15),
                               # font_source='Code New Roman.otf',
                               )

        self.palette_set(PALETTE, 0, 0, 0, 0, 0) # bg
        self.palette_set(PALETTE, 1, *color)# fg

        pxw, pxh = self.cell_size
        self.size_hint_min = (pxw * COLS, pxh * ROWS)

        for row_count in range(ROWS):
            row = self.cellrow_get(row_count)
            for cell in row:
                cell.codepoint = ' '
                cell.fg = 1
                cell.bg = 0
            self.cellrow_set(row_count, row)

        self.lines = lines
        self.scroll_pos = 0

    def scroll_to(self, line):
        self.scroll_pos = min(line, len(self.lines) - ROWS)

    def scroll_rel(self, offset):
        self.scroll_to(self.scroll_pos + offset)

    def redraw(self):
        # TODO avoid redraw if we are still at the bottom
        for row_num in range(ROWS):
            if row_num >= len(self.lines):
                break

            row = self.cellrow_get(row_num)
            for i, cell in enumerate(row):
                cell.codepoint = self.lines[self.scroll_pos + row_num][i]
            self.cellrow_set(row_num, row)

        self.update_add(0, 0, COLS, ROWS)


class Pigreco(object):
    def __init__(self, args):
        self.lines = []
        self.count = 0
        self.exe = None

        self.win = PiWin(self)

        for i in range(ROWS-1):
            self.lines.append(' ' * COLS)
        self.lines.append('3.' + ' ' * (COLS-2))
        self.win.tg.redraw()

        
        self.generator_start(args.generator)

    def generator_start(self, command):
        self._start_time = self._line_time = time.time()
        self.exe = ecore.Exe('%s %s %d' % (sys.executable, command, COLS),
                             ecore.ECORE_EXE_PIPE_READ |
                             ecore.ECORE_EXE_PIPE_READ_LINE_BUFFERED)
        self.exe.on_data_event_add(self._generator_stdout)
        # exe.on_del_event_add(self._cmd_done)

    def _generator_stdout(self, exe, event):
        self.lines.extend(event.lines)
        num_digits = len(event.lines) * COLS
        self.count += num_digits

        now = time.time()
        total_seconds = now - self._start_time
        line_seconds = now - self._line_time
        self._line_time = now

        self.win.title = 'π  - {:,} decimals in {} ({:.2f} digits/secs)'.format(
                         self.count, format_seconds(total_seconds),
                         num_digits / line_seconds)

    def quit(self):
        elementary.exit()

    def cleanup(self):
        self.win.shutdown()
        if self.exe:
            self.exe.terminate()
        


if __name__ == "__main__":
    elementary.init()

    app = Pigreco(args)
    elementary.run()

    app.cleanup()
    elementary.shutdown()

