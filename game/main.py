#!/usr/bin/env python2
from __future__ import print_function

# Keep this cefpanda import at the top
#from cefpanda import CEFPanda

import os
import sys
import atexit

import direct.gui as dgui
import panda3d.core as p3d
import panda3d.bullet as bullet
p3d.load_prc_file_data('', 'window-type none')
from direct.showbase.ShowBase import ShowBase

import inputmapper
from game_states import MainState


class GameApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.makeDefaultPipe()

        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.setup_user_config()

        self.input_mapper = inputmapper.InputMapper(os.path.join(self.app_dir, 'input.conf'))
        self.disableMouse()

        base.render.set_antialias(p3d.AntialiasAttrib.M_multisample)

        wp = p3d.WindowProperties()
        wp.set_cursor_hidden(True)
        wp.set_mouse_mode(p3d.WindowProperties.MRelative)
        win_size_config = p3d.ConfigVariable('win-size')
        win_size = [win_size_config.get_int_word(0), win_size_config.get_int_word(1)]
        wp.set_size(*win_size)
        self.openDefaultWindow(props=wp)

        # Handle exiting if the window closes (helps CEFPanda)
        self.win.set_close_request_event('quit')
        self.accept('quit', sys.exit)

        #p3d.PStatClient.connect()
        #self.bufferViewer.enable(True)

        # Setup UI
        #self.ui = CEFPanda()
        #self.ui.load('ui/template.html')

        # Don't send compound events with modifiers (e.g., send 'shift' and 'a' instead of 'shift-a')
        self.mouseWatcherNode.set_modifier_buttons(p3d.ModifierButtons())
        self.buttonThrowers[0].node().set_modifier_buttons(p3d.ModifierButtons())

        self.physics_world = bullet.BulletWorld()
        self.physics_world.set_gravity(p3d.LVector3(0, 0, -9.81))
        base.taskMgr.add(self.update_physics, 'Update Physics')

        phydebug = bullet.BulletDebugNode('Physics Debug')
        phydebug.show_wireframe(True)
        phydebug.show_bounding_boxes(True)
        phydebugnp = base.render.attach_new_node(phydebug)
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

        self.state = MainState()
        self.accept('restart_state', self.change_state, [MainState])

    def change_state(self, new_state, *args):
        self.state.destroy()
        #print(self.render.ls())
        #print("Num characters:", self.physics_world.get_num_characters())
        #print("Num ghosts:", self.physics_world.get_num_ghosts())
        #print("Num manifolds:", self.physics_world.get_num_manifolds())
        #print("Num rigid bodies:", self.physics_world.get_num_rigid_bodies())
        #print("Num soft bodies:", self.physics_world.get_num_soft_bodies())
        #print("Num vehicles:", self.physics_world.get_num_vehicles())
        self.state = new_state(*args)

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
                'framebuffer-multisample': '1',
                'multisamples': '4',
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
                config_stream.put(i)
            config_page.write(config_stream)
            config_stream.close()
        atexit.register(write_config)

    # Tasks
    def update_physics(self, task):
        dt = globalClock.getDt()
        self.physics_world.do_physics(dt)
        return task.cont


if __name__ == '__main__':
    app = GameApp()
    app.run()
