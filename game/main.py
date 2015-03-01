#!/usr/bin/env python2
from direct.showbase.ShowBase import ShowBase

import inputmapper


class GameApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.input_mapper = inputmapper.InputMapper('input.conf')


if __name__ == '__main__':
    app = GameApp()
    app.run()
