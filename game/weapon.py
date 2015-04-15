import os
import json

class Weapon(object):
    __slots__ = [
            'name',
            'range',
            '_weapon_conf',
    ]

    def __init__(self, weapon_conf):
        with open(os.path.join('weapons', weapon_conf) + '.json') as f:
            self._weapon_conf = json.load(f)

        self.name = self._weapon_conf['name']
        self.range = self._weapon_conf['range']
