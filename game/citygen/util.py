import panda3d.core as p3d


def mesh_to_p3d_node(mesh, name, material):
        node = p3d.GeomNode(name)

        vdata = p3d.GeomVertexData(name,
            p3d.GeomVertexFormat.get_v3n3(),
            p3d.GeomEnums.UH_stream)
        vdata.unclean_set_num_rows(len(mesh.vertices))

        vwriter = p3d.GeomVertexWriter(vdata, 'vertex')
        nwriter = p3d.GeomVertexWriter(vdata, 'normal')
        for vert in mesh.vertices:
            vwriter.add_data3(*vert.position)
            nwriter.add_data3(*vert.normal)
        vwriter = None
        nwriter = None

        prim = p3d.GeomTriangles(p3d.GeomEnums.UH_stream)
        for face in mesh.faces:
            prim.add_vertices(*face)

        render_state = p3d.RenderState.make_empty()

        render_state = render_state.set_attrib(p3d.MaterialAttrib.make(material))

        geom = p3d.Geom(vdata)
        geom.add_primitive(prim)
        node.add_geom(geom, render_state)

        return node