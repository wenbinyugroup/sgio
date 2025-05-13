#Copyright © 2023 Dassault Systemès Simulia Corp.

"""The :mod:`inpRWErrors` module contains the custom exception types used throughout :mod:`inpRW`."""

# cspell:includeRegExp comments

#==================================================================================================================
class inpRWErrors(Exception):
    """inpRWErrors
        The base class for all custom Exception types used by :mod:`inpRW`."""

    def __init__(self, args=None):
        """__init__(args=None)

            Initializes the exception. *args* should be a :class:`tuple`.

            :class:`~inpRWErrors` is meant to be subclassed, not used directly. It provides a common base class
            for the other exceptions in this module.

            Example usage:

                >>> from inpRWErrors import inpRWErrors
                >>> raise inpRWErrors
                Traceback (most recent call last):
                    ...
                inpRWErrors.inpRWErrors: None

            Args:
                args (tuple): A :class:`tuple` of arguments which will be passed to the class.

        """
        if args == None:
            self.args = (None,)
        else:
            self.args = args

    def __str__(self):
        """__str__()
        
            Creates a string error message of the object using the default Exception :meth:`__str__`.
        """

        return super().__str__()
    
#==================================================================================================================
class KeywordNotFoundError(inpRWErrors):
    """KeywordNotFoundError
        This class is a blank Exception and is raised by :func:`~inpRW._inpFind.Find.findKeyword` to break out of loops 
        if the particular keyword cannot be found in :attr:`~inpRW.inpRW.keywords`.
        
        Example:
            
            >>> from inpRWErrors import KeywordNotFoundError
            >>> raise KeywordNotFoundError
            Traceback (most recent call last):
                ...
            inpRWErrors.KeywordNotFoundError: None
            
            """
    pass

#==================================================================================================================
class DecimalInfError(inpRWErrors):
    """DecimalInfError
        This class is a blank Exception and is raised by :func:`~inpDecimal.inpDecimal.__new__` if the input string
        is 'INF'.
        
        Example:
            
            >>> from inpRWErrors import DecimalInfError
            >>> raise KeywordNotFoundError
            Traceback (most recent call last):
                ...
            inpRWErrors.KeywordNotFoundError: None
            
            """
    
    def __str__(self):

        return f'ERROR! "INF" detected as the input string.'

#==================================================================================================================
class ElementIncorrectNodeNumError(inpRWErrors):
    """ElementIncorrectNodeNumError
        Raised when an element has been assigned the incorrect number of nodes for its element type."""

    def __init__(self, elementType, nodeNum):
        """__init__(elementType, nodeNum)
            
            Sets the arguments which will be used in the Error message.

            Example:

                >>> from inpRWErrors import ElementIncorrectNodeNumError
                >>> raise ElementIncorrectNodeNumError('C3D8', 8)
                Traceback (most recent call last):
                    ...
                inpRWErrors.ElementIncorrectNodeNumError: ERROR! An element of type C3D8 must have 8 nodes.

            If this exception is raised without the proper arguments, a :exc:`TypeError` will instead be raised:

                >>> raise ElementIncorrectNodeNumError # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
                Traceback (most recent call last):
                    ...
                TypeError: ...__init__() missing 2 required positional arguments: 'elementType' and 'nodeNum'

            Args:
                elementType (str)
                nodeNum (int)"""
        self.elementType = elementType
        self.nodeNum = nodeNum

    def __str__(self):
        """__str__()
        
            Produces the string error message."""
        
        nodeNum = self.nodeNum
        if isinstance(nodeNum, list):
            nodeNum = nodeNum[0]
            return f'ERROR! An element of type {self.elementType} must have {nodeNum} nodes.'
        elif isinstance(nodeNum, set):
            nodeNumRange = list(nodeNum)
            nodeNumRange.sort()
            return f'ERROR! An element of type {self.elementType} must have between {nodeNumRange[0]} and {nodeNumRange[-1]} nodes.'
        elif isinstance(nodeNum, int):
            return f'ERROR! An element of type {self.elementType} must have {nodeNum} nodes.'

#==================================================================================================================
class ElementTypeMismatchError(inpRWErrors):
    """ElementTypeMismatchError
        Raised when an :class:`~mesh.Element` is inserted into a :class:`~mesh.MeshElement` class, and
        :attr:`~mesh.Element.eltype` parameter does not match :attr:`~mesh.MeshElement.eltype` parameter."""

    def __init__(self, otherEltype, meshElementType):
        """__init__(otherEltype, meshElementType)
        
            Sets the arguments which will be used in the Error message.

             Example:

                >>> from inpRWErrors import ElementTypeMismatchError
                >>> raise ElementTypeMismatchError('C3D8R', 'C3D8')
                Traceback (most recent call last):
                    ...
                inpRWErrors.ElementTypeMismatchError: ERROR! An element of type C3D8R cannot be added to a MeshElement with eltype C3D8

            If this exception is raised without the proper arguments, a :exc:`TypeError` will instead be raised:

                >>> raise ElementTypeMismatchError # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
                Traceback (most recent call last):
                    ...
                TypeError: ...__init__() missing 2 required positional arguments: 'otherEltype' and 'meshElementType'
            
            Args:
                otherEltype (str)
                meshElementType(str)"""
        self.otherElType = otherEltype
        self.meshElementType = meshElementType

    def __str__(self):
        """__str__()
        
            Produces the string error message."""
        
        return f'ERROR! An element of type {self.otherElType} cannot be added to a MeshElement with eltype {self.meshElementType}'
