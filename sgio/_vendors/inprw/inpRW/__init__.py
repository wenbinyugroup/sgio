#Copyright © 2023 Dassault Systemès Simulia Corp.

# cspell:includeRegExp comments

from ._importedModules import *
from . import _inpR
from . import _inpW
from . import _inpMod
from . import _inpFind
from . import _inpFindRefs
from . import _inpCustom
from ..inpKeywordHelper import inpKeywordHelper, inpKeywordInit
#from inpKeywordInit import inpKeywordInit

#To do
#Add inpDiff function
#Investigate moving the op1, op2, etc. calculations of mesh._parseDataLine to the mesh._parseDataLines function.
#Add function to generate .inpsum
#Modify functions that operate on/search for keyword data to check if the keyword data is parsed before operating.
#Enhance inpDecimal and inpInt so operations produce these types, with the same total character length
#Update installation instructions to make it clear that the source code does not include the .whl files
#Treatment of blank input files, use None as a path
#Check for overconstrained nodes and remove them from one constraint
#Need to add ngen to node dictionary
#volume searching for set/surface creation, box, sphere, etc.
#nodal coordinate calculation should account for *SYSTEM or *ASSEMBLY-type keywords
#element centroid and normal calculations
#Modify_inpMod._createFlatNodeElementGroups to only add section information
#Add function to renumber nodes and elements
#Add functions for un/commenting keyword blocks
#Add function to perform partial keyword and parameter matches
#Add a function to write sets using GENERATE parameter via the ranges function
#Convert breakable bonds (*BOND) to fasteners?


#==================================================================================================================
class inpRW(_inpR.Read, _inpW.Write, _inpMod.Mod, _inpFind.Find, _inpFindRefs.FindRefs, _inpCustom.Custom):
    """inpRW is a collection of Python modules for parsing, modifying, and writing Abaqus input files. 
    
        The inpRW class is composed of :mod:`~inpRW._inpR`, :mod:`~inpRW._inpW`, :mod:`~inpRW._inpMod`, :mod:`~inpRW._inpFind`, 
        :mod:`~inpRW._inpFindRefs`, :mod:`~inpRW._inpCustom`, and :mod:`~inpRW._importedModules`. :mod:`~inpRW._inpR` 
        has the functions for parsing data from the .inp. :mod:`~inpRW._inpW` has functions for writing the data in 
        the :class:`.inpKeyword` object to an input file. :mod:`~inpRW._inpMod` has functions for modifying the 
        data in the inp object structure. :mod:`~inpRW._inpFind` has functions for finding information in 
        :attr:`~inpRW.inpRW.keywords`. :mod:`~inpRW._inpFindRefs` has functions to search for particular named
        items and all their references in the input file (i.e. node 1). :mod:`~inpRW._inpCustom` is empty; whatever 
        functions the end user adds to this module will extend the class. :mod:`~inpRW._importedModules` contains 
        the module imports for all the _inp* modules."""
                
    from ..config import (_slash, _openEncoding, _supFilePath, _elinfopath, _elementTypeDictionary, _mergeDatalineKeywordsOP, 
                        _appendDatalineKeywordsOP, _dofXtoYDatalineKeywordsOP, _opKeywords, _subBlockKWspath, _subBlockKWs, _keywordNamespath,
                        _allKwNames, _EoFKWs, _dataKWs, _EndKWs, _generalSteps, _perturbationSteps, _keywordsDelayPlacingData, _maxParsingLoops)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, inpName, organize=True, ss=False, rmtrailing0=False, jobSuffix='_NEW.inp', parseSubFiles=True, preserveSpacing=True, useDecimal=True, _parentINP='', _parentblock='', _debug=False):
        """__init__(inpName, organize=True, ss=False, rmtrailing0=False, jobSuffix='_NEW.inp', parseSubFiles=True, preserveSpacing=True, useDecimal=True, _parentINP='', _parentblock='', debug=False)
            
            :func:`__init__` is called when :class:`inpRW` is instanced and it sets many instance variables before the input file is parsed.
            
            Args:
                inpName (str): The file name and optionally path to the input file.
                organize (bool): Will group keywords together as parentblock and suboptions if True. Defaults to True.
                ss (bool): Strip spaces from items in input file if True. Defaults to False.
                rmtrailing0 (bool): Remove trailing 0s from decimal numbers if True. Defaults to False.
                jobSuffix (str): Suffix to be appended to each input file (and reference to input files) that inpRW writes out. Defaults to '_NEW.inp'.
                parseSubFiles (bool): Parse sub input files (i.e. target of INCLUDE) if True. Defaults to False.
                preserveSpacing (bool): Preserve the original spacing for every item in the input file if True. Defaults to True.
                useDecimal (bool): If True, :class:`~decimal.Decimal` (or :class:`inpDecimal` if *preserveSpacing* = True) will be used instead of :class:`float` for all floating point numbers. Will be True if :attr:`preserveSpacing` is True. Defaults to True.
                _parentInp (inpRW): An :class:`inpRW` instance to serve as the parent for the new instance. Meant to be used when :class:`inpRW` instances itself recursively to handle child input files (i.e. \*INCLUDE).
                _parentblock (inpKeyword): An inpKeyword block which will serve as the parent to the new :class:`inpRW` instance. All keywords in the child inp will be suboptions to _parentblock.
                _debug (bool): If True, prints some additional information while inpRW is performing certain tasks and keeps :attr:`~inpRW.inpRW._kw` after parsing the input file. Defaults to False.
               
            Returns:
                :class:`inpRW` instance"""

        self._parentINP = _parentINP #: :inpRW: References the parent inp instance if this is reading a sub input file (i.e. \*INCLUDE, \*MANIFEST). This is needed to track some variables from the parent instance.
        self._parentblock = _parentblock #: :inpKeyword: References the parent block. All keyword blocks read by a child inpRW instance will be suboptions of _parentblock.

        if not self._parentINP:
            self.keywords = inpKeywordSequence() #: :inpKeywordSequence: Holds all the parsed keyword blocks. This is the main point of interaction for the user.
            self.nd = self.keywords._nd #: :TotalNodeMesh: Node dictionary. A dictionary type object which contains every node in the input file. :attr:`nd` is populated from :class:`~mesh.Mesh`, which make up the :attr:`~inpKeyword.inpKeyword.data` attribute of \*NODE keyword blocks. When operating on nodes, the user should access them through :attr:`nd`. When adding new nodes, they should be added to an existing :class:`~mesh.Mesh`, or create a new \*NODE keyword block with a new :attr:`~inpKeyword.inpKeyword.data`, and then update :attr:`nd` with the :attr:`~inpKeyword.inpKeyword.data` of the new block.
            self.ed = self.keywords._ed #: :TotalElementMesh: Element dictionary. Identical in concept to :attr:`nd`, but holds element information. See :attr:`nd` for further details.
            self.pd = self.keywords._pd #: :csid: Parameter dictionary, uses each variable defined in \*PARAMETER block datalines as the key, the value is the evaluated result. If the user needs the value of a group of items which may reference parameters, call :py:func:`~inpRW._inpR.Read._subParam` on the group of objects. Defaults to csid().
            self._manBaseStep = None #: :inpKeyword: The last base step for \*MANIFEST simulations. Defaults to None
            self._curBaseStep = None #: :inpKeyword: Tracks the current base step in the model. Defaults to None
            self._delayedPlaceBlocks = self.keywords._delayedPlaceBlocks #: :dict: Tracks blocks that should be parsed on later passes. Any blocks placed into :attr:`~inpRW.inpRW._delayedPlaceBlocks` will have the data in their :attr:`~inpKeyword.inpKeyword._inpItemsToUpdate` inserted at the end of the :func:`~inpRW.inpRW.parse` function. For example, \*PARAMETER keyword blocks should have their data placed before all other blocks (loop 0), and all \*NODE blocks should have their data populated before any \*ELEMENT blocks are placed. Unless otherwise specified in :attr:`~config._keywordsDelayPlacingData`, all blocks will have their data placed in loop 1. Defaults to {0: [], 1: [], 2: []}
            
            #Set variables that should be overridden when parse() is called
            self._nl = '\n'
            self._ParamInInp = False #: :bool: If True, indicates that \*PARAMETER is a keyword block in the input file. Will be set in :func:`parse`. Defaults to False

            #Assign input parameters to instance variables
            try:
                self.inpName = inpName.rsplit(self._slash,1)[1] #: :str: Name of the input file without extension.
                self.inputFolder = inpName.rsplit(self._slash,1)[0] + self._slash #: :str: Name of the folder containing the input file, populated automatically if *inpName* passed to :class:`inpRW` includes a path.
                self.outputFolder = inpName.rsplit(self._slash,1)[0] + self._slash #: :str: Name of the folder to which new input files will be written, populated automatically if *inpName* passed to :class:`inpRW` includes a path.
            except IndexError:
                self.inpName = inpName
                self.inputFolder = ''
                self.outputFolder = ''
            self._kwsumName = f'{self.inpName}sum' #: :str: Name of the file to which a summary of the parsed keyword blocks will be written. Defaults to inpName.inpsum
            #self._kwsumFile = open(self.inputFolder + self._kwsumName, 'w', encoding=self._openEncoding) #: :: File object to which a summary of the parsed keyword blocks will be written. Reference :term:`file object`.
            self._tree = None #: :scipy.spatial.cKDTree: A KDTree of some portion of the nodes in the input file. Created via :func:`~inpRW._inpFind.Find.findCloseNodes`. Defaults to None
            
        else:
            self.nd = self._parentINP.nd
            self.ed = self._parentINP.ed
            self.pd = self._parentINP.pd
            self._manBaseStep = self._parentINP._manBaseStep
            self._curBaseStep = self._parentINP._curBaseStep
            self._delayedPlaceBlocks = self._parentINP._delayedPlaceBlocks
            try:
                self.inpName = inpName.rsplit(self._slash,1)[1]
                self.inputFolder = inpName.rsplit(self._slash,1)[0] + self._slash
                self.outputFolder = inpName.rsplit(self._slash,1)[0] + self._slash
            except IndexError:
                self.inpName = inpName
                self.inputFolder = self._parentINP.inputFolder
                self.outputFolder = self._parentINP.outputFolder
            #self._kwsumName = self._parentINP._kwsumName
            #self._kwsumFile = self._parentINP._kwsumFile
            #self.keywords = self._parentINP.keywords
            self.keywords = inpKeywordSequence()
            self._tree = self._parentINP._tree
        self._numCpus = 1 #: :int: Indicates the number of cpus to use for multi-threaded supported tasks, which is currently parsing keyword blocks. It is not recommended to use more than 1 cpu, as the current speedup does not justify the extra hardware use. Defaults to 1
        self.organize = organize #: :bool: If True, keyword blocks will be grouped together as parent blocks and suboptions. Defaults to True
        if self.organize==True:
            self._parentkws = [] #: :list: Tracks the open parent keyword blocks. Defaults to []
        
        self.ss = ss #: :bool: Strip spaces from strings. Defaults to False.
        if self.ss:
            self._addSpace = ' ' #: :str: Adds a space between items when :attr:`ss` is True.
        else:
            self._addSpace = ''
        self._joinPS = f',{self._addSpace}' #: :str: The string which is used to join items together when writing strings from the parsed data. If :attr:`ss` is True, this will be ', ', else it is '' (spaces are assumed to be tracked with each item in this case).
        
        
        self.rmtrailing0 = rmtrailing0 #: :bool:  Remove the trailing 0s (i.e. 1.0 -> 1.) to reduce file-size. Defaults to False
        self.jobSuffix = jobSuffix #: :str: Suffix to append to each new input file. This should include the file extension. Defaults to '_NEW.inp' 
        self.parseSubFiles = parseSubFiles #: :bool:  Parse sub input files if True. Defaults to True
        self.preserveSpacing = preserveSpacing #: :bool:  Preserve the exact spacing in the input file if true. If that is not important, set to False for a performance improvement. Defaults to True
        if self.preserveSpacing == True:
            self.useDecimal = True #: :bool: Use :class:`~decimal.Decimal` for all floating point numbers if True. Will be True if :attr:`preserveSpacing` is True. Defaults to True
        else:
            self.useDecimal = useDecimal
        self._debug = _debug #: :bool: Stores debug mode status.
        
        #Set default values of instance attributes users might wish to access
        self.includeFileNames = [] #: :list: Contains the names of all input files referenced by this input file. This will be populated as the input file is parsed. Defaults to [].
        self.includeBlockPaths = [] #: :list: Contains the paths to all keyword blocks which reference child input files. This will be populated as the input file is parsed. Defaults to [].
        self.fastElementParsing = True #: :bool: Parse element blocks with the fast mode if True and if the number of nodes to define the element type is less than 10. Defaults to True.
        self._kw = [] #: :list: A list of strings, with each string corresponding to a keyword block. If :attr:`~inpRW.inpRW._debug` = False, :attr:`_kw` will be deleted once all blocks have been parsed.
        self.ktridd = set() #: :set: A :class:`set` containing the Keywords To Remove If Data Deleted from them. Meant to be used with :func:`~inpRW._inpMod.Mod.deleteItemReferences`. Can be updated with :func:`~inpRW._inpMod.Mod.updateKTRIDD`. Defaults to set()
        self.pktricd = csid() #: :csid: A :class:`csid` containing the Parent Keywords To Remove If Child Deleted. Meant to be used with :func:`~inpRW._inpMod.Mod.deleteItemReferences`. Can be set with :func:`~inpRW._inpMod.Mod.updatePKTRICD`. Defaults to csid()
        self._couplingSurfNames = set() #: :set: A set to track the surface names which are used by \*COUPLING keywords.
        self._kinCoupNsetNames = set() #: :set: A set to track the nset names which are used by \*KINEMATIC COUPLING keywords.
        self._distCoupElsetNames = set() #: :set: A set to track the elset names which are used by \*DISTRIBUTING COUPLING keywords.
        self.delayParsingDataKws = set() #: :set: A set for the user to specify the element names which will not have their keywords parsed. The keyword names should be all lower case and include no spaces.
        self._timeout = 300


        self._subP = False #: :bool: When evaluating particular items, check if item is a parameter and substitute the true value. If the input file has \*PARAMETER keyword block, this will be set to True automatically. Defaults to False.

        #Set default values of instance attributes user should not need to access
        self._leadingcomments = None #: :str: Stores any comments prior to the first keyword block. Defaults to None
        self._firstItem = True #: :bool: Tracks the first item to be written to an output input file; a new line character will not be written prior to the item if True. Defaults to True
        self._subkwin = 0 #: :int: Tracks the active suboptions index. Defaults to 0
        self._bad_kwblock = [] #: :list: For development purposes. Defaults to []

        self.namedRefs = self.keywords._namedRefs #: :csid: A :class:`csid` to track references to named objects. The keys will be the names of keyword blocks which can create named references. For example, 'NSET'. Each value will be the block which defines the named reference. This :class:`csid` will be populated during :func:`~inpRW.inpRW.parse`.
        self.nodesUpdatedConnectivity = [] #: :list: Tracks nodes which have had their connectivity updated (i.e. they are connected to fewer elements than they previously were, likely due to the user running :func:`~inpRW._inpMod.Mod.deleteItemReferences`).

        #Set __methods__ and __members__
        self.__methods__ = [i for i in dir(self) if callable(getattr(self, i))] #: :list: Contains all the callable functions that are part of inpRW.
        self.__members__ = [i for i in dir(self) if i not in self.__methods__] #: :list: Contains all the attributes of inpRW.

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parse(self):
        """parse()
            
            This function parses the input file."""

        t1 = timing.time()
        with open(self.inputFolder + self.inpName, 'r', newline='', encoding=self._openEncoding) as self.inp:
            try:
                self._lcpattern = self._getLeadingCommentsPattern()
                self._inpText = self.inp.read() #: :str: Holds the raw text string of the entire input file. Will be deleted once :attr:`_kw` is generated unless :attr:`_debug` = True
                self._nl = self.inp.newlines #: :str: Tracks the new line character used by the file. If new line characters are inconsistent, :attr:`_nl` will be set to '\\n'.
            except UnicodeDecodeError:
                traceback.print_exc()
                print('\nCould not read file with encoding %s. Recommend setting self._openEncoding to another codec from https://docs.python.org/3/library/codecs.html#standard-encodings \
and trying to parse the file again. Once you have found the proper codec, you are recommended to set self._openEncoding to "utf-8" prior to writing \
the new input files, so it will be easier to manage the new files in the future. Check the resulting files to ensure the conversion was correct.' % (self._openEncoding))
                return None
        if isinstance(self._nl, tuple):
            print('WARNING: Inconsistent End of Line characters in %s: %s. \nRereading input file converting new line characters and using LF on the output. Correct the file to avoid this in the future.' % (self.inputFolder+self.inpName, self._nl))
            with open(self.inputFolder + self.inpName, 'r', encoding=self._openEncoding) as self.inp:
                self._lcpattern = self._getLeadingCommentsPattern()
                self._inpText = self.inp.read()
            self._nl = '\n'
        self._ParamInInp = re.search('\*PARAMETER', self._inpText, re.IGNORECASE)
        print(f'\nSplitting string of input file from {self.inputFolder}{self.inpName} into strings representing each keyword block.\n')
        self._splitKeywords() #generates self._kw
        self._kw = [i for i in self._kw if i !=''] 
        kwappend = self.keywords.append
        readInclude = self._readInclude
        readManifest = self._readManifest
        organize = self.organize
        self.inpKeywordArgs = {'preserveSpacing': self.preserveSpacing, 'useDecimal': self.useDecimal, #: :dict: A dictionary containing the attributes from :class:`~inpRW.inpRW` that should be passed to the :class:`~inpKeyword.inpKeyword` constructor. 
                                '_ParamInInp': self._ParamInInp, 'fastElementParsing': self.fastElementParsing, '_joinPS': self._joinPS,
                                'parseSubFiles': self.parseSubFiles, 'delayParsingDataKws': self.delayParsingDataKws,
                                'inputFolder': self.inputFolder, '_nl': self._nl, 'rmtrailing0': self.rmtrailing0, '_debug': self._debug}
        inpKWArgs = self.inpKeywordArgs

        numKwBlocks = len(self._kw)
        print(f'\nParsing {numKwBlocks} keyword blocks using {self._numCpus} cores.')
        if self._numCpus == 1:
            jobs = (inpKeyword(rawstring, createSuboptions=False, **inpKWArgs) for rawstring in self._kw)
        else:
            chunksize = max(int(numKwBlocks / self._numCpus / 128), 1)
            pool = mp.Pool(self._numCpus, initializer=inpKeywordInit, initargs=(self._kw, inpKWArgs))
            jobs = pool.imap(inpKeywordHelper, range(len(self._kw)), chunksize=chunksize)
            pool.close()
            pool.join()
            print(f'  Parsing complete. Time to parse = {timing.time()-t1}. Organizing keyword blocks.')
        if self._ParamInInp:
            self._loop = 0
        else:
            self._loop = 1
        #Start of the block organization loop
        for ind, block in enumerate(jobs):
            Printer(f'Organizing block {ind}')
            name = rsl(block.name)
            kd = self._keywordsDelayPlacingData.get(name)
            if kd == None:
                kd = 1
            if kd == self._loop:
                self._place = True
            else:
                self._place = False
            self._addedSub = False
            self._addedParent = False
            self._readI = False
            self._readM = False

            block.suboptions = inpKeywordSequence(parentBlock=block)
            try:
                #perform subblock checks
                if organize:
                    endkw_flag = self._endSubKW(block)
                    if endkw_flag !=2:
                        self._createSubKW(block)
                    else:
                        self._addedSub = True
                else:
                    if name=='include':
                        if self.parseSubFiles:
                            self._readI = True
                    elif name=='manifest':
                        if self.parseSubFiles:
                            self._readM = True
                
            except:
                traceback.print_exc()
                
            if self._readI:
                readInclude(block)
            elif self._readM:
                readManifest(block)
            if not self._addedSub:
                kwappend(block, self._place, kd)

        if not self._parentINP:
            self.updateInp(updatePaths=True)
            for loop in range(self._loop, self._maxParsingLoops + 1):
                dpb = self._delayedPlaceBlocks.get(loop)
                if dpb:
                    for block in dpb:
                        eval(f'{block.path.rsplit("[", 1)[0]}._placeInpItemsToUpdate(block)')
            #del self._delayedPlaceBlocks
            if not self._debug:
                del self._kw
            if len(self.findKeyword('parameter', printOutput=False)) > 0:
                self._subP = True
            if self.organize:
                for rel_ind, stepBlock in self.steps.values():
                    stepTypeBlock = stepBlock.suboptions[0]
                    name = stepTypeBlock.name
                    stepBlock._baseStep = self._curBaseStep
                    if name in self._generalSteps and not 'perturbation' in stepTypeBlock.parameter:
                        self._curBaseStep = stepBlock
        print('\nFinished parsing %s' % self.inpName)
        print('   time to parse = %s' % (timing.time() - t1))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateInp(self, gkw=True, b=None, startIndex=0, parentBlock='', updatePaths=True):
        """updateInp(gkw=True, b=None, startIndex=0, parentBlock='', updatePaths=True)
        
            This function calls :func:`~inpRW._inpR.Read.updateObjectsPath`, :func:`~inpRW._inpFind.Find._getLastBlockPath`, 
            :func:`~inpRW._inpFind.Find.findStepLocations`, :func:`~inpRW._inpR.Read._groupKeywordBlocks`, :func:`~inpRW._inpFind.Find._findIncludeFileNames`,
            and updates :attr:`__methods__`, :attr:`__members__`, :attr:`_couplingSurfNames`, :attr:`_kinCoupNsetNames`, 
            and :attr:`_distCoupElsetNames`.
            
            Args:
                gkw (bool): If True, calls :func:`~inpRW._inpR.Read._groupKeywordBlocks`. Defaults to True.
                b (list): Passed to :func:`~inpRW._inpR.Read._groupKeywordBlocks`. See that function for details. Defaults to None.
                startIndex (int): Passed to :func:`~inpRW._inpR.Read.updateObjectsPath`. See that function for details. Defaults to 0.
                parentBlock (inpKeyword): Passed to :func:`~inpRW._inpR.Read.updateObjectsPath`. See that function for details. Defaults to ''.
                updatePaths (bool): Updates :attr:`~inpKeyword.inpKeyword.path` in all keyword blocks after *startIndex* if True. Defaults to True."""
            
        if gkw:
            self._groupKeywordBlocks(b=b)
        coup = self.kwg.get('coupling')
        if coup:
            self._couplingSurfNames.clear()
            self._couplingSurfNames.update(set([block.parameter['surface'] for block in coup]))
        kincoup = self.kwg.get('kinematic coupling')
        if kincoup:
            self._kinCoupNsetNames.clear()
            self._kinCoupNsetNames.update(set([line[0] for block in kincoup for line in block.data if isinstance(line[0], str)]))
        distcoup = self.kwg.get('distribution coupling')
        if distcoup:
            self._distCoupElsetNames.clear()
            self._distCoupElsetNames.update(set([block.parameter['elset'] for block in distcoup]))
        if updatePaths:
            self.updateObjectsPath(startIndex=startIndex, _parentBlock=parentBlock)
        self.keywords.mergeSuboptionsGlobalData()
        self._getLastBlockPath()
        self.findStepLocations()
        self._findIncludeFileNames()
        self.__methods__ = [i for i in dir(self) if callable(getattr(self, i))] #: :list: Holds all the method names of the :class:`inpRW` instance.
        self.__members__ = [i for i in dir(self) if i not in self.__methods__] #: :list: Holds all the member names of the :class:`inpRW` instance.
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def printDocs(self):
        """printDocs()
        
        This function will print the documentation strings for all functions inside the inpRW class."""
        
        for item in self.__methods__:
            if item=='__init__' or '__' not in item:
                if eval('self.%s.__doc__' % item):
                    print('***    %s\n' % (eval('self.%s.__doc__' % item)))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
        
            Produces a representation of the :class:`~inpRW.inpRW` instance.

            This representation can be called to produce another :class:`~inpRW.inpRW` instance. This will only include
            the arguments to :class:`~inpRW.inpRW` which contain non-default values. This string does not guarantee 
            producing an identical :class:`~inpRW.inpRW` instance upon calling :func:`~inpRW.inpRW.parse`, as the 
            applicable attributes might have changed after :func:`~inpRW.inpRW.parse` was called, and there are additional
            attributes which affect parsing which are not output by this function.

            Returns:
                str: The form will be ``inpRW(inpName='path/name', arg=value)``. Additional args will be included only if
                    their value differs from the default value.
        
        """

        d = {'organize': True,
             'parseSubFiles': True,
             'preserveSpacing': True,
             'useDecimal': True,
             'ss': False,
             'rmtrailing0': False,
             '_debug': False,
             'jobSuffix': '_NEW.inp',
             '_parentINP': '',
             '_parentblock': ''}
        for k, v in d.items():
            tmp = self.__dict__[k]
            if tmp == v:
                d[k] = ''
            elif isinstance(tmp, str):
                d[k] = f", {k}='{tmp}'"
            else:
                d[k] = f', {k}={tmp}'

        s = (f"inpRW(inpName='{self.inputFolder}{self.inpName}'{d['organize']}{d['ss']}{d['rmtrailing0']}{d['jobSuffix']}{d['parseSubFiles']}"
            f"{d['preserveSpacing']}{d['useDecimal']}{d['_parentINP']}{d['_parentblock']}{d['_debug']})")
        return s

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__()
        
            Produces a string of the :class:`~inpRW.inpRW` instance.

            This string is meant to help identify the :class:`~inpRW.inpRW` instance. It will always include :attr:`~inpRW.inpRW.inpName`
            and :attr:`~inpRW.inpRW.jobSuffix`, and will include :attr:`~inpRW.inpRW.inputFolder`, :attr:`~inpRW.inpRW.outputFolder`,
            :attr:`~inpRW.inpRW._parentINP`, and :attr:`~inpRW.inpRW._parentblock` only if they are non-empty.

            Returns:
                str
        """

        d = {'inputFolder': '', 
             'outputFolder': '',
             '_parentINP': '',
             '_parentblock': ''}
        for k, v in d.items():
            tmp = self.__dict__[k]
            if tmp == v:
                d[k] = ''
            elif isinstance(tmp, str):
                d[k] = f",\n  {k}='{tmp}'"
            else:
                d[k] = f',\n  {k}={tmp}'

        s = (f"inpRW.inpRW instance:"
            f"\n  inpName='{self.inpName}'{d['inputFolder']}{d['outputFolder']},"
            f"\n  jobSuffix='{self.jobSuffix}'{d['_parentINP']}{d['_parentblock']}")
        return s

#doctests to run
__test__ = {'createPathFromSequence': _inpR.Read.createPathFromSequence,
            #'parsePath': _inpR.Read.parsePath, # Purposefully skipped from doctest, this is tested via unittest function instead
            'sortKWs': _inpR.Read.sortKWs,
            'subBlockLoop': _inpR.Read.subBlockLoop,
            'updateObjectsPath': _inpR.Read.updateObjectsPath,
            '_createSubKW': _inpR.Read._createSubKW,
            '_endSubKW': _inpR.Read._endSubKW,
            '_groupKeywordBlocks': _inpR.Read._groupKeywordBlocks,
            '_readInclude': _inpR.Read._readInclude,
            '_readManifest': _inpR.Read._readManifest,
            '_splitKeywords': _inpR.Read._splitKeywords,
            '_subParam': _inpR.Read._subParam}

