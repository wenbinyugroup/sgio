#Copyright © 2023 Dassault Systemès Simulia Corp.

"""The :mod:`mesh` module contains classes that store node and element data."""

# cspell:includeRegExp comments

from .misc_functions import rsl, makeDataList
from .csid import *
from traceback import print_exc
from .eval2 import eval2
from sys import intern
from .inpRWErrors import ElementIncorrectNodeNumError, ElementTypeMismatchError
from .config import _elementTypeDictionary

#==================================================================================================================  
class Node(object):
    r"""The Node class stores nodal information from a single node (i.e. one dataline from a \*NODE keyword block)."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, dataline='', label=None, data=None, elements=None, _joinS=', ', _ParamInInp=False, preserveSpacing=True, useDecimal=True):
        r"""__init__(dataline='', elements=None, _ParamInInp=False, preserveSpacing=True, useDecimal=True)
           __init__(label=None, data=None, elements=None, _joinS=', ')
        
            Initializes attributes of the Node. 

            In most cases, this will be used by :func:`~inpKeyword.inpKeyword._parseDataNode`. That function will handle
            creating the inputs to this class from the string corresponding to the node dataline. See that function 
            for an example of instancing this class. If you are instancing this class manually, there are two recommended
            options. 
            
            First, specify the *dataline* parameter and the other related parameters if you know them prior to
            creating the :class:`Node` instance and/or do not wish to use the default values. *dataline* will be parsed,
            and :attr:`label` and :attr:`data` will be populated from the parsed information.

            Here's an example using the default settings, which will use :class:`~inpInt.inpInt`, :class:`inpDecimal.inpDecimal`,
            and :class:`~inpString.inpString` to store data items and preserve the exact spacing:

                >>> from mesh import Node
                >>> dataline = '   21, 70.00,   0.00'
                >>> node = Node(dataline)
                >>> node
                Node(label=inpInt('   21'), data=[inpInt('   21'), inpDecimal(' 70.00'), inpDecimal('   0.00')], elements=[])

            The :func:`repr` of an :class:`Node` instance is consistent across the different methods to instantiate
            the class. If you wish to see how the :class:`Node` will be written out, you can use a function to call
            its string representation. For example:
                
                >>> print(node)
                   21, 70.00,   0.00
            
            Here's an example of turning off the mechanisms for preserving the exact spacing (for a performance benefit):

                >>> node = Node(dataline, preserveSpacing=False, useDecimal=False)
                >>> print(node)
                21, 70.0, 0.0

            We can also specify a custom separator to join the parsed strings when we create a string of the node. This will
            only be applied if *preserveSpacing* and *useDecimal* are False. Example:

                >>> node = Node(dataline, _joinS = ',__', preserveSpacing=False, useDecimal=False)
                >>> print(node)
                21,__70.0,__0.0

            If an item in *dataline* could be a \*PARAMETER reference, either *_ParamInInp* or *preserveSpacing* must be True,
            or else a :exc:`ValueError` will be raised. Example:

                >>> dataline = '   21, <coord>,   0.00'
                >>> node = Node(dataline, preserveSpacing=False, useDecimal=False)
                Traceback (most recent call last):
                    ...
                ValueError: could not convert string to float: ' <coord>'

            The second option is to specify *label* and *data* instead of *dataline*. Those items should be formatted properly 
            prior to instancing :class:`Node`. Example:

                >>> label = 21
                >>> data = [21, 70.0, 0.00]
                >>> node = Node(label=label, data=data)
                >>> print(node)
                21, 70.0, 0.0

            Using either method, *elements* can be specified if the user knows the list of elements which connect to the node.
            In most cases, this should not be specified, and the elements connected to the node should instead be added using
            :func:`~mesh.Element.setConnectedNodes`.

            Args:
                dataline (str): The string which contains the entire dataline for the node. Will be parsed to populate
                    the :class:`node's <Node>` attributes. Defaults to ''
                label (int): The label for the node. Defaults to None.
                data (list): The data for the node. This will be a parsed dataline. The format should be
                    [:class:`int`, :class:`float`, :class:`float`, ...]. Defaults to None.
                elements (list): The elements which are connected to the :class:`Node` instance. Defaults to None.
                _joinS (str): The string used to join the data items together when creating strings of the :class:`Node` instance. 
                    Defaults ', '.
                _ParamInInp (bool): Indicates if \*PARAMETER is in the input file, which would mean that the dataline items 
                    could be strings instead of exclusively integers. Defaults to False.
                preserveSpacing (bool): If True, the exact spacing of all items will be preserved by using :class:`~inpInt.inpInt`.
                    In most cases when creating new :class:`.Element` instances, you will want to use the same value that the rest
                    of the input file was parsed with. Defaults to True. 
                useDecimal (bool): If True, any floating point numbers will be parsed as :class:`~decimal.Decimal` or :class:`~inpDecimal.inpDecimal`.
                    In most cases when creating new :class:`.Element` instances, you will want to use the same value that the rest
                    of the input file was parsed with. Defaults to True.
        """

        self._joinS = _joinS #: :str: The string used to join data items together when creating a string for the entire dataline. Defaults to ', ', which will be sufficient for most cases.
        self._ParamInInp = _ParamInInp #: :bool: Indicates if \*PARAMETER is in the input file. If True, data items could be references to \*PARAMETER functions, and the datalines might be strings, so the :func:'~eval2.eval2' function must be used when parsing data items instead of assuming they must be integers. Defaults to False.
        self.preserveSpacing = preserveSpacing #: :bool: If True, the exact spacing of all items will be preserved by using :class:`~inpInt.inpInt` instead of :class:`int`. :attr:`_joinS` will be set to ',' if *preserveSpacing* is True, as the spacing will be stored in the data objects. Defaults to True.
        self.useDecimal = useDecimal #: If True, any floating point numbers will be parsed as :class:`~decimal.Decimal` or :class:`~inpDecimal.inpDecimal`. Defaults to True.

        if dataline:
            self._parseDataLine(dataline)
            if self.preserveSpacing:
                self.useDecimal = True 
                self._joinS = ','
        else:
            self.label = label #: :int: The node label.
            if data == None:
                self.data = []
            else:
                self.data = data #: :list: A list containing the parsed data items.
        if elements == None:
            self.elements = [] #: :list: Will store the elements that reference this :class:`Node`. This is populated by :func:`Element.setConnectedNodes`.
        else:
            self.elements = elements
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataLine(self, dataline):
        r"""_parseDataLine(dataline)
        
            Populates the :class:`Node` instance by parsing the *dataline* string. 

            This function will be called automatically when :class:`Node` is initialized if *datalines* is specified.

            Example usage:

                >>> from mesh import Node
                >>> node = Node()
                >>> node._parseDataLine('   21, 70.00,   0.00')
                >>> node
                Node(label=inpInt('   21'), data=[inpInt('   21'), inpDecimal(' 70.00'), inpDecimal('   0.00')], elements=[])
            
            Args:
                dataline (str): A string containing the information for the entire dataline.
        """

        ps = self.preserveSpacing
        ud = self.useDecimal
        if not self._ParamInInp and not ps and not ud:
            ls = dataline.split(',')
            key = int(ls[0])
            value = [float(j) for j in ls[1:]]
            value.insert(0, key)
            self.label = key
            self.data = value
        else:
            ls = dataline.split(',')
            key = eval2(ls[0], t=int, ps=ps, useDecimal=ud)
            value = [eval2(j, t=float, ps=ps, useDecimal=ud) for j in ls[1:]]
            value.insert(0, key)
            self.label = key
            self.data = value

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _mergeElementData(self, other):
        r"""_mergeElementData(other)
        
            Currently unused"""

        self.elements = other.elements

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateElements(self, ed):
        r"""updateElements(ed)
       
            Checks if each element in :attr:`elements` exists in *ed*. Returns 0 if :attr:`elements` is empty, 1 if
            elements have been removed, or 2 if no changes were made.
            
            Args:
                ed (TotalMesh): This is the :class:`TotalMesh` instance containing elements in which to check for :attr:`elements`.

            Returns:
                int: 0 if :attr:`elements` is now empty, 1 if :attr:`elements` was modified, 2 if :attr:`elements` is unchanged."""

        elements = self.elements[:]
        mod = False
        for element in elements:
            temp = ed.get(element)
            if temp == None:
                self.elements.remove(element)
                mod = True
        if len(self.elements) == 0:
            return 0
        elif mod:
            return 1
        else:
            return 2

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        r"""__repr__()
            
            Produces a repr of the Node.
            
            Example:

                >>> from mesh import Node
                >>> Node('   21, 70.00,   0.00')
                Node(label=inpInt('   21'), data=[inpInt('   21'), inpDecimal(' 70.00'), inpDecimal('   0.00')], elements=[])
                
                """

        tmpData = f'label={self.label!r}, data={self.data!r}, elements={self.elements!r}'
        
        return f'Node({tmpData})'

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Produces a str of the dataline for the Node.
            
            Example:

                >>> from mesh import Node
                >>> node = Node('   21, 70.00,   0.00')
                >>> print(node)
                   21, 70.00,   0.00

                """

        tmpData = self._joinS.join([str(i) for i in self.data])
        
        return f'{tmpData}'

#==================================================================================================================  
class Element(object):
    r"""The Element class stores element information from a single element (i.e. one dataline from a \*ELEMENT keyword block).r"""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, eltype, numNodes=None, datalines=None, label=None, data=None, _lineEnd=None, _npll=None, _joinS=', ', _ParamInInp=False, preserveSpacing=True, useDecimal=True, _checkNumNodes=True, _nl='\n'):
        r"""__init__(eltype, numNodes=None, datalines=None, ', _ParamInInp=False, preserveSpacing=True, useDecimal=True, _checkNumNodes=True, _nl='\n')
           __init__(eltype, numNodes=None, label=None, data=None, _lineEnd=None, _npll=None, _joinS=', ')
        
            Initializes attributes of the Element. 

            In most cases, this will be used by :func:`~inpKeyword.inpKeyword._parseDataElement`. That function will handle
            creating the inputs to this class from the string corresponding to the element dataline. See that function 
            for more details. If you are instancing this class manually, you can omit specifying the private parameters. 
            The default values should be sufficient.

            All parameters are optional except *eltype*, but there are two recommend methods to create an instance of this class. The
            first method is to specify *datalines* and allow :class:`Element` to parse these datalines to populate :attr:`.label`
            and :attr:`.data`. Here is an example of this use case with a CPS4R element:

                >>> from mesh import Element
                >>> datalines = ' 1, 1, 2, 102, 101'
                >>> element = Element(eltype='CPS4R', datalines=datalines)
                >>> element
                Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt(' 1'), inpInt(' 2'), inpInt(' 102'), inpInt(' 101')], eltype='CPS4R', numNodes=4)
                
            The :func:`repr` of an :class:`Element` instance is consistent across the different methods to instantiate
            the class. If you wish to see how the :class:`Element` will be written out, you can use a function to call
            its string representation. For example:
                
                >>> print(element)
                 1, 1, 2, 102, 101
            
            Here's a similar example with an element defined over multiple lines: 

                >>> datalines = [' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,',
                ... '      96,  98,  97,  99, 100']
                >>> Element(eltype='C3D20', datalines=datalines)
                Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt('  16'), inpInt('   4'), inpInt('  24'), inpInt('  57'), inpInt('  13'), inpInt('   1'), inpInt('  32'), inpInt('  66'), inpInt('  92'), inpInt('  91'), inpInt('  90'), inpInt('  89'), inpInt('  93'), inpInt('  94'), inpInt('  95'), inpInt('      96'), inpInt('  98'), inpInt('  97'), inpInt('  99'), inpInt(' 100')], eltype='C3D20', numNodes=20)

            We can also specify *datalines* as a single string with newline characters. Example:

                >>> datalines = ' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,\n     96,  98,  97,  99, 100'
                >>> Element(eltype='C3D20', datalines=datalines)
                Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt('  16'), inpInt('   4'), inpInt('  24'), inpInt('  57'), inpInt('  13'), inpInt('   1'), inpInt('  32'), inpInt('  66'), inpInt('  92'), inpInt('  91'), inpInt('  90'), inpInt('  89'), inpInt('  93'), inpInt('  94'), inpInt('  95'), inpInt('     96'), inpInt('  98'), inpInt('  97'), inpInt('  99'), inpInt(' 100')], eltype='C3D20', numNodes=20)

            If we set *preserveSpacing*, *useDecimal*, and *_ParamInInp* all to False, we gain some performance at the expense 
            of some formatting accuracy. See the difference below:

                >>> datalines = ' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,\n     96,  98,  97,  99, 100'
                >>> print(Element(eltype='C3D20', datalines=datalines, preserveSpacing=False, useDecimal=False))
                1, 16, 4, 24, 57, 13, 1, 32, 66, 92, 91, 90, 89, 93, 94, 95,
                96, 98, 97, 99, 100
                >>> print(Element(eltype='C3D20', datalines=datalines))
                 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,
                     96,  98,  97,  99, 100
            
            The second method is to instead specify *label* and *data* directly. We will need to get the data into a suitable 
            form prior to inserting it into the :class:`Element` instance. You will use this option most often if you are
            creating new elements and do not start with a string containing the entire element definition. Example usage:

                >>> label = 1
                >>> data = [1, 16, 4, 24, 57, 13, 1, 32, 66, 92, 91, 90, 89, 93, 94, 95, 96, 98, 97, 99, 100]
                >>> element = Element(eltype='C3D20', label=label, data=data)
                >>> print(element)
                1, 16, 4, 24, 57, 13, 1, 32, 66, 92, 91, 90, 89, 93, 94, 95,
                96, 98, 97, 99, 100

            If you don't specify the number of nodes to include per each line via *_npll*, there will be 16 items per line.

            We can also specify the strings used to join data items (*_joinS*), and a string to include at the end of 
            each line (*_lineEnd*). This should normally be whitespace characters, but different characters are used
            here for illustrative purposes:

                >>> element = Element(eltype='C3D20', label=label, data=data, _lineEnd=['++', None], _joinS = ',_')
                >>> print(element)
                1,_16,_4,_24,_57,_13,_1,_32,_66,_92,_91,_90,_89,_93,_94,_95,++
                96,_98,_97,_99,_100

            Args:
                eltype (str): The element type name. Should be a valid Abaqus element type name, or the name of a user-element.
                numNodes (int): The number of nodes the element needs. If not specified, this will be retrieved from 
                    :attr:`_elementTypeDictionary[eltype] <config._elementTypeDictionary>`. This should only be specified if
                    an element type is not in that dictionary, which will mainly be for user or substructure elements.
                datalines (list, str): A list of strings representing the datalines for the :class:`Element`. This can also be a 
                    string representing the entirety of the data for the element, with new line characters if the definition is
                    spread across multiple lines. Defaults to None.
                label (int): The label for the element. Defaults to None.
                data (list): The data for the element. This will be a parsed dataline. The format should be
                    [:class:`int`, :class:`int`, ...].
                _lineEnd (str, list): Holds any additional whitespace characters to include at the end of the dataline. Mainly used
                    to exactly reproduce the string representation of the keyword block. Defaults to None. If the data must be
                    printed across multiple lines, _lineEnd will be expanded to a list if necessary, with each item in the list
                    corresponding to the old value of :attr:`_lineEnd`. If a _lineEnd item is None, nothing will be added to the end
                    of that line. If a _lineEnd item is a string, the _lineEnd item will follow a comma on the effected line.
                _npll (list): Nodes Per Line List, controls how many nodes should be printed on each line when converting
                    the Element to a string. The default value of None will cause the maximum number of nodes to be
                    printed on each line (up to 15 for line 0, and up to 16 for all subsequent lines).
                _joinS (str): The string used to join the data items together when creating strings of the :class:`Element` instance. 
                    Defaults to None, which will use ', '. If *preserveSpacing* is True and *datalines* is not None, ',' will be used.
                _ParamInInp (bool): Indicates if \*PARAMETER is in the input file, which would mean that the dataline items 
                    could be strings instead of exclusively integers. Defaults to False.
                preserveSpacing (bool): If True, the exact spacing of all items will be preserved by using :class:`~inpInt.inpInt`.
                    In most cases when creating new :class:`.Element` instances, you will want to use the same value that the rest
                    of the input file was parsed with. Defaults to True. 
                useDecimal (bool): If True, any floating point numbers will be parsed as :class:`~decimal.Decimal` or :class:`~inpDecimal.inpDecimal`.
                    In most cases when creating new :class:`.Element` instances, you will want to use the same value that the rest
                    of the input file was parsed with. Defaults to True.
                _checkNumNodes (bool): If True, the number of nodes parsed from *datalines* will be checked against :attr:`.numNodes`.
                    If the :class:`.Element` has the incorrect number of nodes, an :exc:`~inpRWErrors.ElementIncorrectNodeNumError`
                    will be raised. Defaults to True.
                _nl (str): Used to split *datalines* if it is a string. Defaults to '\n'. """

        self.eltype = eltype #: :str: Indicates the element type name. Should be a valid Abaqus element type.
        self._checknumNodes = _checkNumNodes #: :bool: If True, the number of nodes parsed from datalines will be checked against the number in :attr:`.numNodes`. Defaults to True.
        self.numNodes = numNodes #: :int: The number of nodes needed for the Element. Can be specified by the user, or will be retrieved from :attr:`_elementTypeDictionary[eltype] <config._elementTypeDictionary>`.
        if numNodes == None and eltype != None:
            try:
                self.numNodes = _elementTypeDictionary[eltype].numNodes
            except KeyError:
                self.numNodes = numNodes
                self._checknumNodes = False
                print(f'Warning! Element type {eltype} is not well understood. The element definition will not be checked for the proper number of nodes.')
            except AttributeError:
                self.numNodes = _elementTypeDictionary[eltype].numNodesSet
        self._lineEnd = _lineEnd #: :str: Holds any additional whitespace characters to include at the end of the dataline.
        if _npll == None:
            self._npll = []
        else:
            self._npll = _npll #: :list: Nodes Per Line List, controls how many nodes will be printed on each line when converting :class:`Element` to a string.
        self._joinS = _joinS #: :str: The string used to join the data items together when creating strings of the :class:`Element` instance. 
        self._ParamInInp = _ParamInInp #: :bool: Indicates if \*PARAMETER is in the input file. If True, data items could be references to \*PARAMETER functions, and the datalines might be strings, so the :func:'~eval2.eval2' function must be used when parsing data items instead of assuming they must be integers. Defaults to False.
        self.preserveSpacing = preserveSpacing #: :bool: If True, the exact spacing of all items will be preserved by using :class:`~inpInt.inpInt` instead of :class:`int`. Defaults to True.
        self.useDecimal = useDecimal #: :bool: If True, any floating point numbers will be parsed as :class:`~decimal.Decimal` or :class:`~inpDecimal.inpDecimal`. Defaults to True.
        self._nl = _nl #: :str: Used to split *datalines* if it is a string. Defaults to '\n', which should be correct for most cases.

        if datalines != None:
            if self.preserveSpacing:
                self.useDecimal = True 
                self._joinS = ','
            self._parseDataLines(datalines)
        else:
            self.label = label #: :int: The element label.
            self.data = data #: :list: The data for the element. This will be a parsed dataline. The format should be [:class:`int`, ...].
            if self.data:
                if self._npll == []:
                    self._npll = [len(i) for i in makeDataList(self.data)] 
                    self._npll[0] -= 1
                if not isinstance(self._lineEnd, list):
                    self._lineEnd = [self._lineEnd] * len(self._npll)
                    if self._lineEnd[0] == None and len(self._lineEnd) > 1:
                        self._lineEnd[0] = ''

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def checkNumberNodes(self):
        r"""checkNumberNodes() 
        
            This function will check if the number of nodes in :attr:`data` matches that specified in :attr:`numNodes`.
            
            It raises an :exc:`~inpRWErrors.ElementIncorrectNodeNumError` if the number of nodes does not match the
            element type requirements. Otherwise, it does nothing. This function will be called by :func:`_parseDataLines`
            if :attr:`_checknumNodes` is True (thus, it will be called if :class:`Element` is initialized with *datalines*
            and the default settings). It should be called manually if the :class:`Element` is populated in another manner.

            Example:

                >>> from mesh import Element
                >>> element = Element(eltype='CPS4R', label=1, data=[1, 1, 2, 102, 101, 103])
                >>> element.checkNumberNodes()
                Traceback (most recent call last):
                    ...
                inpRWErrors.ElementIncorrectNodeNumError: ERROR! An element of type CPS4R must have 4 nodes.
            
            Raises:
                ElementIncorrectNodeNumError"""

        numNodes = self.numNodes
        numNodes_internal = len(self.data) - 1
        if isinstance(numNodes, int):
            if numNodes_internal != numNodes:
                raise ElementIncorrectNodeNumError(self.eltype, numNodes)
        elif isinstance(numNodes, set):
            if numNodes_internal not in numNodes:
                raise ElementIncorrectNodeNumError(self.eltype, numNodes)
        elif isinstance(numNodes, list):
            if numNodes_internal != numNodes[0]:
                raise ElementIncorrectNodeNumError(self.eltype, numNodes)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataLines(self, datalines):
        r"""_parseDataLines(datalines)
        
            Populates the :class:`Element` instance by parsing the strings in *datalines*.

            This function will also call :func:`checkNumberNodes` if :attr:`_checknumNodes` = True. It is called automatically
            if :class:`Element` is instantiated with the *datalines* argument.

            Example usage:

                >>> from mesh import Element
                >>> element = Element(eltype='CPS4R')
                >>> element._parseDataLines('1, 1, 2, 102, 101')
                >>> print(element)
                1,  1,  2,  102,  101
            
            Args:
                datalines (list): A list of strings containing the information for the entire dataline."""
        
        datalines = self._processDataLinesInput(datalines)
        self._parseDataLine(datalines.pop(0))
        if len(datalines) > 0:
            while True:
                try:
                    self._parseDataLine(datalines.pop(0), con=True)
                except IndexError:
                    break
        if self._checknumNodes:
            self.checkNumberNodes()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataLine(self, dataline, con=False):
        r"""_parseDataLine(dataline, con=False)
        
            Parses an individual \*ELEMENT dataline. Meant to be used by :func:`_parseDataLines`.

            Example usage:

                >>> from mesh import Element
                >>> dataline1 = ' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,'
                >>> dataline2 = '     96,  98,  97,  99, 100'
                >>> element = Element(eltype='C3D20')
                >>> element._parseDataLine(dataline1)
                >>> element
                Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt('  16'), inpInt('   4'), inpInt('  24'), inpInt('  57'), inpInt('  13'), inpInt('   1'), inpInt('  32'), inpInt('  66'), inpInt('  92'), inpInt('  91'), inpInt('  90'), inpInt('  89'), inpInt('  93'), inpInt('  94'), inpInt('  95')], eltype='C3D20', numNodes=20)
                >>> element._parseDataLine(dataline2, con=True)
                >>> element
                Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt('  16'), inpInt('   4'), inpInt('  24'), inpInt('  57'), inpInt('  13'), inpInt('   1'), inpInt('  32'), inpInt('  66'), inpInt('  92'), inpInt('  91'), inpInt('  90'), inpInt('  89'), inpInt('  93'), inpInt('  94'), inpInt('  95'), inpInt('     96'), inpInt('  98'), inpInt('  97'), inpInt('  99'), inpInt(' 100')], eltype='C3D20', numNodes=20)
            
            Args:
                dataline (str): The string containing the information for one line of data. 
                con (bool): If True, this function will treat *dataline* as a continuation of the previous dataline 
                    (i.e. all items represent node labels, instead of an element label and then node labels). Defaults
                    to False."""

        ps = self.preserveSpacing
        ud = self.useDecimal

        def case1(ls):
            r"""Parses the information in ls as integers. Used when preserveSpacing and useDecimal are both False."""

            key = int(ls[0])
            value = [int(i) for i in ls]
            return key, value

        def case2(ls):
            r"""Parses the information in ls using eval2. Used when one or both of preserveSpacing and useDecimal are True."""

            key = eval2(ls[0], t=int, ps=ps)
            value = [eval2(i, t=int, ps=ps, useDecimal=ud) for i in ls]
            return key, value

        def case3(ls):
            r"""Parses the information in ls as integers. This will handle subsequent datalines of an element definition, where every item is 
            a node label. Used when preserveSpacing and useDecimal are both False."""

            value = [int(i) for i in ls]
            return value

        def case4(ls):
            r"""Parses the information in ls as integers. This will handle subsequent datalines of an element definition, where every item is 
            a node label. Used when one or both of preserveSpacing and useDecimal are True."""

            value = [eval2(i, t=int, ps=ps, useDecimal=ud) for i in ls]
            return value

        def findLineEnd(ls):
            r"""Tracks any whitespace characters at the end of the dataline."""

            endstr = ls[-1]
            if len(endstr) > 0 and endstr.isspace():
                _lineEnd = intern(ls.pop(-1))
            elif len(endstr) == 0:
                _lineEnd = intern(ls.pop(-1))
            else:
                _lineEnd = None
            return ls, _lineEnd

        if not self._ParamInInp and not ps and not ud:
            op1 = case1
            op2 = case3
        else:
            op1 = case2
            op2 = case4

        ls = dataline.split(',')
        ls, _lineEnd = findLineEnd(ls)
        if not con:
            key, value = op1(ls)
            self.label = key
            self.data = value
            self._lineEnd = [_lineEnd]
            if self._npll == []:
                self._npll.append(len(ls) - 1)
        else:
            value = op2(ls)
            self.data += value
            self._npll.append(len(ls))
            self._lineEnd.append(_lineEnd)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _processDataLinesInput(self, datalines):
        r"""_processDataLinesInput(datalines)
        
            If *datalines* is a string, split *datalines* on :attr:`_nl`, which will convert *datalines* to a string.

            This is called automatically by :func:`_parseDataLines`, so the user will likely never need to call it directly.

            Example usage:

                >>> from mesh import Element
                >>> element = Element(eltype='CPS4R')
                >>> element._processDataLinesInput('  1, 1, 2, 102, 101')
                ['  1, 1, 2, 102, 101']
                >>> element._processDataLinesInput(' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,\n     96,  98,  97,  99, 100')
                [' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,', '     96,  98,  97,  99, 100']

            Args:
                datalines (str, list): A string or list of strings. If a string, will be converted to a list by 
                    splitting on :attr:`_nl`.

            Returns:
                list
        """

        nl = self._nl
        if isinstance(datalines, str):
            datalines = datalines.split(nl)
        return datalines

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setConnectedNodes(self, nd):
        r"""setConnectedNodes(nd)
       
            This function will find each node in *nd* corresponding to the node labels in :attr:`~Element.data` and 
            append :attr:`~Element.label` to the :attr:`~Node.elements`.
            
            Args:
                nd (TotalMesh): The TotalMesh instance containing the nodes for the input file."""
        
        label = self.label
        for nodeLabel in self.data[1:]:
            node = nd.get(nodeLabel)
            if node == None:
                nd[nodeLabel] = Node(label=nodeLabel, elements=[label])
            else:
                nd[nodeLabel].elements.append(label)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        r"""__repr__()
            
            Produces a repr of the dataline for the Element.
            
            Example usage:

                >>> from mesh import Element
                >>> Element(eltype='CPS4R', datalines=' 1, 1, 2, 102, 101')
                Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt(' 1'), inpInt(' 2'), inpInt(' 102'), inpInt(' 101')], eltype='CPS4R', numNodes=4)

            Returns:
                string
            
            """

        tmpData = f'label={self.label!r}, data={self.data!r}, eltype={self.eltype!r}, numNodes={self.numNodes!r}'
        
        return f'Element({tmpData})'

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Produces a str of the dataline for the Element.
            
            Example usage:

                >>> from mesh import Element
                >>> print(Element(eltype='CPS4R', datalines='1, 1, 2, 102, 101'))
                1, 1, 2, 102, 101
            
            Returns:
                string
            """

        leadchar = '\n'
        _joinS = self._joinS

        output = []
        prev = 0
        for ind,c in enumerate(self._npll):
            _lineEnd = self._lineEnd[ind]
            if _lineEnd != None:
                _lineEnd = f',{_lineEnd}'
            else:
                _lineEnd = ''
            if prev:
                output.append(f'{leadchar}{_joinS.join([str(i) for i in self.data[prev:prev+c]])}{_lineEnd}')
                prev += c
            else:
                output.append(f'{_joinS.join([str(i) for i in self.data[prev:c+1]])}{_lineEnd}')
                prev += c + 1
        tmpData = ''.join(output)
        
        return f'{tmpData}'

#==================================================================================================================  
class Mesh(csid):
    r"""This class is a :class:`csid` used to store the data from a node :term:`keyword block`. """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, data=None):
        r"""__init__(data=None)
        
            Initializes the class. In most cases, users should not directly instantiate this class. Rather, they should
            create a \*NODE :class:`~inpKeyword.inpKeyword` instance and allow that keyword block to handle the logistics.

            Example usage:

                >>> from mesh import Node, Mesh
                >>> node1 = Node('   1 ,  0.00,   0.00')
                >>> node2 = Node('   21, 70.00,   0.00')
                >>> Mesh([[i.label, i] for i in [node1, node2]])
                csid(inpInt('   1 '): Node(label=inpInt('   1 '), data=[inpInt('   1 '), inpDecimal('  0.00'), inpDecimal('   0.00')], elements=[]), inpInt('   21'): Node(label=inpInt('   21'), data=[inpInt('   21'), inpDecimal(' 70.00'), inpDecimal('   0.00')], elements=[]))
            
            Args:
                data: *data* should be a format that can generate a :class:`dictionary <dict>`. Defaults to None, which
                    will produce a blank object."""

        if data != None:
            super().__init__(data)
        else:
            super().__init__()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        r"""__repr__()
            
            Uses the default __repr__ method from :class:`dict`.
            
            Example usage:

                >>> from mesh import Node, Mesh
                >>> node1 = Node('   1 ,  0.00,   0.00')
                >>> node2 = Node('   21, 70.00,   0.00')
                >>> Mesh([[i.label, i] for i in [node1, node2]])
                csid(inpInt('   1 '): Node(label=inpInt('   1 '), data=[inpInt('   1 '), inpDecimal('  0.00'), inpDecimal('   0.00')], elements=[]), inpInt('   21'): Node(label=inpInt('   21'), data=[inpInt('   21'), inpDecimal(' 70.00'), inpDecimal('   0.00')], elements=[]))
                
        """

        return super().__repr__()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Uses the default __str__ method from :class:`dict`.
            
            Example usage:

                >>> from mesh import Node, Mesh
                >>> node1 = Node('   1 ,  0.00,   0.00')
                >>> node2 = Node('   21, 70.00,   0.00')
                >>> print(Mesh([[i.label, i] for i in [node1, node2]]))
                {
                   1 :    1 ,  0.00,   0.00
                   21:    21, 70.00,   0.00
                }

            """
        #for key, value in self.items():
        s = (f'{key}: {value}' for key, value in self.items())
        data_string = '\n'.join(s)
        out_str = f"\u007b\n{data_string}\n\u007d"

        return out_str

#==================================================================================================================  
class MeshElement(Mesh):
    r""":class:`MeshElement` is identical to :class:`Mesh`, except that it checks to make sure that every item added to
    it has the same element type."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, eltype, data=None):
        r"""__init__(eltype, data=None) 
        
            Initializes the class. In most cases, users should not directly instantiate this class. Rather, they should
            create a \*ELEMENT :class:`~inpKeyword.inpKeyword` instance and allow that keyword block to handle the logistics.
            
            Example usage:

                >>> from mesh import Element, MeshElement
                >>> element1 = Element(eltype='C3D20', datalines=' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,\n     96,  98,  97,  99, 100')
                >>> element2 = Element(eltype='C3D20', datalines=' 2,  15,  16,  57,  58,  14,  13,  66,  65, 103,  89, 102, 101, 104,  96, 105,\n    106, 107,  98, 100, 108')
                >>> mesh = MeshElement(eltype='C3D20', data=[[i.label, i] for i in [element1, element2]])
                >>> mesh
                csid(inpInt(' 1'): Element(label=inpInt(' 1'), data=[inpInt(' 1'), inpInt('  16'), inpInt('   4'), inpInt('  24'), inpInt('  57'), inpInt('  13'), inpInt('   1'), inpInt('  32'), inpInt('  66'), inpInt('  92'), inpInt('  91'), inpInt('  90'), inpInt('  89'), inpInt('  93'), inpInt('  94'), inpInt('  95'), inpInt('     96'), inpInt('  98'), inpInt('  97'), inpInt('  99'), inpInt(' 100')], eltype='C3D20', numNodes=20), inpInt(' 2'): Element(label=inpInt(' 2'), data=[inpInt(' 2'), inpInt('  15'), inpInt('  16'), inpInt('  57'), inpInt('  58'), inpInt('  14'), inpInt('  13'), inpInt('  66'), inpInt('  65'), inpInt(' 103'), inpInt('  89'), inpInt(' 102'), inpInt(' 101'), inpInt(' 104'), inpInt('  96'), inpInt(' 105'), inpInt('    106'), inpInt(' 107'), inpInt('  98'), inpInt(' 100'), inpInt(' 108')], eltype='C3D20', numNodes=20))

            Args:
                eltype (str): The string representing the Abaqus element type name.
                data: *data* should be a format that can generate a :class:`dictionary <dict>`. Defaults to None, which
                    will produce a blank object."""

        self.eltype = eltype #: :str: A string representing the element type name
        super().__init__(data)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __setitem__(self, label, element):
        r"""__setitem__(label, element)
        
            Checks if *element*.eltype matches :attr:`eltype`. If it does, set MeshElement[label] = element, else raise
            :exc:`~inpRWErrors.ElementTypeMismatchError`.

            Correct usage, the :attr:`eltype` of the :class:`Element` matches that of the :class:`MeshElement`:

                >>> from mesh import Element, MeshElement
                >>> element1 = Element(eltype='C3D20', datalines=' 1,  16,   4,  24,  57,  13,   1,  32,  66,  92,  91,  90,  89,  93,  94,  95,\n     96,  98,  97,  99, 100')
                >>> mesh = MeshElement(eltype='C3D20', data=[[element1.label, element1]])
                
            The class raises a :exc:`~inpRWErrors.ElementTypeMismatchError` if we try to add an element with a different
            eltype:

                >>> element2 = Element(eltype='CPS4R', datalines='1, 1, 2, 102, 101')
                >>> mesh[element2.label] = element2
                Traceback (most recent call last):
                    ...
                inpRWErrors.ElementTypeMismatchError: ERROR! An element of type CPS4R cannot be added to a MeshElement with eltype C3D20
            
            Args:
                label (int): The element label.
                element (Element): The :class:`Element` to add to the :class:`MeshElement`.
                
            Raises:
                ElementTypeMismatchError"""

        if element.eltype != self.eltype:
            raise ElementTypeMismatchError(element.eltype, self.eltype)
        else:
            super().__setitem__(label, element)
        

#==================================================================================================================  
class TotalMesh(csid):
    r""":class:`TotalMesh` is a parent class, and not meant to be instantiated directly. Users should instead work with
    one of the sub-classes, which are :class:`TotalNodeMesh` and :class:`TotalElementMesh`. 

    Users should not need to created instances of this class or the child classes directly. In most cases, they can rely
    on :class:`~inpKeywordSequence.inpKeywordSequence` to create and manage these instances.
    
    Every :class:`~inpKeywordSequence` contains attributes :attr:`~inpKeywordSequence.inpKeywordSequence._nd`
    and :attr:`~inpKeywordSequence.inpKeywordSequence._ed`, which are :class:`TotalNodeMesh` and :class:`TotalElementMesh`
    instances, respectively. They provide a convenient method to access all the mesh and element data in an input file, 
    without needing to navigate through multiple keyword blocks. These instances of the top-level 
    :class:`~inpKeywordSequence.inpKeywordSequence` (:attr:`~inpRW.inpRW.keywords`) will be mapped to 
    :attr:`~inpRW.inpRW.nd` and :attr:`~inpRW.inpRW.ed`.
   
    Any operations on items in this class will be propagated back to the data of the appropriate node and element
    :class:`~inpKeyword.inpKeyword` blocks.
    
    Items should not be directly deleted from a :class:`TotalMesh`, in most cases. The user should instead use a 
    combination of :func:`~inpRW._inpFind.Find.findItemReferences` along with :func:`~inpRW._inpMod.Mod.deleteItemReferences` 
    to delete these entities, as it will also find and delete all references to those entities throughout the input file.
    
    A function for replacing item references still needs to be written.
    
    Items should not be added to this class directly. Rather, they should be added to :attr:`~inpKeyword.inpKeyword.data` of
    a \*NODE or \*ELEMENT keyword block and added to this class via :func:`~inpRW.inpRW.updateInp`."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, _data=None):
        r"""__init__(_data=None)
       
            A :class:`TotalMesh` instance holds all the nodes or elements for the children of an :class:`~inpKeywordSequence.inpKeywordSequence`.
            This class is meant to be initialized with *_data* = None. Data should be added to it via :func:`~TotalMesh.update` 
            using a :class:`Mesh` instance.

            Args:
                _data: Can be any construct used to populate a :class:`dict`. Should not be used in most cases,
                    as the data should instead be populated through a :class:`Mesh`, and then calling :func:`~TotalMesh.update`
                    on that :class:`Mesh` instance."""

        if _data != None:
            super().__init__(_data)
        else:
            super().__init__()
        self.subMeshes = [] #: :list: Will hold a shared memory reference to every :class:`Mesh` or :class:`TotalMesh` instance which is a child of this object. This is thus a link to the :attr:`~inpKeyword.inpKeyword.data` attributes of the appropriate keyword blocks.

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def removeEmptySubMeshes(self):
        r"""removeEmptySubMeshes()
       
            Deletes any :attr:`subMeshes` which are now empty. This will also delete the :class:`Mesh` instance."""

        emptySubMeshes = [ind for ind,i in enumerate(self.subMeshes) if len(i) == 0 and isinstance(i, Mesh)]
        emptySubMeshes.sort()
        emptySubMeshes.reverse()
        for ind in emptySubMeshes:
            del self.subMeshes[ind]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def renameKeys(self, mapping):
        r"""renameKeys(mapping)
       
            Renames all keys in the :class:`TotalMesh` instance (d) as specified by mapping. 
            
            d and each :attr:`subMesh <subMeshes>` will be cleared and repopulated with the renamed keys to preserve
            the original order. Thus, this can be an expensive operation, so try to provide the entirety of the information
            to rename and call this function only once."""

        self.clear()
        for ind, m in enumerate(self.subMeshes):
            newData = [(mapping[i], m[i]) if i in mapping else (i, m[i]) for i in m.keys()]
            self.subMeshes[ind].clear()
            self.subMeshes[ind].update(newData)
            self.update(self.subMeshes[ind])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def update(self, other):
        r"""update(other)
       
            Adds the data from *other* to the :class:`TotalMesh` instance (d), and tracks *other* in :attr:`subMeshes`.
            
            Args:
                other (Mesh, TotalMesh): A :class:`Mesh` or :class:`TotalMesh` instance whose items will be included
                    in """
        
        if other:
            if not isinstance(other, (Mesh, TotalMesh)):
                print('Error. Only mesh.Mesh or TotalMesh instances should be added to mesh.TotalMesh.')
            else:
                super().update(other)
        if other not in self.subMeshes:
            self.subMeshes.append(other)
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __delitem__(self, key):
        r"""__delitem__(key)
        
            Deletes key and value in self and in the subMesh.
            
            Args:
                key: A valid hashable key. Should be an integer in most cases, as the node and element labels will be integers."""

        super().__delitem__(key)
        for m in self.subMeshes:
            if key in m:
                del m[key]
   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        r"""__repr__()
            
            Uses the default __repr__ method from :class:`dict`."""

        return super().__repr__()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __setitem__(self):
        r"""__setitem__()
            
            Items should not be added to the :class:`TotalMesh` instance. Add them instead to the appropriate
            :class:`Mesh` instance and then :func:`~TotalMesh.update` :class:`TotalMesh` with :class:`Mesh`."""
            
        print('Error! Items should not be added directly to a TotalMesh instance. Instead add them to the proper Mesh instance, and then update TotalMesh with Mesh.')
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Uses the default __str__ method from :class:`dict`."""

        return super().__str__()

#==================================================================================================================  
class TotalNodeMesh(TotalMesh):
    r"""A :class:`TotalNodeMesh` enhances :class:`TotalMesh` with some additional functions specific to working with
        Abaqus nodes."""


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setNodesConnectedElements(self, nd):
        r"""setNodesConnectedElements(nd)
        
            This function will set the :attr:`~mesh.Node.elements` attribute of each node in the :class:`~mesh.TotalMesh` 
            instance for each node found in *nd*.
            
            It should be passed a :class:`~mesh.Mesh` instance which maps the node labels to the elements connected to those nodes.
            In most cases, this special :class:`~mesh.Mesh` instance should be created by :func:`~inpKeyword.inpKeyword._parseDataElement`
            and it will be available as the :attr:`~inpKeyword.inpKeyword._nd` attribute of a \*ELEMENT keyword block and
            as the 'nd_ed' entry of :attr:`~inpKeyword.inpKeyword._inpItemsToUpdate`.
            
            Args:
                nd (Mesh): The :class:`~mesh.Mesh` instance which contains the node and element label mapping."""

        for k,v in nd.items():
            try:
                self[k].elements.extend(v.elements)
            except KeyError:
                pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateNodesConnectedElements(self, ed):
        r"""updateNodesConnectedElements(ed)
       
            Calls :func:`~Node.updateElements` on all :class:`Node` instances.
            
            Args:
                ed (TotalMesh): This should be the :class:`TotalMesh` instance holding the elements.
                
            Returns:
                dict: A dictionary with the node labels as the key, and the return value of :func:`~Node.updateElements`
                as the value."""

        updateD = {}
        for nlabel in self.keys():
            updateD[nlabel] = self[nlabel].updateElements(ed)
        return updateD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        r"""__repr__()
            
            Uses the default __repr__ method from :class:`dict`."""

        return super().__repr__()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Uses the default __str__ method from :class:`dict`."""

        return super().__str__()

#==================================================================================================================  
class TotalElementMesh(TotalMesh):
    r"""A :class:`TotalElementMesh` is merely a subclass of :class:`TotalMesh` with no additional behavior."""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        r"""__repr__()
            
            Uses the default __repr__ method from :class:`dict`."""

        return super().__repr__()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        r"""__str__()
            
            Uses the default __str__ method from :class:`dict`."""

        return super().__str__()