#Copyright © 2023 Dassault Systemès Simulia Corp.

# cspell:includeRegExp comments

from decimal import Decimal
from .config_re import re7, re8, re9, re10, re11, re19
from sys import intern
from .inpRWErrors import DecimalInfError

#==================================================================================================================
class inpDecimal(Decimal):
    """An :class:`inpDecimal` object behaves like a regular :class:`~decimal.Decimal`, except it has new attributes
       :attr:`_formatStr` and possibly :attr:`_formatExp`. These attributes are used to create exact string representations
       of the original object."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __new__(cls, inputStr):
        """__new__(inputStr)
        
            This function processes the *inputStr* and handles some problematic strings.
            
            It replaces 'd' and 'D' characters in *inputStr* prior to creating the base :class:`~decimal.Decimal` instance.
            It also raises an :exc:`~inpRWErrors.DecimalInfError` if *inputStr* contains 'INF' (not case-sensitive). 'INF'
            will create a valid :class:`~decimal.Decimal` object, but there should be no cases where an infinite number
            is valid for an Abaqus input file. Thus, an exception is raised which triggers :mod:`inpRW` to handle the input
            as a string-like object instead of a :class:`~decimal.Decimal`.

            The original *inputStr* will be passed to :func:`__init__`.
            
            Args:
                inputStr (str): The string to be processed. Should contain a floating-point like object.

            Raises:
                inpRWErrors.DecimalInfError
        """
        
        if 'INF' in inputStr.upper():
            raise DecimalInfError
        inputStr = re10.sub('E', inputStr) #replace d or D with E when parsing the value, as Python cannot use D for scientific notation
        return super().__new__(cls, inputStr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, inputStr):
        """__init__(inputStr)
        
            Creates the :class:`.inpDecimal` instance. 
            
            This is like the :class:`~decimal.Decimal` class, except it also tracks the exact formatting of the original
            number string.

            Args:
                inputStr (str): The string representing the number which should be parsed.
                
            Examples:
                ::
            
                    >>> from inpDecimal import inpDecimal
                    >>> a = inpDecimal('  3.14e0')
                    >>> str(a)
                    '  3.14e0'

                Since :class:`inpDecimal` inherits from :class:`~decimal.Decimal`, they support the same operations.
                Note that the resultant of most operations between two :class:`inpDecimal` objects will be a 
                :class:`~decimal.Decimal`, as shown in the following example:

                    >>> b = inpDecimal(' 2')
                    >>> a * b
                    Decimal('6.28')

                Operations between an :class:`inpDecimal` and a :class:`float` will raise a :exc:`TypeError`, as expected:

                    >>> a * 2.0
                    Traceback (most recent call last):
                        ...
                    TypeError: unsupported operand type(s) for *: 'inpDecimal' and 'float'
            
            """

        self._formatExp = None #:  Stores the exponent string if the original number string is in scientific notation. Defaults to None
        self._formatStr = None #: Stores the whitespace information of *inputStr*, with placeholder symbols ("%s") where digits should be reinserted. Defaults to None
        self._evalDecimal(inputStr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _evalDecimal(self, inputStr):
        """_evalDecimal(inputStr)
        
            Parses *inputStr* to recognize the numeric value and the original formatting.
            
            This function will populate :attr:`_formatExp` and :attr:`_formatStr`, but it has no direct return. It will
            be called as part of :func:`__init__` and should not be called by itself.
            
            Example usage:

                >>> from inpDecimal import inpDecimal
                >>> a = inpDecimal('  1.234E-2')

            This will set the following additional attributes, which track the exact formatting:

                >>> a._formatStr
                '  %s.%s%s%sE%s'
                >>> a._formatExp
                '-2'

            It also handles numbers which use "d" or "D" for the exponent notation:

                >>> inpDecimal('5.678d+10')
                inpDecimal('5.678d+10')

            Args:
                inputStr (str): The string representing the number which should be parsed."""

        ecase = re7.findall(inputStr)
        if ecase:
            tmp = re8.split(inputStr)
            fs = ecase[0].join([re9.sub("%s", tmp[0]), tmp[1]])
            fs = fs.replace(tmp[1], "%s")
            #inputStr = re10.sub('E', inputStr) #replace d or D with E when parsing the value, as Python cannot use D for scientific notation
        else:
            fs = re9.sub('%s', inputStr)
        tmp = re11.sub('', inputStr)
        self._formatStr = intern(fs)
        m = re19.search(tmp)
        if m:
            self._formatExp = m.group(0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _outstr(self):
        r"""_outstr()
       
            Generates the output string. This should not be called by the user directly, as it is called automatically
            by :func:`__repr__` and :func:`__str__`.

            Example usage:

                >>> from inpDecimal import inpDecimal
                >>> str(inpDecimal(' 1.234'))
                ' 1.234'
           
            Returns:
                str: The string in the original formatting."""

        oat = self.as_tuple()
        fs = self._formatStr
        fe = self._formatExp
        numsub = fs.count('%s')
        pre0s = []

        if fe:
            numsub -= 1
            oe = int(fe) #object exponent
            ed = oat[2] - oe #exponent difference
            if ed <0:
                pre0s = [0] * (numsub - len(oat[1]))
            try:
                out = fs % tuple(pre0s + list(oat[1]) + [fe])
            except TypeError:
                out = fs % tuple([0] + pre0s + list(oat[1]) + [fe])
        else:
            pre0s = [0] * (numsub - len(oat[1]))
            try:
                out = fs % tuple(pre0s + list(oat[1]))
            except TypeError:
                out = fs % tuple([0] + pre0s + list(oat[1]))

        return out

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
       
            Creates a string representation which can be used to recreate the object.

            Example:

                >>> from inpDecimal import inpDecimal
                >>> inpDecimal('  -01.097 ')
                inpDecimal('  -01.097 ')
            
            Returns:
                str:"""

        #return f'{self}'
        return "{}('{}')".format(self.__class__.__name__, self._outstr())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Calls :func:`_outstr` to create a string of object in the original formatting.

            Example:

                >>> from inpDecimal import inpDecimal
                >>> str(inpDecimal('\t-01.097 '))
                '\t-01.097 '
            
            Returns:
                str:"""

        return self._outstr()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __reduce__(self):
        """__reduce__()
    
            This function is required so the class can pickle/unpickle properly. This enables multiprocessing.
            
            Example:
            
                >>> from inpDecimal import inpDecimal
                >>> inpDecimal('5.678D+10').__reduce__()
                (<class 'inpDecimal.inpDecimal'>, ('5.678D+10',))
                
                """
    
        return (self.__class__, (self._outstr(),))