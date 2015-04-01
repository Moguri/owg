#!/usr/bin/env python2
from __future__ import print_function

import random
import os
import atexit

import direct.gui as dgui
import panda3d.bullet as bullet
import panda3d.core as p3d
p3d.load_prc_file_data('', 'window-type none')
from direct.showbase.ShowBase import ShowBase

import citygen

import inputmapper
import character
from player_controller import PlayerController
from demon_manager import DemonManager


class GameApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.makeDefaultPipe()

        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.setup_user_config()

        self.input_mapper = inputmapper.InputMapper(os.path.join(self.app_dir, 'input.conf'))
        self.disableMouse()

        wp = p3d.WindowProperties()
        wp.set_cursor_hidden(True)
        wp.set_mouse_mode(p3d.WindowProperties.MRelative)
        win_size_config = p3d.ConfigVariable('win-size')
        win_size = [win_size_config.get_int_word(0), win_size_config.get_int_word(1)]
        wp.set_size(*win_size)
        self.openDefaultWindow(props=wp)

        # Don't send compound events with modifiers (e.g., send 'shift' and 'a' instead of 'shift-a')
        self.mouseWatcherNode.set_modifier_buttons(p3d.ModifierButtons())
        self.buttonThrowers[0].node().set_modifier_buttons(p3d.ModifierButtons())

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

        gen = citygen.CityGen()
        gen.generate()
        city = gen.city

        self.import_city(city)
        player_spawn = random.choice(city.spawn_points)

        player = character.Character('player', self.render, 1.75, 0.6)
        player.set_pos(player_spawn)
        self.player_controller = PlayerController(player)
        self.taskMgr.add(self.player_controller.update, 'Player Controller')

        self.demon_manager = DemonManager(city, self.physics_world)
        self.taskMgr.add(self.demon_manager.update, 'Demon Manager')

        self.city_map = citygen.CityMap(city)

        def toggle_map(display):
            if display:
                self.city_map.show()
            else:
                self.city_map.hide()

        self.accept('display_map', toggle_map, [True])
        self.accept('display_map-up', toggle_map, [False])

    def setup_user_config(self):
        # TODO this should probably go in a user directory
        config_path = os.path.join(self.app_dir, 'user_config.prc')

        if not os.path.exists(config_path):
            print('Creating new user_config.prc')
            config_page = p3d.load_prc_file_data('user_config.prc', '')
        else:
            config_page = p3d.load_prc_file('user_config.prc')

        # Check for missing defaults
        win_size = self.pipe.get_display_width(), self.pipe.get_display_height()
        defaults = {
                'win-size': '{} {}'.format(*win_size),
                'fullscreen': '#t',
                'mousex-sensitivity': '100',
                'mousey-sensitivity': '100',
        }
        found = set()

        decls = [config_page.get_declaration(i) for i in range(config_page.get_num_declarations())]
        for decl in decls:
            decl_var = decl.get_variable()
            decl_name = decl_var.get_name()
            if decl_name in defaults:
                # print('Found config variable', decl_name)
                found.add(decl_name)
                if not decl_var.get_default_value():
                    decl_var.set_default_value(decl.get_string_value())

        # print('found set', found)
        # print('missing set', frozenset(defaults.keys()) - found)
        for i in frozenset(defaults.keys()) - found:
            print('Adding default to user-config:', i, defaults[i])
            decl = config_page.make_declaration(i, defaults[i])
            decl_var = decl.get_variable()
            if not decl_var.get_default_value():
                decl_var.set_default_value(defaults[i])


        def write_config():
            print('writing user-config to disk')
            # Write the config file to disk
            config_stream = p3d.OFileStream(config_path)
            for i in '# This file is auto-generated\n':
                config_stream.put(ord(i))
            config_page.write(config_stream)
            config_stream.close()
        atexit.register(write_config)

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
            np = self.render.attach_new_node(node)
            np.set_pos(p3d.VBase3(*building.position))
            building.nodepath = np

            node = bullet.BulletRigidBodyNode(name)
            node.add_shape(bullet.BulletBoxShape(p3d.Vec3(building.collision)))
            if building.resource != "NONE":
                node.set_python_tag('building', building)
            np = self.render.attach_new_node(node)
            pos = list(building.position)
            pos[2] += building.collision[2]
            np.set_pos(p3d.VBase3(*pos))
            self.physics_world.attach_rigid_body(node)

        road_mat = p3d.Material()
        road_mat.set_shininess(1.0)
        color = [c/255.0 for c in (7, 105, 105)]
        road_mat.set_diffuse(p3d.VBase4(color[0], color[1], color[2], 1.0))
        node = citygen.mesh_to_p3d_node(city.road_mesh, "road", road_mat)
        self.render.attach_new_node(node)

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
