from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectWaitBar
from direct.showbase.DirectObject import DirectObject
import panda3d.core as p3d


class Hud(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)

        # Frame to parent everything to and make cleanup easier
        self.frame = DirectFrame()

        # Crosshair
        self.crosshair = OnscreenImage(image='crosshair.png',
                                       scale=(0.1, 0, 0.1),
                                       pos=(0, 0, 0))
        self.crosshair.set_transparency(p3d.TransparencyAttrib.MAlpha)
        self.crosshair.reparent_to(self.frame)

        self.player_health = DirectWaitBar(text="", value=0, pos=(-1, 0, -0.85), scale=0.2)
        self.player_health.reparent_to(self.frame)

        self.alpha_resource = OnscreenText(pos=(-0.6, -0.9), mayChange=True)
        self.alpha_resource.reparent_to(self.frame)
        self.beta_resource = OnscreenText(pos=(-0.4, -0.9), mayChange=True)
        self.beta_resource.reparent_to(self.frame)
        self.gamma_resource = OnscreenText(pos=(-0.2, -0.9), mayChange=True)
        self.gamma_resource.reparent_to(self.frame)
        self.empty_resource = OnscreenText(pos=(0.0, -0.9), mayChange=True)
        self.empty_resource.reparent_to(self.frame)

    def destroy(self):
        self.frame.destroy()

    def update(self, player):
        pc = player.player
        self.player_health['value'] = pc.hp * 100 / pc.max_hp
        txt = "A: {}".format(player.resources['ALPHA'])
        self.alpha_resource.setText(txt)
        txt = "B: {}".format(player.resources['BETA'])
        self.beta_resource.setText(txt)
        txt = "C: {}".format(player.resources['GAMMA'])
        self.gamma_resource.setText(txt)
        txt = "E: {}".format(player.resources['EMPTY'])
        self.empty_resource.setText(txt)
