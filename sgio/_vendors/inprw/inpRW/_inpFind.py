#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains functions for finding information in :attr:`~inpRW.inpRW.keywords`."""

# cspell:includeRegExp comments

from ._importedModules import *
from functools import reduce

class Find:
    """The :class:`~inpRW._inpFind.Find` class contains functions related to finding information from the :class:`~inpRW.inpRW`
        data structure."""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findItemReferences(self, blockName, refNames):
        """findItemReferences(blockName, refNames)
            
            This function will call the appropriate function from :class:`~inpRW._inpFindRefs.FindRefs` based on the
            value of *blockName*. *refNames* will serve as the input to the final function.
            
            This function is mainly meant to be used in :func:`~inpRW._inpMod.Mod.deleteItemReferences`, where chains
            of data items and their references need to be deleted. When this happens, a function needs to be called
            which will search for references to the new keyword block.
            
            Args:
                blockName (str): A string which should be the :attr:`~inpKeyword.inpKeyword.name` attribute of a keyword block.
                    This function will call ``rsl(blockName).title()`` to format *blockName* prior to calling the appropriate
                    function in :class:`~inpRW._inpFindRefs.FindRefs`, so the user just needs to specify the full name of the 
                    Abaqus keyword in any formatting, without the \*.
                refNames (list): A sequence of reference items for which to search. These could be strings (i.e.
                    names of sets, surfaces, etc.) or integers (i.e. node labels).
                    
            Returns:
                csid"""

        kwList = self.namedRefs.get(blockName)
        if kwList:
            rslblockName = rsl(blockName)
            if refNames:
                if rslblockName == 'nset':
                    tmpD = self.findNodeRefs(nodes=refNames, mode='set')
                elif rslblockName == 'elset':
                    tmpD = self.findElementRefs(elements=refNames, mode='set')
                elif rslblockName == 'tie':
                    tmpD = None
                else:
                    findFuncString = f'self.find{rsl(blockName).title()}Refs(names=refNames)'
                    tmpD = eval(findFuncString)
                return tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findKeyword(self, keywordName='', parameters=None, excludeParameters=None, data='', mode='all', printOutput=True, parentBlock=''):
        """findKeyword(keywordName='', parameters=None, excludeParameters=None, data='', mode='all', printOutput=True, parentBlock='')

            Finds keyword blocks in :attr:`~inpRW.inpRW.keywords` using multiple criteria.
            
            This function uses a system of filters to find keyword blocks. It will first create a list of potential
            blocks by getting blocks that match *keywordName*. It will then try to match using *parameters*, and finally
            *data*. If one of *keywordName*, *parameters*, or *data* are not specified, they will not be used to filter the
            search. For example, if we call ``inp.findKeyword(keywordName='BOUNDARY')``, this will return all \*BOUNDARY 
            keyword blocks. If we call ``inp.findKeyword(keywordName='BOUNDARY', parameters='AMPLITUDE=amp1')`` this will 
            return the \*BOUNDARY keyword blocks that include 'AMPLITUDE=amp1' as a parameter. 
            
            All inputs to this function are case-insensitive.
            
            *keywordName* can be a string or a list of strings indicating for which keywords to search. Potential blocks
            will be taken from matching entries in :attr:`~inpRW.inpRW.kwg` instead of looping through every block in
            :attr:`~inpRW.inpRW.keywords` to find matches.
            
            *parameters* can be a string, a list, or a dictionary of parameters for which to look. The parameters may or 
            may not include values. Specifying *parameters* as a string will be the simplest option for the user. This 
            function will convert *parameters* to a parameter :class:`csid` if it is not already one.

            *excludeParameters* can be a string, a list, or a dictionary of parameters. A keyword block must not include
            a parameter in *excludeParameters* for :func:`findKeyword` to match the keyword block. The parameters may or 
            may not include values. Specifying *excludeParameters* as a string will be the simplest option for the user. This 
            function will convert *excludeParameters* to a parameter :class:`csid` if it is not already one.
            
            *data* should be a string for which the entirety of the data for the keyword block will be searched, or it can
            be a list containing parsed data objects. If *data* is a list, the matching will be very strict, so it is best
            to retrieve the list items from the keyword block's data field directly. Specifying *data* as a list is 
            primarily intended for cases where you have identified a keyword block of interest, but need to perform an 
            operation that moves the keyword block (such as deleting or inserting keywords) and precisely find the same
            keyword block in its new location.
            
            *mode* should specifically be 'all' (default), 'any', or 'keyandone'. If *mode* == 'all', only keyword blocks
            that match every input to this function will be returned. If *mode* == 'any', every keyword block that matches
            one of the inputs will be returned. If *mode* == 'keyandone', every keyword block that matches *keywordName*
            and at least one other input will be returned. *mode* == 'all' will likely be the most useful.
            
            *printOutput* is a boolean: True (default) or False. If True, the function will print whether it found
            any keyword blocks matching the input parameters. True is useful if using this function interactively,
            False is useful if calling this function in batch and you don't want a lot of printed output.
            
            *parentBlock* should be a keyword object that will contain suboptions. This function will search for
            keywords that match the input parameters, but the potential matches are limited to the suboptions of
            *parentBlock*. This is very useful for finding a \*BOUNDARY in a specific \*STEP, for example.
            
            .. note::
               modes 'any', and 'keyandone' have not been extensively tested with the *parentBlock* and list of *keywordName*
               options, so they might not behave properly. 

            .. warning::
               Do not use this function if you need to search for many specific keywords in a large keyword group. For
               example, you should not use this function to search for 100,000 \*COUPLING blocks with different surface
               names. Each time this function is called, it will loop through the list of available keywords searching for
               the appropriate item. If you have a specific search you need to perform multiple times, you should instead
               create a :class:`csid` using the item of interest as the key and the block as the value. Example:
               ``coupD = csid([ [[block.parameter['surface']], [block]] for block in self.kwg['coupling'] ])``
               
            .. todo::
               The search for data functionality should be augmented to search for data in specific lines or locations 
               in a line to give fewer false positives.
            
            Args:
                keywordName (str or list): The name(s) of the keyword(s) for which to search. Defaults to ''.
                parameters (list or str or dict): The parameters and possibly values for which to search. Users
                    are recommended to use a string, as this will be simplest.
                excludeParameters (list or str or dict): The parameters and possibly values which should not be in
                    keywords (i.e. the block will only match if the other parameters are matched and *excludeParameters*
                    is not matched). Users are recommended to use a string, as this will be simplest.
                data (str or list): A string or list for which to search in any potential block's data.
                mode (str): Indicates the matching mode. Can be one of 'all', 'any', or 'keyandone'. Defaults to 'all'
                printOutput (bool): Indicates if this function should print out a summary (i.e. how many keyword blocks
                    matched the given criteria). Defaults to True.
                parentBlock (inpKeyword): If parentBlock is specified, the search will be restricted to 
                    :attr:`.suboptions` of parentBlock.

            Returns:
                list: A list of all matching :class:`inpKeyword` blocks. """
        
        mode = mode # options 'all', 'any', 'keyandone'
        keywordNames = []
        matchingBlock = []
        self._potentialBlocks = []
        pba = self._potentialBlocks.append
        exp = csid()
        if keywordName and isinstance(keywordName, str):
            keywordNames.append(rsl(keywordName)) #This command makes the search work with or without spaces
        elif keywordName and isinstance(keywordName, list):
            keywordNames = [rsl(i) for i in keywordName]
        elif keywordName and isinstance(keywordName, set):
            keywordNames = [rsl(i) for i in keywordName]
        searchparameters = False
        expParameters = False
        if parameters:
            if isinstance(parameters, str):
                parameters = createParamDictFromString(parameters)
                searchparameters = True
            elif type(parameters)==type([]):
                parameters = csid(parameters)
                searchparameters = True
            elif isinstance(parameters, dict):
                parameters = csid(parameters)
                searchparameters = True
            else:
                print('parameters has not been entered properly as a list of [name, value] pairs as a string (i.e. "REF NODE=1, ISOTHERMAL=NO"), or as a dictionary.')
                if mode.lower()=='all':
                    print(' Aborting search.')
                    raise KeywordNotFoundError()
                else:
                    print(f' Skipping check for parameters {parameters}')
        if excludeParameters:
            if isinstance(excludeParameters, str):
                exp = createParamDictFromString(excludeParameters)
                expParameters = True
            elif isinstance(excludeParameters, list):
                exp = csid(excludeParameters)
                expParameters = True
            elif isinstance(excludeParameters, dict):
                exp = csid(excludeParameters)
                expParameters = True
            else:
                print('excludeParameters has not been entered properly as a list of [name, value] pairs as a string (i.e. "REF NODE=1, ISOTHERMAL=NO"), or as a dictionary.')
                if mode.lower()=='all':
                    print(' Aborting search.')
                    raise KeywordNotFoundError()
                else:
                    print(f' Skipping negative check for parameters {excludeParameters}')

        if parentBlock:
            potBlocks = parentBlock.suboptions
            if keywordNames:
                self._potentialBlocks.extend([i for i in potBlocks if rsl(i.name) in keywordNames])
            else:
                self._potentialBlocks.extend(potBlocks)
        else:
            if keywordNames:
                self._potentialBlocks.extend(flatten([self.sortKWs(self.kwg[i]) for i in keywordNames if i in self.kwg]))
            else:
                for block in self.keywords:
                    pba(block)
                    if block.suboptions:
                        self.subBlockLoop(block, pba)
        if self._potentialBlocks:
            for block in self._potentialBlocks:
                try:
                    bp = block.parameter
                    if keywordNames:
                        if rsl(block.name) in keywordNames:
                            if mode.lower()=='all':
                                pass
                            elif mode.lower()=='keyandone':
                                pass
                            else:
                                matchingBlock.append(block)
                        else:
                            if mode.lower()=='all':
                                raise KeywordNotFoundError()
                            else:
                                pass
                    if expParameters:
                        for ep, epv in exp.items():
                            bep = bp.get(ep)
                            if bep != None:
                                if epv == '' or epv == bep:
                                    raise KeywordNotFoundError()
                    if searchparameters:
                        a = parameters
                        for pk in a.keys():
                            if pk in bp:
                                tmpa = a[pk]
                                tmpb = bp[pk]
                                if tmpa == '':
                                    if mode.lower()=='all':
                                        pass
                                    else:
                                        matchingBlock.append(block)
                                        break
                                elif isinstance(tmpa, str) and isinstance(tmpb, str):
                                    if rsl(tmpa) in rsl(tmpb):
                                        if mode.lower()=='all':
                                            pass
                                        else:
                                            matchingBlock.append(block)
                                            break
                                    else:
                                        raise KeywordNotFoundError()
                                elif tmpa == tmpb:
                                    if mode.lower()=='all':
                                        pass
                                    else:
                                        matchingBlock.append(block)
                                        break
                                else:
                                    if mode.lower()=='all':
                                        raise KeywordNotFoundError
                                    else:
                                        pass
                            else:
                                if mode.lower()=='all':
                                    raise KeywordNotFoundError()
                    if data:
                        if isinstance(data, list):
                            for line in data:
                                if line in block.data:
                                    if mode.lower() == 'all':
                                        pass
                                    else:
                                        matchingBlock.append(block)
                                        break
                                else:
                                    if mode.lower()=='all':
                                        raise KeywordNotFoundError()
                        elif isinstance(data, str):
                            tmpout = []
                            self.writeBlocks([block], tmpout)
                            dataString = rsl('\n'.join(tmpout))
                            data = rsl(data)
                            if data in dataString:
                                if mode.lower()=='all':
                                    pass
                                else:
                                    matchingBlock.append(block)
                                    break
                            else:
                                if mode.lower()=='all':
                                    raise KeywordNotFoundError()
                                else:
                                    pass
                        else:
                            print('"data" specified incorrectly. It must be an instance of list or string.')
                            raise KeywordNotFoundError()
                except KeywordNotFoundError:
                    pass
                else:
                    if mode.lower()=='all':
                        matchingBlock.append(block)
        if type(parameters)==type([]):
            parameters = csid(parameters)
        elif parameters == None:
            parameters = csid()
        if matchingBlock:
            matchingBlock = list(dict.fromkeys(matchingBlock)) # Removes any duplicate values found using mode='any'
            parameterString = formatStringFromParamDict(parameters, joinPS=', ')
            if printOutput:
                print(f'Found {len(matchingBlock)} matching block(s) for search "*{keywordName}", parameters: "{parameterString}", data="{data}", excluding parameters "{excludeParameters}"')
            del self._potentialBlocks
            return matchingBlock
        else:
            parameterString = formatStringFromParamDict(parameters, joinPS=', ')
            if printOutput:
                print(f'Did not find a keyword block with name: "*{keywordName}", parameters: "{parameterString}", data="{data}", excluding parameters "{excludeParameters}"')
            del self._potentialBlocks
            return matchingBlock
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findKeywordsIgnoreParam(self, kwNameGroup):
        """findKeywordsIgnoreParam(kwNameGroup)
    
            Searches :attr:`~inpRW.inpRW.kwg` for the keywords in *kwNameGroup*, and returns the keyword groups it finds.
        
            Args:
                kwNameGroup (list): A sequence of strings designating the keyword names of interest. 
            
            Returns:
                list: This returns a list of :attr:`keyword groups <inpRW.inpRW.kwg>` as specified by "kwNameGroup"."""
        
        kwSub = [self.sortKWs(self.kwg[i]) for i in kwNameGroup if i in self.kwg]
        return kwSub

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findStepLocations(self):
        """findStepLocations()
        
            Creates objects :attr:`~inpRW.inpRW.steps` and :attr:`~inpRW.inpRW.step_paths`.
            
            If a step does not set the "name" :attr:`.parameter`, the key for the step will be its index in 
            :attr:`kwg['STEP'] <inpRW.inpRW.kwg>`.
        
            This function is called by :func:`~inpRW.inpRW.updateInp`."""
        
        if 'step' in self.kwg:
            print(" Searching for *STEP locations")
            try:
                self.steps = csid([[i.parameter['name'] if 'name' in i.parameter else index, [index,i]]  for index,i in enumerate(self.sortKWs(self.kwg['STEP']))]) #: :csid: Provides quick access to the steps in :attr:`~inpRW.inpRW.keywords` if the step names are known. The key is the step name and the value is ``[index in inp.sortKWs(kwg['step']) , inpKeyword]``. If a step does not have a name, the index is used for the key. 
                self.step_paths = [i[1].path for i in list(self.steps.values())] #: :list: Stores the :attr:`.path` to every \*STEP keyword block, in order of appearance in the input file.
            except (IndexError, TypeError, KeyError):
                print('Found no steps in input file')
                self.steps = csid()
        else:
            print('Found no steps in input file')
            self.steps = csid()
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findValidParentKW(self, child):
        """findValidParentKW(child)
        
            Prints the keyword names that can be parent blocks for child.

            This function searches through all subkeywords for every parent keyword in :attr:`~config._subBlockKWs`.
            :attr:`~config._subBlockKWs` gives you the valid child keywords for a given parent keyword; this function
            finds the valid parent keywords for a given child keyword.

            Args:
                child (str): The keyword name for which the valid keyword block"""

        foundParent = False
        for item in self._subBlockKWs:
            if rsl(child) in self._subBlockKWs[item]:
                print(item)
                foundParent = True
        if not foundParent:
            print(f'Keyword {child} is not a suboption of any keyword.')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getParentBlock(self, item, parentKWName='', _level=1):
        """getParentBlock(item, parentKWName='', _level=1)
        
            Retrieves the parent block for *item*. 
            
            This function will find the parent keyword block for *item*. If *parentKWName* is specified, the function will
            keep searching up the :attr:`.path` of *item* until it finds *parentKWName*.

            Args:
                item (inpKeyword, str, list, or tuple): If *item* is a string, it must be of the form in :attr:`.path`.
                        Example: ``'self.keywords[0].suboptions[1]'``. If *item* is a list or tuple, it must be of the form 
                        of the *seq* parameter described in :func:`~inpRW._inpR.Read.createPathFromSequence`.
                parentKWName (str): Must correspond to a valid Abaqus keyword. Case- and space-insensitive.
                _level (int): Indicates how many times to split :attr:`item.path <.path>`. Should only be specified by
                        this function.

            Returns:
                inpKeyword or None: If a parent block is found that matches the input parameters, an :class:`inpKeyword`
                is returned. Otherwise, this function returns None."""

        parent = ''
        if type(item)==inpKeyword:
            path = item.path
            tmp = self.parsePath(path.rsplit('.', _level)[0])
        elif type(item)==type(''):
            path = item
            tmp = self.parsePath(path.rsplit('.', _level)[0])
        elif type(item)in [type(tuple()), type([])]:
            path = self.createPathFromSequence(item)
            tmp = self.parsePath(path.rsplit('.', _level)[0])
        if tmp:
            parent = tmp[0]
        if isinstance(parent, inpKeyword):
            if not parentKWName:
                return parent
            else:
                if rsl(parent.name)==rsl(parentKWName):
                    return parent
                else:
                    return self.getParentBlock(item, parentKWName=parentKWName, _level=_level+1)
        else:
            print(f'Could not find a parent block for *{self.parsePath(path)[0].name} at path={path}, parentKWName={parentKWName}')
            return None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _findActiveSystem(self):
        """_findActiveSystem()
        module: _inpFind.py
        
            Finds which \*SYSTEM is active at all points in the .inp
            
            .. warning::
               
               THIS FUNCTION HAS NOT BEEN TESTED WITH THE inpRW MODULE.
               IT NEEDS TO BE REWORKED BEFORE IT SHOULD BE USED."""
        
        self._activeSystem =  [((0.0, 0.0, 0.0, 1.0, 0.0, 0.0),) for i in range(len(self.keywords))]
        if 'SYSTEM' in self.kwg:
            for block in self.sortKWs(self.kwg['SYSTEM']):
                offset = self.parsePath(block.path)[-1]
                for index,sys in enumerate(self._activeSystem[offset:]):
                    if block.data:
                        self._activeSystem[offset+index] = block.data
                    else:
                        self._activeSystem[offset+index] = ((0.0, 0.0, 0.0, 1.0, 0.0, 0.0),)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findCloseNodes(self, nodeGroup1=None, nodeGroup2=None, searchDist=1e-6, _sliceStart=1):
        """findCloseNodes(nodeGroup1=None, nodeGroup2=None, searchDist=1e-6, _sliceStart=1)

            This function searches for nodes that are within *searchDist* of each other. It will generate a cKDTree 
            from :mod:`scipy.spatial`, and the function will return a dictionary using the pairs of nodes which
            fall withing *searchDist* as the key-value pairs.

            *nodeGroup1* must be a :class:`~mesh.TotalMesh` or :class:`~mesh.Mesh` instance. In most cases the user 
            should use :attr:`~inpRW.inpRW.nd`, which will contain all nodes in the input file.

            The nodes in *nodeGroup1* will be used to generate a :class:`~scipy.spatial.cKDTree`, which will be stored 
            to :attr:`~inpRW.inpRW._tree`. If :attr:`~inpRW.inpRW._tree` already exists and *nodeGroup1* contains the 
            same number of entities as :attr:`~inpRW.inpRW._tree`, the existing tree will be used. The 
            :class:`~scipy.spatial.cKDTree` allows for quick nearest-neighbor lookups.

            *nodeGroup2* can be specified as a :class:`~mesh.Mesh` or :class:`~mesh.TotalMesh` instance. These nodes 
            are the source nodes for which this function will search for close nodes from *nodeGroup1*. If *nodeGroup2*
            is not specified, it will be identical to *nodeGroup1*. *nodeGroup2 can be a subset of *nodeGroup1*; this 
            function will automatically filter out nodes which are only close to themselves. A node from *nodeGroup1* 
            will be considered close to a node from *nodeGroup2* if it falls within *searchDist* of the *nodeGroup2* 
            node. The search is performed using :meth:`~scipy.spatial.cKDTree.query_ball_point`, with *nodeGroup2* being 
            passed to the "x" parameter and *searchDist* being passed to the "r" parameter.
            
            Not specifying *nodeGroup2* will thus look for close nodes over the entire mesh. If the user has an idea
            of where to find close nodes (i.e. a particular node set), then *nodeGroup2* should be specified to reduce
            the number of locations this function needs to check.
            
            *searchDist* should be a small float. This defaults to 1e-6.
            
            *_sliceStart* = 1 will remove the 0th data column (i.e. remove the node labels). It should not be changed 
            in most cases as this functions is written specifically to operate on information stored in :class:`~mesh.Mesh`
            or :class:`~mesh.TotalMesh` instances.

            The output dictionary will be key-value pairs of node labels. There will strictly be one value for each key. 
            If *nodeGroup2* is specified, the values of this dictionary will be node labels from *nodeGroup2*, and the 
            keys will be node labels from *nodeGroup1* which are close to each node from *nodeGroup2*. For example, let's
            say we have three nodes (1, 2, and 3) which are within *searchDist* of each other (and many other nodes in 
            the mesh), and we want to search for the nodes which are close to node 3. The output of this function would
            look like the following::

                {1: 3, 2: 3}

            If *nodeGroup2* is not specified, the lower node label will always be the value. 

            Args:

                nodeGroup1 (Mesh or TotalMesh): *nodeGroup1* defines the search domain. In most cases, it should
                    include every node in the input file. Defaults to :attr:`~inpRW.inpRW.nd`, which will include
                    every node.
                nodeGroup2 (Mesh or TotalMesh): *nodeGroup2* defines the nodes for which close nodes should be found
                    If *nodeGroup2* is specified, the each value in the output dictionary will be a node label from
                    *nodeGroup2*. Defaults to :attr:`~inpRW.inpRW.nd`.
                searchDist (float): The distance which defines close nodes. Defaults to 1e-6.
                _sliceStart (int): Used to specify the "column" in a list where the nodal coordinates begin. Since 
                    the datalines for a node begin with the node label before the coordinates, *_sliceStart* 
                    defaults to 1. Since this function needs to operate on :class:`~mesh.Mesh` or :class:`~mesh.TotalMesh`
                    objects, this argument should be left at the default of 1.
                        
            Returns:
                dict: This dictionary will always contain a 1:1 mapping of nodelabels which fall within *searchDist*
                    of each other. If *nodeGroup2* is specified, a nodelabel from *nodeGroup2* will always be the
                    value, otherwise the lower nodelabel will be the value.
            """

        #nodeBlock1 = reduce(lambda x,y: x + y, nodeBlocks1)
        if nodeGroup1==None:
            nodeGroup1 = self.nd
        nodeList1 = list(nodeGroup1.values())
        if nodeGroup2==None:
            nodeList2 = nodeList1
        else:
            nodeList2 = list(nodeGroup2.values())
        nodesToKeepSet = set((i.label for i in nodeList2))
        try:
            if len(self._tree.indices) == len(nodeGroup1):
                pass
            else:
                self._tree = spatial.cKDTree([i.data[_sliceStart:_sliceStart + 3] for i in nodeList1])
        except AttributeError:
            self._tree = spatial.cKDTree([i.data[_sliceStart:_sliceStart + 3] for i in nodeList1])
        dup_node_pairs = (i for i in self._tree.query_ball_point([j.data[1:] for j in nodeList2], searchDist) if len(i)>1)
        #dup_node_labels = [[nodeList1[j].label for j in i] for i in dup_node_pairs]
        dup_node_labels = [[*[nodeList1[j].label for j in i if nodeList1[j].label not in nodesToKeepSet], *[nodeList1[j].label for j in i if nodeList1[j].label in nodesToKeepSet]] for i in dup_node_pairs]
        #self.dup_node_labels = dup_node_labels

        #This section processes any cases where there are more than 2 nodes at the same location. It will remove any items in the list with more than 2 entries and replace them with multiple pairings.
        mdup = [index for index, i in enumerate(dup_node_labels) if len(i)>2]
        mdup.sort(reverse=True)
        for index in mdup:
            try:
                d = dup_node_labels[index : index + 1][0]
            except IndexError:
                d = dup_node_labels[index :][0]
            for label in d[1:]:
                dup_node_labels.insert(index + 1, [d[0], label])
            del dup_node_labels[index]

        dup_node_dict = {i[0]: i[1] for i in dup_node_labels}
        #print(' Found %s close nodes within %s of each other' %  (len(list(dup_node_dict.values())), searchDist))
        return dup_node_dict

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _findData(self, labelD, kwNames=None, parameters=None, excludeParameters=None, mode='all', data_pos='', linesToCheck='', 
                  custom='', dataOffset=None, dataStep=None, lineOffset=None, lineStep=None, dataGroup='line', kwBlocks=None):
        """_findData(labelD, kwNames=None, parameters=None, excludeParameters=None, mode='all', data_pos='', linesToCheck='', custom='', dataOffset=None, dataStep=None, lineOffset=None, lineStep=None, dataGroup='line', kwBlocks=None)
        
            This function will search for references to the keys in labelD in the locations specified by the rest of
            the parameters to this function. It is meant to be called from one of the functions in :class:`~inpRW._inpFindRefs.FindRefs`.

            If *kwBlocks* is specified, :func:`_findData` will check the locations indicated by any combination of 
            *data_pos*, *linesToCheck*, *custom*, *dataOffset*, *dataStep*, *lineOffset*, and *lineStep* for items
            which are in *labelD*. If any location matches an item in *labelD*, the item in *labelD* will be updated with
            the path to the location, along with the region of the keyword block the item affects (specified by *dataGroup*).
            If *kwBlocks* is not specified, *kwNames* must be specified, and :func:`findKeyword` will be called with
            arguments *kwNames*, *parameters*, *excludeParameters*, and *mode*. The function will then run as before,
            but using the resulting keyword blocks from :func:`findKeyword` instead of those specified by *kwBlocks*.

            When using *kwNames*, this function will find the :class:`inpKeyword` blocks to search using this command:
            ```list(flatten([j for j in self.findKeyword(keywordName=kwNames, parameters=parameters, excludeParameters=excludeParameters, mode=mode, printOutput=False) if j]))```
            If this is not sufficient to generate a list of keywords to search, the list should be generated prior to
            calling :func:`_findData` and input using the *kwBlocks* parameter.

            Args:
                labelD (csid): A csid of the form ```csid([[name, []] for name in names])```. The items in names can be
                    :class:`integers <int>` or :class:`strings <str>`, but the function might not work properly if
                    *labelD* contains both types.
                kwNames (list): A sequence containing the keyword names in which to search. Will be passed to
                    :func:`findKeyword`. Defaults to None. Must be specified if *kwBlocks* is omitted.
                parameters: See :func:`findKeyword`. Defaults to None.
                excludeParameters: See :func:`findKeyword`. Defaults to None.
                mode (str): See :func:`findKeyword`. Defaults to 'all'.
                data_pos (int or str): Indicates which positions in the dataline to search for a match. Can be an :class:`int`, 
                    or a :class:`str`. If a :class:`str`, can be 'EVEN', 'ODD', or a string indicating a slicing notation.
                    Defaults to '', which will be converted to '[:]' and check every data position. Works in conjunction with
                    *linesToCheck*
                linesToCheck (int or str): Indicates which datalines to search for a match. Can be an :class:`int`, 
                    or a :class:`str`. If a :class:`str`, can be 'EVEN', 'ODD', or a string indicating a slicing notation.
                    Defaults to '', which will be converted to '[:]' and check every dataline. Works in conjunction with
                    *data_pos*.
                custom (:term:`function`): A custom function to determine which locations should be examined for data matching.
                    This is an alternative to *data_pos* and *linesToCheck*, and should only be used in the few
                    cases where those options are not sufficient. This function will have access to all the local
                    variables of :func:`_findData`, and needs to be written like it's a part of :func:`_findData`.
                    See function externalFieldCustomSub inside :func:`~inpRW._inpFindRefs.FindRefs.findElementRefs` for an example.
                dataOffset, dataStep, lineOffset, lineStep (int): Used to override the value the function will calculate.
                    They are used in this manner with slicing [Offset : : Step]. They should not be used in most
                    cases, as the appropriate values will be calculated from *data_pos* and *linesToCheck*, but
                    they are still options for the rare cases the default calculation is incorrect. Defaults
                    to None.
                dataGroup (str): Must be one of 'line', 'multiline', 'alldata', or 'subline'. Indicates the region
                    of the keyword associated with the reference (i.e. if the reference is deleted, how much of the
                    keyword block must be deleted to still have a valid keyword). 
                    'line' corresponds to the entire data line.
                    'multiline' corresponds to multiple keyword lines as indicated by *linesToCheck*.
                    'alldata' corresponds to the entirety of :attr:`~inpKeyword.inpKeyword.data`.
                    'subline' corresponds to a region of the dataline as indicated by *data_pos*.
                    Defaults to 'line'.
                kwBlocks (list): Each item in *kwBlocks* must be an :class:`inpKeyword`. Defaults to None. One of 
                    kwBlocks or kwNames must be specified."""
        
        #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        def calcStepandOffset(indic, offsetDefault=None, stepDefault=None):
            """calcStepandOffset(indic, offsetDefault=None, stepDefault=None)
            
                Calculates step and offset, which will be used to reconstruct the path to the original items in block.data.
                If *offsetDefault* and *stepDefault* are specified, these will be used over what the function calculates
                from *indic*.
                
                Args:
                    indic (int or str): *indic* should be an integer, 'odd' or 'even', or a string of forms '[1:3]' or '[0::3]'
                    offsetDefault (int): An integer which will override the calculated offset if specified. Defaults to None.
                    stepDefault (int): An integer which will override the calculated step if specified. Defaults to None.
                    
                Returns:
                    (int, int)"""

            step = stepDefault
            offset = offsetDefault
            if isinstance(indic, str):
                indic = rsl(indic)
            if indic == 'odd':
                step = 2
                offset = 1
            elif indic == 'even':
                ls = 2
                lo = 0
            elif isinstance(indic, int):
                step = 1
                offset = 0
            elif indic:
                indic_cc = indic.count(':') # indic_CountColon
                if indic_cc == 1:
                    start, end = indic.strip('[]').split(':')
                    if start:
                        offset = int(start)
                elif indic_cc == 2:
                    start, end, step = indic.strip('[]').split(':')
                    if start:
                        offset = int(start)
                    if step:
                        step = int(step)
            if offsetDefault != None and offset != offsetDefault:
                offset = offsetDefault
            elif offset == None:
                offset = 0
            if stepDefault != None and step != stepDefault:
                step = stepDefault
            elif step == None:
                step = 1
            return offset, step
        #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

        #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        def calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup):
            """calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup) 
            
                Generates the string which indicates the area affected by the found reference.
                
                Args:
                    path (str): The :attr:`~inpKeyword.path` to the keyword block.
                    lineno (int): An integer indicating the data line number.
                    ls (int): An integer representing the step size between lines of interest.
                    datano (int): An integer indicating the position of the data item in the line of interest.
                    ds (int): An integer representing the step size between data items of interest.
                    dataGroup (str): See *dataGroup* in :func:`_findData`.
                    
                Returns:
                    str"""

            fg = rsl(dataGroup)
            if fg == 'line':
                functionalGroupList = [f'{path}.data[{lineno}]']
            elif fg == 'multiline':
                datalist = list(range(lineno, lineno + ls))
                base = f'{path}.data[{{}}]'
                functionalGroupList = [base.format(i) for i in datalist]
            elif fg == 'alldata':
                functionalGroupString = ['{path}']
            elif fg == 'subline':
                datalist = list(range(datano, datano + ds))
                base = f'{path}.data[{lineno}][{{}}]'
                functionalGroupList = [base.format(i) for i in datalist]
            else:
                print(f'dataGroup specified incorrectly. Value {dataGroup} is not one of "line", "multiline", "alldata", or "subline".')
            return functionalGroupList
        #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        #######################
        #START OF MAIN FUNCTION
        #######################
        if kwBlocks:
            sub = kwBlocks
        else:
            sub = list(flatten([j for j in self.findKeyword(keywordName=kwNames, parameters=parameters, excludeParameters=excludeParameters, mode=mode, printOutput=False) if j]))
        if sub:
            #Calculate offsets and steps for lines and data
            lo, ls = calcStepandOffset(linesToCheck, lineOffset, lineStep)
            if dataOffset == None and isinstance(data_pos, int):
                dataOffset = data_pos
            do, ds = calcStepandOffset(data_pos, dataOffset, dataStep)
  
            for block in sub:
                path = block.path
                blockpathstring = '{path}.data[{lineno}][{datano}]'
                datatemp = block.data
                if isinstance(linesToCheck, str):
                    linesToCheck = rsl(linesToCheck)
                if linesToCheck == 'odd':
                    data = datatemp[1::2]
                elif linesToCheck == 'even':
                    data = datatemp[::2]
                elif linesToCheck:
                    try:
                        data = eval('datatemp%s' % linesToCheck)  
                    except TypeError:
                        try:
                            data = [datatemp[i] for i in eval(linesToCheck)]
                        except IndexError:
                            pass
                else:
                    data = datatemp

                if isinstance(data_pos, int):
                    dstring = f'[{data_pos}: {data_pos +1}]'
                elif rsl(data_pos) == 'odd':
                    dstring = '[1::2]'
                elif rsl(data_pos) == 'even':
                    dstring = '[::2]'
                elif data_pos == '':
                    dstring = '[:]'
                elif isinstance(data_pos, str):
                    dstring = data_pos

                loc = locals()
                if custom != '':
                    custom(**loc)
                else:
                    for ind,line in enumerate(data):
                        for indd,item in enumerate(eval(f'line{dstring}')):
                            if isinstance(item, str):
                                item = rsl(item)
                            if item in labelD:
                                lineno = ind * ls + lo
                                datano = indd * ds + do
                                labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _findIncludeFileNames(self):
        """_findIncludeFileNames()
        
            Finds all child input file names in :attr:`~inpRW.inpRW.keywords`.

            This function will search for \*INCLUDE, \*MANIFEST, and any keywords in :attr:`~config._dataKWs` that
            have the "input" :attr:`.parameter`. It will populate 
            :attr:`~inpRW.inpRW.includeFileNames` with all file names it finds and :attr:`~inpRW.inpRW.includeBlockPaths` 
            with the :attr:`paths <.path>` to the blocks that read from child input files.
            
            This function is called by :func:`~inpRW.inpRW.updateInp`."""

        try:
            self.includeFileNames, self.includeBlockPaths = zip(*[[i.parameter['input'], i.path] for i in self.findKeyword(keywordName = self._dataKWs.union({'include'}), printOutput=False) if 'input' in i.parameter])
        except ValueError:
            pass
        try:
            tmpincludeFileNames, tmpincludePaths = zip(*[[i[0], j.path] for j in self.findKeyword(keywordName='manifest', printOutput=False) for i in j.data])
            self.includeFileNames += tmpincludeFileNames
            self.includeBlockPaths += tmpincludePaths
        except ValueError:
            pass    
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _findParam(self, labelD, parameterName, kwNames=None, excludeParameters=None, mode='all', kwBlocks=None):
        """_findParam(labelD, parameterName, kwNames=None, excludeParameters=None, mode='all', kwBlocks=None)
            
            This function will look for keyword blocks that reference items in *labelD*. 
            
            It will search *kwBlocks*, or it will search the blocks returned by 
            ```findKeyword(keywordName=kwNames, parameters=parameterName, excludeParameters=excludeParameters, mode=mode, printOutput=False ```
            

            Args:
                labelD (csid): A csid of the form ```csid([[name, []] for name in names])```. The items in names can be
                    :class:`integers <int>` or :class:`strings <str>`, but the function might not work properly if
                    *labelD* contains both types.
                parameterName (str): A string indicating the parameter name for which to search. This should not
                    include a value. *parameterName* will be passed to *parameters* of :func:`findKeyword` if 
                    *kwBlocks* is not specified. If matching keyword blocks are found, the function will check if the
                    value of ```block.parameter[parameterName]``` is in *labelD*. If so, labelD[parameterName] will 
                    have [{path to parameter}, {path to block}] appended.
                kwNames (list): A sequence containing the keyword names in which to search. Will be passed to
                    :func:`findKeyword`. Defaults to None. Must be specified if *kwBlocks* is omitted.
                excludeParameters: See :func:`findKeyword`. Defaults to None.
                mode (str): See :func:`findKeyword`. Defaults to 'all'.
                kwBlocks (list): Each item in *kwBlocks* must be an :class:`inpKeyword`. Defaults to None. Must be 
                    specified if *kwNames* is omitted."""

        if kwBlocks:
            sub = kwBlocks
        else:
            if kwNames != None:
                sub = list(flatten([j for j in self.findKeyword(keywordName=kwNames, parameters=parameterName, excludeParameters=excludeParameters, mode=mode, printOutput=False) if j]))
            else:
                print(f'Function called incorrectly. At least one of kwNames or kwBlocks must be specified. parameterName={parameterName}, kwNames={kwNames}, excludeParameters={excludeParameters}, mode={mode}, kwBlocks={kwBlocks}.')
                sub = None
        if sub:
            for block in sub:
                a = block.parameter.get(parameterName)
                if a != None and a in labelD:
                    labelD[a].append([f"{block.path}.parameter['{parameterName}']", f"{block.path}"])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getLastBlockPath(self, _block=''):
        """_getLastBlockPath(_block='')
        
            Sets :attr:`~inpRW.inpRW._lbp` to the path of the last block in the input file.
            
            Args:
                _block (inpKeyword): Only meant to be used when this function calls itself to handle blocks with :attr:`.suboptions`.
                
            This function is called by :func:`~inpRW.inpRW.updateInp`."""

        if _block:
            lastblock = _block
        else:
            lastblock = self.keywords[-1]
        if lastblock.suboptions:
            lastblock = self._getLastBlockPath(lastblock.suboptions[-1])
        else:
            self._lbp = lastblock.path #: :str: The path to the last block in :attr:`~inpRW.inpRW.keywords`.

