#!/usr/bin/env python2
from __future__ import print_function

import random

from direct.showbase.ShowBase import ShowBase
import panda3d.bullet as bullet
import panda3d.core as p3d

from citygen import *

import inputmapper
import character
from player_controller import PlayerController


class GameApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.input_mapper = inputmapper.InputMapper('input.conf')
        self.disableMouse()
        wp = p3d.WindowProperties()
        wp.set_cursor_hidden(True)
        wp.set_mouse_mode(p3d.WindowProperties.MRelative)
        self.win.requestProperties(wp)

        self.physics_world = bullet.BulletWorld()
        self.physics_world.set_gravity(p3d.Vec3(0, 0, -9.81))
        self.taskMgr.add(self.update_physics, 'Update Physics')

        phydebug = bullet.BulletDebugNode('Physics Debug')
        phydebug.show_wireframe(True)
        phydebug.show_bounding_boxes(True)
        phydebugnp = self.render.attach_new_node(phydebug)
        # Uncomment to show debug physics
        # phydebugnp.show()
        self.physics_world.set_debug_node(phydebug)

        self.render.set_shader_auto()

        self.camLens.set_near(0.5)

        light = p3d.DirectionalLight('sun')
        light.set_color(p3d.VBase4(1.0, 0.94, 0.84, 1.0))
        light_np = self.render.attach_new_node(light)
        light_np.set_hpr(p3d.VBase3(-135.0, -45.0, 0.0))
        self.render.set_light(light_np)

        light = p3d.DirectionalLight('indirect')
        light.set_color(p3d.VBase4(0.1784, 0.2704, 0.3244, 1.0))
        light_np = self.render.attach_new_node(light)
        light_np.set_hpr(p3d.VBase3(45.0, 45.0, 0.0))
        self.render.set_light(light_np)

        gen = CityGen()
        gen.generate()
        city = gen.city

        self.import_city(city)
        player_spawn = random.choice(city.spawn_points)

        player = character.Character('player')
        playernp = self.render.attach_new_node(player)
        playernp.set_pos(player_spawn)
        self.physics_world.attach_character(player)
        self.player_controller = PlayerController(player,
                                                  playernp,
                                                  self.camera,
                                                  self.physics_world,
                                                  self.mouseWatcherNode,
                                                  self.win)
        self.taskMgr.add(self.player_controller.update, 'Player Controller')

        # Demon portals
        self.demon_portals = random.sample(city.spawn_points, 5)
        model = self.loader.loadModel("models/demon_portal.egg")
        for point in self.demon_portals:
            placeholder = self.render.attach_new_node("placeholder")
            placeholder.set_pos(point[0], point[1], point[2]+1)
            model.instance_to(placeholder)

    def create_mesh(self, mesh, name, material):
            node = p3d.GeomNode(name)

            vdata = p3d.GeomVertexData(name,
                p3d.GeomVertexFormat.get_v3n3(),
                p3d.GeomEnums.UH_stream)
            vdata.unclean_set_num_rows(len(mesh.vertices))

            vwriter = p3d.GeomVertexWriter(vdata, 'vertex')
            nwriter = p3d.GeomVertexWriter(vdata, 'normal')
            for vert in mesh.vertices:
                vwriter.add_data3(*vert.position)
                nwriter.add_data3(*vert.normal)
            vwriter = None
            nwriter = None

            prim = p3d.GeomTriangles(p3d.GeomEnums.UH_stream)
            for face in mesh.faces:
                prim.add_vertices(*face)

            render_state = p3d.RenderState.make_empty()

            render_state = render_state.set_attrib(p3d.MaterialAttrib.make(material))

            geom = p3d.Geom(vdata)
            geom.add_primitive(prim)
            node.add_geom(geom, render_state)

            return self.render.attach_new_node(node)

    def import_city(self, city):
        colors = []
        colors.append((112, 163, 10))
        colors.append((90, 135, 10))
        colors.append((67, 100, 10))
        building_mats = []
        for color in colors:
            mat = p3d.Material()
            mat.set_shininess(1.0)
            color = [c/255.0 for c in color]
            mat.set_diffuse(p3d.VBase4(color[0], color[1], color[2], 1.0))
            building_mats.append(mat)

        for i, building in enumerate(city.buildings):
            mesh = building.mesh
            name = str(i)
            mat = random.choice(building_mats)
            np = self.create_mesh(mesh, name, mat)
            np.set_pos(p3d.VBase3(*building.position))

            node = bullet.BulletRigidBodyNode(name)
            node.add_shape(bullet.BulletBoxShape(p3d.Vec3(building.collision)))
            np = self.render.attach_new_node(node)
            pos = list(building.position)
            pos[2] += building.collision[2]
            np.set_pos(p3d.VBase3(*pos))
            self.physics_world.attach_rigid_body(node)

        road_mat = p3d.Material()
        road_mat.set_shininess(1.0)
        color = [c/255.0 for c in (7, 105, 105)]
        road_mat.set_diffuse(p3d.VBase4(color[0], color[1], color[2], 1.0))
        self.create_mesh(city.road_mesh, "road", road_mat)

        node = bullet.BulletRigidBodyNode('Ground')
        node.add_shape(bullet.BulletPlaneShape(p3d.Vec3(0, 0, 1), 0))
        self.render.attach_new_node(node)
        self.physics_world.attach_rigid_body(node)

    # Tasks
    def update_physics(self, task):
        dt = globalClock.getDt()
        self.physics_world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = GameApp()
    app.run()
