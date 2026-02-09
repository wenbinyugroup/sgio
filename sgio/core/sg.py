from __future__ import annotations

import copy
import logging
from typing import Optional

import numpy as np
from meshio import Mesh

from sgio.core.mesh import SGMesh


logger = logging.getLogger(__name__)


class SGMacroModel:
    """Configuration of SG analysis, independent on the geometry.
    
    Parameters
    ----------
    kwd : str, optional
        Keyword defining the analysis type (default='SD1').
        Prefix determines structural model dimension:
        'SD' for 3D solid, 'PL' for 2D plane, 'BM' for 1D beam.
        
    Attributes
    ----------
    _kwd : str
        Keyword for analysis type.
    _physics : int
        Physics included in analysis (default=0).
    _geo_correct : bool
        Flag for geometrically corrected model (default=False).
    _do_damping : int
        Flag for damping computation (default=0).
    _is_temp_nonuniform : int
        Flag for non-uniform temperature (default=0).
    """
    
    def __init__(self, kwd: str = 'SD1') -> None:
        """Initialize SGMacroModel with analysis configuration.
        
        Parameters
        ----------
        kwd : str, optional
            Keyword defining the analysis type (default='SD1').
        """
        self._kwd = kwd
        self._physics = 0
        self._geo_correct = False
        self._do_damping = 0
        self._is_temp_nonuniform = 0

    @property
    def smdim(self) -> int:
        """Dimension of the material/structural model.
        
        Returns
        -------
        int
            Structural model dimension:
            3 for solid (SD), 2 for plane (PL), 1 for beam (BM).
            
        Raises
        ------
        ValueError
            If keyword prefix doesn't match expected patterns.
        """
        prefix = self._kwd[:2]
        if prefix == 'SD':
            return 3
        elif prefix == 'PL':
            return 2
        elif prefix == 'BM':
            return 1
        else:
            raise ValueError(f'Unknown keyword prefix: {prefix}. Expected SD, PL, or BM.')




class StructureGene:
    """A finite element level structure gene model in the theory of MSG.

    Attributes
    ----------
    name : str
        Name of the SG.
    sgdim : int or None
        Dimension of the SG.
    smdim : int or None
        Dimension of the material/structural model.
    spdim : int or None
        Dimension of the space containing SG.
    analysis : int
        Analysis configurations.
        * 0 - homogenization (default)
        * 1 - dehomogenization/localization/recover
        * 2 - failure (SwiftComp only)
    fn_gmsh_msh : str
        File name of the Gmsh mesh file.
    physics : int
        Physics included in the analysis.
        * 0 - elastic (default)
        * 1 - thermoelastic
        * 2 - conduction
        * 3 - piezoelectric/piezomagnetic
        * 4 - thermopiezoelectric/thermopiezomagnetic
        * 5 - piezoelectromagnetic
        * 6 - thermopiezoelectromagnetic
    model : int
        Macroscopic structural model.
        * 0 - classical (default)
        * 1 - refined (e.g., generalized Timoshenko)
        * 2 - Vlasov model (beam only)
        * 3 - trapeze effect (beam only)
    geo_correct : bool
        Flag of geometrically corrected shell model.
    do_damping : int
        Flag of damping computation.
    is_temp_nonuniform : int
        Flag of uniform temperature.
    force_flag : int
        Force flag.
    steer_flag : int
        Steer flag.
    initial_twist : float
        Initial twist (beam only).
    initial_curvature : list of float
        Initial curvature.
    oblique : list of float
        Oblique (beam only).
    lame_params : list of float
        Lame parameters for geometrically corrected shell model.
    materials : dict[str, MaterialModel]
        Dictionary of materials indexed by material name.
    mocombos : dict[int, tuple[str, float]]
        Dictionary of material-orientation combinations.
        Maps property_id to (material_name, orientation_angle).
    mesh : SGMesh or Mesh or None
        Mesh of the SG.
    ndim_degen_elem : int
        Number of degenerate elements.
    num_slavenodes : int
        Number of slave nodes.
    omega : float
        Omega (see SwiftComp manual).
    itf_pairs : list
        Interface pairs.
    itf_nodes : list
        Interface nodes.
    node_elements : list
        Node elements.
    """

    def __init__(
        self, 
        name: str = '', 
        sgdim: Optional[int] = None, 
        smdim: Optional[int] = None, 
        spdim: Optional[int] = None
    ) -> None:
        """Initialize the SG model.
        
        Parameters
        ----------
        name : str, optional
            Name of the SG (default='').
        sgdim : int, optional
            Dimension of the SG (default=None).
        smdim : int, optional
            Dimension of the material/structural model (default=None).
        spdim : int, optional
            Dimension of the space containing SG (default=None).
            If not provided, defaults to sgdim.
        """
        self.name = name
        self.sgdim = sgdim
        self.smdim = smdim
        self.spdim = sgdim
        if spdim is not None:
            self.spdim = spdim

        self.analysis = 0
        self.fn_gmsh_msh = self.name + '.msh'
        self.physics = 0
        self.model = 0
        self.geo_correct = False
        self.do_damping = 0
        self.is_temp_nonuniform = 0
        self.force_flag = 0
        self.steer_flag = 0
        self.initial_twist = 0.0
        self.initial_curvature = [0.0, 0.0]
        self.oblique = [1.0, 0.0]
        self.lame_params = [1.0, 1.0]

        # Material storage - indexed by material name for O(1) lookup
        self.materials: dict = {}  # {material_name: MaterialModel}
        self.material_name_id_pairs: list = []  # [[name1, id1], [name2, id2], ...]
        self.mocombos: dict = {}  # {property_id: (material_name, angle)}

        # Mesh
        self.mesh: SGMesh | Mesh | None = None
        self.ndim_degen_elem = 0
        self.num_slavenodes = 0
        self.omega = 1

        self.itf_pairs: list = []
        self.itf_nodes: list = []
        self.node_elements: list = []



    @property
    def nnodes(self) -> int:
        """Number of nodes in the mesh.
        
        Returns
        -------
        int
            Number of nodes.
            
        Raises
        ------
        ValueError
            If mesh is not defined.
        """
        if self.mesh is None:
            raise ValueError('Mesh is not defined.')
        return len(self.mesh.points)

    @property
    def nelems(self) -> int:
        """Number of elements in the mesh.
        
        Returns
        -------
        int
            Number of elements.
            
        Raises
        ------
        ValueError
            If mesh is not defined.
        """
        if self.mesh is None:
            raise ValueError('Mesh is not defined.')
        return sum([len(cell.data) for cell in self.mesh.cells])

    @property
    def nma_combs(self) -> int:
        """Number of material-orientation combinations.
        
        Returns
        -------
        int
            Number of material-orientation combinations.
        """
        return len(self.mocombos)

    @property
    def nmates(self) -> int:
        """Number of materials.
        
        Returns
        -------
        int
            Number of materials.
        """
        return len(self.materials)

    @property
    def use_elem_local_orient(self) -> int:
        """Flag of using element local orientation.
        
        Returns
        -------
        int
            1 if using element local orientation, 0 otherwise.
            
        Raises
        ------
        ValueError
            If mesh is not defined.
        """
        if self.mesh is None:
            raise ValueError('Mesh is not defined.')
        if 'property_ref_csys' in self.mesh.cell_data.keys():
            return 1
        else:
            return 0


    def __repr__(self) -> str:
        """String representation of the StructureGene.
        
        Returns
        -------
        str
            Formatted summary of the SG.
        """
        lines = [
            '',
            '='*40,
            'SUMMARY OF THE SG',
            '',
            '-'*30,
            'ANALYSIS',
            f'Structure gene: {self.sgdim}D -> model: {self.smdim}D',
            f'Physics: {self.physics}',
            '',
        ]

        if self.smdim != 3:
            lines.append(f'Model: {self.model}')
            lines.append('')

        if self.mesh is not None:
            lines += [
                '-'*30,
                'MESH',
                f'Number of nodes: {self.nnodes}',
                f'Number of elements: {self.nelems}',
                str(self.mesh),
                '',
            ]

        lines += [
            '-'*30,
            'MATERIALS',
            f'Number of materials: {self.nmates}',
            '',
        ]

        lines += ['END OF SUMMARY', '='*40, '']

        return '\n'.join(lines)


    def copy(self) -> 'StructureGene':
        """Create a deep copy of the StructureGene.
        
        Returns
        -------
        StructureGene
            Deep copy of the current instance.
        """
        return copy.deepcopy(self)

    def translate(self, v: np.ndarray | list) -> None:
        """Translate the mesh.
        
        Parameters
        ----------
        v : array_like
            Translation vector.

        Raises
        ------
        ValueError
            If mesh is not defined.
        """
        if self.mesh is None:
            raise ValueError('Mesh is not defined.')
        v = np.asarray(v)
        self.mesh.points += v


    def get_material(self, name: str):
        """Get material by name.

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        MaterialModel or None
            Material object if found, None otherwise.
        """
        return self.materials.get(name)

    def add_material(self, material, name: Optional[str] = None) -> str:
        """Add a material to the structure gene.

        Parameters
        ----------
        material : MaterialModel
            Material object to add.
        name : str, optional
            Material name. If not provided, uses material.name attribute.

        Returns
        -------
        str
            Material name used as key.

        Raises
        ------
        ValueError
            If material name is empty or None.
        """
        mat_name = name if name is not None else material.name
        if not mat_name:
            raise ValueError('Material must have a non-empty name.')
        self.materials[mat_name] = material
        return mat_name

    def find_combo_by_material_orientation(self, name: str, angle: float) -> Optional[int]:
        """Find material-orientation combination by material name and angle.

        Parameters
        ----------
        name : str
            Material name.
        angle : float
            Orientation angle.

        Returns
        -------
        int or None
            Property/combo id if found, None otherwise.
        """
        for combo_id, (mat_name, mat_angle) in self.mocombos.items():
            if (mat_name == name) and (mat_angle == angle):
                return combo_id
        return None

    def get_material_name_by_id(self, mat_id: int) -> Optional[str]:
        """Get material name by numeric ID from name-ID pairs.

        Parameters
        ----------
        mat_id : int
            Material numeric ID (1-based).

        Returns
        -------
        str or None
            Material name if found, None otherwise.
        """
        for name, mid in self.material_name_id_pairs:
            if mid == mat_id:
                return name
        return None

    def get_material_id_by_name(self, name: str) -> Optional[int]:
        """Get material numeric ID by name from name-ID pairs.

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        int or None
            Material numeric ID (1-based) if found, None otherwise.
        """
        for mat_name, mat_id in self.material_name_id_pairs:
            if mat_name == name:
                return mat_id
        return None

    def add_material_name_id_pair(self, name: str, mat_id: int) -> None:
        """Add a material name-ID pair.

        Parameters
        ----------
        name : str
            Material name.
        mat_id : int
            Material numeric ID (1-based).

        Raises
        ------
        ValueError
            If pair already exists with different ID or name already exists.
        """
        # Check if name already exists with different ID
        existing_id = self.get_material_id_by_name(name)
        if existing_id is not None and existing_id != mat_id:
            raise ValueError(f'Material name "{name}" already exists with ID {existing_id}')
        
        # Check if ID already exists with different name
        existing_name = self.get_material_name_by_id(mat_id)
        if existing_name is not None and existing_name != name:
            raise ValueError(f'Material ID {mat_id} already exists with name "{existing_name}"')
        
        # Add pair if not already present
        if existing_id is None:
            self.material_name_id_pairs.append([name, mat_id])

    def sync_material_name_id_pairs(self) -> None:
        """Synchronize material_name_id_pairs with current materials dictionary.

        Creates consecutive 1-based IDs for all materials in self.materials
        that don't already have an ID in material_name_id_pairs.
        Removes pairs for materials that no longer exist.
        """
        # Remove pairs for materials that no longer exist
        self.material_name_id_pairs = [
            [name, mat_id] for name, mat_id in self.material_name_id_pairs
            if name in self.materials
        ]
        
        # Get next available ID
        used_ids = {mat_id for _, mat_id in self.material_name_id_pairs}
        next_id = max(used_ids, default=0) + 1
        
        # Add pairs for new materials
        for mat_name in self.materials:
            if self.get_material_id_by_name(mat_name) is None:
                # Find next available consecutive ID
                while next_id in used_ids:
                    next_id += 1
                self.material_name_id_pairs.append([mat_name, next_id])
                used_ids.add(next_id)
                next_id += 1

    def get_export_material_ids(self) -> dict[str, int]:
        """Generate material name to numeric ID mapping for export.

        Uses material_name_id_pairs if available, otherwise generates
        consecutive IDs based on materials dictionary order.

        Returns
        -------
        dict[str, int]
            Mapping from material name to export ID (1-based).

        Examples
        --------
        >>> sg = StructureGene()
        >>> sg.materials['Steel'] = steel_mat
        >>> sg.material_name_id_pairs = [['Steel', 1]]
        >>> sg.get_export_material_ids()
        {'Steel': 1}
        """
        # Use material_name_id_pairs if available and complete
        if self.material_name_id_pairs:
            mat_id_map = {name: mat_id for name, mat_id in self.material_name_id_pairs}
            # Check if all materials have IDs
            if all(name in mat_id_map for name in self.materials):
                return mat_id_map
        
        # Fallback: generate consecutive IDs
        return {name: idx + 1 for idx, name in enumerate(self.materials.keys())}

    def find_material_by_name(self, name: str) -> Optional[str]:
        """Find material by name (returns material name if exists).

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        str or None
            Material name if found, None otherwise.

        Notes
        -----
        This method is kept for API compatibility. For direct access,
        use `get_material(name)` or check `name in sg.materials`.
        """
        return name if name in self.materials else None

    # Deprecated methods for backward compatibility
    def findMaterialByName(self, name: str) -> int:
        """Find material by name (deprecated - returns pseudo-ID).
        
        .. deprecated::
            Material storage now uses name-based indexing.
            Use `get_material(name)` to retrieve material directly,
            or `name in sg.materials` to check existence.

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        int
            1 if material exists, 0 if not found.
            Note: Return value is no longer a meaningful ID.
        """
        logger.warning(
            'findMaterialByName is deprecated. '
            'Use get_material(name) or check "name in sg.materials" instead.'
        )
        return 1 if name in self.materials else 0

    def findComboByMaterialOrientation(self, name: str, angle: float) -> int:
        """Find material-orientation combination.
        
        .. deprecated::
            Use :meth:`find_combo_by_material_orientation` instead.

        Parameters
        ----------
        name : str
            Material name.
        angle : float
            Orientation angle.

        Returns
        -------
        int
            Combination id. 0 if not found.
        """
        logger.warning(
            'findComboByMaterialOrientation is deprecated, '
            'use find_combo_by_material_orientation instead'
        )
        result = self.find_combo_by_material_orientation(name, angle)
        return result if result is not None else 0


