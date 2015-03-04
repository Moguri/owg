from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
import panda3d.core as p3d


class PlayerController(DirectObject):

    def __init__(self, player, playernp, camera, mouse_watcher_node, win):
        DirectObject.__init__(self)

        self.player = player
        self.playernp = playernp
        self.camera = camera
        self.mouse_watcher_node = mouse_watcher_node
        self.window = win

        # Crosshair
        self.crosshair = OnscreenImage(image='crosshair.png',
                                       scale=(0.1, 0, 0.1),
                                       pos=(0, 0, 0))
        self.crosshair.set_transparency(p3d.TransparencyAttrib.MAlpha)

        halfx = self.window.get_x_size() / 2
        halfy = self.window.get_y_size() / 2
        self.window.move_pointer(0, halfx, halfy)
        self.mousex_sensitivity = 1000
        self.mousey_sensitivity = 10

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

    def update(self, task):
        # Update movement
        movement = p3d.Vec3(self.player_movement)
        movement.normalize()
        movement *= self.player_speed
        self.player.set_linear_movement(movement, True)

        # Mouse movement
        if self.mouse_watcher_node.has_mouse():
            mouse = self.mouse_watcher_node.get_mouse()
            halfx = self.window.get_x_size() / 2
            halfy = self.window.get_y_size() / 2
            self.window.move_pointer(0, halfx, halfy)
            self.player.set_angular_movement(-mouse.x * self.mousex_sensitivity)

            self.camera_pitch += mouse.y * self.mousey_sensitivity
            if self.camera_pitch > 90:
                self.camera_pitch = 90
            elif self.camera_pitch < -90:
                self.camera_pitch = -90

        # Update the camera
        cam_pos = self.playernp.get_pos()
        cam_pos.z += self.player.get_shape().get_half_height()
        self.camera.set_pos(cam_pos)

        self.camera.set_hpr(self.playernp.get_hpr())
        self.camera.set_p(self.camera_pitch)
        return task.cont
