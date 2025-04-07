import meshio.gmsh.main as mgmsh
import meshio.gmsh._gmsh22 as mgmsh22
import meshio.gmsh._gmsh40 as mgmsh40
import meshio.gmsh._gmsh41 as mgmsh41


def read_buffer(f, **kwargs):
    return mgmsh.read_buffer(f)



