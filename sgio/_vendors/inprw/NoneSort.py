#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains a :data:`None`-like class which will always sort to the minimal value."""

from functools import total_ordering

@total_ordering
class NoneSort(object):
    """A simple class that allows a :data:`None`-like object to be less than every other value.

        A :class:`NoneSort` instance is not :data:`None`, because :data:`None` cannot be subclassed.
    
        Example usage:

            >>> from NoneSort import NoneSort
            >>> ns = NoneSort()
            >>> ns < -599899
            True
            >>> ns > -599899
            False
            >>> ns == None
            True
            >>> ns is None
            False
            >>> bool(ns)
            False

            """
    
    def __bool__(self):
        """__bool__()
        
            Always returns False."""
        return False
    
    def __le__(self, other):
        """__le__()
        
            Always returns True."""
        return True

    def __eq__(self, other):
        """__eq__(other)
           
           Always returns (None is other)"""

        return (None is other)

    def __repr__(self):
        """__repr__()
        
            Returns str(None)"""

        return str(None)

__test__ = {'NoneSort': NoneSort}