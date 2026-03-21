"""Common material reading functions for various file formats.

This module provides shared functionality for reading material properties
from different input formats (VABS, SwiftComp, etc.).
"""

from __future__ import annotations

import logging
from typing import Any, TextIO

import sgio.model as smdl
import sgio.utils as sutl


logger = logging.getLogger(__name__)


def read_material_rotation_combinations(
    file: TextIO,
    ncomb: int,
    comment_char: str = '!'
) -> dict[int, list[int | float]]:
    """Read material-rotation combinations from input file.
    
    This function is used by both VABS and SwiftComp formats to read
    the combinations of material ID and in-plane rotation angle.
    
    Parameters
    ----------
    file : TextIO
        File object to read from.
    ncomb : int
        Number of combinations to read.
    comment_char : str
        Comment character used in the file ('!' for VABS, '#' for SwiftComp).
        
    Returns
    -------
    dict[int, list[int | float]]
        Dictionary mapping combination_id to [material_id, rotation_angle].
    """
    logger.debug('reading combinations of material and in-plane rotations...')
    
    combinations = {}
    
    counter = 0
    while counter < ncomb:
        line = file.readline().split(comment_char)[0].strip()
        while line == '':
            line = file.readline().split(comment_char)[0].strip()
        
        line = line.split()
        comb_id = int(line[0])
        mate_id = int(line[1])
        ip_rotation = sutl.fortran_float(line[2])
        
        combinations[comb_id] = [mate_id, ip_rotation]
        
        counter += 1
    
    return combinations


def read_materials(
    file: TextIO,
    nmate: int,
    comment_char: str = '!',
    has_ntemp: bool = False,
    physics: int = 0
) -> tuple[dict[str, smdl.CauchyContinuumModel], list[list[str | int]]]:
    """Read materials from input file.
    
    Parameters
    ----------
    file : TextIO
        File object to read from.
    nmate : int
        Number of materials to read.
    comment_char : str
        Comment character used in the file ('!' for VABS, '#' for SwiftComp).
    has_ntemp : bool
        Whether the format includes ntemp parameter (SwiftComp format).
    physics : int
        Physics flag for reading thermal properties.
        
    Returns
    -------
    tuple
        (materials_dict, material_name_id_pairs)
        materials_dict: {material_name: MaterialModel}
        material_name_id_pairs: [[name, id], ...]
    """
    logger.debug('reading materials...')
    
    materials = {}
    material_name_id_pairs = []
    
    counter = 0
    while counter < nmate:
        line = file.readline().split(comment_char)[0].strip()
        while line == '':
            line = file.readline().split(comment_char)[0].strip()
        
        line = line.split()
        
        # Read material id, isotropy, and optionally ntemp
        if has_ntemp:
            mate_id, isotropy, ntemp = list(map(int, line))
        else:
            mate_id, isotropy = list(map(int, line))
            ntemp = 1
        
        material = read_material(
            file,
            isotropy,
            ntemp,
            comment_char=comment_char,
            physics=physics
        )
        
        # Use material name as key; generate default name if not set
        mat_name = material.name if material.name else f'Material_{mate_id}'
        material.name = mat_name  # Ensure name is set
        materials[mat_name] = material
        
        # Store name-ID pair
        material_name_id_pairs.append([mat_name, mate_id])
        
        counter += 1
    
    return materials, material_name_id_pairs


def read_material(
    file: TextIO,
    isotropy: int,
    ntemp: int = 1,
    comment_char: str = '!',
    physics: int = 0
) -> smdl.CauchyContinuumModel:
    """Read a single material from input file.
    
    Parameters
    ----------
    file : TextIO
        File object to read from.
    isotropy : int
        Material isotropy level (0=isotropic, 1=orthotropic, 2=anisotropic).
    ntemp : int
        Number of temperature points.
    comment_char : str
        Comment character used in the file.
    physics : int
        Physics flag for reading thermal properties.
        
    Returns
    -------
    CauchyContinuumModel
        Material model with properties.
    """
    mp = smdl.CauchyContinuumModel()
    mp.set('isotropy', isotropy)
    
    temp_counter = 0
    while temp_counter < ntemp:
        # Read temperature and density (SwiftComp format)
        # or just elastic properties first (VABS format)
        if comment_char == '#':  # SwiftComp format
            line = file.readline().strip()
            while line == '':
                line = file.readline().strip()
            line = line.split()
            temperature, density = list(map(sutl.fortran_float, line))
            mp.temperature = temperature
        
        # Read elastic properties
        elastic_props = read_elastic_property(file, isotropy, comment_char)
        mp.setElastic(elastic_props, isotropy)
        
        # Read density (VABS format)
        if comment_char == '!':  # VABS format
            line = file.readline().split(comment_char)[0].strip()
            while line == '':
                line = file.readline().split(comment_char)[0].strip()
            density = sutl.fortran_float(line)
        
        mp.set('density', density)
        
        # Read thermal properties if needed
        if physics in [1, 4, 6] and comment_char == '#':  # SwiftComp
            cte, specific_heat = read_thermal_property(file, isotropy)
            mp.set('cte', cte)
            mp.set('specific_heat', specific_heat)
        
        temp_counter += 1
    
    return mp


def read_elastic_property(
    file: TextIO,
    isotropy: int,
    comment_char: str = '!'
) -> list[float]:
    """Read elastic properties from input file.
    
    Parameters
    ----------
    file : TextIO
        File object to read from.
    isotropy : int
        Material isotropy level (0=isotropic, 1=orthotropic, 2=anisotropic).
    comment_char : str
        Comment character used in the file.
        
    Returns
    -------
    list[float]
        Elastic constants.
    """
    constants = []
    
    if isotropy == 0:
        nrow = 1
    elif isotropy == 1:
        nrow = 3
    elif isotropy == 2:
        nrow = 6
    else:
        nrow = 0
    
    for i in range(nrow):
        line = file.readline().split(comment_char)[0].strip()
        while line == '':
            line = file.readline().split(comment_char)[0].strip()
        constants.extend(list(map(sutl.fortran_float, line.split())))
    
    return constants


def read_thermal_property(
    file: TextIO,
    isotropy: int
) -> tuple[list[float], float]:
    """Read thermal properties from input file.
    
    Parameters
    ----------
    file : TextIO
        File object to read from.
    isotropy : int
        Material isotropy level.
        
    Returns
    -------
    tuple
        (cte, specific_heat) - coefficient of thermal expansion and specific heat.
    """
    cte = []
    specific_heat = 0.0
    
    line = sutl.readNextNonEmptyLine(file)
    line = list(map(sutl.fortran_float, line.split()))
    
    if isotropy == 0:
        cte = line[:1]
        specific_heat = line[1]
    elif isotropy == 1:
        cte = line[:3]
        specific_heat = line[3]
    elif isotropy == 2:
        cte = line[:6]
        specific_heat = line[6]
    
    return cte, specific_heat
