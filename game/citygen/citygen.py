import ctypes
import random
from data import *


def weighted_choice(choices):
    total = sum([i[1] for i in choices])
    r = random.uniform(0, total)
    i = 0
    for choice, weight in choices:
        if i + weight > r:
            return choice
        i += weight


class City(object):
    __slots__ = ["buildings", "road_mesh", "spawn_points", "meshes",
                 "materials", "width", "height"]

    def __init__(self):
        self.buildings = []
        self.meshes = []
        self.materials = []
        self.spawn_points = []
        self.road_mesh = None
        self.width = 0
        self.height = 0

    def get_map(self, resolution_x, resolution_y):
        return gen_map(self, resolution_x, resolution_y)


class CityGen(object):
    def __init__(self):
        self.city = City()

    def generate(self):
        self.city = gen_city()

    def dump_obj(self, path, name):
        write_obj(self.city, path, name)

    def get_map(self, resx, resy):
        return gen_map(self, resx, resy)


def create_lots(lot, block):
    width = lot[2] - lot[0]
    height = lot[3] - lot[1]
    if width < 30 or height < 30:
        if lot[0] == block[0] or lot[1] == block[1] or lot[2] == block[2] or lot[3] == block[3]:
            return [lot]
        return []

    ret = []

    if width > height:
        new_width = width * random.uniform(0.3, 0.7)
        ret += create_lots((lot[0], lot[1], lot[0]+new_width, lot[3]), block)
        ret += create_lots((lot[0]+new_width, lot[1], lot[2], lot[3]), block)
        return ret

    new_height = height * random.uniform(0.3, 0.7)
    ret += create_lots((lot[0], lot[1], lot[2], lot[1]+new_height), block)
    ret += create_lots((lot[0], lot[1]+new_height, lot[2], lot[3]), block)
    return ret


def gen_city(city_width=500, city_height=500, lane_width=6, block_width=80, block_height=80, block_var=0.25):
    city = City()
    city.width = city_width
    city.height = city_height

    x_off = city_width / 2.0
    y_off = city_height / 2.0

    # Roads
    vert_roads = []
    vert_progress = 0
    while True:
        variance = random.random() * block_var * block_width
        progress = block_width + variance
        if vert_progress + progress > city_width:
            break
        vert_progress += progress
        vert_roads.append(vert_progress)

    hor_roads = []
    hor_progress = 0
    while True:
        variance = random.random() * block_var * block_height
        progress = block_height + variance
        if hor_progress + progress > city_height:
            break
        hor_progress += progress
        hor_roads.append(hor_progress)

    x_offset = (city_width - hor_progress) / 2.0
    y_offset = (city_height - vert_progress) / 2.0

    # Blocks
    blocks = []
    road_verts = []
    road_faces = []
    for i in range(len(vert_roads)):
        x1 = 0.0 if i == 0 else vert_roads[i-1] + lane_width
        x1 += x_offset
        x2 = vert_roads[i] - lane_width
        x2 += x_offset
        for j in range(len(hor_roads)):
            y1 = 0.0 if j == 0 else hor_roads[j-1] + lane_width
            y1 += y_offset
            y2 = hor_roads[j] - lane_width
            y2 += y_offset

            blocks.append((x1, y1, x2, y2))

            if i != len(vert_roads)-1 and j != len(hor_roads)-1:
                verts = []
                normal = (0, 0, 1)
                x3 = vert_roads[i] + lane_width + x_offset
                y3 = hor_roads[j] + lane_width + y_offset

                spawn_point = ((x2+x3)/2.0-x_off, (y2+y3)/2.0-y_off, 0.0)
                city.spawn_points.append(spawn_point)

                vert_off = len(road_verts)
                road_verts.append(Vertex((x2 - x_off, y2 - y_off, 0.0), normal))
                road_verts.append(Vertex((x3 - x_off, y2 - y_off, 0.0), normal))
                road_verts.append(Vertex((x3 - x_off, y3 - y_off, 0.0), normal))
                road_verts.append(Vertex((x2 - x_off, y3 - y_off, 0.0), normal))
                road_faces.append((vert_off + 0, vert_off + 1, vert_off + 2))
                road_faces.append((vert_off + 2, vert_off + 3, vert_off + 0))
                if j > 0:
                    road_faces.append((vert_off-1, vert_off-2, vert_off+1))
                    road_faces.append((vert_off+1, vert_off+0, vert_off-1))
                if i > 0:
                    vert_x_off = vert_off - (len(hor_roads)-1) * 4
                    road_faces.append((vert_x_off+1, vert_off+0, vert_off+3))
                    road_faces.append((vert_off+3, vert_x_off+2, vert_x_off+1))
    city.road_mesh = Mesh(road_verts, road_faces)

    # Lots
    lots = []
    for block in blocks:
        lots += create_lots(block, block)

    # Buildings
    resource_choices = [(key, value.weight) for key, value in RESOURCES.items()]
    for lot in lots:
        floors = random.randint(1, 5)
        height = floors * 4

        verts = []
        pos_x = (lot[0] + lot[2]) / 2.0# - x_off
        pos_y = (lot[1] + lot[3]) / 2.0# - y_off

        # Top
        normal = (0, 0, 1)
        verts.append(Vertex((lot[0] - pos_x, lot[1] - pos_y, height), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[1] - pos_y, height), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[3] - pos_y, height), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[3] - pos_y, height), normal))

        #North
        normal = (0, 1, 0)
        verts.append(Vertex((lot[2] - pos_x, lot[1] - pos_y, height), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[1] - pos_y, height), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[1] - pos_y, 0.0), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[1] - pos_y, 0.0), normal))

        # East
        normal = (1, 0, 0)
        verts.append(Vertex((lot[2] - pos_x, lot[3] - pos_y, height), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[1] - pos_y, height), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[1] - pos_y, 0.0), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[3] - pos_y, 0.0), normal))

        # South
        normal = (0, -1, 0)
        verts.append(Vertex((lot[0] - pos_x, lot[3] - pos_y, height), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[3] - pos_y, height), normal))
        verts.append(Vertex((lot[2] - pos_x, lot[3] - pos_y, 0.0), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[3] - pos_y, 0.0), normal))

        # West
        normal = (-1, 0, 0)
        verts.append(Vertex((lot[0] - pos_x, lot[1] - pos_y, height), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[3] - pos_y, height), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[3] - pos_y, 0.0), normal))
        verts.append(Vertex((lot[0] - pos_x, lot[1] - pos_y, 0.0), normal))

        # Bottom
        # verts.append((lot[0] - x_off, lot[1] - y_off, 0.0))
        # verts.append((lot[2] - x_off, lot[1] - y_off, 0.0))
        # verts.append((lot[2] - x_off, lot[3] - y_off, 0.0))
        # verts.append((lot[0] - x_off, lot[3] - y_off, 0.0))


        faces = []
        faces.append((0, 1, 2))
        faces.append((2, 3, 0))

        faces.append((4, 5, 6))
        faces.append((6, 7, 4))

        faces.append((8, 9, 10))
        faces.append((10, 11, 8))

        faces.append((12, 13, 14))
        faces.append((14, 15, 12))

        faces.append((16, 17, 18))
        faces.append((18, 19, 16))

        pos = (pos_x-x_off, pos_y-y_off, 0.0)
        mesh = Mesh(verts, faces)
        city.meshes.append(mesh)
        collision = ((lot[2]-lot[0])/2.0, (lot[3] - lot[1])/2.0, height/2.0)
        if lot[0] < vert_roads[0] + x_offset or lot[2] > vert_roads[-2] + x_offset:
            resource = "NONE"
        elif lot[1] < hor_roads[0] + y_offset or lot[3] > hor_roads[-2] + y_offset:
            resource = "NONE"
        else:
            resource = weighted_choice(resource_choices)
        city.buildings.append(Building(pos, mesh, collision, resource))

    return city


def gen_map(city, resx, resy):
    img_data = (ctypes.c_ubyte * (4 * resx * resy))(*([0, 0, 0, 0] * (resx * resy)))

    city_width = city_height = 500.0
    x_off = city_width / 2.0
    y_off = city_height / 2.0
    w_ratio = resx / city_width
    h_ratio = resy / city_height

    for building in city.buildings:
        x1 = int((building.position[0] - building.collision[0] + x_off) * w_ratio)
        x2 = int((building.position[0] + building.collision[0] + x_off) * w_ratio)
        y1 = int((building.position[1] - building.collision[1] + y_off) * h_ratio)
        y2 = int((building.position[1] + building.collision[1] + y_off) * h_ratio)

        for y in range(y1, y2):
            for x in range(x1, x2):
                i = y * (resy*4) + x*4

                a = 160
                if x <= x1 + 0 or x >= x2 - 1 - 0:
                    r, g, b = (0, 0, 0)
                elif y <= y1 + 0 or y >= y2 - 1 - 0:
                    r, g, b = (0, 0, 0)
                elif building.owner and (x % 8 == 1 or y % 8 == 1):
                    r, g, b = (255, 255, 255)
                else:
                    r, g, b = RESOURCES[building.resource].color

                img_data[i+0] = b
                img_data[i+1] = g
                img_data[i+2] = r
                img_data[i+3] = a

    return img_data


def write_obj(city, path, name):
        with open(path + "/" + name + ".obj", "w") as fout:
            # Some texture coordinates
            fout.write("vt 0.0 1.0\n")
            fout.write("vt 1.0 1.0\n")
            fout.write("vt 1.0 0.0\n")
            fout.write("vt 0.0 0.0\n")


            # Ground plane
            # w = city_width / 2.0
            # h = city_height / 2.0
            # fout.write("v %d %d %d\n" % (-w, -h, 0.0))
            # fout.write("v %d %d %d\n" % (w, -h, 0.0))
            # fout.write("v %d %d %d\n" % (w, h, 0.0))
            # fout.write("v %d %d %d\n" % (-w, h, 0.0))
            # vert_count = 4

            vert_count = 0
            offsets = []

            for building in city.buildings:
                mesh = building.mesh
                offsets.append(vert_count + 1)
                vert_count += len(mesh.vertices)
                for vert in mesh.vertices:
                    fout.write("v %f %f %f\n" % vert.position)
            for building in city.buildings:
                for vert in building.mesh.vertices:
                    fout.write("vn %f %f %f\n" % vert.normal)
            for i, building in enumerate(city.buildings):
                mesh = building.mesh
                fout.write("o %d\n" % i)
                fout.write("usemtl building%d\n" % random.randint(0, 2))
                for face in mesh.faces:
                    fout.write("f %s %s %s\n" % tuple(["%d//%d" % (i, i) for i in face]))

            fout.write("o ground\n")
            fout.write("usemtl ground\n")
            fout.write("f 1 2 3 4\n")

        with open(path + "/" + name + ".mtl", "w") as fout:
            colors = []
            colors.append((112, 163, 10))
            colors.append((90, 135, 0))
            colors.append((67, 100, 0))
            for i, color in enumerate(colors):
                color = tuple([(c/255.0) ** 2.2 for c in color])
                fout.write("newmtl building%d\n" % i)
                fout.write("Ka 1.0 1.0 1.0\n")
                fout.write("Kd %f %f %f\n" % color)
                fout.write("Ks 0.0 0.0 0.0\n")
                fout.write("Ns 0.0\n")
                fout.write("Tr 0.0\n")
                fout.write("illum 1\n")
            ground_color = (17, 127, 127)
            ground_color = tuple([(c/255.0) ** 2.2 for c in ground_color])
            fout.write("newmtl ground\n")
            fout.write("Ka 1.0 1.0 1.0\n")
            fout.write("Kd %f %f %f\n" % ground_color)
            fout.write("Ks 0.0 0.0 0.0\n")
            fout.write("Ns 0.0\n")
            fout.write("Tr 0.0\n")
            fout.write("illum 1\n")


if __name__ == "__main__":
    gen = CityGen()
    gen.generate()
    gen.dump_obj(".", "out")
