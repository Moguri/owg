import os
import json

from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import ZUp
import panda3d.core as p3d
from direct.showbase.DirectObject import DirectObject


class Character(DirectObject):
    next_id = 1
    model_cache = {}

    def __init__(self, cfile, root=None, world_manager=None):
        self.id = Character.next_id
        Character.next_id += 1
        self.linear_movement = p3d.LVector3(0.0)

        self.world_manager = world_manager

        if root is None:
            root = base.render

        with open(os.path.join('characters', cfile) + '.json') as f:
            self.json_data = json.load(f)

        self.hp = self.max_hp = self.json_data['max_health']
        name = self.json_data['name']
        height = self.json_data['height']
        radius = self.json_data['radius']

        # Setup physics
        shape = BulletCapsuleShape(radius, height - 2 * radius, ZUp)
        self.physics_node = BulletCharacterControllerNode(shape, radius, name)
        if self.world_manager is None:
            base.physics_world.attach_character(self.physics_node)
        else:
            self.world_manager.switch_node_physics(self.physics_node, 0)
        self.physics_node.setPythonTag('character_id', self.id)

        # Attach to the scenegraph
        self.nodepath = root.attach_new_node(self.physics_node)

        # Attach a mesh
        self.mesh_node = None
        mesh = os.path.join('models', self.json_data['mesh'])
        if mesh:
            if mesh in self.model_cache:
                model = self.model_cache[mesh]
            else:
                model = base.loader.loadModel(mesh)
                self.model_cache[mesh] = model

            self.mesh_node = model.instance_under_node(self.nodepath, 'mesh')
            bounds = model.get_tight_bounds()
            self.half_height = (bounds[1] - bounds[0]).z / 2.0
            if self.json_data['use_half_height']:
                pos = self.mesh_node.get_pos()
                pos.z -= self.half_height
                self.mesh_node.set_pos(pos)

        self.accept('character_hit', self.on_hit)

        if self.world_manager:
            for i in range(1, 6):
                key = str.format('world_{}-up', i)
                self.accept(key, self.world_manager.switch_node_physics, [self.physics_node, i-1])

    def destroy(self):
        if self.world_manager is None:
            base.physics_world.remove_character(self.physics_node)
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

    def get_linear_movement(self):
        return self.linear_movement

    def set_linear_movement(self, movement, local=True):
        self.physics_node.set_linear_movement(movement, local)
        self.linear_movement = movement

    def set_angular_movement(self, movement):
        self.physics_node.set_angular_movement(movement)

    def is_on_ground(self):
        return self.physics_node.is_on_ground()

    def do_jump(self):
        self.physics_node.do_jump()

    def get_shape(self):
        return self.physics_node.get_shape()
