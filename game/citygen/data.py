class ResourceData(object):
	__slots__ = ["weight", "color"]

	def __init__(self, weight, color):
		self.weight = weight
		self.color = color


RESOURCES = {
	"NONE": ResourceData(0.0, (32, 32, 32)),
	"EMPTY": ResourceData(0.85, (170, 170, 170)),
	"ALPHA": ResourceData(0.05, (170, 0, 0)),
	"BETA": ResourceData(0.05, (0, 0, 170)),
	"GAMMA": ResourceData(0.05, (0, 170, 0)),
}


class Building(object):
	__slots__ = ["position", "mesh", "collision", "resource", "nodepath", "owner"]

	def __init__(self, position, mesh, collision, resource):
		self.position = position
		self.mesh = mesh
		self.collision = collision
		self.resource = resource
		self.nodepath = None
		self.owner = None


class Mesh(object):
	__slots__ = ["vertices", "faces", "material"]

	def __init__(self, vertices, faces, material=None):
		self.vertices = vertices
		self.faces = faces
		self.material = material


class Vertex(object):
	__slots__ = ["position", "normal"]

	def __init__(self, position=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0)):
		self.position = position
		self.normal = normal