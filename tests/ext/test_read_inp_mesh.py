from pathlib import Path
import numpy as np
from sgio import inprw

def read_inp_mesh(filename):
    """
    Read mesh data from an Abaqus INP file.
    
    Parameters
    ----------
    filename : str
        Path to the Abaqus INP file
        
    Returns
    -------
    dict
        Dictionary containing:
        - points : numpy.ndarray
            Array of node coordinates
        - cells : list
            List of tuples containing (cell_type, connectivity_array)
        - cell_sets : dict
            Dictionary of element sets
    """
    # Initialize the inpRW parser
    inp = inprw.inpRW(filename)

    # Parse the input file
    inp.parse()

    # Extract node coordinates
    points = []
    # print(inp.nd)
    for node_id, node in inp.nd.items():
        # Convert node coordinates to float and store
        points.append(list(map(float, node.data[1:])))
    points = np.asarray(points)

    # Process cells (elements)
    cells = []
    cell_types = []
    cell_elem_ids = {}
    cell_sets = {}

    print(inp._ed)

    # Process each element type
    for elem_type, elements in inp.ed.items():
        # Get element connectivity
        connectivity = []
        elem_ids = []

        for elem_id, elem in elements.items():
            # First value is element ID, rest are node IDs
            elem_ids.append(elem_id)
            connectivity.append(list(map(int, elem.data[1:])))

        if connectivity:
            cells.append((elem_type, np.array(connectivity)))
            cell_elem_ids[elem_type] = elem_ids

    # Process element sets if they exist
    if hasattr(inp, 'elset'):
        for set_name, set_data in inp.elset.items():
            cell_sets[set_name] = set_data.data

    return {
        'points': points,
        'cells': cells,
        'cell_sets': cell_sets
    }

# Example usage
if __name__ == '__main__':
    # Resolve path relative to this test file
    test_dir = Path(__file__).parent.parent
    fn = test_dir / 'files' / 'abaqus' / 'sg2_i_simple_eo1.inp'

    mesh_data = read_inp_mesh(str(fn))
    # print(mesh_data)

    # Access the data
    points = mesh_data['points']
    cells = mesh_data['cells']
    element_sets = mesh_data['cell_sets']

    # Print some information
    print(f"Number of nodes: {len(points)}")
    print(f"Number of element types: {len(cells)}")
    for cell_type, connectivity in cells:
        print(f"Element type {cell_type}: {len(connectivity)} elements")
