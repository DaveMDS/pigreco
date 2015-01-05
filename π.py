#!/usr/bin/env python
# encoding: utf-8

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EXPAND_BOTH, FILL_BOTH
from efl import elementary
from efl.elementary.window import StandardWindow, DialogWindow
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.label import Label
from efl.elementary.entry import Entry


class PiWin(StandardWindow):
    def __init__(self, app):

        StandardWindow.__init__(self, "pigreco", "π", resize=False, 
                                autodel=True, size=(600, 600))
        self.callback_delete_request_add(lambda o: elementary.exit())

        box = Box(self, size=(600,600))# size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.resize_object_add(box)
        box.show()
        
        lb = Label(box, text="<title>- π -</title>", scale=10,
                   size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        box.pack_end(lb)
        lb.show()

        self.app = app
        self.show()


class Pigreco(object):
    def __init__(self):
        self.win = PiWin(self)



if __name__ == "__main__":
    elementary.init()

    Pigreco()

    elementary.run()
    elementary.shutdown()

