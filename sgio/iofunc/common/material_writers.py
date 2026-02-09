"""Common material writing functions for various file formats.

This module provides shared functionality for writing material properties
to different output formats (VABS, SwiftComp, etc.).
"""

from __future__ import annotations

import logging
from typing import TextIO

import sgio.model as smdl
import sgio.utils as sutl
from sgio.core.sg import StructureGene


logger = logging.getLogger(__name__)


def write_material_combos(
    sg: StructureGene,
    file: TextIO,
    sfi: str = '8d',
    sff: str = '20.12e',
    comment_char: str = '!'
) -> None:
    """Write material-orientation combinations to file.
    
    Parameters
    ----------
    sg : StructureGene
        Structure gene object containing material combinations.
    file : TextIO
        File object to write to.
    sfi : str
        String format for integers.
    sff : str
        String format for floats.
    comment_char : str
        Comment character ('!' for VABS, '#' for SwiftComp).
    """
    ssfi = '{:' + sfi + '}'
    ssff = '{:' + sff + '}'
    
    # Get material name -> ID mapping for export
    mat_id_map = sg.get_export_material_ids()
    
    count = 0
    for cid, combo in sg.mocombos.items():
        count += 1
        mat_name, angle = combo  # combo is now (material_name, angle)
        mat_id = mat_id_map[mat_name]  # Get numeric ID for export
        file.write((ssfi + ssfi + ssff).format(cid, mat_id, angle))
        if count == 1:
            file.write(f'  {comment_char} combination id, material id, in-plane rotation angle')
        file.write('\n')
    file.write('\n')


def write_material(
    mid: int,
    material: smdl.CauchyContinuumModel,
    file: TextIO,
    analysis: str,
    physics: int = 0,
    sfi: str = '8d',
    sff: str = '20.12e',
    comment_char: str = '!',
    has_ntemp: bool = False
) -> None:
    """Write a single material to file.
    
    Parameters
    ----------
    mid : int
        Material ID number.
    material : CauchyContinuumModel
        Material model to write.
    file : TextIO
        File object to write to.
    analysis : str
        Analysis type ('h' for homogenization, 'f' for failure).
    physics : int
        Physics flag for thermal properties.
    sfi : str
        String format for integers.
    sff : str
        String format for floats.
    comment_char : str
        Comment character ('!' for VABS, '#' for SwiftComp).
    has_ntemp : bool
        Whether to include ntemp in output (SwiftComp format).
    """
    anisotropy = material.get('isotropy')
    
    if analysis == 'h':
        # Write material properties for homogenization
        
        # Material header line
        if has_ntemp:
            sutl.writeFormatIntegers(file, (mid, anisotropy, 1), sfi, newline=False)
            file.write(f'  {comment_char} material id, anisotropy, ntemp\n')
            
            # Temperature and density (SwiftComp format)
            sutl.writeFormatFloats(
                file, (material.get('temperature'), material.get('density')), sff)
        else:
            sutl.writeFormatIntegers(file, (mid, anisotropy), sfi, newline=False)
            file.write(f'  {comment_char} material id, anisotropy\n')
        
        # Write elastic properties
        if anisotropy == 0:
            # Isotropic material
            if has_ntemp:  # SwiftComp format uses e1, nu12
                sutl.writeFormatFloats(
                    file, [material.get('e1'), material.get('nu12')], sff)
            else:  # VABS format uses e, nu
                sutl.writeFormatFloats(
                    file, [material.get('e'), material.get('nu')], sff)
            
            if physics == 3 and not has_ntemp:  # VABS thermal
                sutl.writeFormatFloats(file, [material.get('alpha'),], sff)
        
        elif anisotropy == 1:
            # Orthotropic material
            sutl.writeFormatFloats(
                file, [material.get('e1'), material.get('e2'), material.get('e3')], sff)
            sutl.writeFormatFloats(
                file, [material.get('g12'), material.get('g13'), material.get('g23')], sff)
            sutl.writeFormatFloats(
                file, [material.get('nu12'), material.get('nu13'), material.get('nu23')], sff)
            
            if physics == 3 and not has_ntemp:  # VABS thermal
                sutl.writeFormatFloats(
                    file, [material.get('alpha11'), material.get('alpha22'), material.get('alpha33')], sff)
        
        elif anisotropy == 2:
            # Anisotropic material
            for i in range(6):
                for j in range(i, 6):
                    _v = material.get(f'c{i+1}{j+1}')
                    file.write(f'{_v:{sff}}')
                file.write('\n')
            
            if physics == 3 and not has_ntemp:  # VABS thermal
                sutl.writeFormatFloats(
                    file, [
                        material.get('alpha11'),
                        material.get('alpha12')*2,
                        material.get('alpha13')*2,
                        material.get('alpha22'),
                        material.get('alpha23')*2,
                        material.get('alpha33')
                    ], sff)
        
        # Density (VABS format only)
        if not has_ntemp:
            sutl.writeFormatFloats(file, [material.get('density'),], sff)
        
        # Thermal properties (SwiftComp format)
        if physics in [1, 4, 6] and has_ntemp:
            sutl.writeFormatFloats(
                file, material.get('cte')+[material.get('specific_heat'),], sff)
    
    elif analysis == 'f' or analysis.startswith('f'):
        # Write material properties for failure analysis
        strength = _get_strength_constants(material, anisotropy)
        
        sutl.writeFormatIntegers(
            file,
            [material.failure_criterion, len(strength)],
            sfi
        )
        
        if has_ntemp:  # SwiftComp format
            sutl.writeFormatFloats(file, [material.get('char_len'),], sff)
        
        sutl.writeFormatFloats(file, strength, sff)
    
    file.write('\n')


def write_materials(
    dict_materials: dict[str, smdl.CauchyContinuumModel],
    file: TextIO,
    analysis: str,
    physics: int = 0,
    sfi: str = '8d',
    sff: str = '20.12e',
    comment_char: str = '!',
    has_ntemp: bool = False,
    mat_id_map: dict[str, int] | None = None
) -> None:
    """Write all materials to file.
    
    Parameters
    ----------
    dict_materials : dict
        Dictionary of materials indexed by name.
    file : TextIO
        File object to write to.
    analysis : str
        Analysis type ('h' for homogenization, 'f' for failure).
    physics : int
        Physics flag for thermal properties.
    sfi : str
        String format for integers.
    sff : str
        String format for floats.
    comment_char : str
        Comment character ('!' for VABS, '#' for SwiftComp).
    has_ntemp : bool
        Whether to include ntemp in output (SwiftComp format).
    mat_id_map : dict, optional
        Mapping from material name to numeric ID. If not provided,
        materials are numbered sequentially.
    """
    logger.debug('writing materials...')
    
    # Use provided ID map or create default sequential mapping
    if mat_id_map is None:
        mat_id_map = {name: idx + 1 for idx, name in enumerate(dict_materials.keys())}
    
    for mat_name, m in dict_materials.items():
        mid = mat_id_map[mat_name]
        write_material(
            mid=mid,
            material=m,
            file=file,
            analysis=analysis,
            physics=physics,
            sfi=sfi,
            sff=sff,
            comment_char=comment_char,
            has_ntemp=has_ntemp
        )
    
    file.write('\n')


def write_displacement_rotation(
    file: TextIO,
    displacement: list[float] | None = None,
    rotation: list[list[float]] | None = None,
    sff: str = '20.12e'
) -> None:
    """Write displacement and rotation to file.
    
    Parameters
    ----------
    file : TextIO
        File object to write to.
    displacement : list[float]
        Displacement vector [u1, u2, u3].
    rotation : list[list[float]]
        Direction cosine matrix (3x3).
    sff : str
        String format for floats.
    """
    if displacement is None:
        displacement = [0, 0, 0]
    if rotation is None:
        rotation = [[1,0,0],[0,1,0],[0,0,1]]
    
    sutl.writeFormatFloats(file, displacement, sff)
    file.write('\n')
    sutl.writeFormatFloatsMatrix(file, rotation, sff)


def write_load(
    file: TextIO,
    macro_response: smdl.StateCase,
    model: str,
    sff: str = '20.12e'
) -> None:
    """Write load data to file.
    
    Parameters
    ----------
    file : TextIO
        File object to write to.
    macro_response : StateCase
        Macro response containing load data.
    model : str
        Model type ('BM1', 'BM2', 'PL1', 'PL2', 'SD1').
    sff : str
        String format for floats.
    """
    _load = macro_response.load.data
    
    model_upper = model.upper() if isinstance(model, str) else str(model)
    
    if model_upper == 'BM1' or model == 0:
        sutl.writeFormatFloats(file, _load, fmt=sff)
    
    elif model_upper == 'BM2' or model == 1:
        sutl.writeFormatFloats(file, [_load[i] for i in [0, 3, 4, 5]], fmt=sff)
        sutl.writeFormatFloats(file, [_load[i] for i in [1, 2]], fmt=sff)
        file.write('\n')
        
        # Distributed load
        _distr_load = macro_response.distributed_load
        if _distr_load is None:
            _distr_load = [[0,]*6]*4
        else:
            _distr_load = _distr_load.data
        sutl.writeFormatFloats(file, _distr_load[0], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[1], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[2], fmt=sff)
        sutl.writeFormatFloats(file, _distr_load[3], fmt=sff)
    
    elif model_upper == 'PL1':
        sutl.writeFormatFloats(file, _load, fmt=sff)
    
    elif model_upper == 'PL2' or model_upper == 'SD1':
        pass  # No special handling needed
    
    file.write('\n')


def _get_strength_constants(
    material: smdl.CauchyContinuumModel,
    anisotropy: int
) -> list[float]:
    """Get strength constants for failure analysis.
    
    Parameters
    ----------
    material : CauchyContinuumModel
        Material model.
    anisotropy : int
        Material isotropy level.
        
    Returns
    -------
    list[float]
        Strength constants based on failure criterion.
    """
    strength = []
    
    if material.failure_criterion == 4:  # Tsai-Wu
        if anisotropy != 0:
            strength = [
                material.get('x1t'), material.get('x2t'), material.get('x3t'),
                material.get('x1c'), material.get('x2c'), material.get('x3c'),
                material.get('x23'), material.get('x13'), material.get('x12'),
            ]
    
    return strength
