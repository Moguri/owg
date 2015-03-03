from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import ZUp
from panda3d.core import PandaNode


class Character(BulletCharacterControllerNode):

    def __init__(self, name):
        PandaNode.__init__(self, name)

        # These are rather arbitrary at the moment
        height = 1.75
        radius = 0.4
        self.shape = BulletCapsuleShape(radius, height - 2 * radius, ZUp)

        BulletCharacterControllerNode.__init__(self,
                                               self.shape,
                                               radius,
                                               name)
