import math
import random

import panda3d.bullet as bullet
import panda3d.core as p3d

from character import Character


DEMON_SPEED = 0.75


class DemonPortal(object):
    __slots__ = ["position", "time_to_spawn", "demons"]

    def __init__(self, position):
        self.position = position
        self.time_to_spawn = 0
        self.new_time()
        self.demons = []

    def new_time(self):
        self.time_to_spawn = random.uniform(5, 10)


class DemonManager(object):
    def __init__(self, city, physics_world):
        self.city = city
        self.physics_world = physics_world

        self.demon_model = base.loader.loadModel("models/demon.egg")
        # TODO: Calculate bounds properly once we switch to 1.9
        # bounds = self.demon_model.get_tight_bounds()
        self.demon_model_half_height = 0.75 #(bounds[1] - bounds[0]).z / 2.0
        self.portal_model = base.loader.loadModel("models/demon_portal.egg")

        portal_positions = random.sample(city.spawn_points, 5)
        self.demon_portals = [DemonPortal(i) for i in portal_positions]

        for portal in self.demon_portals:
            placeholder = base.render.attach_new_node("placeholder")
            placeholder.set_pos(portal.position)
            self.portal_model.instance_to(placeholder)

    def update(self, task):
        dt = globalClock.getDt()
        for portal in self.demon_portals:
            for demon in portal.demons[:]:
                if demon.hp <= 0:
                    demon.destroy()
                    portal.demons.remove(demon)
                    continue

                r = (random.random() - random.random()) * (math.pi / 12.0)
                (old_x, old_y, old_z) = demon.get_linear_movement()
                x = old_x * math.cos(r) - old_y * math.sin(r)
                y = old_x * math.sin(r) + old_y * math.cos(r)
                movement = p3d.Vec3(x, y, 0)
                movement.normalize()
                movement *= DEMON_SPEED
                demon.set_linear_movement(movement, local=False)

            if len(portal.demons) >= 5:
                continue

            portal.time_to_spawn -= dt
            if portal.time_to_spawn < 0:
                portal.new_time()

                demon = Character("Demon", base.render, 1.75, 0.6)

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

                # Attach a mesh
                np = self.demon_model.instance_under_node(demon.nodepath, 'demon_mesh')
                pos = np.get_pos()
                pos.z -= self.demon_model_half_height
                np.set_pos(pos)

                portal.demons.append(demon)

        return task.cont

