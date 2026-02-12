"""Format registry initialization module.

This module automatically registers all available format adapters
with the global format registry when imported.

Usage
-----
Import this module to ensure all format adapters are registered:

>>> from sgio.iofunc import registry_init
>>> # or
>>> import sgio.iofunc.registry_init

Then use the registry to get format adapters:

>>> from sgio.iofunc.base import get_format_registry
>>> registry = get_format_registry()
>>> reader = registry.get_reader('vabs')
>>> writer = registry.get_writer('swiftcomp')
"""

from __future__ import annotations

from .base import get_format_registry

# Import all format adapters
from .vabs.adapter import VABSReader, VABSWriter
from .swiftcomp.adapter import SwiftCompReader, SwiftCompWriter
from .gmsh.adapter import GmshReader, GmshWriter
from .abaqus.adapter import AbaqusReader, AbaqusWriter


def register_all_formats():
    """Register all available format adapters with the global registry.
    
    This function is called automatically when this module is imported.
    It can also be called manually to re-register all formats.
    """
    registry = get_format_registry()
    
    # Register VABS format
    vabs_reader = VABSReader()
    vabs_writer = VABSWriter()
    registry.register_reader('vabs', vabs_reader)
    registry.register_writer('vabs', vabs_writer)
    
    # Register SwiftComp format
    swiftcomp_reader = SwiftCompReader()
    swiftcomp_writer = SwiftCompWriter()
    registry.register_reader('swiftcomp', swiftcomp_reader)
    registry.register_writer('swiftcomp', swiftcomp_writer)
    
    # Register Gmsh format
    gmsh_reader = GmshReader()
    gmsh_writer = GmshWriter()
    registry.register_reader('gmsh', gmsh_reader)
    registry.register_writer('gmsh', gmsh_writer)
    
    # Register Abaqus format
    abaqus_reader = AbaqusReader()
    abaqus_writer = AbaqusWriter()
    registry.register_reader('abaqus', abaqus_reader)
    registry.register_writer('abaqus', abaqus_writer)


# Automatically register all formats when this module is imported
register_all_formats()


# Convenience exports
__all__ = [
    'register_all_formats',
]
