import math
import random

import panda3d.bullet as bullet
import panda3d.core as p3d

from character import Character


DEMON_SPEED = 0.75


class DemonPortal(object):
    __slots__ = [
            "position",
            "time_to_spawn",
            "demons",
            "demons_destroyed",
            "node_path"
    ]

    def __init__(self, position):
        self.position = position
        self.time_to_spawn = 0
        self.new_time()
        self.demons = []
        self.demons_destroyed = 0
        self.node_path = None

    def destroy(self):
        self.node_path.remove_node()
        for demon in self.demons:
            demon.destroy()

    def new_time(self):
        self.time_to_spawn = random.uniform(5, 10)


class DemonManager(object):
    def __init__(self, city, physics_world):
        self.city = city
        self.physics_world = physics_world

        self.portal_model = base.loader.loadModel("models/demon_portal")

        portal_positions = random.sample(city.spawn_points, 5)
        self.demon_portals = [DemonPortal(i) for i in portal_positions]

        for portal in self.demon_portals:
            placeholder = base.render.attach_new_node("placeholder")
            placeholder.set_pos(portal.position)
            portal.node_path = placeholder
            self.portal_model.instance_to(placeholder)

    def destroy(self):
        for portal in self.demon_portals:
            for demon in portal.demons:
                demon.destroy()
            portal.destroy()

    def update(self, task):
        dt = globalClock.getDt()
        for portal in self.demon_portals[:]:
            for demon in portal.demons[:]:
                if demon.hp <= 0:
                    demon.destroy()
                    portal.demons.remove(demon)
                    portal.demons_destroyed += 1
                    continue

                r = (random.random() - random.random()) * (math.pi / 12.0)
                (old_x, old_y, old_z) = demon.get_linear_movement()
                x = old_x * math.cos(r) - old_y * math.sin(r)
                y = old_x * math.sin(r) + old_y * math.cos(r)
                movement = p3d.Vec3(x, y, 0)
                movement.normalize()
                movement *= DEMON_SPEED
                demon.set_linear_movement(movement, local=False)

            if portal.demons_destroyed >= 5:
                portal.destroy()
                self.demon_portals.remove(portal)
                continue

            if len(portal.demons) >= 5:
                continue

            portal.time_to_spawn -= dt
            if portal.time_to_spawn < 0:
                portal.new_time()

                demon = Character('demon')

                # Position the new demon
                pos = p3d.Vec3(portal.position)
                # x = random.random() * 2.0 - 1.0
                # y = random.random() * 2.0 - 1.0
                # offset = p3d.Vec3(x, y, 0)
                # pos += offset * 0.0
                demon.set_pos(pos)

                # Get the demon moving
                ori = random.random() * math.pi * 2.0
                movement = p3d.Vec3(math.cos(ori), math.sin(ori), 0) * DEMON_SPEED
                demon.set_linear_movement(movement, local=False)

                portal.demons.append(demon)

        return task.cont

