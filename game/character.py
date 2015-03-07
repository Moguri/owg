from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import ZUp
from direct.showbase.DirectObject import DirectObject


class Character(DirectObject):
    next_id = 1

    def __init__(self, name, root, height, radius):
        self.hp = 1
        self.id = Character.next_id
        Character.next_id += 1

        # Setup physics
        shape = BulletCapsuleShape(radius, height - 2 * radius, ZUp)
        self.physics_node = BulletCharacterControllerNode(shape, radius, name)
        base.physics_world.attach_character(self.physics_node)
        self.physics_node.setPythonTag('character_id', self.id)

        # Attach to the scenegraph
        self.nodepath = root.attach_new_node(self.physics_node)

        self.accept('character_hit', self.on_hit)

    def destroy(self):
        base.physics_world.remove(self.physics_node)
        self.nodepath.remove_node()
        self.ignoreAll()

    def on_hit(self, id):
        if id == self.id:
            self.hp -= 1

    def set_pos(self, pos):
        self.nodepath.set_pos(pos)

    def get_pos(self):
        return self.nodepath.get_pos()

    def set_hpr(self, hpr):
        self.nodepath.set_hpr(hpr)

    def get_hpr(self):
        return self.nodepath.get_hpr()

    def set_linear_movement(self, movement, local=True):
        self.physics_node.set_linear_movement(movement, local)

    def set_angular_movement(self, movement):
        self.physics_node.set_angular_movement(movement)

    def is_on_ground(self):
        return self.physics_node.is_on_ground()

    def do_jump(self):
        self.physics_node.do_jump()

    def get_shape(self):
        return self.physics_node.get_shape()
