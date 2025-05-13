#Copyright © 2023 Dassault Systemès Simulia Corp.

# cspell:includeRegExp comments

import traceback
from sys import intern
from .config_re import re12

#==================================================================================================================
class inpInt(int):
    """An :class:`inpInt` object behaves like a regular :class:`int`, except it has a new attribute :attr:`_formatStr`. 
       This attribute is used to create exact string representations of the original object."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __new__(cls, inputStr):
        """__new__(inputStr)
        
            Creates the :class:`.inpInt` instance.
        """
        
        return super().__new__(cls, inputStr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, inputStr):
        """__init__(inputStr) 
        
            Initializes the :class:`inpInt` instance, represented by *inputStr*. Parses the integer value contained
            in *inputStr*, and also tracks any whitespace characters included in *inputStr*.

            Example usage:

                >>> from inpInt import inpInt
                >>> num1 = inpInt('  2 ')
                >>> num1
                inpInt('  2 ')
                >>> str(num1)
                '  2 '

            Since an :class:`inpInt`, all of the typical :class:`int` operations will work:

                >>> num2 = inpInt('  2 ')
                >>> num1 + num2
                4

            Please note that most :class:`int` operations will produce a :class:`int`, not a :class:`inpInt`:

                >>> type(num1 + num2)
                <class 'int'>

            Args:
                inputStr (str): The string containing an integer which will be parsed, maintaining the original
                    formatting."""

        self._formatStr = intern(re12.sub("%s", inputStr)) #: Stores the whitespace information of *inputStr*, with placeholder symbols ("%s") where the integer value should be reinserted. Will include leading 0s, the positive sign, or the negative sign if it precedes leading 0s.
        if '0' in self._formatStr:
            self._outstr = self._outstr_lead0
        #self = int(inputStr)  #: Stores the non-whitespace information of *inputStr*.

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _outstr_lead0(self):
        """_outstr_lead0()
        
            Generates the output string for cases which include a leading 0.

            Example usage:

                >>> from inpInt import inpInt
                >>> str(inpInt(' -01'))
                ' -01'

            Returns:
                str: The string in the original formatting.
        """

        fs = self._formatStr
        try:
            out = fs % abs(self.numerator)
        except TypeError:
            out = fs
        return out

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _outstr(self):
        """_outstr()
       
            Generates the output string.

            Example usage:

                >>> from inpInt import inpInt
                >>> str(inpInt('  2 '))
                '  2 '
           
            Returns:
                str: The string in the original formatting."""

        fs = self._formatStr
        try:
            out = fs % self.numerator
        except TypeError:
            out = fs
        return out

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
       
            Creates a string representation which can be used to recreate the object.

            Example usage:

                >>> from inpInt import inpInt
                >>> inpInt('  2 ')
                inpInt('  2 ')
            
            Returns:
                str:"""

        #return super().__repr__()
        return "{}('{}')".format(self.__class__.__name__, self._outstr())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__()
            
            Calls :func:`_outstr` to create a string of object in the original formatting.

            Example usage:

                >>> from inpInt import inpInt
                >>> str(inpInt('  2 '))
                '  2 '
            
            Returns:
                str:"""

        return self._outstr()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __getnewargs__(self):
        """__getnewargs__()
    
        This function is required so the class can pickle/unpickle properly. This enables multiprocessing.
        
        Example:
        
            >>> from inpInt import inpInt
            >>> inpInt('  2 ').__getnewargs__()
            ('  2 ',)

        Returns:
            tuple

        """
    
        return (self._outstr(),)