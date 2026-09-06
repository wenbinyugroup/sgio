from __future__ import annotations

import copy
import logging
from collections.abc import Mapping, MutableMapping
from typing import Any, Optional

import numpy as np

from .fe_model import FEModel
from .mesh import SGMesh
from .section import Section
from .sg_analysis_config import SGAnalysisConfig


logger = logging.getLogger(__name__)


class _MocombosView(MutableMapping[int, tuple[str, float]]):
    """Mutable compatibility view over ``StructureGene.sections``."""

    def __init__(self, sg: StructureGene) -> None:
        self._sg = sg

    def __getitem__(self, key: int) -> tuple[str, float]:
        section = self._sg.get_section_by_property_id(key)
        if section is None:
            raise KeyError(key)
        return (section.material, section.orientation)

    def __setitem__(self, key: int, value: tuple[str, float]) -> None:
        material, orientation = value
        section = self._sg.get_section_by_property_id(key)
        if section is None:
            self._sg.add_section(
                name=f"section_{int(key)}",
                material=material,
                orientation=float(orientation),
                property_id=int(key),
            )
            return
        section.material = material
        section.orientation = float(orientation)

    def __delitem__(self, key: int) -> None:
        section = self._sg.get_section_by_property_id(key)
        if section is None:
            raise KeyError(key)
        del self._sg.sections[section.name]

    def __iter__(self):
        return iter(self._sg._sections_by_property_id())

    def __len__(self) -> int:
        return len(self._sg.sections)


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
    analysis_config : SGAnalysisConfig
        Analysis configuration object.
    fn_gmsh_msh : str
        File name of the Gmsh mesh file.
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
    sections : dict[str, Section]
        FE sections indexed by section name.
    mocombos : dict[int, tuple[str, float]]
        Backward-compatible mapping view derived from ``sections``.
        Maps property_id to (material_name, orientation_angle).
    mesh : SGMesh or None
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
        self._fe = FEModel(name=name)
        self.analysis_config = SGAnalysisConfig()
        self.sgdim = sgdim
        self.smdim = smdim
        self.spdim = sgdim if spdim is None else spdim

        self.fn_gmsh_msh = self.name + '.msh'
        self.initial_twist = 0.0
        self.initial_curvature = [0.0, 0.0]
        self.oblique = [1.0, 0.0]
        self.lame_params = [1.0, 1.0]

        self.ndim_degen_elem = 0
        self.num_slavenodes = 0
        self.omega = 1

        self.itf_pairs: list = []
        self.itf_nodes: list = []
        self.node_elements: list = []

    @classmethod
    def from_fe(
        cls,
        fe_model: FEModel,
        sgdim: Optional[int] = None,
        smdim: Optional[int] = None,
        spdim: Optional[int] = None,
    ) -> 'StructureGene':
        """Wrap an existing ``FEModel`` into a ``StructureGene``.

        Symmetric to :meth:`StructuralModel.from_fe`: the ``fe_model`` is
        deep-copied to back the SG's FE core, SG-specific dimensions come from
        the arguments, and ``analysis_config`` keeps its constructor defaults
        (to be set by the caller or adapter afterwards).

        Parameters
        ----------
        fe_model : FEModel
            Source finite element model.
        sgdim : int, optional
            Dimension of the SG.
        smdim : int, optional
            Dimension of the material/structural model.
        spdim : int, optional
            Dimension of the space containing the SG. Defaults to ``sgdim``.

        Returns
        -------
        StructureGene
            New structure gene with a deep-copied backing ``FEModel``.
        """
        sg = cls(name=fe_model.name, sgdim=sgdim, smdim=smdim, spdim=spdim)
        sg._fe = copy.deepcopy(fe_model)
        return sg

    @property
    def fe_model(self) -> FEModel:
        """Finite element core model owned by the structure gene."""
        return self._fe

    @property
    def name(self) -> str:
        """Name of the structure gene."""
        return self._fe.name

    @name.setter
    def name(self, value: str) -> None:
        self._fe.name = value

    @property
    def mesh(self) -> SGMesh | None:
        """Finite element mesh."""
        return self._fe.mesh

    @mesh.setter
    def mesh(self, value: SGMesh | None) -> None:
        self._fe.mesh = value

    @property
    def materials(self) -> dict[str, Any]:
        """Materials indexed by material name."""
        return self._fe.materials

    @materials.setter
    def materials(self, value: dict[str, Any]) -> None:
        self._fe.materials = value

    @property
    def mocombos(self) -> MutableMapping[int, tuple[str, float]]:
        """Legacy material-orientation combinations derived from sections."""
        return _MocombosView(self)

    @mocombos.setter
    def mocombos(self, value: Mapping[int, tuple[str, float]]) -> None:
        self.sections = {
            f"section_{int(property_id)}": Section(
                name=f"section_{int(property_id)}",
                material=material,
                orientation=float(angle),
                property_id=int(property_id),
            )
            for property_id, (material, angle) in sorted(value.items())
        }

    @property
    def orientations(self) -> dict[str, Any]:
        """Placeholder FE orientations."""
        return self._fe.orientations

    @orientations.setter
    def orientations(self, value: dict[str, Any]) -> None:
        self._fe.orientations = value

    @property
    def sections(self) -> dict[str, Section]:
        """FE sections indexed by section name."""
        return self._fe.sections

    @sections.setter
    def sections(self, value: Mapping[str, Section | Mapping[str, Any]]) -> None:
        self._fe.sections = {
            name: self._coerce_section(name, section)
            for name, section in value.items()
        }

    @property
    def extras(self) -> dict[str, Any]:
        """Additional FE-level metadata."""
        return self._fe.extras

    @extras.setter
    def extras(self, value: dict[str, Any]) -> None:
        self._fe.extras = value


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
            f'Physics: {self.analysis_config.physics}',
            '',
        ]

        if self.smdim != 3:
            lines.append(f'Model: {self.analysis_config.model}')
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


    def get_material(self, name: str) -> Any | None:
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

    def add_material(self, material: Any, name: Optional[str] = None) -> str:
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

    def add_section(
        self,
        name: str,
        material: str,
        orientation: float = 0.0,
        property_id: int | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> Section:
        """Add a FE section to the structure gene.

        Parameters
        ----------
        name : str
            Section name.
        material : str
            Referenced material name.
        orientation : float, optional
            In-plane orientation angle in degrees.
        property_id : int or None, optional
            Internal element->section binding key (see :class:`Section`). Users
            normally omit it and reference sections by name; when omitted the
            next available id is assigned automatically. It is not part of the
            public serialization contract.
        extras : mapping, optional
            Extra adapter-specific metadata.

        Returns
        -------
        Section
            Newly created section object.
        """
        if not name:
            raise ValueError("Section must have a non-empty name.")
        if property_id is None:
            property_id = self._next_property_id()
        section = Section(
            name=name,
            material=material,
            orientation=float(orientation),
            property_id=int(property_id),
            extras=dict(extras or {}),
        )
        self.sections[name] = section
        return self.sections[name]

    def get_section_by_property_id(self, property_id: int) -> Section | None:
        """Get a section by property/layer identifier."""
        return self._sections_by_property_id().get(int(property_id))

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

    def _coerce_section(
        self,
        name: str,
        value: Section | Mapping[str, Any],
    ) -> Section:
        """Convert input section payload to a :class:`Section` instance."""
        if isinstance(value, Section):
            if value.name != name:
                value.name = name
            return value
        extras = value.get("extras", {})
        return Section(
            name=name,
            material=value["material"],
            orientation=float(value.get("orientation", 0.0)),
            property_id=value.get("property_id"),
            extras=dict(extras),
        )

    def _sections_by_property_id(self) -> dict[int, Section]:
        """Return sections indexed by property ID, assigning missing IDs."""
        sections_by_id: dict[int, Section] = {}
        next_id = 1
        for section in self.sections.values():
            if section.property_id is None:
                while next_id in sections_by_id:
                    next_id += 1
                section.property_id = next_id
            property_id = int(section.property_id)
            if property_id in sections_by_id and sections_by_id[property_id] is not section:
                raise ValueError(f"Duplicate section property_id detected: {property_id}")
            sections_by_id[property_id] = section
            next_id = max(next_id, property_id + 1)
        return dict(sorted(sections_by_id.items()))

    def _next_property_id(self) -> int:
        """Get the next available section property ID."""
        sections_by_id = self._sections_by_property_id()
        return max(sections_by_id, default=0) + 1


