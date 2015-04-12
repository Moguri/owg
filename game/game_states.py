from __future__ import print_function

import random

from direct.showbase.DirectObject import DirectObject
import panda3d.core as p3d
import panda3d.bullet as bullet

import citygen
import character
from player_controller import PlayerController
from demon_manager import DemonManager

class MainState(DirectObject):
    def __init__(self):
        gen = citygen.CityGen()
        gen.generate()
        city = gen.city

        self.city_nodepath = base.render.attach_new_node("City")
        self.import_city(city)
        player_spawn = random.choice(city.spawn_points)

        player = character.Character('player', base.render, 1.75, 0.6)
        player.set_pos(player_spawn)
        self.player_controller = PlayerController(player)
        base.taskMgr.add(self.player_controller.update, 'Player Controller')

        self.demon_manager = DemonManager(city, base.physics_world)
        base.taskMgr.add(self.demon_manager.update, 'Demon Manager')

        self.city_map = citygen.CityMap(city)

        def toggle_map(display):
            if display:
                self.city_map.show()
            else:
                self.city_map.hide()

        self.accept('display_map', toggle_map, [True])
        self.accept('display_map-up', toggle_map, [False])

    def destroy(self):
        base.taskMgr.remove('Player Controller')
        base.taskMgr.remove('Demon Manager')

        self.city_nodepath.remove_node()

        for body in base.physics_world.get_rigid_bodies():
            base.physics_world.remove(body)

        self.player_controller.destroy()
        self.demon_manager.destroy()
        self.ignoreAll()

    def import_city(self, city):
        building_mats = {}
        for resource, data in citygen.RESOURCES.items():
            mat_set = []
            for factor in (0.8, 1.0, 1.2):
                mat = p3d.Material()
                mat.set_shininess(1.0)
                adj_color = [min(c*factor/255.0, 1.0) for c in data.color]
                mat.set_diffuse(p3d.VBase4(adj_color[0], adj_color[1], adj_color[2], 1.0))
                mat_set.append(mat)
            building_mats[resource] = mat_set

        for i, building in enumerate(city.buildings):
            mesh = building.mesh
            name = str(i)
            mat = random.choice(building_mats[building.resource])
            node = citygen.mesh_to_p3d_node(mesh, name, mat)
            np = self.city_nodepath.attach_new_node(node)
            np.set_pos(p3d.VBase3(*building.position))
            building.nodepath = np

            node = bullet.BulletRigidBodyNode(name)
            node.add_shape(bullet.BulletBoxShape(p3d.Vec3(building.collision)))
            if building.resource != "NONE":
                node.set_python_tag('building', building)
            np = self.city_nodepath.attach_new_node(node)
            pos = list(building.position)
            pos[2] += building.collision[2]
            np.set_pos(p3d.VBase3(*pos))
            base.physics_world.attach_rigid_body(node)

        road_mat = p3d.Material()
        road_mat.set_shininess(1.0)
        color = [c/255.0 for c in (7, 105, 105)]
        road_mat.set_diffuse(p3d.VBase4(color[0], color[1], color[2], 1.0))
        node = citygen.mesh_to_p3d_node(city.road_mesh, "road", road_mat)
        self.city_nodepath.attach_new_node(node)

        node = bullet.BulletRigidBodyNode('Ground')
        node.add_shape(bullet.BulletPlaneShape(p3d.Vec3(0, 0, 1), 0))
        self.city_nodepath.attach_new_node(node)
        base.physics_world.attach_rigid_body(node)
