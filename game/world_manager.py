import panda3d.core as p3d
import panda3d.bullet as bullet


class WorldData(object):
    def __init__(self, name):
        self.id = -1
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
        self.active = self.nodepath.get_parent().is_empty()
        self._texbuffer.set_active(self.active)

    def destroy(self):
        base.graphicsEngine.remove_window(self._texbuffer)
        self.nodepath.remove_node()

class WorldManager(object):
    def __init__(self, nodepath):
        self.nodepath = nodepath

        self._worlds = []
        self._id_counter = 0

    def destroy(self):
        for world in self._worlds:
            world.destroy()

    def get_world(self, wid):
        return [world for world in self._worlds if world.id == wid][0]

    def add_world(self, world_data):
        world_data.id = self._id_counter
        self._id_counter += 1
        self._worlds.append(world_data)
        return world_data.id

    def switch_node_physics(self, phys_node, wid):
        for world in self._worlds:
            world.physics_world.remove(phys_node)

        self.get_world(wid).physics_world.attach(phys_node)

    def switch_world(self, wid):
        self.hide_all_worlds()
        self.show_world(wid)

    def show_world(self, wid):
        world = self.get_world(wid)
        world.nodepath.reparent_to(self.nodepath)

    def hide_all_worlds(self):
        for world in self._worlds:
            world.nodepath.detachNode()

    def hide_world(self, wid):
        world = self.get_world(wid)
        world.nodepath.detachNode()

    def update(self):
        dt = globalClock.getDt()
        main_xform = base.camera.get_net_transform()

        for world in self._worlds:
            world.activate()
            world.camera.set_transform(main_xform)
            world.physics_world.do_physics(dt)

