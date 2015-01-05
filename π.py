#!/usr/bin/env python
# encoding: utf-8

from efl import evas
from efl.evas import EVAS_TEXTGRID_PALETTE_STANDARD, \
    EVAS_HINT_EXPAND, EXPAND_BOTH, EXPAND_HORIZ, EXPAND_VERT, \
    EVAS_HINT_FILL, FILL_BOTH, FILL_HORIZ, FILL_VERT

from efl import elementary
from efl.elementary.window import StandardWindow
from efl.elementary.label import Label



class PiWin(StandardWindow):
    def __init__(self, app):

        StandardWindow.__init__(self, "pigreco", "π", autodel=True)
        self.callback_delete_request_add(lambda o: elementary.exit())

        lb = Label(self, text="π", scale=20)
        self.resize_object_add(lb)
        lb.show()

        tg = TG(self.evas)
        self.resize_object_add(tg)
        tg.show()

        self.tg = tg
        self.app = app
        self.show()


class TG(evas.Textgrid):
    width = 40
    height = 15
    def __init__(self, canvas):

        evas.Textgrid.__init__(self, canvas,
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



if __name__ == "__main__":
    elementary.init()

    Pigreco()

    elementary.run()
    elementary.shutdown()

