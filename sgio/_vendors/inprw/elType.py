#Copyright © 2023 Dassault Systemès Simulia Corp.

"""The :mod:`elType` module provides the :class:`.elType` class, which stores information about an Abaqus element type."""

# cspell:includeRegExp comments

#==================================================================================================================
class elType(object):
    """The :class:`.elType` class stores information about a particular Abaqus element type."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, name, numNodes, solvers='', description=''):
        """__init__(name, numNodes, solvers, description='')
        
            Initializes attributes of the :class:`.elType` class.

            At the moment, :attr:`.numNodes` is the only attribute used by :mod:`inpRW`. The other attributes are
            provided for the user's convenience.
            
            If *numNodes* is an integer, it will be stored to :attr:`.numNodes`. If *numNodes* is a set, it will be
            stored to :attr:`.numNodesSet`.

            Args:
                name (str): The name of the element type.
                numNodes (int or set): The number of nodes needed to define the element. This is either an integer or
                    a set of integers if the element type can have a varying number of nodes.
                solvers (str): A string indicating which Abaqus solvers support the element type. 'S' for Standard, 
                    'E' for Explicit, and 'SE' for both.
                description (str): The description string for the element type, taken from the Abaqus documentation.

            Examples:

                Here's the basic usage of the class:
                    
                    >>> from elType import elType
                    >>> elType('AC1D2', 2, 'S', '    2-node acoustic link')
                    elType(name='AC1D2', numNodes=2, solvers='S', description='    2-node acoustic link')

                If *numNodes* is a set, you need to use the :attr:`.numNodesSet` attribute instead of :attr:`.numNodes`:

                    >>> elType1 = elType('C3D15V', {16, 17, 18, 15}, 'S', '    15 to 18-node triangular prism')
                    >>> l = list(elType1.numNodesSet)
                    >>> l.sort()
                    >>> l
                    [15, 16, 17, 18]
        """

        self.name = name #: :str: The element type name.
        
        if isinstance(numNodes, set):
            self.numNodesSet = numNodes #: :set: A set of all the numbers of nodes which can define the element.
        else:
            self.numNodes = numNodes #: :int: The number of nodes needed to define the element.
        self.description = description #: :str: The description string for the element type, taken from the Abaqus documentation.
        self.solvers = solvers #: :str: A string indicating which Abaqus solvers support the element type. 'S' for Standard, 'E' for Explicit, and 'SE' for both.

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __getattr__(self, name):
        """__getattr__(name)
        
            Overrides the default attribute retrieval behavior for cases where :attr:`.numNodes` is not defined.

            This function raises an :exc:`AttributeError` guiding users towards the :attr:`.numNodesSet` attribute
            if :attr:`.numNodes` does not exist.
            
            See :meth:`~object.__getattr__` for more information.

            Args:
                name (str): The attribute name.

            Raises:
                AttributeError

            Examples:
                Here's an example of trying to retrieve :attr:`.numNodes` if it doesn't exist:
                    
                    >>> from elType import elType
                    >>> elType1 = elType('C3D15V', {16, 17, 18, 15}, 'S', '    15 to 18-node triangular prism')
                    >>> elType1.numNodes # doctest: +ELLIPSIS
                    Traceback (most recent call last):
                        ...
                    AttributeError: elType object has no attribute 'numNodes'. Use 'numNodesSet' instead...

                The error is slightly different for any other attribute:

                    >>> elType1.test 
                    Traceback (most recent call last):
                        ...
                    AttributeError: elType object has no attribute 'test'.
            
        """
        
        if name == 'numNodes':
            raise AttributeError(f"elType object has no attribute '{name}'. Use 'numNodesSet' instead.")
        else:
            raise AttributeError(f"elType object has no attribute '{name}'.")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
           
            Produces a repr of the :class:`.elType` instance.

            If the instance includes :attr:`.numNodesSet`, this will be reported as numNodes.
            
            Returns:
                str

            Examples:

                Here's a basic example:
                    
                    >>> from elType import elType
                    >>> elType('AC1D2', 2, 'S', '    2-node acoustic link')
                    elType(name='AC1D2', numNodes=2, solvers='S', description='    2-node acoustic link')

                If the instance has :attr:`.numNodesSet`, this will be listed as 'numNodes':

                    >>> elType('C3D15V', {16, 17, 18, 15}, 'S', '    15 to 18-node triangular prism')
                    elType(name='C3D15V', numNodes={16, 17, 18, 15}, solvers='S', description='    15 to 18-node triangular prism')

        """

        try:
            numNodes = self.numNodes
        except AttributeError:
            numNodes = self.numNodesSet

        return f"elType(name={self.name!r}, numNodes={numNodes}, solvers={self.solvers!r}, description={self.description!r})"
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__()
        
            Produces a string of the :class:`elType` instance.

            Produces an identical string as :func:`~elType.elType.__repr__`.

            Returns:
                str

            Examples:

                >>> from elType import elType
                >>> str(elType(name='C3D8R', numNodes=8, solvers='SE'))
                "elType(name='C3D8R', numNodes=8, solvers='SE', description='')"

        """
        return self.__repr__()