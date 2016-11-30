#!/usr/bin/env python

from .basemodel import ModelParser, Exporter, Vertex, FaceVertex, Face
from .mesh import MeshPart

import os.path

def is_stl(filename):
    return filename[-4:] == '.stl'

class STLParser(ModelParser):

    def __init__(self, up_conversion = None):
        super().__init__(up_conversion)
        self.parsing_solid = False
        self.parsing_face = False
        self.parsing_loop = False
        self.current_face = None
        self.face_vertices = None

    def parse_line(self, string):

        if string == '':
            return

        split = string.split()

        if split[0] == 'solid':
            self.parsing_solid = True
            return

        if split[0] == 'endsolid':
            self.parsing_solid = False
            return

        if self.parsing_solid:

            if split[0] == 'facet' and split[1] == 'normal':
                self.parsing_face = True
                self.face_vertices = [FaceVertex(), FaceVertex(), FaceVertex()]
                self.current_face = Face(*self.face_vertices)
                return

            if self.parsing_face:

                if split[0] == 'outer' and split[1] == 'loop':
                    self.parsing_loop = True
                    return

                if split[0] == 'endloop':
                    self.parsing_loop = False
                    return

                if self.parsing_loop:

                    if split[0] == 'vertex':
                        current_vertex = Vertex().from_array(split[1:])
                        self.add_vertex(current_vertex)
                        self.face_vertices[0].vertex = len(self.vertices) - 1
                        self.face_vertices.pop(0)
                        return

                if split[0] == 'endfacet':
                    self.parsing_face = False
                    self.add_face(self.current_face)
                    self.current_face = None
                    self.face_vertices = None


class STLExporter(Exporter):
    def __init__(self, model):
        super().__init__(model)

    def __str__(self):
        string = 'solid {}\n'.format(os.path.basename(self.model.path[:-4]))

        self.model.generate_face_normals()

        faces = sum(map(lambda x: x.faces, self.model.parts), [])

        for face in faces:

            n  = self.model.normals[face.a.normal]
            v1 = self.model.vertices[face.a.vertex]
            v2 = self.model.vertices[face.b.vertex]
            v3 = self.model.vertices[face.c.vertex]

            string += "facet normal {} {} {}\n".format(n.x, n.y, n.z)

            string += "\touter loop\n"
            string += "\t\tvertex {} {} {}\n".format(v1.x, v1.y, v1.z)
            string += "\t\tvertex {} {} {}\n".format(v2.x, v2.y, v2.z)
            string += "\t\tvertex {} {} {}\n".format(v3.x, v3.y, v3.z)

            string += "\tendloop\n"
            string += "endfacet\n"

        string += 'endsolid {}'.format(os.path.basename(self.model.path[:-4]))
        return string
