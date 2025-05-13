#Copyright © 2023 Dassault Systemès Simulia Corp.

# cspell:includeRegExp comments

from .misc_functions import rsl, stripSpace
from .config_re import re4, re5
from sys import intern
import traceback
#==================================================================================================================
class inpString(str):
    """An :class:`inpString` object behaves like a regular :class:`str`, except it will internally store the string
        value without any leading or trailing spaces (Abaqus is space-insensitive regarding leading or trailing spaces
        in names). This class will track the leading and trailing spaces using interned string patterns, which will be
        used to reproduce the original string exactly."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __new__(cls, inputStr, ss=False):
        """__new__(inputStr, ss=False)"""
        
        return super().__new__(cls, inputStr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, inputStr, ss=False):
        r"""__init__(inputStr, ss)
        
            Creates the :class:`.inpString` instance. 
            
            This is meant to operate on text which corresponds to a single string item. For example, a set name, a 
            parameter name, etc. Thus, in most cases *inputStr* should be a single word with surrounding whitespace.
            The only time *inputStr* should contain a space between alphanumeric characters is when the value of interest
            is a quoted string and includes spaces between words.

            Example usage:

                >>> from inpString import inpString
                >>> inpString('  Nodeset-1')
                inpString('  Nodeset-1', False)
            
            If we desire to remove trailing and leading spaces, we can set *ss* = True:
                
                >>> inpString('  Nodeset-1', ss=True)
                inpString('Nodeset-1', True)

            Args:
                inputStr (str): The unformatted string for which the :class:`.inpString` will be created.
                ss (bool): If True, leading and trailing spaces will be removed from *inputStr*, and not reinserted
                    when producing the output string.
        """

        self.ss = ss #: :bool: If True, leading and trailing spaces will be permanently removed from *inputStr*. Defaults to False.
        self._value = None #: Stores the non-whitespace information of *inputStr*. Defaults to None
        self._formatStr = None #: Stores the whitespace information of *inputStr*, with placeholder symbols ("%s") where :attr:`~inpString.inpString._value` should be reinserted. Defaults to None
        self._evalString(inputStr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _evalString(self, inputStr):
        """_evalString(inputStr) 
        
            Evaluates the input string and performs some formatting. This will separate whitespace from alphanumeric characters,
            but it will leave spaces between alphanumeric characters. 
            
            This will set :attr:`~inpString.inpString._value` and :attr:`~inpString.inpString._formatStr`, but the function
            has no direct return.
            
            Here's an example of the :attr:`_value` and :attr:`_formatStr` attributes for a simple case:
            
                >>> from inpString import inpString
                >>> s1 = inpString('  Nodeset-1')
                >>> s1._value
                'Nodeset-1'
                >>> s1._formatStr
                '  %s'

            Here are the same attributes when *ss* = True:

                >>> s2 = inpString('  Nodeset-1', ss=True)
                >>> s2._value
                'Nodeset-1'
                >>> s2._formatStr
                '%s'

            Finally, if we have a quoted string with spaces, the spaces inside the quotes are included with :attr:`_value`
            because they're meaningful. The spaces outside the quotes are tracked in :attr:`_formatStr` as usual:

                >>> s3 = inpString('  "Nodeset Name with Spaces"')
                >>> s3._value
                '"Nodeset Name with Spaces"'
                >>> s3._formatStr
                '  %s'
                
                """
        
        obj = stripSpace(inputStr, self.ss) #Respect self.ss
        s_tmp = re4.sub("_", obj) #replace spaces between words with _ so fs has one %s, out will have one value
        fs = re5.sub('%s', s_tmp)
        self._formatStr = intern(fs)
        tmp = stripSpace(obj.replace('\t', ''), True) # Strip spaces when storing the object in self. They are tracked in self.formatStr and will be reapplied when writing file.
        self._value = tmp
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _outstr(self):
        """_outstr()
       
            Generates the output string. :attr:`_value` is subbed into :attr:`_formatStr`. Should not need to be called
            by the user directly.

            Example usage:

                >>> from inpString import inpString
                >>> s = inpString('  Nodeset-1')
                >>> s._outstr()
                '  Nodeset-1'
           
            This function can also handle cases where *inputStr* to :func:`__init__` was only whitespace:

                >>> s = inpString('    ')
                >>> s._outstr()
                '    '

            Returns:
                str: The string in the original formatting."""

        try:
            #s = super().__str__()
            out = self._formatStr % self._value
        except TypeError:
            out = self._formatStr #unideal workaround meant to handle whitespace only strings
        return out

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Calls :func:`_outstr` to create a string of object in the original formatting.

            Example usage:

                >>> from inpString import inpString
                >>> print(inpString('  Nodeset-1'))
                  Nodeset-1
            
            Returns:
                str:"""

        return self._outstr()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
       
            Creates a string representation which can be used to recreate the object.

            Example usage:

                >>> from inpString import inpString
                >>> inpString('  Nodeset-1')
                inpString('  Nodeset-1', False)
            
            Returns:
                str:"""
        
        return "{}('{}', {})".format(self.__class__.__name__, self._outstr(), self.ss)
        #return self._outstr()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __getnewargs__(self):
        """__getnewargs__():
    
        This function is required so the class can pickle/unpickle properly. This enables multiprocessing, and should 
        not need to be called by the user.
        
        Example usage:
            
            >>> from inpString import inpString
            >>> s = inpString('  Nodeset-1')
            >>> s.__getnewargs__()
            ('  Nodeset-1', False)
            
            """
    
        return (self._outstr(), self.ss)
