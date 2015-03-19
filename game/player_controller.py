from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
import panda3d.core as p3d


class PlayerController(DirectObject):

    def __init__(self, player):
        DirectObject.__init__(self)

        self.player = player

        # Crosshair
        self.crosshair = OnscreenImage(image='crosshair.png',
                                       scale=(0.1, 0, 0.1),
                                       pos=(0, 0, 0))
        self.crosshair.set_transparency(p3d.TransparencyAttrib.MAlpha)

        halfx = base.win.get_x_size() / 2
        halfy = base.win.get_y_size() / 2
        base.win.move_pointer(0, halfx, halfy)
        mx_sens_config = p3d.ConfigVariableInt('mousex-sensitivity')
        self.mousex_sensitivity = mx_sens_config.get_value() * 10.0
        my_sens_config = p3d.ConfigVariableInt('mousey-sensitivity')
        self.mousey_sensitivity = my_sens_config.get_value() / 10.0

        self.camera_pitch = 0

        self.player_movement = p3d.Vec3(0, 0, 0)
        self.player_speed = 10

        self.accept('move_forward', self.update_movement, ['forward', True])
        self.accept('move_forward-up', self.update_movement, ['forward', False])
        self.accept('move_backward', self.update_movement, ['backward', True])
        self.accept('move_backward-up', self.update_movement, ['backward', False])
        self.accept('move_left', self.update_movement, ['left', True])
        self.accept('move_left-up', self.update_movement, ['left', False])
        self.accept('move_right', self.update_movement, ['right', True])
        self.accept('move_right-up', self.update_movement, ['right', False])
        self.accept('jump', self.jump)
        self.accept('fire', self.fire)

    def update_movement(self, direction, activate):
        move_delta = p3d.Vec3(0, 0, 0)

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

    def fire(self):
        from_point = p3d.Point3()
        to_point = p3d.Point3()
        base.camLens.extrude(p3d.Point2(0, 0), from_point, to_point)

        from_point = base.render.get_relative_point(base.camera, from_point)
        to_point = base.render.get_relative_point(base.camera, to_point)

        result = base.physics_world.ray_test_closest(from_point, to_point)

        node = result.get_node()
        if (node and node.get_python_tag('character_id')):
            cid = node.get_python_tag('character_id')
            base.messenger.send('character_hit', [cid])

    def update(self, task):
        # Update movement
        movement = p3d.Vec3(self.player_movement)
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
        cam_pos = self.player.get_pos()
        cam_pos.z += self.player.get_shape().get_half_height()
        base.camera.set_pos(cam_pos)

        base.camera.set_hpr(self.player.get_hpr())
        base.camera.set_p(self.camera_pitch)
        return task.cont
