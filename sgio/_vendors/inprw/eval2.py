#Copyright © 2023 Dassault Systemès Simulia Corp.

# cspell:includeRegExp comments

from decimal import Decimal, InvalidOperation
from .config_re import re10, re13
from .inpInt import inpInt
from .inpString import inpString
from .inpDecimal import inpDecimal 
from .misc_functions import stripSpace
from .inpRWErrors import DecimalInfError

### SPLIT THIS FUNCTION INTO SUBFUNCTIONS, PLACE THE LOGIC RELATED TO PS, SS, AND USEDECIMAL IN THE CALLING FUNCTIONS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def eval2(obj, t=None, ps=False, useDecimal=True):
    """eval2(obj, t=None, ps=False, useDecimal=True)

        This function will convert a string into the appropriate data type.

        This function is similar in concept to :func:`eval`, although it does not inherit from it. It produces
        different types than :func:`eval` to suit the needs of :mod:`inpRW`. 
        
        If *ps* is True, :func:`eval2` will return an :class:`inpString`, :class:`inpInt`, or :class:`inpDecimal` 
        as appropriate. If *ps* is False, :func:`eval2` will return :class:`str`, :class:`int`, and :class:`float` 
        (if *useDecimal* = False) or :class:`~decimal.Decimal` (if *useDecimal* = True).

        If *t* is not set, :func:`eval2` will first try to convert *obj* to an integer type, and then a
        decimal type, and then finally a string type. If the underlying type of obj is known ahead of time, 
        *t* can be set to this type to for better performance. However, if *t* is specified incorrectly, *obj* 
        will be treated as a string. You should specify *t* when you are confident of the underlying type, as the 
        function will run much faster.

        Here are some example scenarios, first using *ps* = True:

            >>> from eval2 import eval2
            >>> eval2(' "Nodeset (1)"', t=str, ps=True)
            inpString(' "Nodeset (1)"', False)
            >>> eval2(' 100 ', t=int, ps=True)
            inpInt(' 100 ')
            >>> eval2(' 1.234E1 ', t=float, ps=True)
            inpDecimal(' 1.234E1 ')

        If we set *ps* and *useDecimal* to False, we get the built-in types:

            >>> eval2(' "Nodeset (1)"', t=str, useDecimal=False)
            ' "Nodeset (1)"'
            >>> eval2(' 100 ', t=int, useDecimal=False)
            100
            >>> eval2(' 1.234E1 ', t=float, useDecimal=False)
            12.34

        *useDecimal* = True only applies to floating point numbers, which will instead be evaluated to 
        :class:`~decimal.Decimal`:

            >>> eval2(' 1.234E1 ', t=float)
            Decimal('12.34')

        Not specifying *t* is slower, but :func:`eval2` will find the best type:

            >>> eval2(' 1.23', ps=True)
            inpDecimal(' 1.23')

        If we specify *t* incorrectly, we will get a string type as the output:

            >>> eval2(' 1.23', t=int, ps=True)
            inpString(' 1.23', False)
    
        Args:
            obj (str): A string representation of the object to evaluate.
            t (str or float or int): The expected type of *obj*. Pass in the type, not an object of the type.
            ps (bool): Preserve Spacing. If True, :class:`~inpInt`, :class:`~inpDecimal`, and :class:`~inpString` objects
                will be created. Defaults to False.
            useDecimal (bool): If True, :class:`~float`-like objects will instead be evaluated to :class:`~decimal.Decimal`
                objects. Defaults to True.
         
        Returns:
           :class:`str`, :class:`inpString`, :class:`int`, :class:`inpInt`, :class:`~decimal.Decimal`, or :class:`inpDecimal`"""
    
    if ps:
        try: # This block will always be run. If an error is produced, an inpString will be returned
            if t == str:
                return inpString(obj)
            elif t == float:
                return inpDecimal(obj)
            elif t == int:
                return inpInt(obj)
        except:
            return inpString(obj)
        else: # If t was not specified, we end up here
            try:
                return inpInt(obj)
            except ValueError:
                try:
                   return inpDecimal(obj)
                except (InvalidOperation, DecimalInfError):
                    return inpString(obj)
            except:
                return inpString(obj)
    else:
        try: # This block will always be run. If an error is produced, an inpString will be returned
            if t == str:
                return obj
            elif t == float or isinstance(obj, Decimal) or isinstance(obj, float):
                if useDecimal:
                    return Decimal(obj)
                else:
                    return float(obj)
            elif t == int or isinstance(obj, int):
                return int(obj)
        except:
            return obj
        else: # If t was not specified, we end up here
            try:
                return int(obj)
            except ValueError:
                try:
                    if useDecimal:
                        return Decimal(obj)
                    else:
                        return float(obj)
                except (InvalidOperation, ValueError):
                    return obj
            except:
                return obj
