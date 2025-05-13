#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains miscellaneous functions that can be used outside of :mod:`inpRW`."""

# cspell:includeRegExp comments

import collections
from itertools import groupby
import math
from functools import reduce
from decimal import Decimal
from numpy import array as nparray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def cfc(obj):
    """cfc(obj)

        Short for Check For Comment. 
        Checks if *obj* is an Abaqus comment (i.e. begins with '**'). This function will 
        remove spaces and tabs before performing the check.

        Args:
            obj (str): The string to check.

        Returns:
            bool: True if ``obj.strip(' \t')[:2] == '**'``, else False.

        For example, as long as '**' is at the start of the string, cfc will return True:

            >>> from misc_functions import cfc
            >>> cfc('***Node')
            True

        cfc also returns True if there are leading spaces and/or tabs:

            >>> cfc('  ***Node')
            True
            >>> cfc('  \t***Node')
            True
   
        And of course, it returns False if the item does not lead with '**':

            >>> cfc('*Node')
            False
    """

    tmp = obj.strip(' \t')[:2]
    if tmp == '**':
        return True
    else:
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def chunks(obj, n):
    """chunks(obj, n)
    
        Splits *obj* into slices of *n* size.

        This could be used to split up a large :term:`iterable` for parallel processing.
        
        Args:
            obj: The object to be sliced into smaller pieces. This must be an :term:`iterable`.
                n (int): The number of objects per slice.
            
        Yields:
            :term:`generator iterator`: The type of the output will be the type of *obj*.
            
        Note that in the following example, converting output and obj to lists is for illustrative and testing 
        purposes only.
        
        Example usage:
        
            >>> from misc_functions import chunks
            >>> obj = list(range(16))
            >>> obj
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
            >>> list(chunks(obj, n=4))
            [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]
            
        """

    for i in range(0, len(obj), n):
        yield obj[i : i + n]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def flatten(iterable):
    """flatten(iterable)
    
        Creates a completely flattened :term:`generator` from a nested sequence. 
        
        This function does not care the size of each item in the iterable, that they are consistently sized, or how deep
        the nesting goes, it will create a one-level deep :term:`generator` from whatever is passed in.

        Please note that passing a mapping type to this function will yield only the keys, and that unordered types
        like sets will be flattened, but the items of the set will not be in any particular order with respect to
        each other.
    
        Args:
            iterable: Any :term:`iterable` object. :class:`Strings <str>` will not be processed, as they are naturally flattened.
            
        Yields:
            :term:`generator iterator`: 
            
        Note that in the following example, converting the output to a list is for illustrative and testing purposes only.
        Example usage:
            
            >>> from misc_functions import flatten
            >>> l = [1, 'abc', [2, 3, [4, 5, (6, 7, 8)]]]
            >>> list(flatten(l))
            [1, 'abc', 2, 3, 4, 5, 6, 7, 8]
            
            """
    
    for i in iterable:
        if isinstance(i, collections._collections_abc.Iterable) and not isinstance(i, str):
            for sub in flatten(i):
                yield sub
        else:
            yield i

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def makeDataList(iterable, numPerLine=16):
    """makeDataList(iterable, numPerLine=16)
    
        Returns a list of lists, with *numPerLine* items per line and then the remainder. 
        
        Example usage:
        
            >>> from misc_functions import makeDataList
            >>> data = list(range(12))
            >>> data
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            >>> makeDataList(data, numPerLine=12)
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]

        If the number of items in *data* is not evenly divisible by *numPerLine*, this will return as many lists of
        len *numPerLine* as possible, and then the remaining items in a shorter list. Example:

            >>> makeDataList(data, numPerLine=8)
            [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11]]

        Args:
            iterable (list): A flat iterable.
            numPerLine (int): The number of items desired per dataline. Defaults to 16.
            
        Returns:
            list: A list of lists with numPerLine items on all indices except the last, which will have the remainder.
        """
    
    whole, rem = divmod(len(iterable), numPerLine)
    tmp = []
    for i in range(whole):
        tmp.append(iterable[numPerLine*i:numPerLine*i+numPerLine])
    if rem:
        tmp.append(iterable[whole*numPerLine:])
    return tmp

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def nestedSort(iterable, reverse=False, _level=None):
    """nestedSort(iterable, reverse=False, _level=None)

        Sorts a sequence of sequences on multiple levels. 
        
        It starts with the least important field (furthest to the right) and ends with the most important. This 
        function uses :func:`sorted` with a custom key function to perform the sorting operation. This will 
        return a new iterable.

        This was written to sort :term:`positionls <positionl>` representing the keyword, suboptions, and data position indices. 
        For example, the item at the path ``'self.keywords[1].suboptions[0].suboptions[0].data[0][1]'`` would have 
        the :term:`positionl` ``[1, [0,0], [0,1]]``. 

        Thus, when sorting keyword :term:`positionls <positionl>`, *reverse* = False will sort the items in top-down order, 
        while *reverse* = True will sort them in bottom-up order.
        
        Args:
            iterable: Any iterable type item with a nested data structure that needs to be sorted.
            reverse (bool): If True, iterable will be sorted in reverse (bottom-up) order. Defaults to False.
            _level (int): Allows the user to specify the level to which to sort. Overrides the default value for level,
                which is ``len(iterable[0])``.
        Returns:
            list: A new list with all the items of iterable in the specified order.
            
        Examples:
            ::
            
                >>> from misc_functions import nestedSort
                >>> iterable = [[0,[1,0],0], [0,[0,0],0], [1,[1],0], [0,[1,0],1], [1,[0,0],0]]
                >>> nestedSort(iterable)
                [[0, [0, 0], 0], [0, [1, 0], 0], [0, [1, 0], 1], [1, [0, 0], 0], [1, [1], 0]]

            And then sorting the original list in reverse order:

                >>> nestedSort(iterable, reverse=True)
                [[1, [1], 0], [1, [0, 0], 0], [0, [1, 0], 1], [0, [1, 0], 0], [0, [0, 0], 0]]

            Thus, all the right-most items will be sorted first. That order will be maintained while the level one to
            the left is sorted, until the finish.
    """

    if _level == None:
        level = len(iterable[0]) - 1
    else:
        level = _level
    levelIter = range(level,-1,-1)
    #print(levelIter)
    for l in levelIter:
        iterable = sorted(iterable, key=lambda nested: nested[l], reverse=reverse)
    return iterable

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def normalize(v):    
    """normalize(v)

        This function will return a unit vector in the same direction. v should be a vector.
        
        Example::

            >>> from misc_functions import normalize
            >>> normalize([10, 0, 0])
            (1.0, 0.0, 0.0)

        This also works with :class:`~decimal.Decimal` numbers: 
            
            >>> from decimal import Decimal as D
            >>> normalize([D('15'), D('2'), D('1')])
            array([Decimal('0.9890707100936805070769772310'),
                   Decimal('0.1318760946791574009435969641'),
                   Decimal('0.06593804733957870047179848207')], dtype=object)
        """
    
    try:
        tmp = math.sqrt(reduce(lambda x,y: x + y**2, [0.0] + list(v)))
        out = tuple([i/tmp for i in v])
    except TypeError:
        tmp = Decimal.sqrt(reduce(lambda x,y: x + y**2, [Decimal(0.0)] + list(v)))
        out = nparray([i/tmp for i in v])
    return out

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ranges(iterable):
    """ranges(iterable)
    
        Yields a list of ranges of *iterable*.
        
        This function will determine the ranges needed to represent a sequence of integers. 
        
        For example::
        
            >>> from misc_functions import ranges
            >>> iterable = [1,2,4,5,6,10]
            >>> list(ranges(iterable))
            [(1, 2), (4, 6), (10, 10)]
        
        *iterable* will first be sorted before the functions searches for groups of integers. A gap between integers
        greater than 1 will start a new group. Duplicate integers are ignored.

        This function is used by :func:`~inpRW._inpMod.Mod._consolidateDofXtoYDatalines`

        Args:
            iterable: A :term:`sequence <iterable>` of integers.
            
        Yields:
            :term:`generator iterator`: """
    
    iterable = sorted(set(iterable))
    for key, group in groupby(enumerate(iterable), lambda t: t[1] - t[0]):
        group = list(group)
        yield group[0][1], group[-1][1]
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def rsl(obj):
    """rsl(obj)
    
        Lowers the case of *obj*, and then removes all spaces. Name is short for "remove spaces and lowercase".

        :func:`rsl` is used throughout :mod:`inpRW` to provide case- and space-insensitivity on string comparisons.
        
        Args:
            obj (str): If obj is not a :class:`str`, this function will return None.
            
        Returns:
            str: *obj*.lower().replace(' ', '').
            None: If *obj* is not a string, this function will return None.
            
        Example usage:
        
            >>> from misc_functions import rsl
            >>> rsl(' This is a test STRING')
            'thisisateststring'
            
        
            """

    try:
        return obj.lower().replace(' ', '')
    except AttributeError:
        return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def rstl(obj):
    """rstl(obj)
    
        Lowers the case of *obj*, and then removes all spaces and tabs. Name is short for "remove spaces, tabs and lowercase".

        :func:`rstl` can be used throughout :mod:`inpRW` to provide case- and white-space-insensitivity on string comparisons.
        It is slower than :func:`rsl`, so it will only be used if there are tabs in the input file.
        
        Args:
            obj (str): If obj is not a :class:`str`, this function will return None.
            
        Returns:
            str: *obj*.lower().replace(' ', '').replace('\t', '').
            None: If *obj* is not a string, this function will return None.
            
        Example usage:
        
            >>> from misc_functions import rsl
            >>> rstl(' \tThis is a test STRING')
            'thisisateststring'
            
            """

    try:
        return obj.lower().replace(' ', '').replace('\t', '')
    except AttributeError:
        return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ssl(obj, ss=True):
    """ssl(obj, ss=True)
    
        Calls :func:`stripSpace` on *obj*.lower(). Name is short for "strip spaces and lowercase".
        
        Args:
            obj (str):
            ss (bool):
            
        Returns:
            str: *obj*.lower() without leading and trailing spaces if *ss* == True, else *obj*.lower().
            
        Example usage: 
        
            >>> from misc_functions import ssl
            >>> ssl('   Test string')
            'test string'

        And if *ss* = False, *obj* is made lowercase and then returned:
            
            >>> ssl('   Test string', ss=False)
            '   test string'
            
            """        

    return stripSpace(obj.lower(), ss)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def stripSpace(obj, ss=True):
    """stripSpace(obj, ss=True)
    
        Strips spaces from the beginning and end of *obj* if *ss* == True.

        Args:
            obj (str):
            ss (bool):
            
        Returns:
            str: *obt* without leading and trailing spaces if *ss* == True, else *obj*.
            
        Example usage:
            
            >>> from misc_functions import stripSpace
            >>> stripSpace('   Test string')
            'Test string'

        The function does returns *obj* unmodified if *ss* = False:

            >>> stripSpace('   Test string', ss=False)
            '   Test string'

        """    
    
    if ss:
        tmp = obj.strip(' ').lstrip(' ')
        return tmp
    else:
        return obj


__test__ = {'cfc': cfc,
            'chunks': chunks,
            'flatten': flatten,
            'makeDataList': makeDataList,
            'nestedSort': nestedSort,
            'normalize': normalize,
            'ranges': ranges,
            'rsl': rsl,
            'ssl': ssl,
            'stripSpace': stripSpace}