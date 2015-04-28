import math

from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpPosInterval
import panda3d.core as p3d

from hud import Hud
from weapon import Weapon


class PlayerController(DirectObject):

    BUY_DISTANCE = 50
    PLAYER_WALK_SPEED = 20
    PLAYER_SPRINT_SPEED = 50

    CAMERA_DISTANCE = 6
    CAMERA_HEIGHT = 1.25
    CAMERA_SPRINT_SCALE = 1.2

    def __init__(self, player):
        DirectObject.__init__(self)

        self.player = player

        self.hud = Hud()

        halfx = base.win.get_x_size() / 2
        halfy = base.win.get_y_size() / 2
        base.win.move_pointer(0, halfx, halfy)
        mx_sens_config = p3d.ConfigVariableInt('mousex-sensitivity')
        self.mousex_sensitivity = mx_sens_config.get_value() * 10.0
        my_sens_config = p3d.ConfigVariableInt('mousey-sensitivity')
        self.mousey_sensitivity = my_sens_config.get_value() / 10.0

        # Camera setup
        self.camera_pitch = 0

        self.camera_pivot = self.player.nodepath.attach_new_node('camera_pivot')
        pos = self.camera_pivot.get_pos()
        pos.z += self.CAMERA_HEIGHT
        self.camera_pivot.set_pos(pos)

        base.camera.reparent_to(self.camera_pivot)
        pos = base.camera.get_pos()
        pos.y -= self.CAMERA_DISTANCE
        self.sprint_camera_interval = LerpPosInterval(
            base.camera,
            0,
            pos)
        self.sprint_camera_interval.start()

        self.player_movement = p3d.LVector3(0, 0, 0)
        self.player_speed = self.PLAYER_WALK_SPEED

        # Building acquisition
        self.in_buy_mode = False
        self.current_building = None
        self.resources = {
                'ALPHA': 0,
                'BETA': 0,
                'GAMMA': 0,
                'EMPTY': 0,
        }

        self.left_weapon = Weapon('rifle')
        self.right_weapon = Weapon('melee')

        self.accept('move_forward', self.update_movement, ['forward', True])
        self.accept('move_forward-up', self.update_movement, ['forward', False])
        self.accept('move_backward', self.update_movement, ['backward', True])
        self.accept('move_backward-up', self.update_movement, ['backward', False])
        self.accept('move_left', self.update_movement, ['left', True])
        self.accept('move_left-up', self.update_movement, ['left', False])
        self.accept('move_right', self.update_movement, ['right', True])
        self.accept('move_right-up', self.update_movement, ['right', False])
        self.accept('jump', self.jump)
        self.accept('sprint', self.sprint, [True])
        self.accept('sprint-up', self.sprint, [False])
        self.accept('left_fire', self.fire, [self.left_weapon])
        self.accept('right_fire', self.fire, [self.right_weapon])
        self.accept('purchase', self.purchase_building)
        self.accept('buy_mode', lambda: setattr(self, 'in_buy_mode', True))
        self.accept('buy_mode-up', lambda: setattr(self, 'in_buy_mode', False))

        # DEBUG PC HEALTH
        def damage_health():
            base.messenger.send('character_hit', [self.player.id])
        self.accept('pc_health', damage_health)

    def destroy(self):
        self.ignoreAll()
        self.hud.destroy()
        self.player.destroy()

    @property
    def is_dead(self):
        return self.player.hp <= 0

    def update_movement(self, direction, activate):
        move_delta = p3d.LVector3(0, 0, 0)

        if direction == 'forward':
            move_delta.set_y(1)
        elif direction == 'backward':
            move_delta.set_y(-1)
        elif direction == 'left':
            move_delta.set_x(-1)
        elif direction == 'right':
            move_delta.set_x(1)

        if not activate:
            move_delta *= -1

        self.player_movement += move_delta

    def jump(self):
        if self.player.is_on_ground():
            self.player.do_jump()

    def sprint(self, activate):
        if activate:
            self.player_speed = self.PLAYER_SPRINT_SPEED
            cam_distance_target = -self.CAMERA_DISTANCE * self.CAMERA_SPRINT_SCALE
        else:
            self.player_speed = self.PLAYER_WALK_SPEED
            cam_distance_target = -self.CAMERA_DISTANCE


        # Move the camera smoothly
        a = abs(cam_distance_target - base.camera.get_pos().get_y())
        b = float(self.CAMERA_DISTANCE * self.CAMERA_SPRINT_SCALE) - self.CAMERA_DISTANCE
        factor = a / b
        print(base.camera.get_pos().get_y(), cam_distance_target, factor)
        self.sprint_camera_interval.finish()
        self.sprint_camera_interval = LerpPosInterval(
            base.camera,
            0.4 * factor,
            p3d.Point3(0, cam_distance_target, self.CAMERA_HEIGHT),
            other=self.player.nodepath
        )
        self.sprint_camera_interval.start()

    def _get_object_at_cursor(self, distance):
        from_point = p3d.Point3()
        to_point = p3d.Point3()
        far_point = p3d.Point3()
        base.camLens.extrude(p3d.Point2(0, 0), from_point, to_point)
        to_point = (to_point - from_point) / base.camLens.get_far() * distance

        from_point = base.render.get_relative_point(base.camera, from_point)
        to_point = base.render.get_relative_point(base.camera, to_point)

        return base.physics_world.ray_test_closest(from_point, to_point)

    def fire(self, weapon):
        result = self._get_object_at_cursor(weapon.range)

        node = result.get_node()
        if (node and node.get_python_tag('character_id')):
            cid = node.get_python_tag('character_id')
            base.messenger.send('character_hit', [cid])

    def purchase_building(self):
        if self.in_buy_mode and self.current_building:
            print('BUYING', self.current_building.resource)
            self.current_building.owner = 'PLAYER'
            self.current_building.nodepath.set_color_scale(0, 0, 10, 1)
            self.resources[self.current_building.resource] += 1
            self.current_building = None

    def update(self, task):
        # Update movement
        movement = p3d.LVector3(self.player_movement)
        movement.normalize()
        movement *= self.player_speed
        self.player.set_linear_movement(movement)

        # Mouse movement
        if base.mouseWatcherNode.has_mouse():
            mouse = base.mouseWatcherNode.get_mouse()
            halfx = base.win.get_x_size() / 2
            halfy = base.win.get_y_size() / 2
            base.win.move_pointer(0, halfx, halfy)
            self.player.set_angular_movement(-mouse.x * self.mousex_sensitivity)

            self.camera_pitch += mouse.y * self.mousey_sensitivity
            if self.camera_pitch > 90:
                self.camera_pitch = 90
            elif self.camera_pitch < -90:
                self.camera_pitch = -90

        # Update the camera
        self.camera_pivot.set_p(self.camera_pitch)

        # Highlight buildings when in buy_mode:
        if self.in_buy_mode:
            result = self._get_object_at_cursor(self.BUY_DISTANCE).get_node()
            building = None

            if result and result.get_python_tag('building'):
                building = result.get_python_tag('building')

            if building and not building.owner and building != self.current_building:
                if self.current_building:
                    self.current_building.nodepath.clear_color_scale()
                self.current_building = building
                self.current_building.nodepath.set_color_scale(2, 0, 0, 1)
                print("BUY {}?".format(building.resource))
        elif self.current_building:
            self.current_building.nodepath.clear_color_scale()
            self.current_building = None

        self.hud.update(self)
        return task.cont
