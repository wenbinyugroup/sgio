#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains functions with different methods of calculating centroids."""

# cspell:includeRegExp comments

import numpy as np

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def averageVertices(nodeCoords):
    """averageVertices(nodeCoords)
    
    Estimates the centroid of *nodeCoords* by simply averaging the coordinates.
    
    Args:
        nodeCoords (list): A list of lists containing the nodal coordinates to be averaged.
        
    Returns:
        numpy.ndarray: A numpy array containing the coordinates of the element centroid."""
    
    c = np.average(nodeCoords,0)
    return c