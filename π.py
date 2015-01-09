#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os

from efl import evas
from efl import ecore
from efl import elementary
from efl.elementary.window import StandardWindow
from efl.elementary.layout import Layout

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, \
    EVAS_TEXTGRID_PALETTE_STANDARD as PALETTE


COLS = 50
ROWS = 20


class PiWin(StandardWindow):
    def __init__(self, app):

        StandardWindow.__init__(self, 'pigreco', 'π', autodel=True)
        self.callback_delete_request_add(lambda o: app.quit())

        self.layout = Layout(self, file=('theme.edj', 'pigreco/layout'))
        self.resize_object_add(self.layout)
        self.layout.show()

        digits_color = self.layout.data_get('digits_color')
        digits_color = map(int, digits_color.split())

        tg = TG(self, app.lines, digits_color)
        self.layout.part_content_set('textgrid.swallow', tg)
        tg.show()

        self.tg = tg
        self.app = app
        self.show()


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
    def __init__(self):
        self.lines = []
        self.count = 0
        self.exe = None

        self.win = PiWin(self)

        for i in range(ROWS-1):
            self.lines.append(' ' * COLS)
        self.lines.append('3.' + ' ' * (COLS-2))
        self.win.tg.redraw()

        self.timer = ecore.Timer(1.0, self._timer_cb)
        self.generator_start('generator_spigot.py')

    def generator_start(self, executable):
        self.exe = ecore.Exe('python %s %d' % (executable, COLS),
                             ecore.ECORE_EXE_PIPE_READ |
                             ecore.ECORE_EXE_PIPE_READ_LINE_BUFFERED)
        self.exe.on_data_event_add(self._generator_stdout)
        # exe.on_del_event_add(self._cmd_done)

    def _generator_stdout(self, exe, event):
        self.lines.extend(event.lines)
        self.count += len(event.lines) * COLS
        self.win.title = 'π  - {:,} decimals'.format(self.count)

    def _timer_cb(self):
        if self.timer.interval > 0.1:
            self.timer.interval -= 0.02

        self.win.tg.scroll_rel(+1)
        self.win.tg.redraw()

        return ecore.ECORE_CALLBACK_RENEW

    def quit(self):
        elementary.exit()

    def cleanup(self):
        if self.timer:
            self.timer.delete()
        if self.exe:
            self.exe.terminate()
        


if __name__ == "__main__":
    elementary.init()

    app = Pigreco()
    elementary.run()

    app.cleanup()
    elementary.shutdown()

