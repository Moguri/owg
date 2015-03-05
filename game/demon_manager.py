import random

import panda3d.bullet as bullet
import panda3d.core as p3d


class DemonPortal(object):
    __slots__ = ["position", "time_to_spawn", "demons"]

    def __init__(self, position):
        self.position = position
        self.time_to_spawn = 0
        self.new_time()
        self.demons = []

    def new_time(self):
        self.time_to_spawn = random.uniform(5, 10)


class DemonSoldier(object):
    __slots__ = ["node_path"]

    def __init__(self, node_path):
        self.node_path = node_path


class DemonManager(object):
    def __init__(self, city, physics_world):
        self.city = city
        self.physics_world = physics_world

        self.demon_model = base.loader.loadModel("models/demon.egg")
        self.portal_model = base.loader.loadModel("models/demon_portal.egg")

        portal_positions = random.sample(city.spawn_points, 1)
        self.demon_portals = [DemonPortal(i) for i in portal_positions]

        for portal in self.demon_portals:
            placeholder = base.render.attach_new_node("placeholder")
            placeholder.set_pos(portal.position)
            self.portal_model.instance_to(placeholder)

    def update(self, task):
        dt = globalClock.getDt()
        for portal in self.demon_portals:
            if len(portal.demons) >= 5:
                continue

            portal.time_to_spawn -= dt
            if portal.time_to_spawn < 0:
                portal.new_time()

                node = bullet.BulletRigidBodyNode("Demon")
                node.add_shape(bullet.BulletBoxShape(p3d.Vec3(0.5, 0.5, 0.75)))
                self.physics_world.attach_rigid_body(node)

                np = base.render.attach_new_node(node)
                pos = p3d.Vec3(portal.position)
                x = random.random() * 2.0 - 1.0
                y = random.random() * 2.0 - 1.0
                offset = p3d.Vec3(x, y, 0)
                pos += offset * 5
                np.set_pos(pos)
                portal.demons.append(DemonSoldier(np))
                self.demon_model.instance_to(np)

        return task.cont

