#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module implements the :class:`inpKeyword` class, which will parse and store information from an Abaqus keyword
block. The module also contains a couple functions outside the class, but which are closely associated with the class."""

# cspell:includeRegExp comments

from .csid import csid
from .config_re import *
from .mesh import Node, Element, Mesh, MeshElement
from .misc_functions import cfc, rsl, flatten
from .eval2 import eval2
from .repr2 import repr2
import traceback
from os import path as ospath
from sys import platform as sysplatform
from .config import (_openEncoding, _dataKWs, _elementTypeDictionary)
from .inpRWErrors import ElementIncorrectNodeNumError

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createParamDictFromString(parameterString, ps=True, useDecimal=True):
    r"""createParamDictFromString(parameterString, ps=True, useDecimal=True)
        
        This function will create a :class:`csid` from a string representing a keyword block's parameters.

        Use :func:`~inpKeyword.inpKeyword.formatParameterOutput` to write a string from the parameter dictionary.        
        
        Args:
            parameterString (str): A string that contains the parameter information for a keyword block. This should
              include neither the keyword name nor the comma following the keyword name.
            ps (bool): Short for Preserve Spaces. If True, :class:`.inpString`, :class:`.inpDecimal`, and :class:`.inpInt` 
              classes will be used to preserve the exact spacing of the parent string when the items are parsed. 
              Defaults to True.
            useDecimal (bool): If True, all numbers that would evaluate to :class:`float` will instead be 
              :class:`.inpDecimal` or :class:`~decimal.Decimal`. Defaults to True.
            
        Returns:
            csid: A case and space insensitive dictionary containing the parameter names (keys) and values.
            
        Examples:
            This shows the default behavior of the function.
                
                >>> from inpKeyword import createParamDictFromString
                >>> createParamDictFromString("change number=1000, pole")
                csid(csiKeyString('change number'): inpInt('1000'), csiKeyString(' pole'): '')

            If *ps* and *useDecimal* are both set to False, the items in *parameterString* will be parsed as :class:`str`, 
            :class:`int`, and :class:`float` instead of :class:`inpString`, :class:`inpInt`, and :class:`inpDecimal`:

                >>> createParamDictFromString("change number=1000, pole", ps=False, useDecimal=False)
                csid(csiKeyString('change number'): 1000, csiKeyString(' pole'): '')
                
    """
    
    if ps == True:
        useDecimal = True

    quotes = re2.findall(parameterString)
    if len(quotes) > 0:
        pstmp = parameterString
        for i in quotes:
            pstmp = pstmp.replace(i, "%s")
        z = [i.replace('%s', quotes.pop(0)) if '%s' in i else i for i in pstmp.split(',')]
    else:
        z = parameterString.split(',')
    #temp = [[eval2(k[0], ps=ps), eval2(k[1], ps=ps)] if len((k := j.split('=',1)))>1 else [eval2(k[0], ps=self.preserveSpacing), '']  for j in z] #Python 3.8+ only
    parameters = csid()
    for j in z:
        k = j.split('=',1)
        if len(k) > 1:
            temp = csid([[eval2(k[0], ps=ps, useDecimal=useDecimal), eval2(k[1], ps=ps, useDecimal=useDecimal)]])
        else:
           temp = csid([[eval2(k[0], ps=ps, useDecimal=useDecimal), '']])
        parameters.update(temp)
    return parameters

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def findElementNodeNum(t, lines):
    r"""findElementNodeNum(t, lines)

        Returns the number of nodes needed to define an element in the given keyword block.

        The element type is determined from :attr:`block.parameter['type'] <.inpKeyword.parameter>`. The number
        of nodes is then retrieved from :attr:`inpKeyword._elementTypeDictionary <config._elementTypeDictionary>`, 
        if it is defined, or it is estimated from the element data.

        For variable node elements, this function looks up the valid number of nodes to define the element. Then, it keeps
        reading data lines until it finds a line which does not end with a comma. If the number of nodes is in the set of
        valid node numbers for the element type (:attr:`~elType.elType.numNodesSet`), this function returns an integer. 
        If the number of nodes is not in the set, an :exc:`~inpRWErrors.ElementIncorrectNodeNumError` is raised.

        For undefined element type labels, this function will read datalines until it finds one which does not end with a comma.
        It will return the number of nodes it thinks the element has. For accurate results with user or sub-structure 
        elements, the user should add an entry to :attr:`~config._elementTypeDictionary` before calling :func:`~inpRW.inpRW.parse`.

        This function will only be called once per \*ELEMENT keyword block, so it assumes all elements in the keyword block
        are defined with the same number of nodes.
        
        Returns:
            int: The number of nodes required for the element type.
            None: If the keyword block is not an ELEMENT keyword block.

        Raises:
            inpRWErrors.ElementIncorrectNodeNumError
            
        Examples:
            If the element type is defined in :attr:`~inpKeyword._elementTypeDictionary <config._elementTypeDictionary>`, this function simply
            looks up the appropriate entry:

                >>> from inpKeyword import findElementNodeNum
                >>> lines = ['1, 22, 2, 10, 3, 45, 25, 33, 26',
                ...          '2, 5, 4, 15, 23, 28, 27, 38, 46']
                >>> findElementNodeNum('C3D8R', lines)
                8

            If the element can have a variable number of nodes, this function will read from *lines* until it finds a line which
            ends without a comma. It then verifies that the number of nodes is found in :attr:`~elType.elType.numNodesSet` of
            the element type entry:

                >>> lines = ['101,101,102,103,104,105,106,107,108,',
                ...          '109,110,111,112,113,114,115,'
                ...          '201,202,203',
                ...          '**',
                ...          '102,103,102,117,106,105,116,108,122,',
                ...          '118,111,121,119,115,114,120,',
                ...          '202,204,205']
                >>> findElementNodeNum('c3d15v', lines)
                18

            If the datalines are not formatted properly, this function will not be able to find the proper number of
            nodes and will raise an :exc:`~inpRWErrors.ElementIncorrectNodeNumError`:

                >>> lines = ['101,101,102,103,104,105,106,107,108,',
                ...          '109,110,111,112,113,114,115,'
                ...          '201,202,203,',
                ...          '**',
                ...          '102,103,102,117,106,105,116,108,122,',
                ...          '118,111,121,119,115,114,120,',
                ...          '202,204,205']
                >>> findElementNodeNum('c3d15v', lines)
                Traceback (most recent call last):
                    ...
                inpRWErrors.ElementIncorrectNodeNumError: ERROR! An element of type c3d15v must have between 15 and 18 nodes.

            For undefined element types (such as sub-structure or user elements), this function will keep reading datalines until
            one which does not end with a comma is encountered:

                >>> lines = ['1, 1451,1452,1453,1454,1455,1456,1457,1483,1484,1485,1486,1487,',
                ...          '1488,1489,1596,1597,1629,1630,1652,1653,1681,1682,1704,1705,',
                ...          '1735,1736,1758,1759,2380,2381,2382,2383,2384,2385,2386,2412,',
                ...          '2413,2414,2415,2416,2417,2418,2525,2526,2558,2559,2581,2582,',
                ...          '2610,2611,2633,2634,2664,2665,2687,2688,7507,7508,7530,7531,',
                ...          '7551,7552,7574,7575,7973,7974,7996,7997,8017,8018,8040,8041']
                >>> findElementNodeNum('Z1', lines)
                 WARNING! Element type 'Z1' is not well documented. It looks like this element type needs 72 nodes to define the element. 
                    If this is incorrect, please specify the 'numNodes' attribute by running inp._elementTypeDictionary['Z1'] = elType(name='Z1', numNodes=NUM)
                72
            
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _findNumNodes(lines):
        
        tmp = ''
        for line in lines:
            if not cfc(line):
                # Fixed: Use raw string for regex pattern (Python 3.12+ compatibility)
                if re.search(r',\s*(?!\S)\Z', line):
                    tmp += line
                else:
                    tmp += line
                    break
        elementNodeNum = tmp.count(',')
        return elementNodeNum
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    try:
        elementNodeNum = _elementTypeDictionary[t].numNodes
    except KeyError:
        elementNodeNum = _findNumNodes(lines)
        if elementNodeNum != 0:
            print(f" WARNING! Element type '{t}' is not well documented. It looks like this element type needs {elementNodeNum} nodes to define the element. \n    If this is incorrect, please specify the 'numNodes' attribute by running inp._elementTypeDictionary['{t}'] = elType(name='{t}', numNodes=NUM)")
        else:
            print(f" ERROR! Could not find the proper number of nodes for element type '{t}'. \n    Please specify the 'numNodes' attribute by running inp._elementTypeDictionary['{t}'] = elType(name='{t}', numNodes=NUM) before parsing the input file again.")
            raise ElementIncorrectNodeNumError(elementType=t, nodeNum=elementNodeNum)
    except AttributeError: #For variable node elements
        elementNodeNum = _elementTypeDictionary[t].numNodesSet
        elementNodeNum_tmp = _findNumNodes(lines)
        if not elementNodeNum_tmp in elementNodeNum:
            #print(f" ERROR! Could not find the proper number of nodes for element type '{t}'. Found {elementNodeNum_tmp} nodes. \n    This is most likely caused by a syntax error in the element definition.")
            raise ElementIncorrectNodeNumError(elementType=t, nodeNum=elementNodeNum)
        else:
            elementNodeNum = elementNodeNum_tmp
    return elementNodeNum

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def formatStringFromParamDict(parameters, joinPS=',', rmtrailing0=False):
    r"""formatStringFromParamDict(parameters, joinPS=',', rmtrailing0=False)
    
        Creates a string from the Abaqus keyword :attr:`~inpKeyword.parameter` in valid keyword line formatting. 
        
        The dictionary should be a one-level structure. The output will be of the form key=item. If item is '',
        then only key will appear in the output. key-item pairs are separated with joinPS, which defaults to ','.

        Args:
            parameters (dict): The dictionary type whose contents should be formatted. Should be :attr:`~inpKeyword.parameter` 
                or a portion of it.
            joinPS (str): The string used to join parameter key-item pairs. Defaults to ','.
            rmtrailing0 (bool): If True, trailing 0s in number types will be omitted. Defaults to False.
            
        Returns:
            str
            
        Examples:
            
            This shows the creation of a parameter dictionary, modifying one of the values in the dictionary, and
            creating a string from the dictionary::
        
                >>> from inpKeyword import *
                >>> d = createParamDictFromString('INC=2000, NLGEOM, UNSYMM=YES')
                >>> d['inc'] = int(d['inc'] / 2)
                >>> formatStringFromParamDict(d)
                'INC=1000, NLGEOM, UNSYMM=YES'
    
    """

    parameterString = joinPS.join(['%s=%s' % (repr2(i[0], rmtrailing0), repr2(i[1], rmtrailing0)) if i[1]!='' else '%s' % repr2(i[0], rmtrailing0) for i in parameters.items()])
    return parameterString

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _insertComments(data, comments):
    r"""_insertComments(data, comments)
    
        This function will insert each item in *comments* to the appropriate location in *data*.

        *data* should be a list of strings from the data from an :class:`.inpKeyword`, while *comments* should
        be :attr:`inpKeyword.comments`. 

        The user should not call this function in most circumstances. The :func:`~inpKeyword._formatDataOutput` and 
        :func:`~inpKeyword._formatDataLabelDict` functions are meant to call this function.
        
        Args:
            data (list): A :class:`list` of :class:`strings <str>`. This list should be produced from the formatData
              function inside :func:`~inpKeyword._formatDataOutput` or :func:`~inpKeyword._formatDataLabelDict`.
            comments (list): A :class:`list` of :class:`lists <list>` of the form [[:class:`int`, :class:`str`], ...].
              Should be :attr:`~inpKeyword.comments`.
            
        Returns:
            list: A list of strings corresponding to the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments`
              properly ordered.
              
        Examples:
            
            We'll create an :class:`inpKeyword` which contains a comment line::

                >>> from inpKeyword import inpKeyword
                >>> block = inpKeyword('''*ELEMENT, TYPE=C3D4
                ... 1, 1, 2, 3, 4
                ... **2, 5, 6, 7, 8
                ... 3, 9, 10, 11, 12''')
                
            If we print :attr:`~inpKeyword.inpKeyword.data` and :attr:`~inpKeyword.inpKeyword.comments`, we can verify
            the data and comment lines are stored separately::

                >>> print(block.data)
                {
                1: 1, 1, 2, 3, 4
                3: 3, 9, 10, 11, 12
                }
                >>> print(block.comments)
                [[1, '**2, 5, 6, 7, 8']]

            Finally, calling :func:`~inpKeyword.inpKeyword.formatData` will automatically call the appropriate 
            sub-function for formatting the datalines and comments. The sub-function will automatically call 
            :func:`_insertComments` to place the comment strings to their original location::

                >>> block.formatData()
                ['\n1, 1, 2, 3, 4', '\n**2, 5, 6, 7, 8', '\n3, 9, 10, 11, 12']

            Since the position of the comment lines is stored absolutely, if we delete a data line, the comment will 
            likely not end up in the same relative position::

                >>> del block.data[1]
                >>> block.formatData()
                ['\n3, 9, 10, 11, 12', '\n**2, 5, 6, 7, 8']
    
    """

    if len(comments) > 0:
        for comment in comments:
            data.insert(comment[0], f'\n{comment[1]}')
    return data

#==================================================================================================================        
class inpKeyword:
    r"""This class creates a blank :class:`inpKeyword` object.

        The :class:`inpKeyword` object is almost identical in the structure to that created by the 
        `inpParser module <https://help.3ds.com/2022/English/DSSIMULIA_Established/SIMACAEKERRefMap/simaker-m-InpPyc-sb.htm?contextscope=all&id=7f27801fe15b4d959283a017d5756e11>`_, 
        except data containers are mostly mutable instead of tuples.
        
        Using print on an instance of this object will create a string of the :class:`inpKeyword` in valid Abaqus
        formatting. This could potentially print a huge amount of data, so the user should have some idea what the 
        :class:`inpKeyword` instance holds before printing it. This applies to any operation that will trigger 
        :meth:`~object.__str__`. 
        
        This will print all information corresponding to the :class:`inpKeyword` block, but not any information
        from :attr:`~inpKeyword.suboptions`. This will include :attr:`~inpKeyword.data` that was read and/or will
        be written to a sub-input file as specified by the INPUT parameter.
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, inputString='', name='', parameter=None, data=None, path='', suboptions=None, comments=None, createSuboptions=True, **inpRWargs):
        r"""__init__(inputString='', name='', parameter=None, data=None, path='', suboptions=None, comments=None, createSuboptions=True, **inpRWargs)
        
            Initializes the :class:`inpKeyword`.

            There are three methods to initialize :class:`inpKeyword`. The first is to specify no input arguments to 
            create a blank :class:`inpKeyword`. The second is to specify any or all of *name*, *parameter*, *data*,
            *path*, *suboptions*, and *comments* directly; if using this option, each of the items will need to be
            formatted properly prior to insertion. The third option is to specify *inputString*, which is a string
            consisting of the entirety of the Abaqus keyword block in proper Abaqus input file syntax. If *inputString*
            is specified, the __init__ process will handle parsing *inputString* and populating the appropriate attributes, 
            thus sparing the user this task. The user can also pass additional arguments to this function to control
            certain formatting options. See the *inpRWargs* entry in the Args section for more details.

            The most important attributes of :class:`inpKeyword` are the following:

            :attr:`name`,
            :attr:`parameter`,
            :attr:`data`,
            :attr:`comments`,
            :attr:`path`,
            :attr:`suboptions`

            Users might need to be aware of these attributes (especially if creating keywords from scratch), but they
            should not often need to access them directly:

            :attr:`_inpItemsToUpdate`,
            :attr:`_data`,
            :attr:`_subdata`,
            :attr:`_dataParsed`
            
            The most important user functions are the following:

            :func:`parseKWData`,
            :func:`formatData`,
            :func:`formatKeywordLine`,
            :func:`formatParameterOutput`,
            :func:`writeKWandSuboptions`,
            :func:`_setMiscInpKeywordAttrs`

            Args:
                inputString (str): The string corresponding to the entirety of the keyword block. This must be one string, 
                  not a sequence of strings. Defaults to ''.
                name (str): The keyword name. Defaults to ''.
                parameter (csid): Stores the parameters and their values. Defaults to an empty :class:`csid`.
                data (list): A list of lists to hold dataline information. Each sublist corresponds to one
                    dataline. Defaults to [].
                path (str): Stores the path to access the keyword block in :attr:`~inpRW.inpRW.keywords`. Defaults to ''.
                suboptions (list): Stores the sub blocks to the :class:`inpKeyword` object if 
                    :attr:`~inpRW.inpRW.organize` = True. Defaults to :class:`~inpKeywordSequence`.
                comments (list): Stores the comments of the :class:`inpKeyword`. Defaults to [].
                createSuboptions (bool): If True, will set the :attr:`suboptions` attribute to a blank :class:`~inpKeywordSequence.inpKeywordSequence`
                    instance. If False, :attr:`suboptions` will be None. Defaults to True. 
                inpRWargs (dict): Should contain attributes from :class:`inpRW` that are needed for proper formatting
                    and organization of the parsed data. :func:`~inpRW.inpRW.parse` will pass the appropriate values to
                    this function automatically. :class:`inpKeyword` can be used without any of these attributes
                    specified, in which case default values that allow a standalone :class:`inpKeyword` will be used.
                    To be consistent with the rest of the parsed keyword blocks, you should pass the :attr:`~inpRW.inpRW.inpKeywordArgs`
                    dictionary to this function as follows ::
                        
                        inpKeyword(arg1, arg2, argn, **inp.inpKeywordArgs)

            Examples:
                
                Here's an example of creating an :class:`inpKeyword` by specifying the *inputString* argument::

                    >>> from inpKeyword import inpKeyword
                    >>> blocka = inpKeyword('''*Node, nset=Nset-1
                    ... 1, 0.0, 0.0, 0.0
                    ... **Comment
                    ... 2, 1.0, 0.0, 0.0''')
                    >>> blocka
                    inpKeyword(name='Node', parameter=csid(csiKeyString(' nset'): inpString('Nset-1', False)), data=csid(inpInt('1'): Node(label=inpInt('1'), data=[inpInt('1'), inpDecimal(' 0.0'), inpDecimal(' 0.0'), inpDecimal(' 0.0')], elements=[]), inpInt('2'): Node(label=inpInt('2'), data=[inpInt('2'), inpDecimal(' 1.0'), inpDecimal(' 0.0'), inpDecimal(' 0.0')], elements=[])), path='', comments=[[1, '**Comment']], suboptions=inpKeywordSequence(num child keywords: 0, num descendant keywords: 0, path: .suboptions))
                    >>> str(blocka)
                    '\n*Node, nset=Nset-1\n1, 0.0, 0.0, 0.0\n**Comment\n2, 1.0, 0.0, 0.0'

                We can create the equivalent block if we forgo the *inputString* argument and instead specify the *name*, *parameter*,
                *data*, and *comments* arguments, although this will be more work for the user in many cases. Example:

                    >>> from inpKeyword import createParamDictFromString
                    >>> from mesh import *
                    >>> name = 'Node'
                    >>> parameter = createParamDictFromString(' nset=Nset-1')
                    >>> node1 = Node('1, 0.0, 0.0, 0.0')
                    >>> node2 = Node('2, 1.0, 0.0, 0.0')
                    >>> data = Mesh([[i.label, i] for i in [node1, node2]])
                    >>> comments = [[1, '**Comment']]
                    >>> blockb = inpKeyword(name=name, parameter=parameter, data=data, comments=comments)
                    >>> str(blocka) == str(blockb)
                    True
                
        """
        
        #Set default values of parameters that should be defined from inp instance
        self.preserveSpacing = True #: See :attr:`inpRW.preserveSpacing <inpRW.inpRW.preserveSpacing>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to True
        self.useDecimal = True #: See :attr:`inpRW.useDecimal <inpRW.inpRW.useDecimal>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to True
        self._ParamInInp = False #: See :attr:`inpRW._ParamInInp <inpRW.inpRW._ParamInInp>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to False
        self.fastElementParsing = True #: See :attr:`inpRW.fastElementParsing <inpRW.inpRW.fastElementParsing>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to True
        self._joinPS = ',' #: See :attr:`inpRW._joinPS <inpRW.inpRW._joinPS>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to ','
        self.parseSubFiles = False #: See :attr:`inpRW.parseSubFiles <inpRW.inpRW.parseSubFiles>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to False
        self.inputFolder = '' #: See :attr:`inpRW.inputFolder <inpRW.inpRW.inputFolder>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to ''
        self._nl = '\n' #: See :attr:`inpRW._nl <inpRW.inpRW._nl>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to '\n'
        self.rmtrailing0 = False #: See :attr:`inpRW.rmtrailing0 <inpRW.inpRW.rmtrailing0>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to False
        self._addSpace = '' #: See :attr:`inpRW._addSpace <inpRW.inpRW._addSpace>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to ''
        #self.jobSuffix = '' #: See :attr:`inpRW.jobSuffix <inpRW.inpRW.jobSuffix>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to ''
        self._debug = False #: See :attr:`inpRW._debug <inpRW.inpRW._debug>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to False
        self.delayParsingDataKws = set() #: See :attr:`inpRW.delayParsingDataKws <inpRW.inpRW.delayParsingDataKws>`. Should be passed from the :class:`~inpRW.inpRW` instance via *inpRWargs*. Defaults to set()
        self._subinps = [] #: :list: Contains each sub :class:`~inpRW.inpRW` instance associated for this block. Only populated for \*INCLUDE and \*MANIFEST.

        #
        self._firstItem = False #: See :attr:`inpRW._firstItem <inpRW.inpRW._firstItem>`. Defaults to False
        self._leadstr = None #: :str: Stores any whitespace characters that occur on a keyword line prior to the \* symbol. Defaults to None
        self._baseStep = None #: :inpKeyword: Stores the base step for \*STEP keyword blocks.
        self._dataParsed = False #: :bool: Indicates if the data for the keyword block has been parsed. Will be set to True by :func:`parseKWData` if the keyword's data was parsed. Defaults to False
        self._namedRefs = csid() #: See :attr:`inpRW.namedRefs <inpRW.inpRW.namedRefs>`. Defaults to csid()
        self._inpItemsToUpdate = {'namedRefs': self._namedRefs} #: :dict: Contains the items from the :class:`inpKeyword` block that need to be set in the :class:`~inpRW.inpRW` instance. Defaults to {'namedRefs': self._namedRefs}
        self.pd = csid() #: See :attr:`inpRW.pd <inpRW.inpRW.pd>`. Defaults to None
        

        #These attributes are set so they can be documented. They are deleted so they don't interfere with the normal operation of the inpKeyword. They will be recreated when parsing keywords in inpRW._dataKWs if they are needed.
        self._data = None #: :inpKeyword: A sub-instance of :class:`inpKeyword` that contains the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments` of the keyword block that are in the main input file if the keyword block is set to read data from a sub-file using the INPUT parameter. Does not exist by default.
        self._subdata = None #: :inpKeyword: A sub-instance of :class:`inpKeyword` that contains the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments` of the keyword block that are in the sub input file if the keyword block is set to read data from a sub-file using the INPUT parameter. Does not exist by default.
        self._nd = Mesh() #: :Mesh: A :class:`~mesh.Mesh` instance which will hold node labels and the elements connected to them. Only exists for \*ELEMENT keyword blocks.
        del self._data
        del self._subdata
        del self._nd


        #Handling function parameters and the main class attributes:
        self.inputString = inputString #: :str: The unparsed string representing the entirety of the keyword block. Will be the value of the *inputString* parameter for :func:`~inpKeyword.__init__`. Defaults to ''
        self.name = name #: :str: The name of the keyword block (i.e. "ELEMENT" for a \*ELEMENT keyword block). Defaults to ''
        if parameter == None:
            self.parameter = csid() #: :csid: Stores the keyword parameters and their values. Defaults to csid()
        else:
            self.parameter = parameter
        if data == None:
            self.data = [] #: :list or Mesh: Stores the parsed data. Each item in :attr:`data` will be a list containing the parsed entries from one dataline. If the keyword block is \*NODE or \*ELEMENT, :attr:`data` will instead be a :class:`~mesh.Mesh` instance. If the keyword block specifies data in a sub-input file via the INPUT parameter, :attr:`~inpKeyword.data` will first list the data from the main input file, and then the data from the sub-input file. Defaults to []
        else:
            self.data = data
            self._dataParsed = True
        self.path = path #: :str: Stores a string representation of the path to the :class:`inpKeyword` object through :attr:`keywords <inpRW.inpRW.keywords>`. Defaults to ''
        if suboptions == None and createSuboptions:
            import inpKeywordSequence
            self.suboptions = inpKeywordSequence.inpKeywordSequence(parentBlock=self) #: :inpKeywordSequence: Stores the sub blocks to the :class:`inpKeyword` object if :attr:`~inpRW.inpRW.organize` = True. The suboptions for each block will be set during the block organization loop of :func:`~inpRW.inpRW.parse`. Defaults to :class:`.inpKeywordSequence`
        elif suboptions == None:
            self.suboptions = None 
        else:
            self.suboptions = suboptions
        if comments==None:
            self.comments = [] #: :list: Stores the commented lines with the keyword block (i.e. any line that starts with "\*\*" following the keyword line, but before the next keyword line. Each item in comments will be of the form [ind, line] where ind is the index of the line in :attr:`~inpKeyword.inpKeyword.data` and line is the string of the comment line. If the keyword block specifies data in a sub-input file via the INPUT parameter, :attr:`~inpKeyword.comments` will first list the comments from the main input file, and then the comments from the sub-input file. Defaults to []
        else:
            self.comments = comments

        # {'ps': self.preserveSpacing, 'useDecimal': self.useDecimal,
        #  '_ParamInInp': self._ParamInInp, 'fastElementParsing': self.fastElementParsing, '_joinPS': self._joinPS,
        #  'parseSubFiles': self.parseSubFiles, 'inputFolder': self.inputFolder, 'rmtrailing0': self.rmtrailing0}

        self.__dict__.update(inpRWargs)

        if self.inputString != '':
            if not hasattr(self, 'lines'):
                self.lines = self._parseInputString() #: :list: Stores the input strings for the keyword block; these will have been split on new line characters. This is normally deleted when the block is parsed, but it will include the unparsed strings representing the datalines if the data was not parsed.
            dummy = self.parseKWData(parseDelayed=False)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def formatData(self, includeSubData=True):
        r"""formatData(includeSubData=True)
       
            This function maps the actual formatting function used by a given keyword block to a consistent name (formatData).
            
            If the *inputString* or *name* parameters are specified, formatData will actually be an attribute mapping
            to the appropriate function for formatting the data of the keyword block. This function exists solely to
            create the mapping to the real function and call the real function. This function will not be used in most cases.

            Args:
                includeSubData (bool): If True, data from :attr:`_subdata` will also be included in the output.
                    Defaults to True.
                    
            Returns:
                list: A list with a string for each line in :attr:`data`. 
                
            Examples:
                This example shows creating a keyword block by populating the individual fields::

                    >>> from inpKeyword import inpKeyword, createParamDictFromString
                    >>> name = 'Nset'
                    >>> parameters = createParamDictFromString('nset= "Nset 2"')
                    >>> data = [[1,2,3,4,5]]
                    >>> block = inpKeyword(name=name, parameter=parameters, data=data)
                    >>> block.formatData()
                    ['\n1,2,3,4,5']

                Any method which populates the :attr:`~inpKeyword.inpKeyword.data` attribute will automatically set
                :func:`~inpKeyword.inpKeyword.formatData` to the appropriate sub-function. We can see this for the previous keyword block::

                    >>> block.formatData.__name__
                    '_formatDataOutput'
                
                formatData is mapped to :func:`~inpKeyword.inpKeyword._formatDataLabelDict` for \*NODE and \*ELEMENT keyword blocks::

                    >>> block2 = inpKeyword('*ELEMENT, elset=test, type=C3D8R\n1, 1, 2, 3, 4, 5, 6, 7, 8')
                    >>> block2.formatData.__name__
                    '_formatDataLabelDict'

                The only case where this is not set automatically is if we create a blank :class:`inpKeyword` instance
                and then populate it. In this case, :func:`~inpKeyword.inpKeyword.formatData` will not be remapped until it has been called once::

                    >>> block3 = inpKeyword()
                    >>> block3name = 'ELSET'
                    >>> block3parameter = createParamDictFromString(' elset=test_elset')
                    >>> block3data = [[1, 2, 3, 4, 5, 6, 7, 8]]
                    >>> block3.name = block3name
                    >>> block3.parameter = block3parameter
                    >>> block3.data = block3data
                    >>> block3.formatData.__name__
                    'formatData'

                Now calling :func:`~inpKeyword.inpKeyword.formatData` picks the correct sub-function based on the element name and remaps
                the formatData name from this function to the sub-function::

                    >>> block3.formatData()
                    ['\n1,2,3,4,5,6,7,8']
                    >>> block3.formatData.__name__
                    '_formatDataOutput'
                
        """

        name = rsl(self.name)
        #print(f' formatData has not been set for keyword {name}.')
        if name in {'node', 'element'}:
            self.formatData = self._formatDataLabelDict
        else:
            self.formatData = self._formatDataOutput
        return self.formatData(includeSubData=includeSubData)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def formatKeywordLine(self):
        r"""formatKeywordLine()
        
            Creates a printable string for the keyword line(s) of the :class:`inpKeyword` instance. 

            Keyword lines include the keyword name and the parameters, but not the datalines. If the :class:`inpKeyword` instance 
            originally had multiple keyword lines, this function will also write out multiple keyword lines.

            Returns:
                str: A string representing the keyword line(s).

            Examples:

                First we create a sample keyword block, and then call the function::

                    >>> from inpKeyword import inpKeyword
                    >>> block = inpKeyword('''*Nset, nset= "Nset 2"
                    ... 1, 2, 3, 4, 5''')
                    >>> block.formatKeywordLine()
                    '\n*Nset, nset= "Nset 2"'

                This will also handle cases where the keywordline is split across multiple lines:

                    >>> block = inpKeyword('''*Element, type=C3D8,
                    ... elset= Elset-1
                    ... 1, 1, 2, 3, 4, 5, 6, 7, 8''')
                    >>> block.formatKeywordLine()
                    '\n*Element, type=C3D8,\nelset= Elset-1'

                If :attr:`~inpKeyword.inpKeyword.name` is not set, this function simply returns a blank string::

                    >>> block = inpKeyword()
                    >>> block.formatKeywordLine()
                    ''
            
        """
        
        if self._leadstr != None:
            leadchar = self._leadstr
        else:
            leadchar = ''

        if self._firstItem:
            pass
        else:
            leadchar = '\n' + leadchar

        if self.name:
            if len(self.parameter)>=1:
                if hasattr(self, '_kwLineSep'): #this loop deals with keyword lines split over multiple lines
                    a = list(flatten(self._parameterLines))
                    b = self.parameter.keys()
                    if len(a) < len(b):
                        missing = set(b) - set(a)
                        for key in missing:
                            self._parameterLines[-1].append(key)
                    parameterStrings = [formatStringFromParamDict(csid(zip(i, [self.parameter[j] for j in i]))) + self._kwLineSep[ind] for ind,i in enumerate(self._parameterLines)]
                    parameterString = ''.join(parameterStrings)
                else:
                    parameterString = self.formatParameterOutput()
                keywordLine = '%s*%s,%s%s' % (leadchar, self.name, self._addSpace, parameterString)
            else:
                keywordLine = '%s*%s' % (leadchar, self.name)
            self._firstItem = False
        else:
            keywordLine = ''
        return keywordLine
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def formatParameterOutput(self):
        r"""formatParameterOutput()
        
            Turns the parameter dictionary into a printable string.

            Returns:
                str: A string representation of the parameter dictionary.

            Examples:

                You can use this function if you need to create a string just from the parameters. The parameters
                will be written in their original order::

                    >>> from inpKeyword import inpKeyword
                    >>> block = inpKeyword('''*STEP, INC=2000, NLGEOM, UNSYMM=YES
                    ...  STEP 3 - EARTHQUAKE''')
                    >>> block.formatParameterOutput()
                    ' INC=2000, NLGEOM, UNSYMM=YES'

        """
        
        parameterString = formatStringFromParamDict(self.parameter, self._joinPS, self.rmtrailing0)
        #parameterString = self._joinPS.join(['%s=%s' % (repr2(i[0], self.rmtrailing0), repr2(i[1], self.rmtrailing0)) if i[1]!='' else '%s' % repr2(i[0], self.rmtrailing0) for i in self.parameter.items()])
        return parameterString

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parseKWData(self, parseDelayed=False):
        r"""parseKWData(parseDelayed=False)
            
            This function calls :func:`_parseData` to parse keyword block data, and adds the results of that function 
            call to :attr:`~inpKeyword.data` . It is called during :func:`~inpKeyword.__init__` if the *inputString* parameter
            is not ''.

            This function will not parse the keyword block data if :attr:`~inpKeyword.name` is in :attr:`~inpKeyword.delayParsingDataKws`
            and *parseDelayed* = False (the default). This will allow the user to avoid costly parsing 
            operations if they only need access to the organization of the keywords. If the data is not parsed, it will
            be stored as a list of strings in the :attr:`~inpKeyword.inpKeyword.lines` attribute, and this list will be included
            when a string of the entire keyword block is produced.

            .. note::

                You should only place keyword block names in :attr:`~inpKeyword.delayParsingDataKws` if you know for certain
                you will not need to access the data in those keyword blocks. :mod:`~inpRW` currently does not include a
                mechanism to automatically parse the data of keyword blocks after the :class:`inpKeyword` has been initialized.
                This will likely be enhanced in the future.

            If :attr:`~inpKeyword.name` is in :attr:`_dataKWs <config._dataKWs>` and the keyword includes the INPUT parameter,
            :func:`~inpKeyword._parseData` will delete the :attr:`~inpKeyword.data` attribute and create :attr:`~inpKeyword._data`
            and :attr:`~inpKeyword._subdata`, which are sub-instances of :class:`~inpKeyword`. The data and comments from 
            the main input file will be stored in :attr:`~inpKeyword._data`. If :attr:`~inpKeyword.parseSubFiles` = True, 
            this function will also read the data and comments from the sub-file (whose name is specified by the value of the INPUT parameter) and store them
            to :attr:`~inpKeyword._subdata`. The user should rarely need to directly access :attr:`~inpKeyword._data` and
            :attr:`~inpKeyword._subdata`. If :attr:`~inpKeyword.data` or :attr:`~inpKeyword.comments` are not set, 
            :func:`~inpKeyword.__getattr__` will retrieve the information from :attr:`~inpKeyword._data` and 
            :attr:`~inpKeyword._subdata` automatically.
            
            Args:
                parseDelayed (bool): If True, will parse data for any blocks which were set to parse on a later loop.
                    This is controlled by :func:`~inpRW.inpRW.parse` and :attr:`~inpRW.inpRW.delayParsingDataKws`.
                    Defaults to False.
                    
            Returns:
                bool: None if :attr:`~inpKeyword.data` should not be populated at this time, else no return.
            
            Examples:

                In the most basic case, we parse a simple keyword block, which calls this function automatically::

                    >>> from inpKeyword import inpKeyword
                    >>> block1 = inpKeyword(r'''*NSET,NSET=MIDPLANE
                    ... 204,303,402,214,315,416
                    ... 1902,2003,1916,2015
                    ... **''')
                    >>> block1.data
                    [[inpInt('204'), inpInt('303'), inpInt('402'), inpInt('214'), inpInt('315'), inpInt('416')], [inpInt('1902'), inpInt('2003'), inpInt('1916'), inpInt('2015')]]
                    
                If a keyword block has some data and/or comments in the main input file, but some data in a separate file
                specified by the INPUT parameter, the information from each file will be stored in separate :attr:`~inpKeyword.inpKeyword._data`
                and :attr:`~inpKeyword.inpKeyword._subdata` attributes (these keyword names are store in :attr:`config._dataKWs`). 
                The user can still simply use :attr:`~inpKeyword.inpKeyword.data` to access the combined information; the 
                information from the main input file will always be reported first. When the input file is written, any 
                information in :attr:`~inpKeyword.inpKeyword._subdata` will be written to the file specified by the INPUT parameter. 
                Example::

                    >>> from config import _slash as sl
                    >>> block2 = inpKeyword(f'''*NODE,NSET=HANDLE,INPUT=sample_input_files{sl}inpKeyword{sl}tennis_rig1.inp
                    ... **
                    ... **''', parseSubFiles=True)
                    >>> print(block2) # doctest: +ELLIPSIS
                    <BLANKLINE>
                    *NODE,NSET=HANDLE,INPUT=sample_input_files...inpKeyword...tennis_rig1.inp
                    **
                    **
                       50001,        0.54,      -8.425,        0.25
                       50002,        0.54,    -9.80625,        0.25
                       50003,        0.54,    -11.1875,        0.25
                
                We can verify the information is stored in separate containers::
                    
                    >>> print(block2._data)
                    <BLANKLINE>
                    **
                    **
                    >>> print(block2._subdata.data)
                    {
                       50001:    50001,        0.54,      -8.425,        0.25
                       50002:    50002,        0.54,    -9.80625,        0.25
                       50003:    50003,        0.54,    -11.1875,        0.25
                    }

                Of course, if the INPUT parameter is not part of the keyword block, :attr:`~inpKeyword.inpKeyword._data` and
                :attr:`~inpKeyword.inpKeyword._subdata` won't be created::

                    >>> block3 = inpKeyword('''*NODE
                    ... **  Bottom curve.
                    ...  104, -2.700,-6.625,0.
                    ...  109,  0.000,-8.500,0.
                    ...  114,  2.700,-6.625,0.''')
                    >>> hasattr(block3, '_data')
                    False

                If you won't need to access the data of a keyword type and wish to avoid parsing all blocks with that name,
                you can include that name in :attr:`~inpKeyword.delayParsingDataKws`. You would typically set this at the 
                :class:`~inpRW.inpRW`, but it's shown here for illustration. This will save some processing time, especially
                for keyword blocks with a lot of data.
                    
                    >>> block4 = inpKeyword('''*NODE
                    ... **  Bottom curve.
                    ...  104, -2.700,-6.625,0.
                    ...  109,  0.000,-8.500,0.
                    ...  114,  2.700,-6.625,0.''', delayParsingDataKws={'node'})
                    >>> block4.data
                    csid()

                The data is still stored as a list of unparsed strings in the :attr:`~inpKeyword.inpKeyword.lines` attribute,
                so it will still be included when a string of the :class:`~inpKeyword.inpKeyword` block is produced.
                    
                    >>> print(block4)
                    <BLANKLINE>
                    *NODE
                    **  Bottom curve.
                     104, -2.700,-6.625,0.
                     109,  0.000,-8.500,0.
                     114,  2.700,-6.625,0.

            .. todo::
                Replace return None with raise a custom exception type.
        
        """

        name = rsl(self.name)
        parameter = self.parameter
        data = []
        if parseDelayed == False:
            if name in self.delayParsingDataKws:
                return None

        if name in _dataKWs:
            subName = parameter.get('input')
            if subName != None:
                if name == 'matrixinput' and rsl(subName.split('.')[-1]) == 'sim':
                    pass
                else:
                    del self.data
                    del self.comments
                    parentKwLine = self.formatKeywordLine()
                    subKwArgs = {'inputFolder': self.inputFolder, '_nl': self._nl, '_debug': self._debug, 'name': self.name, 'parameter': self.parameter}
                    parseDataName = self._parseData.__name__
                    formatDataName = self.formatData.__name__
                    self._data = inpKeyword()
                    self._subdata = inpKeyword(**subKwArgs)
                    self._subdata._setMiscInpKeywordAttrs()
                    self._data._parseData = eval(f'self._data.{parseDataName}')
                    self._data.formatData = eval(f'self._data.{formatDataName}')
                    self._data.data = self._parseData()
                    self._data._dataParsed = True
                    if self.parseSubFiles:
                        self._subdata._parseData = eval(f'self._subdata.{parseDataName}')
                        self._subdata.formatData = eval(f'self._subdata.{formatDataName}')
                        try:
                            self._subdata._parseSubData(subName=subName, parentKwLine=parentKwLine)
                        except FileNotFoundError:
                            print(f'\n  WARNING! Could not find file {subName} for keyword block {parentKwLine}\n')
                        except:
                            traceback.print_exc()
                    self._dataParsed = True
                    return None #prevents self.data from being assigned at the end of the function
            else:
                data = self._parseData()
        else:
            data = self._parseData()
        if isinstance(data, list):
            self.data.extend(data)
        else:
            self.data.update(data)
        self._dataParsed = True
        del self.lines

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def printKWandSuboptions(self, includeSubData=False):
        r"""printKWandSuboptions(includeSubData=False)
        
            This function will print the list of strings generated by by :func:`writeKWandSuboptions`.
            
            Args:
                includeSubData (bool): If True, will include :attr:`~inpKeyword.data` read from a sub file in the output 
                    string list. Defaults to False.

            Examples:

                We'll first parse an input file::
                
                    >>> import inpRW
                    >>> from config import _slash as sl
                    >>> inp = inpRW.inpRW(f'sample_input_files{sl}inpKeyword{sl}mcooot3vlp.inp')
                    >>> inp.parse() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
                    <BLANKLINE>
                    Splitting string of input file from ... into strings representing each keyword block.
                    <BLANKLINE>
                    <BLANKLINE>
                    Parsing 36 keyword blocks using 1 cores.
                    ...
                     Updating keyword blocks' paths
                     Searching for *STEP locations
                    <BLANKLINE>
                    Finished parsing mcooot3vlp.inp
                       time to parse = ...
                    
                Next, we'll find the \*STEP keyword containing the \*TEMPERATURE block and call 
                :func:`~inpKeyword.inpKeyword.printKWandSuboptions` on it::
                    
                    >>> for tempblock in inp.kwg['temperature']: # Each kwg entry is a set, so we must iterate through it to select the only TEMPERATURE block
                    ...    break 
                    >>> step = inp.getParentBlock(tempblock, parentKWName='step')
                    >>> step.printKWandSuboptions()
                    *STEP,INC=10
                    STEP 3 - REST OF NONLINEAR
                    *STATIC,DIRECT
                    1.,10.
                    *BOUNDARY
                    7,3,,-.005
                    5,3,,-.005
                    6,3,,-.005
                    8,3,,-.005
                    *TEMPERATURE,INPUT=mcooot3vlp_temp.inp
                    *END STEP

                If we activate the *includeSubData* parameter, the contents of sub-input files will be shown in the output::

                    >>> step.printKWandSuboptions(includeSubData=True)
                    *STEP,INC=10
                    STEP 3 - REST OF NONLINEAR
                    *STATIC,DIRECT
                    1.,10.
                    *BOUNDARY
                    7,3,,-.005
                    5,3,,-.005
                    6,3,,-.005
                    8,3,,-.005
                    *TEMPERATURE,INPUT=mcooot3vlp_temp.inp
                    1,20.
                    2,20.
                    3,20.
                    4,20.
                    5,20.
                    6,20.
                    7,20.
                    8,20.
                    <BLANKLINE>
                    *END STEP
        
        """

        print(''.join(self.writeKWandSuboptions(firstItem=True, includeSubData=includeSubData)))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writeKWandSuboptions(self, firstItem=False, includeSubData=False):
        r"""writeKWandSuboptions(firstItem=False, includeSubData=False)
        
            This function will create a list of strings representing each line of the :class:`inpKeyword`, and all blocks
            in :attr:`~inpKeyword.suboptions`, except for :attr:`~inpKeyword.suboptions` of \*INCLUDE or \*MANIFEST blocks.
            If *includeSubData* is True, the data read from sub files will also be included.
            
            The first character of the output will be a new line character, unless *firstItem* = True. This prevents adding
            an extra new line character to the start of the text block or input file.

            Args:
                firstItem (bool): If True, a new line character will not be written to the start of the output string list.
                    Defaults to False.
                    
                includeSubData (bool): If True, will include :attr:`~inpKeyword.data` read from a sub file in the output 
                    string list. Defaults to False.
                    
            Returns:
                list: A list of strings.
                
            Examples:

                We'll first parse an input file::
                
                    >>> import inpRW
                    >>> from config import _slash as sl
                    >>> inp = inpRW.inpRW(f'sample_input_files{sl}inpKeyword{sl}mcooot3vlp.inp')
                    >>> inp.parse() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
                    <BLANKLINE>
                    Splitting string of input file from ... into strings representing each keyword block.
                    <BLANKLINE>
                    <BLANKLINE>
                    Parsing 36 keyword blocks using 1 cores.
                    ...
                     Updating keyword blocks' paths
                     Searching for *STEP locations
                    <BLANKLINE>
                    Finished parsing mcooot3vlp.inp
                       time to parse = ...
                    
                Next, we'll find the \*STEP keyword containing the \*TEMPERATURE block and call 
                :func:`~inpKeyword.inpKeyword.printKWandSuboptions` on it::
                    
                    >>> for tempblock in inp.kwg['temperature']: # Each kwg entry is a set, so we must iterate through it to select the only TEMPERATURE block
                    ...    break 
                    >>> step = inp.getParentBlock(tempblock, parentKWName='step')
                    >>> step.writeKWandSuboptions()
                    ['\n*STEP,INC=10', '\nSTEP 3 - REST OF NONLINEAR', '\n*STATIC,DIRECT', '\n1.,10.', '\n*BOUNDARY', '\n7,3,,-.005', '\n5,3,,-.005', '\n6,3,,-.005', '\n8,3,,-.005', '\n*TEMPERATURE,INPUT=mcooot3vlp_temp.inp', '\n*END STEP']

                *firstItem* = True will prevent a newline character from being added to the first output item::

                    >>> step.writeKWandSuboptions(firstItem=True)
                    ['*STEP,INC=10', '\nSTEP 3 - REST OF NONLINEAR', '\n*STATIC,DIRECT', '\n1.,10.', '\n*BOUNDARY', '\n7,3,,-.005', '\n5,3,,-.005', '\n6,3,,-.005', '\n8,3,,-.005', '\n*TEMPERATURE,INPUT=mcooot3vlp_temp.inp', '\n*END STEP']
                
                If we activate the *includeSubData* parameter, the contents of sub-input files will be shown in the output::

                    >>> step.writeKWandSuboptions(includeSubData=True)
                    ['\n*STEP,INC=10', '\nSTEP 3 - REST OF NONLINEAR', '\n*STATIC,DIRECT', '\n1.,10.', '\n*BOUNDARY', '\n7,3,,-.005', '\n5,3,,-.005', '\n6,3,,-.005', '\n8,3,,-.005', '\n*TEMPERATURE,INPUT=mcooot3vlp_temp.inp', '\n1,20.', '\n2,20.', '\n3,20.', '\n4,20.', '\n5,20.', '\n6,20.', '\n7,20.', '\n8,20.', '\n', '\n*END STEP']
            """

        if firstItem == True:
            self._firstItem = True
        name = rsl(self.name)
        outputlines = []
        outputlinesapp = outputlines.append
        outputlinesapp(self.formatKeywordLine())
        outputdata = self.formatData(includeSubData=includeSubData)
        outputlinesapp(outputdata)
        suboptions = self.suboptions
        if suboptions and name not in {'include', 'manifest'}:
            subblocks = [subblock.writeKWandSuboptions(includeSubData=includeSubData) for subblock in suboptions]
            outputlinesapp(subblocks)
        output = list(flatten(outputlines))
        return output

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _cloneKW(self, attributes=None):
        r"""_cloneKW(attributes=None) 
        
            Creates a new keyword object which is an identical copy of self.
            
            Args:
                attributes (list): A list indicating the attributes of self to copy to the new keyword object. If None,
                    all attributes will be copied. Valid attributes are 'name', 'parameter', 'data', 'path', 'suboptions',
                    and 'comments'. Defaults to None.
                    
            Returns:
                inpKeyword
                
            .. todo ::
                
                This function needs to be reworked. There are more robust ways to implement it. Use with caution.
        """

        ###NEED TO PASS INPRW ARGS TO NEW KEYWORD

        if attributes == None:
            newKW = inpKeyword(inputString=self.inputString, name=self.name, parameter=self.parameter, data=self.data, path=self.path, suboptions=self.suboptions, comments=self.comments)
        else:
            newKW = inpKeyword()
            for a in attributes:
                exec(f'newKW.{a} = self.{a}')
        return newKW

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _formatDataOutput(self, includeSubData=True):
        r"""_formatDataOutput(includeSubData=True)
        
            Creates a list of printable strings for the datalines of the :class:`inpKeyword` instance. 

            New line characters will be prepended to the string for each line, unless the :class:`inpKeyword` instance 
            has no keyword line and this is the first block in the input file.

            Args:
                includeSubData (bool): If True, the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments` in the 
                    :attr:`~inpKeyword._subdata` (i.e. data lines read from a sub file) will be included in the output. 
                    They will be included after the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments` from the
                    main input file. Defaults to True.

            Returns:
                list: A list of strings, with each item corresponding to a dataline.
                
            Examples:
                In the most basic case, we parse a simple keyword block and then call this function::

                    >>> from inpKeyword import inpKeyword
                    >>> block1 = inpKeyword(r'''*NSET,NSET=MIDPLANE
                    ... 204,303,402,214,315,416
                    ... 1902,2003,1916,2015
                    ... **''')
                    >>> block1._formatDataOutput()
                    ['\n204,303,402,214,315,416', '\n1902,2003,1916,2015', '\n**']

                This function will also format data and comments from sub files if *includeSubData* = True (the default)::

                    >>> from config import _slash as sl
                    >>> block2 = inpKeyword(fr'''*TEMPERATURE,INPUT=sample_input_files{sl}inpKeyword{sl}mcooot3vlp_temp.inp
                    ... **''', parseSubFiles=True)
                    >>> block2._formatDataOutput()
                    ['\n**', '\n1,20.', '\n2,20.', '\n3,20.', '\n4,20.', '\n5,20.', '\n6,20.', '\n7,20.', '\n8,20.', '\n']

                If we call it with *includeSubData* = False, this will return just the information from the main block::

                    >>> block2._formatDataOutput(includeSubData=False)
                    ['\n**']

        """
        
        leadchar = '\n'
        jps = self._joinPS

        #= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
        def _formatData(data):
            """ """

            try:
                outdata = [leadchar + jps.join([repr2(j, self.rmtrailing0) for j in i]) if not isinstance(i, str) else leadchar + i for i in data]
            except ValueError:
                outdata = [leadchar + jps.join([repr2(j, self.rmtrailing0) for j in i]) for i in data] 
            except TypeError:
                outdata = [leadchar + repr2(i, self.rmtrailing0) for i in data]
            except:
                traceback.print_exc()
                print(self.formatKeywordLine())
            return outdata
        #= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

        if hasattr(self, '_data'):
            data = _formatData(self._data.data)
            comments = self._data.comments
            data = _insertComments(data, comments)
            if includeSubData:
                subdata = _formatData(self._subdata.data)
                subcomments = self._subdata.comments
                subdata = _insertComments(subdata, subcomments)
                data = data + subdata
        else:
            data = _formatData(self.data)
            comments = self.comments
            data = _insertComments(data, comments)
        
        # The preceding always adds a leading newline character to each data line. The following code removes the leading 
        # newline character if the block has no keyword line and if this is the first item. This must be done to prevent
        # extra new lines from being written to the resultant input file(s). This occurs most often when an input file is 
        # merely data meant to be read via the INPUT parameter of another keyword block.
        if not self.name and self._firstItem: 
            try:
                data[0] = data[0][1:]
            except IndexError:
                pass

        return data
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _formatDataLabelDict(self, includeSubData=True):
        r"""_formatDataLabelNodeDict(includeSubData=True)
        
            This function will create strings for the datalines for \*NODE and \*ELEMENT keyword blocks, which have their 
            :attr:`~inpKeyword.inpKeyword.data` stored in a dictionary-like construct.

            New line characters will be prepended to the string for each line, unless the :class:`inpKeyword` instance 
            has no keyword line and this is the first block in the input file.
            
            Args:
                includeSubData (bool): If True, the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments` in the 
                    :attr:`~inpKeyword._subdata` (i.e. data lines read from a sub file) will be included in the output. 
                    They will be included after the :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments` from the
                    main input file. Defaults to True.
            
            Returns:
                list: A list of strings, with each item corresponding to a dataline.
                
            Examples:
                In the most basic case, we parse a simple keyword block and then call this function::

                    >>> from inpKeyword import inpKeyword
                    >>> block1 = inpKeyword('''*NODE
                    ... **  Bottom curve.
                    ...  104, -2.700,-6.625,0.
                    ...  109,  0.000,-8.500,0.
                    ...  114,  2.700,-6.625,0.''')
                    >>> block1._formatDataLabelDict()
                    ['\n**  Bottom curve.', '\n 104, -2.700,-6.625,0.', '\n 109,  0.000,-8.500,0.', '\n 114,  2.700,-6.625,0.']

                This function will also format data and comments from sub files if *includeSubData* = True (the default)::

                    >>> from config import _slash as sl
                    >>> block2 = inpKeyword(fr'''*NODE,NSET=HANDLE,INPUT=sample_input_files{sl}inpKeyword{sl}tennis_rig1.inp
                    ... **
                    ... **''', parseSubFiles=True)
                    >>> block2._formatDataLabelDict()
                    ['\n**', '\n**', '\n   50001,        0.54,      -8.425,        0.25', '\n   50002,        0.54,    -9.80625,        0.25', '\n   50003,        0.54,    -11.1875,        0.25']

                If we call it with *includeSubData* = False, this will return just the information from the main block::

                    >>> block2._formatDataLabelDict(includeSubData=False)
                    ['\n**', '\n**']
                    
        """

        leadchar = '\n'

        #= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
        def _formatData(data):
            """ """

            outdata = [f'{leadchar}{i}' for i in data]
            return outdata
        #= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

        if hasattr(self, '_data'):
            data = _formatData(self._data.data.values())
            comments = self._data.comments
            if self.name.replace(' ', '').lower() == 'element':
                comments.reverse()
            data = _insertComments(data, comments)
            if includeSubData:
                subdata = _formatData(self._subdata.data.values())
                subcomments = self._subdata.comments
                if self.name.replace(' ', '').lower() == 'element':
                    subcomments.reverse()
                subdata = _insertComments(subdata, subcomments)
                data = data + subdata
        else:
            data = _formatData(self.data.values())
            comments = self.comments
            if self.name.replace(' ', '').lower() == 'element':
                comments.reverse()
            data = _insertComments(data, comments)
        
        if not self.name and self._firstItem:
            try:
                data[0] = data[0][1:]
            except IndexError:
                pass
        return data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _handleComment(self, line, ind):
        r"""_handleComment(line, ind)

            Appends a list of [:class:`int`, :class:`str`] to :attr:`~inpKeyword.inpKeyword.comments` of the keyword block. 
            The :class:`int` represents the position of the comment in the data, and the :class:`str` is the unparsed
            string of the commented line.

            Args:
                line (str): The comment data line as a string.
                ind (int): The integer representing the position of *line* in :attr:`~inpKeyword.data`.
        """

        self.comments.append([ind, line])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _handleCommentSub(self, line, ind):
        r"""_handleCommentSub(line, ind)

            Appends a list of [:class:`int`, :class:`str`] to :attr:`~inpKeyword.inpKeyword.comments` of the _data keyword block. 
            The :class:`int` represents the position of the comment in the data, and the :class:`str` is the unparsed

            Args:
                line (str): The comment data line as a string.
                ind (int): The integer representing the position of *line* in :attr:`~inpKeyword.data`.
        """

        self._data.comments.append([ind, line])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseData(self):
        r"""_parseData()
       
            This function maps the actual parsing function used by a given keyword block to a consistent name (_parseData).
            
            It will be overridden by :func:`~inpKeyword._parseKWLine`. In case :func:`~inpKeyword._parseKWLine` is not called
            (for example, the attributes of the keyword block are populated manually instead of parsed from a string), 
            this function will overwrite itself with the call to the proper parsing function based on :attr:`~inpKeyword.name`.
        """

        name = rsl(self.name)
        #print(f'  _parseData has not been set for keyword {name}.')
        if name in {'heading', 'endstep'}:
            self._parseData = self._parseDataHeading
        elif name == 'parameter':
            self._parseData = self._parseDataParameter
        elif name == 'rebarlayer':
            self._parseData = self._parseDataRebarLayer
        elif name in {'elset', 'nset'}:
            self._parseData = self._parseDataSet
        elif name == 'surface':
            tmp = self.parameter.get('type')
            if not rsl(tmp) in {'node', 'element'}:
                pass
            else:
                self._parseData = self._parseDataSurface
        elif name == 'node':
            self._parseData = self._parseDataNode
        elif name == 'element':
            self._parseData = self._parseDataElement
        else:
            self._parseData = self._parseDataGeneral
        return self._parseData()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataElement(self):
        r"""_parseDataElement()
        
            Parses the data in \*ELEMENT blocks. 

            This function will parse the data in the \*ELEMENT block. It will also add some information to :attr:`~inpKeyword._nd`. 
            Comments are left as strings and added to the appropriate :attr:`.comments` section. 
            
            This function will read a dataline and check if the number of nodes in that dataline matches the element
            type's specification. If not, the next dataline will be read until the appropriate number of nodes have been found.

            This function has a fast mode which runs if :attr:`~inpKeyword.fastElementParsing` = True
            and the number of nodes to define the element is less than or equal to 10. This assumes the element 
            definition is not split across multiple lines. This should cover the most common Abaqus element types, as 
            long as the pre-processor has not written the element data across more than 1 line.
            
            Returns:
                Mesh: A :class:`.Mesh` instance containing the data for the keyword block. Uses the element label as
                    the key and the parsed dataline as the value.
        """

        lines = self.lines
        con = False
        path = self.path
        eltype = self.parameter['type']
        data = MeshElement(eltype=eltype)
        nd = self._nd
        #ed = self.ed
        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        ps = self.preserveSpacing
        ud = self.useDecimal
        _ParamInInp = self._ParamInInp

        nodeNum = findElementNodeNum(eltype, lines)

        if nodeNum <= 10 and self.fastElementParsing: #fast track for elements with fewer than 10 nodes, which should cover the most common ones. This assumes the element definition is not split across multiple lines.
            #Slower method without assignment expressions, for Python 3.7-
            for ind, line in enumerate(lines):
                if not cfc(line) and line !='':
                    element = Element(datalines=line, eltype=eltype, numNodes=nodeNum, _npll=[nodeNum], _joinS=self._joinPS, _ParamInInp=_ParamInInp, preserveSpacing=ps, useDecimal=ud, _checkNumNodes=False)
                    data[element.label] = element
                    element.setConnectedNodes(nd)
                else:
                    handleComment(line, ind)
        else:
            elcount = 0
            for line in lines:
                if not cfc(line) and line !='':
                    if not con:
                        element = Element(datalines=line, eltype=eltype, numNodes=nodeNum, _joinS=self._joinPS, _ParamInInp=_ParamInInp, preserveSpacing=ps, useDecimal=ud, _checkNumNodes=False)
                        data[element.label] = element
                    else:
                        element._parseDataLine(line, con=True)
                    if len(data[element.label].data)-1 < nodeNum:
                        con = True
                    else:
                        con = False
                        element.setConnectedNodes(nd)
                        elcount +=1
                else:
                    handleComment(line, elcount)

        return data
        #Faster method using assignment expressions, for Python 3.8+ only, need to check before enabling
        #data, td = zip(* ( [(d := [eval2(i, t=int, ps=ps) for i in line.split(",")]), [(dint := [eval2(i, int, True, False) for i in d])[0], csid(zip(['data', 'path', 'type'], [dint, path + '.data[%s]' % ind, eltype] )) ] ] if not cfc(line) else [line, [None, None]] for ind,line in enumerate(lines) ) )
        #data, td = zip(* ( [d := [eval2(i, t=int, ps=ps) for i in line.split(",")], [dint := [self._subParam(i) for i in d][0], csid(zip(['data', 'path', 'type'], [dint, path + '.data[%s]' % ind, eltype] )) ] ] if not cfc(line) else [line, [None, None]] for ind,line in enumerate(lines) ) )
        #data = list(data)
        #tmp = ( [d := [eval2(i, t=int, ps=self.preserveSpacing) for i in line.split(",")], [dint := [self._subParam(i) for i in d][0], csid(zip(['data', 'path', 'type'], [dint, path + '.data[%s]' % ind, eltype] )) ] ] if not cfc(line) else [line, [None, None]] for ind,line in enumerate(lines) )
        #data = list(map(itemgetter(0), tmp))
        #td = map(itemgetter(1), tmp)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataGeneral(self):
        r"""_parseDataGeneral()

            Parses datalines without any special considerations.

            This method parses any type of data. It splits the data lines and tries to turn each data item into their 
            non-text type using :func:`eval2`. This function will split each data line on the "," symbol and 
            :func:`eval2` each item individually. All comments are stored in :attr:`~inpKeyword.inpKeyword.comments`,
            or in the comments attribute if :attr:`~inpKeyword._data`, if appropriate.

            The other _parseData\* functions will work similarly to :func:`_parseDataGeneral` (i.e. check if the dataline
            is a comment, split the dataline on commas to separate items, :func:`eval2(item) <eval2>`). The other 
            functions will either take a shortcut in :func:`eval2` by specifying the expected data type or will
            perform some additional action(s) while looping through the data.

            Returns:
                list: A list of lists containing the data for the keyword block.
        """
        
        lines = self.lines
        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        ps = self.preserveSpacing
        ud = self.useDecimal
        try:
            data = [[eval2(j, ps=ps, useDecimal=ud) for j in i.split(',')] if not cfc(i) else handleComment(i, ind) for ind, i in enumerate(lines)]
        except TypeError: #meant to handle one-length sets
            data = [[eval2(i, ps=ps, useDecimal=ud)] if not cfc(i) else handleComment(i, ind) for ind, i in enumerate(lines)]
        try:
            tmp = self.comments[:]
        except AttributeError:
            tmp = self._data.comments[:]
        tmp.reverse()
        for comment in tmp:
            del data[comment[0]]
        return data
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataHeading(self):
        r"""_parseDataHeading()

            Parses the datalines of \*HEADING keyword blocks.
        
            Special method to parse the \*HEADING data lines. Simply returns the raw string as a list of lines
            without operating on the text.
                
            Returns:
                list: A list of strings containing the data for the keyword block.
        """
        
        lines = self.lines
        data = [i for i in lines]
        return data
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataNode(self):
        r"""_parseDataNode()
            
            Parses the datalines of \*NODE keyword blocks.

            This is a special method for parsing \*NODE keyword blocks with data lines that must be exclusively
            integers or floats. All comments are stored in the appropriate :attr:`~inpKeyword.inpKeyword.comments` section.
            
            Returns:
                Mesh: A :class:`.Mesh` instance that uses the node label as the key, and the parsed dataline as the value.
        """

        #Faster method using assignment expressions, for Python 3.8+ only, needs to be rewritten for latest changes, but likely won't be done until 3DEXPERIENCE supports Python 3.8+
        #data, td = zip(* ( [ d := [eval2((i := line.split(","))[0], t=int, ps=self.preserveSpacing) ] + [eval2(j, t=float, ps=self.preserveSpacing) for j in i[1:]], [dint := self._subParam(d[0]), csid(zip(['data', 'path'], [[dint] + [self._subParam(i) for i in d[1:]], path + '.data[%s]' % (ind)])) ] ] if not cfc(line) else [line, [None, None]] for ind,line in enumerate(lines) ) )
        #data = list(data)
        #tmp = [ [ d := [eval2((i := line.split(","))[0], t=int, ps=self.preserveSpacing) ] + [eval2(j, t=float, ps=self.preserveSpacing) for j in i[1:]], [dint := self._subParam(d[0]), csid(zip(['data', 'path'], [[dint] + [self._subParam(i) for i in d[1:]], path + '.data[%s]' % (ind)])) ] ] if not cfc(line) else [line, [None, None]] for ind,line in enumerate(lines) ]
        #data = list(map(itemgetter(0), tmp))
        #td = map(itemgetter(1), tmp)

        #Slower method without assignment expressions, for Python 3.7-
        lines = self.lines
        data = Mesh()
        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        joinPS = self._joinPS
        ps = self.preserveSpacing
        ud = self.useDecimal
        _ParamInInp = self._ParamInInp
        for ind, line in enumerate(lines):
            if not cfc(line) and line !='':
                node = Node(dataline=line, _joinS=joinPS, _ParamInInp=_ParamInInp, preserveSpacing=ps, useDecimal=ud)
                data[node.label] = node
            else:
                handleComment(line, ind)
        return data
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataParameter(self):
        r"""_parseDataParameter()
        
            Parses the datalines of \*PARAMETER keyword blocks.

            This function parses the datalines of \*PARAMETER keyword blocks. In addition to filling :attr:`~inpKeyword.inpKeyword.data`
            of the keyword block, this function will execute all the parameter functions and store the results in
            :attr:`~inpKeyword.pd` using the parameter name as the key. All comments are stored in 
            :attr:`~inpKeyword.inpKeyword.comments`.

            Returns:
                list: A list of lists containing the data for the keyword block.
        """

        from math import acos, asin, atan, cos, log, log10, pi, sin, sqrt, tan
        lines = self.lines
        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        ps = self.preserveSpacing
        ud = self.useDecimal
        pd = self.pd
        data = [[eval2(i, t=str, ps=ps, useDecimal=ud)] if i != '' and not cfc(i) and i.strip(' ')[0] != '#' else handleComment(i, ind) for ind, i in enumerate(lines)]
        tmp = self.comments[:]
        tmp.reverse()
        for comment in tmp:
            del data[comment[0]]
        for line in data:
            PARAMDATA = line[0]
            w = PARAMDATA.strip(' ')
            if w!= '' and w[:2] != '**' and w[0] != '#':
                del w
                try:
                    PARAMDATA = PARAMDATA.split('#')[0]
                    PARAMDATA = PARAMDATA.split(';')
                    for item in PARAMDATA:
                        PARAMKEY,PARAMVALUE = item.strip(' ').split('=')
                        exec('%s = %s' % (PARAMKEY, PARAMVALUE), globals(), locals())
                        pd[PARAMKEY] = eval(PARAMVALUE)
                except:
                    traceback.print_exc()
                    print([PARAMKEY, PARAMVALUE])
        return data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataRebarLayer(self):
        r"""_parseDataRebarLayer()
        
            Parses the datalines of \*REBAR LAYER keyword blocks.

            This function parses the datalines of \*REBAR LAYER keyword blocks. In addition to filling :attr:`~inpKeyword.inpKeyword.data`
            of the keyword block, this function will add the rebar layer names to :attr:`~inpKeyword._namedRefs`. 
            All comments are stored in :attr:`~inpKeyword.inpKeyword.comments`.
            
            Returns:
                list: A list of lists containing the data for the keyword block.
        """

        def setNamedRefs(dataline, nr):
            """ """

            nr.setdefault('rebarlayer', csid([[dataline[0], self]]))

        lines = self.lines
        nr = self._namedRefs
        setnr = setNamedRefs

        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        
        ps = self.preserveSpacing
        ud = self.useDecimal
        data = []
        dataapp = data.append
        for ind,line in enumerate(lines):
            if not cfc(line):
                dataline = [eval2(j, t=int, ps=ps, useDecimal=ud) for j in line.split(',')]
                dataapp(dataline)
                setnr(dataline, nr) #Will add rebar layer name and block to self._namedRefs['rebarlayer']
            else:
                handleComment(line, ind)
        #tmp = self.comments[:]
        #tmp.reverse()
        #for comment in tmp:
        #    breakpoint()
        #    del data[comment[0]]        
        return data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataSet(self):
        r"""_parseDataSet()

            Parses the \*NSET and \*ELSET keyword blocks.
        
            This is a special method for parsing \*NSET and \*ELSET keyword blocks. For keyword blocks with 100 or more 
            datalines, all items are assumed to be integers (i.e. labels). If items are not labels (i.e. set names), 
            they will be treated as strings. This should increase the performance of the code for very large set keyword 
            blocks, while hurting performance for sets defined by referencing existing sets (which should not have many 
            datalines). For blocks with less than 100 datalines, :func:`_parseDataGeneral` will be called on lines, 
            as this will avoid raising Exceptions in :func:`eval2` if a data item is not an integer. All comments are 
            stored in :attr:`~inpKeyword.inpKeyword.comments`.

            Returns:
                list: A list of lists containing the data for the keyword block.
        """

        lines = self.lines
        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        ps = self.preserveSpacing
        ud = self.useDecimal
        if len(lines) < 100:
            data = self._parseDataGeneral()
        else:
            data = [[eval2(j, t=int, ps=ps, useDecimal=ud) for j in i.split(',')] if not cfc(i) else handleComment(i, ind) for ind, i in enumerate(lines)]
            tmp = self.comments[:]
            tmp.reverse()
            for comment in tmp:
                del data[comment[0]]
        return data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseDataSurface(self):
        r"""parseDataSurface()

            Parses \*SURFACE keyword blocks.
        
            This is a special method for parsing \*SURFACE keyword blocks. It provides a fast method for TYPE=ELEMENT and
            TYPE=NODE, which should have much more data then the other types. It has an optimized path if len(lines) > 100.
            Otherwise, it simply calls :func:`_parseDataGeneral` on the data. All comments are stored in 
            :attr:`~inpKeyword.inpKeyword.comments`.
            
            Returns:
                list: A list of lists containing the data for the keyword block.
        """
        
        lines = self.lines
        if hasattr(self, '_data'):
            handleComment = self._handleCommentSub
        else:
            handleComment = self._handleComment
        ps = self.preserveSpacing
        ud = self.useDecimal

        if len(lines)>100: #assumes that anything big will be using element labels in field 0. If small, call _parseDataGeneral to avoid triggering Exceptions in eval2
            #Faster method using assignment expressions, for Python 3.8+ only
            #data = [[eval2((j := i.split(","))[0], t=int, ps=ps)] + [eval2(k, t=str, ps=ps) for k in j[1:]]  if not cfc(i) else i for i in lines]
            
            #Slower method without assignment expressions, for Python 3.7-
            data = []
            dataapp = data.append
            for ind,line in enumerate(lines):
                if not cfc(line):
                    j = line.split(',')
                    dataapp([eval2(j[0], t=int, ps=ps, useDecimal=ud)] + [eval2(k, t=str, ps=ps, useDecimal=ud) for k in j[1:]])
                else:
                    handleComment(line, ind)
        else:
            data = self._parseDataGeneral()
        return data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseInputString(self, inputString='', parseKwLine=True):
        r"""_parseInputString(inputString='', parseKwLine=True)
        
            This function will split the :attr:`~inpKeyword.inputString` attribute on new lines, and will identify the 
            keyword line (calling subfunctions to handle the tasks). It will populate the :attr:`~inpKeyword.name` and
            :attr:`~inpKeyword.parameter` attributes, and it will return a list of strings corresponding to the data lines.

            If :attr:`~inpKeyword._debug` is not True and *parseKwLine* is True, this function will set 
            :attr:`~inpKeyword.inputString` to '' upon completion as a means to reduce memory consumption.
            
            Args:
                inputString (str): A single string (with new line characters) composing the entirety of the keyword block.
                    If *inputString* is not specified (thus ''), this function will parse :attr:`inputString`. Defaults to ''.
                parseKwLine (bool): If True, this function will parse the keyword line. Setting this to False will simply
                    split the string into separate lines (used mainly for keyword blocks with no keyword line, which
                    :mod:`inpKeyword` does internally to house data read from sub files). Defaults to True.

            Returns:
                list: A list of strings corresponding to the datalines. The keyword line(s) will not be output if *parseKwLine* = True.
        """

        if inputString == '':
            inputString = self.inputString
        lines = re14.split(inputString)
        if parseKwLine:
            
            #This block checks for any whitespace prior to the * character in the keyword line
            line0split = re18.split(lines[0])
            if len(line0split) == 1:
                pass
            else:
                lines[0] = line0split[-1]
                self._leadstr = line0split[1]

            if lines[0][0]=='*':
                kwlines = [lines.pop(0)]
                m = kwlines[0].rsplit(',',1)
                if not re1.search(m[-1]):
                    _kwLineSep = [',' + m[-1] + '\n']
                    while True:
                        try:
                            kwlines.append(lines.pop(0))
                        except IndexError:
                            break
                        m2 = kwlines[-1].rsplit(',',1)
                        if re1.search(m2[-1]):
                            _kwLineSep.append('') #added to help writing out string
                            break
                        else:
                            kwlines[-1] = kwlines[-1][::-1].replace(m2[-1][::-1] + ',', '', 1)[::-1] # reverse string, remove m2[-1] reversed and 1 comma, reverse string again
                            _kwLineSep.append(',' + m2[-1] + '\n')
                    self._kwLineSep = _kwLineSep
                    self._parseKWLine(m[0])
                else:
                    self._parseKWLine(kwlines[0])
                if len(kwlines)>1:
                    _parameterLines = [list(self.parameter.keys())]
                    if not self.parameter.keys():
                        self._kwLineSep[0] = m[-1] + '\n' # special case for multi-line keyword with no parameters on first line, to prevent extra comma 
                    for item in kwlines[1:]:
                        tmpd = createParamDictFromString(item)
                        _parameterLines.append(list(tmpd.keys()))
                        self.parameter.update(tmpd)
                    self._parameterLines = _parameterLines
        self._setMiscInpKeywordAttrs()
        if not self._debug:
            self.inputString = ''
        return lines

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseKWLine(self, line):
        r"""_parseKWLine(line)
            
            Populates :attr:`~inpKeyword.inpKeyword.name` and :attr:`~inpKeyword.inpKeyword.parameter`
            from the keyword line string. This function will also set :func:`~inpKeyword._parseData` and :func:`~inpKeyword.formatData`
            based on :attr:`~inpKeyword.name`.

            This function is meant to be called by :func:`_parseInputString`. 
            
            Args:
                line (str): A string containing the entirety of the keyword line, but only a single line. 
                    :func:`_parseInputString` will handle parameters on subsequent lines for keyword lines which span
                    multiple lines.
        """


        kwlinep = line.split(',', 1) # keyword line and parameters
        self.name = kwlinep[0][1:] # keyword name
        try:
            self.parameter = createParamDictFromString(kwlinep[1], ps=self.preserveSpacing, useDecimal=self.useDecimal)
        except IndexError:
            pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _parseSubData(self, subName, parentKwLine=''):
        r"""_parseSubData(subName, parentKwLine='')
        
            Populates the :attr:`~inpKeyword.data` attributed of a keyword block by reading from *subName*.
            
            This function is meant to be called as part of :func:`~inpKeyword._parseData`, as that function will handle 
            some organizational operations. See that function for more details.
            
            This function will only be called if :attr:`~inpKeyword.parseSubFiles` is True.
            
            Args:
                subName (str): A string representing the sub-file from which to read. This should taken from the INPUT
                    parameter of the parent :class:`~inpKeyword` block.
                parentKwLine (str): A string representing the keyword line of the parent :class:`~inpKeyword` block.
                    This is only used to print some information, so it is not strictly necessary. Defaults to ''.
        """
        
        subName = subName
        fileName = f'{self.inputFolder}{subName}' 
        #print('\n Reading data for block %s from file %s' % (parentKwLine, fileName))
        with open(fileName, 'r', newline=self._nl, encoding=_openEncoding) as subFile:
            self.inputString = subFile.read()
        self.lines = self._parseInputString(parseKwLine=False)
        data = self._parseData()
        self.data = data
        #breakpoint()
        #if isinstance(data, list):
        #    self.data.extend(data)
        #else:
        #    self.data.update(data)
        self._dataParsed = True
        del self.lines

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _populateRebarLayerNamedRefs(self):
        r"""_populateRebarLayerNamedRefs() 
        
            This function will populate :attr:`_namedRefs` with the \*REBAR LAYER names and a reference to this 
            :class:`inpKeyword`. 
            
            This function should only be called if you directly specify the :attr:`data` attribute of the block, and
            not if you created the block by parsing *inputString*. The parsing method will automatically perform the
            same operation.
        """

        def setNamedRefs(dataline, nr):
            """setNamedRefs(dataline, nr)
            
                Args:
                    dataline (list)
                    nr: self._namedRefs"""
            nr.setdefault('rebarlayer', csid([[dataline[0], self]]))

        nr = self._namedRefs
        setnr = setNamedRefs
        for dataline in self.data:
            setnr(dataline, nr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _setMiscInpKeywordAttrs(self):
        r"""_setMiscInpKeywordAttrs(parentInp) 
        
            This function should be called after the :attr:`~inpKeyword.inpKeyword.name` and :attr:`parameter`
            attributes have been set. It will set :func:`_parseData`, :func:`formatData`, and set and populate the 
            appropriate items for :attr:`_inpItemsToUpdate`.
            
            This function is called by :func:`_parseKWLine`, and thus automatically if :class:`inpKeyword` is
            instanced with the *inputString* parameter specified. It should be called manually if the :class:`inpKeyword` 
            is created without parsing *inputString*.
        """

        nr = self._namedRefs
        nrsetdefault = nr.setdefault
        name = rsl(self.name)
        #Sets defaults data parsing and formatting functions for all keyword types. Specific keywords in the following section will override these functions.
        self._parseData = self._parseDataGeneral
        self.formatData = self._formatDataOutput

        def namedRefsSetName(block):

            itemname = block.parameter.get('name')
            if itemname != None:
                dummy = block._namedRefs.setdefault(rsl(block.name), csid([[itemname, block]]))

        #Set attributes specific to each keyword type
        if name in {'heading', 'endstep'}:
            self._parseData = self._parseDataHeading
            self._inpItemsToUpdate = {}

        elif name == 'parameter':
            self._parseData = self._parseDataParameter
            self._inpItemsToUpdate = {'pd': self.pd}

        elif name == 'rebarlayer':
            self._parseData = self._parseDataRebarLayer

        elif name in {'elset', 'nset'}:
            if name == 'nset':
                nset = self.parameter['nset']
                dummy = nrsetdefault('nset', csid([[nset, self]]))
            elif name == 'elset':
                elset = self.parameter['elset']
                dummy = nrsetdefault('elset', csid([[elset, self]]))
            self._parseData = self._parseDataSet
        
        elif name =='elgen':
            elset = self.parameter.get('elset')
            if elset:
                dummy = nrsetdefault('elset', csid([[elset, self]]))

        elif name =='ngen':
            nset = self.parameter.get('nset')
            if nset:
                dummy = nrsetdefault('nset', csid([[nset, self]]))

        elif name == 'surface':
            tmp = self.parameter.get('type')
            if not rsl(tmp) in {'node', 'element'}:
                pass
            else:
                self._parseData = self._parseDataSurface
            namedRefsSetName(self)

        elif name == 'rigidbody':
            tmp = self.parameter.get('analytical surface')
            if tmp != None:
                dummy = nrsetdefault('rigidbody', csid([[tmp, self]]))

        elif name == 'rigidsurface':
            tmp = self.parameter.get('name')
            if tmp != None:
                dummy = nrsetdefault('surface', csid([[tmp, self]]))

        elif name == 'contactpair':
            tmp = self.parameter.get('cpset')
            if tmp != None:
                dummy = nrsetdefault('contactpair', csid([[tmp, self]]))

        elif name == 'node':
            nset = self.parameter.get('nset')
            if nset:
                dummy = nrsetdefault('nset', csid([[nset, self]]))
            self.data = Mesh()
            self._parseData = self._parseDataNode
            self.formatData = self._formatDataLabelDict
            self._inpItemsToUpdate = {'nd': self.data, 'namedRefs': self._namedRefs}

        elif name == 'element':
            elset = self.parameter.get('elset')
            if elset:
                dummy = nrsetdefault('elset', csid([[elset, self]]))
            self.data = Mesh()
            self._nd = Mesh() 
            self._parseData = self._parseDataElement
            self.formatData = self._formatDataLabelDict
            self._inpItemsToUpdate = {'ed': self.data, 'namedRefs': self._namedRefs, 'nd_ed': self._nd}
        
        else:
            namedRefsSetName(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _yieldInpRWItemsToUpdate(self):
        r"""_yieldInpRWItemsToUpdate():
            
            Yields the items in :attr:`~inpKeyword._inpItemsToUpdate`.
            
            The items to yield are set according to the keyword :attr:`~inpKeyword.name` in :func:`~inpKeyword._parseKWLine`.
            They will be populated as part of the parsing function. These items are needed by the :class:`inpRW.inpRW` 
            for further operations, and will be adding when the :class:`~inpKeyword` block is inserted into the 
            :class:`~inpKeywordSequence`.
            
            Yields:
                dict
        """
        
        for items in self._inpItemsToUpdate.items():
            yield items

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __getattr__(self, name):
        r"""__getattr__(name) 
        
            Overrides the default behavior for cases where :attr:`~inpKeyword.data` and :attr:`~inpKeyword.comments`
            are not defined (i.e. when the keyword block reads data from a sub file).

            See :meth:`~object.__getattr__` for more information.
            
            Args:
                name (str): The name of the attribute to retrieve.
                
            Returns:
                list: A list containing the :attr:`~inpKeyword.data` or :attr:`~inpKeyword.comments` from 
                  :attr:`~inpKeyword._data` and :attr:`~inpKeyword._subdata`.
                 
            Raises:
                AttributeError: Will be raised if :class:`inpKeyword` does not have attribute *name*, unless 
                  *name* is 'data' or 'comments'.
        """
        
        if name == 'data':
            data = self._data.data
            if isinstance(data, list):
                return data + self._subdata.data
            elif isinstance(data, dict):
                tmpdata = data.copy()
                tmpdata.update(self._subdata.data)
                return tmpdata
        elif name == 'comments':
            return self._data.comments + self._subdata.comments
        else:
            raise AttributeError(f"'inpKeyword' object has no attribute {name}")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self, includeSubData=True):
        r"""__str__(includeSubData=True)

            Produces a string representation from the object in valid Abaqus formatting. All data of this
            :class:`inpKeyword` instance will be fully expanded.

            The *includeSubData* parameter defaults to True and cannot be accessed by the user when using built-in Python
            functions like :class:`str` or :func:`print`. You must specifically call ``block.__str__(includeSubData=False)``
            if you need to modify this parameter. :func:`~inpRW._inpW.Write.writeBlocks` sets this to False to prevent
            writing the :attr:`_subdata` with the main keyword block; the :attr:`_subdata` will instead be written to
            the proper subfile.

            Args:
                includeSubData (bool): If True, the string of this :class:`inpKeyword` will include all sub data. Defaults
                    to True.
            
            Returns:
                str
        """

        name = self.name.lower().replace(' ', '')
        if self._dataParsed:
            data = self.formatData(includeSubData=includeSubData)
        elif self.data:
            data = self.formatData(includeSubData=includeSubData)
            self._dataParsed = True
        elif hasattr(self, 'lines'):
            data = [f'\n{line}' for line in self.lines]
        else:
            data = ['']
        if not 'dummy-manifest' in name:
            keywordLine = self.formatKeywordLine()
        output = ''.join(list(flatten([keywordLine] + data)))
        return output

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self, expand=False):
        r"""__repr__(expand=False)

            Produces a string representation of the :class:`inpKeyword` object. 
            
            By default, this will not expand :attr:`suboptions` or the entirety of :attr:`data` if len(:attr:`data`)>10. 
            Set *expand* = True to display the entirety of :attr:`data` and all :attr:`suboptions` and their :attr:`suboptions`.
            Be aware that the block could contain an enormous amount of information.
            
            Args:
                expand (bool): If True, print the entire contents of the :class:`inpKeyword`. Defaults to False.
                
            Returns:
                str
        """
        
        if expand:
            return '{}(name={!r}, parameter={!r}, data={!r}, path={!r}, comments={!r}, suboptions={!r})'.format(self.__class__.__name__, self.name, self.parameter, self.data, self.path, self.comments, self.suboptions)
        else:
            try:
                tmpdata1 = self.data
            except AttributeError:
                tmpdata1 = []
            if len(tmpdata1)>10:
                if isinstance(tmpdata1, dict):
                    tmpdata = list(tmpdata1.items())[0:10]
                else:
                    tmpdata = tmpdata1[:10]
                tmpdata.append('...')
            else:
                tmpdata = tmpdata1
            if self.suboptions:
                return '{}(name={!r}, parameter={!r}, data={!r}, path={!r}, comments={!r}, suboptions=[...] Len {})'.format(self.__class__.__name__, self.name, self.parameter, tmpdata, self.path, self.comments, len(self.suboptions))
            else:
                return '{}(name={!r}, parameter={!r}, data={!r}, path={!r}, comments={!r}, suboptions={!r})'.format(self.__class__.__name__, self.name, self.parameter, tmpdata, self.path, self.comments, self.suboptions)