#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module implements a few classes that together enable a custom case- and space-insensitive dictionary class."""

# cspell:includeRegExp comments

from .misc_functions import rsl
from decimal import Decimal, InvalidOperation
import numpy as np
from .inpDecimal import inpDecimal

#==================================================================================================================  
class csid(dict):
    """This is a custom class that overrides lookup functions of dictionary classes. It makes their keys  
    case-insensitive and space-insensitive.
    
    Since this class inherits from the dictionary type, it behaves almost exactly like a dictionary. The main
    difference is the keys to the dictionary. Any operation with a :class:`csid` instance will automatically
    generate and use a :class:`csiKeyString` for the key if the key is a string type, or a :class:`csiKeyDecimal`
    if the key is a :class:`float` (the hash of a float is not consistent with the hash of a :class:`~decimal.Decimal`). Otherwise, 
    the object itself will be used as the key, as other object types should not support spaces nor capitalization. 
    
    Constructing a :class:`csid` instance uses the same syntax as constructing a dictionary, or you
    can convert an existing dictionary to a :class:`csid` via ``csid(dict)``."""
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, data=None):
        """__init__(data=None)
        
            Creates the dictionary. Uses the same construction methods as :class:`dict`.

            If *data* is specified, each key in *data* will be converted to a :class:`csiKeyDecimal` or :class:`csiKeyString`
            prior to creating the entry in the :class:`csid`.

            Example usage:

                >>> from csid import csid
                >>> d = csid()
                >>> d[' Nodeset-1'] = 'test'
                >>> d[' Nodeset-2'] = 'test2'
                >>> print(d)
                {
                ' Nodeset-1': 'test',
                ' Nodeset-2': 'test2'
                }

            We can also populate the :class:`csid` using existing data, providing it's in a format which can be used
            to create a :class:`dict`:

                >>> l = [['Nodeset-1', 1],['Nodeset-2', 2],['Nodeset-3', 3]]
                >>> csid(l)
                csid(csiKeyString('Nodeset-1'): 1, csiKeyString('Nodeset-2'): 2, csiKeyString('Nodeset-3'): 3)

            If *data* is not formatted properly, a :exc:`TypeError` or :exc:`ValueError` will be raised:

                >>> csid([['Nodeset-1', 'Nodeset-2', 'NodeSet-3'], [1, 2, 3]])
                Traceback (most recent call last):
                    ...
                ValueError: too many values to unpack (expected 2)
                >>> csid([1,2,3])
                Traceback (most recent call last):
                    ...
                TypeError: cannot unpack non-iterable int object

            Please note that if two keys in *data* are identical once they have been made lowercase and had spaces
            removed, the second entry will overwrite the first one. Example:

                >>> csid([['Nodeset-1', 1],['NODESET-1', 2],['Nodeset-3', 3]])
                csid(csiKeyString('Nodeset-1'): 2, csiKeyString('Nodeset-3'): 3)

            Args:
                data (:term:`iterable`): Defaults to None."""

        if isinstance(data, dict):
            for k,v in data.items():
                self.__setitem__(k, v)
        elif data==None:
            super().__init__()
        else:
            for k,v in data:
                self.__setitem__(k, v)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get(self, key, default=None):
        """get(key, default=None)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then retrieves the entry
            in the :class:`csid` instance using :meth:`~dict.get`. 
            
            If *key* is not in the :class:`csid`, *default* will be returned.

            Example usage:

                >>> from csid import csid
                >>> d = csid([[100, 1]])
                >>> d.get(100)
                1

            If *key* is not in the :class:`csid`, *default* is returned:
                
                >>> print(d.get(200))
                None
            
            Args:
            
                key (:class:`str`, :class:`float`, :class:`~decimal.Decimal`): The key to the item to retrieve from the dictionary. *key* will be converted
                    to a :class:`csiKeyString` or :class:`csiKeyDecimal` if needed.
                    
            Returns:
                The value or None. """

        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().get(key, default)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mergeSubItems(self, other):
        """mergeSubItems(other)
        
            Merges the sub-items of *other* into the appropriate item in d (the :class:`csid` instance). 
            
            For k and v in other.items(), if d[k] is not defined, set d[k] to v. If d[k] is a list, perform d[k].extend(v).
            If d[k] is a dictionary, perform d[k].update(v).
            
            This function is meant for cases where :func:`update` won't be sufficient. For example, if d and *other* both
            have a key k, the content of each is a list, and you wish the value associated with k to be a list containing
            the contents of both entries.

            Example usage:

                >>> from csid import csid
                >>> d = csid([[1, [1,2,3]]])
                >>> d2 = csid([[1, [4,5,6]]])
                >>> d.mergeSubItems(d2)
                >>> d
                csid(1: [1, 2, 3, 4, 5, 6])

            If we just try to update the :class:`csid` with the other dictionary, we would instead get this behavior:

                >>> d = csid([[1, [1,2,3]]])
                >>> d2 = csid([[1, [4,5,6]]])
                >>> d.update(d2)
                >>> d
                csid(1: [4, 5, 6])
            
            Args:
                other (dict): Other should be a dictionary structure where the values of each item in other are lists
                    or dictionaries. Example: ``other = {key: {sub-key1: value1, sub-key2: value2}}`` """

        for k, v in other.items():
            item = self.get(k)
            if item == None:
                self[k] = v
            elif isinstance(item, list):
                item.extend(v)
            elif isinstance(item, dict):
                item.update(v)
            else:
                print(f'Unhandled item type when merging sub items: {k}: {type(k)}')
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def pop(self, key):
        """pop(key)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then retrieves the entry
            in the :class:`csid` instance and removes it using :meth:`dict.pop`.
            
            Example:

                >>> from csid import csid
                >>> d = csid([['a', 1], ['b', 2], ['c', 3]])
                >>> d.pop('a')
                1
                >>> d
                csid(csiKeyString('b'): 2, csiKeyString('c'): 3)

            This will raise a :exc:`KeyError` if key is not in the :class:`csid`:

                >>> d.pop('a')
                Traceback (most recent call last):
                    ...
                KeyError: csiKeyString('a')

            Returns:
                The value at *key*. The key, value pair is removed from the :class:`csid`."""

        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().pop(key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setdefault(self, key, default=None):
        """setdefault(key, default=None)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then retrieves the entry
            in the :class:`csid` instance. If *key* is not in the :class:`csid`, insert *key* with a value of *default*
            and return *default*.
            
            If *key* is in the :class:`csid`, this simply retrieves its value:

                >>> from csid import csid
                >>> d = csid([['a', 1]])
                >>> d.setdefault('a')
                1

            If *key* is not in the :class:`csid`, this will insert *key* and set the value to *default*:

                >>> d.setdefault('b', 2)
                2
                >>> d
                csid(csiKeyString('a'): 1, csiKeyString('b'): 2)

            Args:
                key (:class:`str`, :class:`float`, :class:`~decimal.Decimal`): The key for which to retrieve or set a value. *key* will be converted to a
                    :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary.
                default: The value which will be inserted into the :class:`csid` for *key* if *key* is not already
                    in the :class:`csid`. Defaults to None.

            Returns:
            
                The value mapped to *key*, or *default* if *key* was not in the :class:`csid`."""

        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().setdefault(key, default)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def update(self, other):
        """update(other)
            
            If *other* is not a :class:`csid`, converts it to one, and then calls :meth:`~dict.update` using the :class:`csid`
            of *other*.

            Example usage:

                >>> from csid import csid
                >>> d = csid([['a', 1]])
                >>> d.update([['b', 2]])
                >>> d
                csid(csiKeyString('a'): 1, csiKeyString('b'): 2)
            
            This function operates more quickly if *other* is already a :class:`csid`, although the end result will be the same:

                >>> d.update(csid([['c', 3]]))
                >>> d
                csid(csiKeyString('a'): 1, csiKeyString('b'): 2, csiKeyString('c'): 3)
            
            Args:
            
                other (:term:`iterable`): An iterable which is a :class:`dict` type or can be used to construct a :class:`csid`."""
        
        if not isinstance(other, csid):
            other = csid(other)
        return super().update(other)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __contains__(self, key):
        """__contains__(key)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then checks if *key* is
            in the :class:`csid` instance.

            Here's an example where we create a :class:`csid` from a dictionary which uses an :class:`int` as the key, and
            then we test if an :class:`~inpInt.inpInt` with a value of the :class:`int` is a key in the :class:`csid`:

                >>> from csid import csid
                >>> from inpInt import inpInt
                >>> from decimal import Decimal
                >>> d = csid({25: 'int', 'A1': 'str', 1.234: 'float'})
                >>> inpInt('  25') in d
                True
                >>> 'A1' in d
                True
                >>> Decimal('1.234') in d
                True

            If *key* is not in the :class:`csid`, this will of course return False. The following example illustrates this,
            along with the fact that creating a :class:`~decimal.Decimal` directly from a :class:`float` inherits the :class:`float`
            inaccuracy:

                >>> Decimal(1.234) in d
                False
            
            Returns:
                bool: True if key in d else False."""

        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().__contains__(key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __delitem__(self, key):
        """__delitem__(key)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then deletes the entry
            in the :class:`csid` instance.
            
            Example:
            
                >>> from csid import csid
                >>> d = csid([['a', 1], ['b', 2], ['c', 3]])
                >>> del d['C']
                >>> d
                csid(csiKeyString('a'): 1, csiKeyString('b'): 2)

            If *key* is not defined in the :class:`csid`, this will raise a :exc:`KeyError` as expected:

                >>> del d['D']
                Traceback (most recent call last):
                    ...
                KeyError: csiKeyString('D')
                
                """

        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().__delitem__(key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __getitem__(self, key):
        """__getitem__(key)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then retrieves the entry
            in the :class:`csid` instance. Reference: :meth:`__getitem__`.
            
            Example:

                >>> from csid import csid
                >>> d = csid([['a', 1], ['b', 2], ['c', 3]])
                >>> d['C']
                3

            If *key* is not defined in the :class:`csid`, this will raise a :exc:`KeyError` as expected:

                >>> d['D']
                Traceback (most recent call last):
                    ...
                KeyError: csiKeyString('D')

            """

        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().__getitem__(key)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __setitem__(self, key, value):
        """__setitem__(key, value)
        
            Converts *key* to a :class:`csiKeyString` or :class:`csiKeyDecimal` if necessary, and then creates 
            ``d[key] = value``.
            
            Example:
            
                >>> from csid import csid
                >>> d = csid([['a', 1], ['b', 2], ['c', 3]])
                >>> d['d'] = 4
                >>> d
                csid(csiKeyString('a'): 1, csiKeyString('b'): 2, csiKeyString('c'): 3, csiKeyString('d'): 4)

                """
        
        if isinstance(key, str):
            key = csiKeyString(key)
        elif isinstance(key, (float, Decimal)):
            key = csiKeyDecimal(key)
        return super().__setitem__(key, value)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
            
            Produces a string which can reproduce the :class:`csid`.

            Example:

                >>> from csid import csid
                >>> csid([['a', 1], ['b', 2], ['c', 3]])
                csid(csiKeyString('a'): 1, csiKeyString('b'): 2, csiKeyString('c'): 3)
            
            """

        return f'csid({super().__repr__()[1:-1]})'

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__()
            
            Creates a string for the :class:`csid` where each (key, value) pair is on its own line.
            
            Example:
            
                >>> from csid import csid
                >>> print(csid([['a', 1], ['b', 2], ['c', 3], [4, 'd']]))
                {
                'a': 1,
                'b': 2,
                'c': 3,
                4: 'd'
                }

                """
        def _quoteStr(item):

            if isinstance(item, str):
                return f"'{item}'"
            else:
                return item

        s = (f"{_quoteStr(key)}: {_quoteStr(value)}" for key, value in self.items())
        data_string = ',\n'.join(s)
        out_str = f"\u007b\n{data_string}\n\u007d"

        return out_str

#==================================================================================================================  
class csiKeyString(str):
    """Creates a key derived from a string instance for :class:`csid`."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, key):
        """__init__(key)

            Sets the :attr:`.key` attr.

            Example:

                >>> from csid import csiKeyString
                >>> csiKeyString('  Nodeset-1')
                csiKeyString('  Nodeset-1')

            *key* should be a string. Other types will raise an :exc:`AttributeError` when the other functions of 
            this class are called. Example:

                >>> a = csiKeyString(100)
                >>> hash(a)
                Traceback (most recent call last):
                    ...
                AttributeError: 'int' object has no attribute 'lower'

            *key* is not automatically converted to a string for performance reasons. Therefore, if the user needs
            to use this class directly, they must first ensure that *key* is a string before instancing it.
            
            Args:
                key (str): An instance of a string object to serve as the case- and space-insensitive key."""

        self.key = key #: :str: A string type object.

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __hash__(self):
        """__hash__()

            Hashes :func:`rsl(key) <misc_functions.rsl>`.

            Strings which differ only in capitalization and spacing will hash to the same value. For example:

                >>> from csid import csiKeyString
                >>> hash(csiKeyString('  Nodeset-1')) == hash(csiKeyString('NODESET-1'))
                True

            Strings which have larger differences will not hash to the same value:

                >>> hash(csiKeyString('  Nodeset-1')) == hash(csiKeyString('"NODESET-1"'))
                False

            Returns:
                int: The hashed value of :func:`rsl(key) <misc_functions.rsl>`."""

        return hash(self.key.lower().replace(' ', ''))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __eq__(self, other):
        """__eq__(other)

            Checks if :attr:`key` is equal to *other*.
            
            *other* should be a :class:`csiKeyString`. This function will not convert *other* to a :class:`csiKeyString`, 
            because in most cases this class should only be used through a :class:`csid`, which will handle the conversion.
            
            Args:
                other (str): An instance of a string object to which :attr:`key` will be compared.
                
            Returns:
                bool: True if :func:`rsl(key) <.rsl>` == :func:`rsl(other) <.rsl>`, else False.
                
            Examples:
                Here's the typical usage::

                    >>> from csid import csiKeyString
                    >>> csiKeyString('  Nodeset-1') == csiKeyString('Nodeset-1')
                    True

            If *other* is not a :class:`csiKeyString`, this will convert *other* to a :class:`csiKeyString` before proceeding:

                >>> csiKeyString('  Nodeset-1') == 'Nodeset-1'
                True

        """

        try:
            return self.key.lower().replace(' ', '') == other.key.lower().replace(' ', '')
        except AttributeError:
            other = csiKeyString(other)
            return self.key.lower().replace(' ', '') == other.key.lower().replace(' ', '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__()
       
            Returns str(:attr:`key`).
            
            Example:
            
                >>> from csid import csiKeyString
                >>> str(csiKeyString('  Nodeset-1'))
                '  Nodeset-1'
                
        """

        return str(self.key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
            
            Returns the string needed to recreate the object.
            
            Example:
            
                >>> from csid import csiKeyString
                >>> csiKeyString('  Nodeset-1')
                csiKeyString('  Nodeset-1')
            
            Returns:
                str"""

        return f"csiKeyString('{self.key}')"

#==================================================================================================================  
class csiKeyDecimal(Decimal):
    """Creates a key derived from a float instance for :class:`csid`. The key will be a precise :class:`~decimal.Decimal` 
    implementation of ``str(float)`` as the float is written, as opposed to a :class:`~decimal.Decimal` of the evaluated 
    float."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __new__(cls, key):
        """__new__(key)
        
        If *key* is a float, convert it to a string before creating the base :class:`~decimal.Decimal` instance.
        
        Args:
            key (:class:`float`, :class:`~decimal.Decimal`, :class:`str`): An object which will be converted to a Decimal-type.
            
        Returns:
            csiKeyDecimal:"""


        if isinstance(key, float):
            key = str(key)
        try:
            return super().__new__(cls, key)
        except InvalidOperation:
            return super().__new__(cls, inpDecimal(key))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, key):
        """__init__(key)
       
            Does nothing by itself. :func:`__new__` does the necessary processing to the input.

            If *key* is a float, it will be converted to a :class:`~decimal.Decimal`:

                >>> from csid import csiKeyDecimal
                >>> csiKeyDecimal(1.234)
                csiKeyDecimal('1.234')

            This also accepts Decimal-types as *key*:

                >>> from inpDecimal import inpDecimal
                >>> csiKeyDecimal(inpDecimal(' 1.234'))
                csiKeyDecimal('1.234')

            Strings are also acceptable keys:

                >>> csiKeyDecimal('  1.234')
                csiKeyDecimal('1.234')

            However, if the string does not evaluate to a :class:`~decimal.Decimal`, a :exc:`decimal.InvalidOperation`
            will be raised:

                >>> csiKeyDecimal('  1.234a')
                Traceback (most recent call last):
                    ...
                decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

            Args:
                key (:class:`float`, :class:`~decimal.Decimal`, :class:`str`): Captures the input from :class:`__new__`."""
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __hash__(self):
        """__hash__()

            Hashes the :class:`csiKeyDecimal` object.

            Example:

                >>> from csid import csiKeyDecimal
                >>> hash(csiKeyDecimal(1.234))
                152185638608103802

            The hash value will be identical using different input methods to :class:`csiKeyDecimal`, provided the different
            input values will evaluate to the same :class:`~decimal.Decimal` value:

                >>> from inpDecimal import inpDecimal
                >>> hash(csiKeyDecimal(inpDecimal('  1.234e0'))) == hash(csiKeyDecimal('  12.34e-1'))
                True


            Returns:
                int: The hashed value of the :class:`csiKeyDecimal` object."""

        return super().__hash__()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __eq__(self, other):
        """__eq__(other)

            Converts *other* to a :class:`csiKeyDecimal` (if necessary) and then returns ``self.as_tuple() == other.as_tuple()``.
            
            Examples:

                >>> from csid import csiKeyDecimal
                >>> csiKeyDecimal('  12.34e-1') == 1.234
                True
                >>> csiKeyDecimal('  12.34e-1') == 1.237
                False
            
            Args:
                other (:class:`float`, :class:`~decimal.Decimal`, :class:`str`): An instance of a :class:`float`, :class:`~decimal.Decimal`, 
                    or :class:`str` object to which the :class:`csiKeyDecimal` will be compared.
                
            Returns:
                bool: True if ``self.as_tuple() == other.as_tuple()``, else False."""

        if not isinstance(other, csiKeyDecimal):
            other = csiKeyDecimal(other)
        return self.as_tuple() == other.as_tuple()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__()
       
            Returns a string representation of the :class:`csiKeyDecimal`.

            Example:

                >>> from csid import csiKeyDecimal
                >>> str(csiKeyDecimal('  12.34e-1'))
                '1.234'

            """

        return f'{self}'

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
            
            Returns the string needed to recreate the object.
            
            Example:

                >>> from csid import csiKeyDecimal
                >>> csiKeyDecimal('  1.234')
                csiKeyDecimal('1.234')

            """

        #return "{}".format(self.key)
        return f"csiKeyDecimal('{self}')"
