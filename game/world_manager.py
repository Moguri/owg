import panda3d.core as p3d
import panda3d.bullet as bullet

from direct.filter.FilterManager import FilterManager


class WorldData(object):
    def __init__(self, world_id, name):
        self.id = world_id
        self.name = name
        self.nodepath = p3d.NodePath(p3d.PandaNode(name))
        self.nodepath.set_state(base.render.get_state())
        self.physics_world = bullet.BulletWorld()

        sx = base.win.get_x_size()
        sy = base.win.get_y_size()
        self._texbuffer = base.win.make_texture_buffer(self.name + "Buffer", sx, sy)
        self._texbuffer.set_sort(-1)
        self.camera = base.makeCamera(self._texbuffer)
        self.camera.node().set_lens(base.camLens)
        self.camera.reparent_to(self.nodepath)

        self.active = False

    def activate(self):
        self.active = True #self.nodepath.get_parent().is_empty()
        self._texbuffer.set_active(self.active)

    def destroy(self):
        base.graphicsEngine.remove_window(self._texbuffer)
        self.nodepath.remove_node()

class WorldManager(object):
    def __init__(self, nodepath):
        self.nodepath = nodepath

        self._worlds = []
        self._active_world = 0
        self.do_compositing = False

        # Setup post-process portal compositing
        self._manager = FilterManager(base.win, base.cam)
        self._texture = p3d.Texture()
        self._dtexture = p3d.Texture()
        self._quad = self._manager.renderSceneInto(colortex=self._texture, depthtex=self._dtexture)
        self._quad = self._manager.renderSceneInto(colortex=self._texture)
        self._quad.set_shader(p3d.Shader.load(p3d.Shader.SL_GLSL, "portal.vs", "portal.fs"))
        self._quad.set_shader_input("main_texture", self._texture)

    def destroy(self):
        for world in self._worlds:
            world.destroy()
        self._manager.cleanup()

    def get_world(self, wid):
        return [world for world in self._worlds if world.id == wid][0]

    def add_world(self, name):
        world_data = WorldData(len(self._worlds), name)
        self._worlds.append(world_data)
        self._quad.set_shader_input("world_texture_{}".format(world_data.id), world_data._texbuffer.get_texture(0))
        self._quad.set_shader_input("num_worlds", len(self._worlds))
        return world_data

    def switch_node_physics(self, phys_node, wid):
        for world in self._worlds:
            world.physics_world.remove(phys_node)

        self.get_world(wid).physics_world.attach(phys_node)

    def switch_world(self, wid):
        self.hide_all_worlds()
        self.show_world(wid)
        self._active_world = wid
        self._quad.set_shader_input("active_world", wid)

    def show_world(self, wid):
        world = self.get_world(wid)
        world.nodepath.reparent_to(self.nodepath)
        self._active_world = wid
        self._quad.set_shader_input("active_world", wid)

    def hide_all_worlds(self):
        for world in self._worlds:
            world.nodepath.detachNode()

    def hide_world(self, wid):
        world = self.get_world(wid)
        world.nodepath.detachNode()

    def update(self):
        dt = globalClock.getDt()
        main_xform = base.camera.get_net_transform()

        self._quad.set_shader_input("do_compositing", self.do_compositing)

        for world in self._worlds:
            world.activate()
            world.camera.set_transform(main_xform)
            world.physics_world.do_physics(dt)

