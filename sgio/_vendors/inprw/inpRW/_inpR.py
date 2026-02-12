#Copyright © 2023 Dassault Systemès Simulia Corp.

r"""This module contains functions for parsing the data in the input file."""

# cspell:includeRegExp comments

from ._importedModules import *
import sgio._vendors.inprw.inpRW as inpRW
# from . import inpRW

class Read:   
    r"""The :class:`~inpRW._inpR.Read` class contains functions related to reading information from the input file."""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def createPathFromSequence(self, seq, base='self'):
        r"""createPathFromSequence(seq, base='self')
            
            Generates a path string from a sequence of sequences.
        
            This function takes a sequence of sequences representing the keyword position, suboptions (optional), and 
            data (optional). It will generate a path string from the sequence. If calling this function from inside the 
            :class:`~inpRW` class, do not specify *base*. If calling it outside the class, *base* can be set to 
            the instance name of :class:`.inpRW`.
            
            Example:

                >>> import inpRW
                >>> inp = inpRW.inpRW('dummy.inp')
                >>> inp.createPathFromSequence([0])
                'self.keywords[0]'

            If we need to specify a series of suboptions locations, we use a sublist as the first entry of seq. We can
            also specify a different base string:
                
                >>> inp.createPathFromSequence([0, [0, 1]], base='inp')
                'inp.keywords[0].suboptions[0].suboptions[1]'

            Finally, we can specify the path to data items in the 2nd entry of seq. Make sure to include a blank list
            for the suboptions entry if you do not need to specify a sub-keyword block. Negative integers are allowed:
                
                >>> inp.createPathFromSequence([-1, [], [0, 1]])
                'self.keywords[-1].data[0][1]'
            
            Args:
                seq (list, tuple): A list or tuple of the form [0, [0,1], [0,1]] or [0, [0,1], 0]. Item 0 represents the 
                    keyword index, item 1 is optional and represents the suboption indices, item 2 is optional and 
                    represents the data position(s). Defaults to [None, [], None].
                base (str): A string that will be the base of the output path. Defaults to 'self'.

            Returns:
                str: A string containing the path to the object as specified by *seq*."""

        seqtmp = [None, [], None]
        for ind, i in enumerate(seq):
            seqtmp[ind] = i
        kwpos, subpos, datapos = seqtmp
        kw = f'.keywords[{kwpos}]'
        subtmp = '.suboptions[{}]' * len(subpos)
        sub = subtmp.format(*subpos)
        if isinstance(datapos, int):
            data = f'.data[{datapos}]'
        elif datapos and isinstance(datapos, collections.abc.Sequence) and not isinstance(datapos, str):
            datatmp1 = '[{}]' * (len(datapos) -1)
            datatmp2 = f'.data[{datapos[0]}]{datatmp1}'
            data = datatmp2.format(*datapos[1:])
        elif not isinstance(datapos, NoneSort) and datapos != None:
            data = '.data'
        else:
            data = ''
        path = f'{base}{kw}{sub}{data}'
        return path

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parsePath(self, path):
        r"""parsePath(path)

            Returns a list containing the object at *path* and a list of integers representing the path. The object should
            be somewhere in the keywords -> subkeywords -> data structure (i.e. it should represent a keyword block, or
            a data item in a keyword block.
            
            Here's an example. First, we need to parse the input file:

                >>> import inpRW
                >>> inp = inpRW.inpRW('example_inp.inp')
                >>> inp.parse()

            Now, we can call the function and print the keyword block and the position list (positionl):

                >>> block, positionl =  inp.parsePath('self.keywords[16].suboptions[2]')
                >>> print(block)
                <BLANKLINE>
                *Restart, write, frequency=0
                >>> positionl
                [16, [2], None]
            
            We can also retrieve a particular data item:
                >>> inp.parsePath('self.keywords[12].suboptions[0].data[0][0]')
                (inpDecimal('210000.'), [12, [0], [0, 0]])

            If there is no object at the specified path, this will return (None, indices):

                >>> inp.parsePath('self.keywords[18]')
                No keyword block at self.keywords[18].
                (None, [18, [], None])
            
            Args:
                path (str): Should be the :attr:`path <inpKeyword.inpKeyword.path>` string from an 
                            :class:`inpKeyword <inpKeyword.inpKeyword>` object.

            Returns:
                list: A list containing the object at path and a list of lists containing integers representing the 
                    keyword index and possibly suboptions and data indices."""

        NoneS = NoneSort()
        indices = [NoneS, [], NoneS]
        base = 'self'
        keywstr = ''
        substr = ''
        datastr = ''
        keym = re21.search(path)
        if keym:
            keywpos = int(keym.group())
            indices[0] = keywpos
            keywstr = f'.keywords[{keywpos}]'
        subm = re22.findall(path)
        if subm:
            subpos = [int(i) for i in subm]
            indices[1] = subpos
            substrtmp = '.suboptions[{}]' * len(subpos)
            substr = substrtmp.format(*subpos)
        datampath = path.split('.data')
        if len(datampath) > 1:
            datam = re24.findall(datampath[1])
            datapos = [int(i) for i in datam]
            indices[2] = datapos
            dataposstr = '[{}]'*len(datapos)
            datastr = f'.data{dataposstr}'.format(*datapos)
        try:
            obj = eval(f'{base}{keywstr}{substr}{datastr}')
        except IndexError:
            print(f'No keyword block at {base}{keywstr}{substr}{datastr}.')
            return None, indices
        return obj, indices
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def sortKWs(self, iterable, reverse=False):
        r"""sortKWs(iterable, reverse=False)
       
            This function will sort the keyword blocks in *iterable* by their top-down order in the input file.
            
            It is needed to sort keywords properly when using *organize* = True when instancing :class:`inpRW`.
            
            Args:
                iterable (list): A sequence of :class:`inpKeyword` blocks.
                reverse (bool): If True, sort the keyword blocks in reverse order. Defaults to False.
                
            Returns:
                list: The keyword blocks sorted in the top-down (or reversed) order as they appear in the input file."""

        parsePath = self.parsePath
        cpfs = self.createPathFromSequence
        positionls = [parsePath(block.path)[1] for block in iterable if parsePath(block.path)[0]]
        sortedPositions = nestedSort(positionls, _level=1, reverse=reverse)
        sortedBlocks = [parsePath(cpfs(p))[0] for p in sortedPositions]
        return sortedBlocks
   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def subBlockLoop(self, block, func):
        r"""subBlockLoop(block, func)
            
            Performs *func* on all items in *block.suboptions*.
            
            This will perform *func* on all subblocks in *block.suboptions*. *func* should be a function reference.
        
            Example::
        
                self._potentialBlocks = []
                pBa = self._potentialBlocks.append
                for block in self.keywords:
                    pBa(block)
                    if block.suboptions:
                        self.subBlockLoop(block, pBa)
            
            Args:
                block (inpKeyword): An :class:`inpKeyword <inpKeyword.inpKeyword>` object with 
                    :attr:`suboptions <inpKeyword.inpKeyword.suboptions>`
                func (:term:`function`): A function which will be run on all blocks in *block*.suboptions. Thus, *func* must accept
                    a single :class:`inpKeyword` as an input."""
        
        for subblock in block.suboptions:
            func(subblock)
            if subblock.suboptions:
                self.subBlockLoop(subblock, func)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateObjectsPath(self, startIndex=0, _parentBlock=''):
        r"""updateObjectsPath(startIndex=0, _parentBlock='')
        
            Updates the :attr:`path <inpKeyword.inpKeyword.path>` string of each keyword block after *startIndex*.

            This should be called after inserting, deleting, or replacing keyword blocks. It is called in 
            :func:`~inpRW._inpMod.Mod.insertKeyword`, :func:`~inpRW._inpMod.Mod.deleteKeyword`,
            and :func:`~inpRW._inpMod.Mod.replaceKeyword`, unless it is toggled off.
            
            *_parentBlock* is intended to be used when this function calls itself recursively, so that nested suboptions 
            will also have their paths updated.
            
            Args:
                startIndex (int): The index of a keyword block in :attr:`keywords <inpRW.inpRW.keywords>`
                _parentBlock (inpKeyword): When *_parentBlock* is specified, this function will loop through *_parentBlock*.suboptions
                    and update those paths. 
                                           
            This function is called by :func:`~inpRW.inpRW.updateInp`."""
        
        if not _parentBlock:           
            print(" Updating keyword blocks' paths")
            blocks = self.keywords[startIndex:]
            pathString = 'self.keywords[{combinedIndex}]'
        else:
            blocks = _parentBlock.suboptions
            pathString = '{_parentBlock.path}.suboptions[{index}]'
        psf = pathString.format
        for index, block in enumerate(blocks):
            combinedIndex = startIndex + index
            block.path = psf(**locals())
            if block.suboptions:
                self.updateObjectsPath(_parentBlock=block)
      
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _createSubKW(self, block):
        r"""_createSubKW(block)

            Checks if the keyword name in *block* matches a key in :attr:`~config._subBlockKWs`. If so, a subkw block, 
            and subsequent keyword blocks will be placed into :attr:`~inpKeyword.inpKeyword.suboptions` of this keyword
            block if they are valid suboptions.
            
            Args:
                block (inpKeyword): An inpKeyword object."""
        
        try:
            p = self._parentkws[-1]
            p.suboptions.append(block, self._place, self._loop)
            p.suboptions[-1].path = p.path + '.suboptions[%s]' % (len(p.suboptions)-1)
            self._addedSub = True
        except IndexError:
            if self._parentblock:
                p = self._parentblock
                p.suboptions.append(block, self._place, self._loop)
                p.suboptions[-1].path = p.path + '.suboptions[%s]' % (len(p.suboptions)-1)
                self._addedSub = True
        
        rslbname = rsl(block.name)
        if rslbname in self._subBlockKWs:
            self._parentkws.append(block)
            self._addedParent = True
        
        if rslbname == 'include':
            if self.parseSubFiles:
                self._addedParent = True
                self._readI = True
            
        elif rslbname == 'manifest':
            if self.parseSubFiles:
                self._addedParent = True
                self._readM = True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _endSubKW(self, block):
        r"""_endSubKW(block)

            This function tries to close any and all open sub keyword blocks.
        
            It compares the values of :attr:`~config._subBlockKWs` with the name of *block* to determine if *block* can close 
            the open parent block.
            
            Args:
                block (inpKeyword): An :class:`~inpKeyword.inpKeyword` object.r"""
        
        try:
            p = self._parentkws[-1]
        except IndexError:
            return 1 # no active keyword block groups
        if rsl(p.name) in self._EoFKWs:
            pass
        elif block.name.lower()[:3]=='end':
            parentkw = rsl(block.name).split('end')[-1].replace('\t', '')
            pBlock = [b for b in self._parentkws if parentkw in rsl(b.name)][-1]
            block.path = pBlock.path + '.suboptions[%s]' % (len(pBlock.suboptions))
            pBlock.suboptions.append(block, self._place, self._loop)
            pBlockIndex = self._parentkws.index(pBlock)
            del self._parentkws[pBlockIndex:]
            return 2 # Added END *Keyword* to parent block group
        else:
            if rsl(block.name) not in self._subBlockKWs[p.name]:
                if rsl(self._parentkws[-1].name) not in self._EndKWs:
                    del self._parentkws[-1]
                    self._endSubKW(block)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getLeadingCommentsPattern(self):
        r"""_getLeadingCommentsPattern()
        
            This function finds the location where the first keyword block begins in an input file and returns a regular
            expression pattern to identify that location.

            The pattern will be used by :func:`_splitKeywords` to split the input file immediately before the start of 
            the first keyword block.

            Returns:
                str: A string representing the re pattern which will be used to split the text of the input file on
                    the characters prior to the first keyword block.
        r"""
        
        c = 0
        while 1:
            sp = self.inp.tell()
            line = self.inp.readline()
            if self.inp.tell() == sp:
                return '()'
            if cfc(line):
                c += 1
                continue
            tmp = re25.search(line)
            if tmp:
                self.inp.seek(0)
                nlsearch = '.*\n' * c
                pattern = f'({nlsearch}{tmp.group()})'
                return pattern
            c += 1


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _groupKeywordBlocks(self, b=None, _parentBlock=''):
        r"""_groupKeywordBlocks(b=None, parentBlock='')
        
            Creates :attr:`~inpRW.inpRW.kwg`, with the unique keyword names in the input file as the keys, and a set of
            blocks as each value.

            :attr:`~inpRW.inpRW.kwg` can be used to quickly find all keyword blocks of a given keyword name.

            Args:
                b (list): A list of :class:`inpKeyword blocks <.inpKeyword>`. If specified, only the blocks in *b* will be updated in :attr:`~inpRW.inpRW.kwg`.
                _parentBlock (inpKeyword): Only meant to be specified when this function calls itself recursively, so 
                    subblocks are included in :attr:`~inpRW.inpRW.kwg`.
                                          
            This function is called by :func:`~inpRW.inpRW.updateInp`."""
        
        if not _parentBlock:
            print(' Grouping keyword blocks together')
            if not hasattr(self, 'kwg'):
                self.kwg = csid() #: :csid: A :class:`csid` that groups keyword blocks by their keyword name.
                self._kwgExists = False
            else:
                self._kwgExists = True
            if b==None:
                blocks = self.keywords
            else:
                blocks = b
        else:
            if b==None:
                blocks = _parentBlock.suboptions
            else:
                blocks = b
        kwg = self.kwg
        if not self._kwgExists:
            for block in blocks:
                bname = block.name
                tmp = kwg.setdefault(bname, set())
                if block not in tmp:
                    tmp.add(block)
                if block.suboptions:
                    self._groupKeywordBlocks(_parentBlock=block)
        else:
            for block in blocks:
                bname = block.name
                tmp = kwg.setdefault(bname, set())
                tmp.add(block)
                if block.suboptions:
                    self._groupKeywordBlocks(_parentBlock=block)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _readInclude(self, block):
        r"""_readInclude(block)
        
            Creates a sub-instance of :class:`~inpRW` to read the \*INCLUDE input file. 
            
            The contents of the new input will be placed in the :attr:`suboptions <inpKeyword.inpKeyword.suboptions>` of *block*.
            
            Args:
                block (inpKeyword): An :class:`inpKeyword <inpKeyword.inpKeyword>` object with :attr:`name <inpKeyword.inpKeyword.name>`
                    = INCLUDE"""
        
        inputFileName = block.parameter['input']
        inputFileName_ss = inputFileName.strip(' ')
        subpath = inputFileName
        if os.path.exists(inputFileName):
            pass
        elif os.path.exists(inputFileName_ss):
            subpath = inputFileName_ss
        elif os.path.exists(self.inputFolder + inputFileName):
            subpath = self.inputFolder + inputFileName
        elif os.path.exists(self.inputFolder + inputFileName_ss):
            subpath = self.inputFolder + inputFileName_ss
        print('\n Reading *INCLUDE file %s' % subpath)
        try:
            inpsub = inpRW.inpRW(subpath, organize=self.organize, ss=self.ss, rmtrailing0=self.rmtrailing0, parseSubFiles=self.parseSubFiles, preserveSpacing=self.preserveSpacing, _parentINP=self, _debug=self._debug)
            inpsub.parse()
            block._subinps.append(inpsub)
            block.suboptions = inpsub.keywords
        except:
            print(f'Could not read sub input file of *INCLUDE block {block.formatKeywordLine()}. Related traceback:\n')
            traceback.print_exc()
            print('\n')
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _readManifest(self, block):
        r"""_readManifest(block)

            Creates a sub-instance of :class:`~inpRW` to read the \*MANIFEST input files. 
            
            The contents of the new input will be placed in the :attr:`suboptions <inpKeyword.inpKeyword.suboptions>` of *block*.
            
            Args:
                block (inpKeyword): An :class:`inpKeyword <inpKeyword.inpKeyword>` object with :attr:`name <inpKeyword.inpKeyword.name>` = MANIFEST"""
        
        bsa = block.suboptions.append
        for ind,line in enumerate(block.data):
            line = line[0]
            if cfc(line):
                continue
            else:
                dummyBlock = inpKeyword(name=f'DUMMY-MANIFEST_{line}')
                bsa(dummyBlock)
                subpath = line
                if os.path.exists(line):
                    print('\n Reading *MANIFEST sub-file %s' % subpath)
                elif os.path.exists(self.inputFolder + line):
                    subpath = self.inputFolder + line
                    print('\n Reading *MANIFEST sub-file %s' % subpath)
                else:
                    print('Sub file %s for *MANIFEST not found. Skipping this file.' % subpath)
                    continue
                inpsub = inpRW.inpRW(subpath, organize=self.organize, ss=self.ss, rmtrailing0=self.rmtrailing0, parseSubFiles=self.parseSubFiles, preserveSpacing=self.preserveSpacing, _parentINP=self, _parentblock=dummyBlock, _debug=self._debug)
                inpsub._curBaseStep = self._manBaseStep
                inpsub.parse()
                block._subinps.append(inpsub)
                block.suboptions.append(inpsub.keywords)
                if ind == 0:
                    if 'basestate' in block.parameter:
                        if rsl(block.parameter['basestate']) == 'yes':
                            self._manBaseStep = inpsub._curBaseStep
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _splitKeywords(self):
        r"""_splitKeywords()
        
            Splits the text string of the input file using the * and letter characters.    

            This function splits the text string of the input file using the * and letter characters. Comment lines 
            (denoted with "**") will be included with the previous string. Comments prior to the first keyword block
            will be stored in :attr:`_leadingcomments <inpRW.inpRW._leadingcomments>`."""
        
        tmp = re.split(self._lcpattern, self._inpText,1)
        self._leadingcomments = tmp[0] + tmp[1]
        self._inpText = tmp[2]
        
        self._kw = re15.split(self._inpText)
        if not self._debug:
            del self._inpText
          
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _subParam(self, obj):
        r"""_subParam(obj)
     
            Converts references to a parameter defined in \*PARAMETER to the actual value.

            If *obj* is not an instance of :class:`str`, *obj* will be returned untouched. If *obj* is an 
            instance of :class:`str` this function will check if it is a reference to a \*PARAMETER value (i.e. '<var1>'). 
            If so, it will retrieve the appropriate value from :attr:`pd <inpRW.inpRW.pd>`. If not, *obj* will be returned.

            This function will not modify the original :attr:`data <inpKeyword.inpKeyword.data>` object.

            Args:
                obj (str or inpString): obj should be a :class:`str` or :class:`inpString` for this function to operate on it.

            Returns:
                The type of the returned item is determined by the \*PARAMETER function, or obj is returned."""

        if not self._subP:
            return obj
        if isinstance(obj, str):
            param = re3.findall(obj)
            if param:
                param =  param[0]
                try:
                    return eval2(self.pd[param], ps=False)
                except KeyError:
                    print('WARNING! Key %s not found in self.pd. Check parameter definition.' % param )
                    return eval2(obj, t=str, ps=self.preserveSpacing)
            else:
                return obj
        else:
            return obj

