from meshio import Mesh

class SGMesh(Mesh):
    """Extended mesh class that inherits from meshio.Mesh.
    
    This class provides additional functionality and custom format support
    while maintaining compatibility with the original meshio.Mesh class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



