#Copyright © 2023 Dassault Systemès Simulia Corp.

from decimal import Decimal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def repr2(obj, rmtrailing0=False):
    """repr2(obj, rmtrailing0=False)
    
    Produces the string representation of *obj* using str(*obj*). 
    
    This function calls str(*obj*) to produce a string representation of *obj*. Thus, *obj* can be any type, so
    long as __str__ is defined for *obj*. :class:`~decimal.Decimal` objects add a trailing '.' if not already in 
    the string representation. Can optionally remove trailing 0 if *rmtrailing0* is True (i.e. 1.0 -> 1.).
    
    Args:
        obj: Can be any type. :func:`repr2` will use obj's built-in __str__ method to produce the string.

        rmtrailing0 (bool): Remove trailing 0s from decimal numbers if True. Defaults to False.
        
    Returns:
        str: The string representation for obj.
        
    Example usage:

        >>> from repr2 import repr2
        >>> repr2(1.0)
        '1.0'
        >>> from decimal import Decimal
        >>> repr2(Decimal('1'))
        '1.'
        >>> repr2(Decimal('1.0'))
        '1.0'
        >>> repr2(1.0, rmtrailing0=True)
        '1.'
        
        """
    
    
    if type(obj)==Decimal: #This is designed not to operate on inpDecimal objects
        if '.' not in str(obj):
            out = f'{obj}.'
        else:
            out = f'{obj}'
    else:
        out = str(obj)
    if rmtrailing0:
        try:
            a = out.split('.')[1]
            if a=='0'*len(a):
                out = out.split('.')[0]+'.'
        except IndexError:
            pass            
    return out

__test__ = {'repr2': repr2}