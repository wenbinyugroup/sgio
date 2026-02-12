"""Interface parsing utilities for Structure Gene data.

This module provides functions for reading interface pairs and nodes
from Structure Gene interface files.
"""

from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


def readSGInterfacePairs(fn: str) -> list[list[int | float]]:
    """Read Structure Gene interface pairs from file.
    
    Parameters
    ----------
    fn : str
        Filename of the interface pairs file.
        
    Returns
    -------
    list[list[int | float]]
        List of interface pairs, each containing [id1, id2, x1, y1, x2, y2].
    """
    logger.debug('reading sg interface paris: {0}...'.format(fn))
    
    itf_pairs = []
    
    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue
            
            line = line.split()
            
            _pair = [
                int(line[1]), int(line[2]),
                float(line[3]), float(line[4]),
                float(line[5]), float(line[6])
            ]
            
            itf_pairs.append(_pair)
    
    return itf_pairs


def readSGInterfaceNodes(fn: str) -> list[list[int]]:
    """Read Structure Gene interface nodes from file.
    
    Parameters
    ----------
    fn : str
        Filename of the interface nodes file.
        
    Returns
    -------
    list[list[int]]
        List of interface node groups, each containing a list of node IDs.
    """
    logger.debug('reading sg interface nodes: {0}...'.format(fn))
    
    itf_nodes = []
    
    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue
            
            line = line.split()
            
            _nodes = []
            for nid in line[1:]:
                _nodes.append(int(nid))
            
            itf_nodes.append(_nodes)
    
    return itf_nodes
