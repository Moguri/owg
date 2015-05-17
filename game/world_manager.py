import panda3d.core as p3d
import panda3d.bullet as bullet


class WorldData(object):
    def __init__(self, name):
        self.id = -1
        self.name = name
        self.nodepath = p3d.NodePath(p3d.PandaNode(name))
        self.physics_world = bullet.BulletWorld()


class WorldManager(object):
    def __init__(self, nodepath):
        self.nodepath = nodepath

        self._worlds = []
        self._id_counter = 0

    def destroy(self):
        for world in self._worlds:
            world.nodepath.remove_node()

    def get_world(self, wid):
        return [world for world in self._worlds if world.id == wid][0]

    def add_world(self, world_data):
        world_data.id = self._id_counter
        self._id_counter += 1
        self._worlds.append(world_data)
        return world_data.id

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
