from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
import panda3d.core as p3d


class Hud(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)

        # Crosshair
        self.crosshair = OnscreenImage(image='crosshair.png',
                                       scale=(0.1, 0, 0.1),
                                       pos=(0, 0, 0))
        self.crosshair.set_transparency(p3d.TransparencyAttrib.MAlpha)

        self.alpha_resource = OnscreenText(pos=(-1, -0.9), mayChange=True)
        self.beta_resource = OnscreenText(pos=(-0.8, -0.9), mayChange=True)
        self.gamma_resource = OnscreenText(pos=(-0.6, -0.9), mayChange=True)
        self.empty_resource = OnscreenText(pos=(-0.4, -0.9), mayChange=True)

    def update(self, player):
        txt = "A: {}".format(player.resources['ALPHA'])
        self.alpha_resource.setText(txt)
        txt = "B: {}".format(player.resources['BETA'])
        self.beta_resource.setText(txt)
        txt = "C: {}".format(player.resources['GAMMA'])
        self.gamma_resource.setText(txt)
        txt = "E: {}".format(player.resources['EMPTY'])
        self.empty_resource.setText(txt)
