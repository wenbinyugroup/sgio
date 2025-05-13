#Copyright © 2023 Dassault Systemès Simulia Corp.

# cspell:includeRegExp comments

from .misc_functions import flatten
from .mesh import TotalNodeMesh, TotalElementMesh
from .csid import csid
from .config import _maxParsingLoops

#Move keyword organization functions from inpRW to inpKeywordSequence
#Add merge function, also merge organized keywords

#==================================================================================================================
class inpKeywordSequence(list):
    """An :class:`inpKeywordSequence` inherits from :class:`list`, but it has some additional enhancements to make it
        more useful to :mod:`inpRW`. Mainly, an :class:`inpKeywordSequence` automatically builds a reference to certain
        important information from each :class:`~inpKeyword.inpKeyword` instance placed into the :class:`inpKeywordSequence`,
        and it has a a function which the main :class:`~inpRW.inpRW` instance can call to retrieve this information from
        the main :class:`inpKeywordSequence`, and all its children recursively. String formatting has also been modified
        to be more suited to this application."""
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __new__(cls, iterable=None, parentBlock=None):
        """__new__(iterable=None, parentBlock=None)"""

        return super().__new__(cls, iterable)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, iterable=None, parentBlock=None):
        """__init__(iterable=None, parentBlock=None)
        
        This class creates a blank :class:`inpKeywordSequence` object, which inherits from the list type. It's main purpose
        is to hold :class:`~inpKeyword.inpKeyword` objects, and it provides convenient methods for gathering important
        information from certain keyword blocks and making it available to the :class:`~inpRW.inpRW` instance.

        Creating a string representation of this class will create a useful summary of the keyword lines for each block,
        along with the :attr:`~inpKeyword.inpKeyword.path` to the block, and the same information for the :attr:`~inpKeyword.inpKeyword.suboptions`
        of each block if :attr:`printSubBlocks` = True.

        For most users, the details of this class can be ignored. Simply create :class:`~inpKeyword.inpKeyword` objects
        using one of the recommended options, and add the keyword blocks to the appropriate location.

        In particular, this class has the following attributes which hold information needed by :class:`~inpRW.inpRW`:
        :attr:`_nd`, :attr:`_ed`, :attr:`_pd`, :attr:`_namedRefs`, and :attr:`_delayedPlaceBlocks`. The first four items
        are created when instancing particular keyword blocks and stored in :attr:`~inpKeyword.inpKeyword._inpItemsToUpdate`, 
        and will be automatically inserted into the :class:`inpKeywordSequence` if :class:`~inpRW.inpRW` is on the correct
        insertion loop (specified by :attr:`~config._keywordsDelayPlacingData`) when the keyword block is added to the 
        :class:`inpKeywordSequence`. 

        This class is also setup to pull these attributes from the same attributes from child :class:`inpKeywordSequences <inpKeywordSequence>`
        via :func:`mergeSuboptionsGlobalData`.
        
        Args:
            iterable (list): A sequence of :class:`inpKeyword` blocks with which to pre-populate the :class:`inpKeywordSequence`.
                Defaults to []
            parentBlock (inpKeyword): If the :class:`inpKeywordSequence` instance is the :attr:`~inpKeyword.inpKeyword.suboptions` 
                attribute of a :class:`inpKeyword` block, *parentBlock* should be set to this :class:`inpKeyword` block.
                This is currently referenced only to report the path to access the :class:~inpKeywordSequence` instance.
                Defaults to None."""

        self.parentBlock = parentBlock #: :inpKeyword: This will be None if the :class:`inpKeywordSequence` is the :attr:`~inpRW.inpRW.keywords` attribute, else it will refer to the :class:`~inpKeyword.inpKeyword` block for which this item is the :attr:`~inpKeyword.inpKeyword.suboptions` attribute.
        if iterable == None:
            iterable = []
        self.printSubBlocks = False #: :bool: If False, generating a string of this :class:`inpKeywordSequence` will generate a string for each block in this sequence, along with the :attr:`~inpKeyword.inpKeyword.path` to each block. If True, the :attr:`~inpKeyword.inpKeyword.suboptions` for each block will also be fully expanded and represented.
        self._nd = TotalNodeMesh() #: :TotalMesh: Stores the nodal data for all keyword blocks in this :class:`inpKeywordSequence`, including that in the :attr:`~inpKeyword.inpKeyword.suboptions` of blocks in this sequence. The user should interact with :attr:`~inpRW.inpRW.nd`, which this attribute will eventually feed.
        self._ed = TotalElementMesh() #: :TotalMesh: Stores the element data for all keyword blocks in this :class:`inpKeywordSequence`, including that in the :attr:`~inpKeyword.inpKeyword.suboptions` of blocks in this sequence. The user should interact with :attr:`~inpRW.inpRW.ed`, which this attribute will eventually feed.
        self._pd = csid() #: :csid: Stores the \*PARAMETER data for all keyword blocks in this :class:`inpKeywordSequence`, including that in the :attr:`~inpKeyword.inpKeyword.suboptions` of blocks in this sequence. The user should interact with :attr:`~inpRW.inpRW.pd`, which this attribute will eventually feed.
        self._namedRefs = csid() #: :csid: Stores the named reference definitions for all keyword blocks in this :class:`inpKeywordSequence`, including that in the :attr:`~inpKeyword.inpKeyword.suboptions` of blocks in this sequence. The user should interact with :attr:`~inpRW.inpRW.namedRefs`, which this attribute will eventually feed.
        self._delayedPlaceBlocks = csid({i: [] for i in range(_maxParsingLoops + 1)}) #: :csid: Contains the loop number on which specific information from keyword blocks should be placed, along with a list of all effected keyword blocks for that loop.
        self._grandchildBlocks = [] #: :list: contains the number of suboptions keyword blocks in each child block with suboptions.
        
        return super().__init__(iterable)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def append(self, x, place=True, loop=None):
        """append(x, place=True, loop=None)
        
            Appends *x* to the end of the :class:`inpKeywordSequence`. 
            
            If *place* = True, will call :func:`self._placeInpItemsToUpdate(x) <_placeInpItemsToUpdate>` before running 
            list.append. If *place* = False, *x* will be appended to :attr:`self.parentInp._delayedPlaceBlocks[loop] <inpRW.inpRW._delayedPlaceBlocks>`,
            and it will also be inserted into the :class:`inpKeywordSequence`. 
            
            Args:
                x (inpKeyword): The :class:`inpKeyword` instance to append.
                place (bool): If True, call :func:`_placeInpItemsToUpdate` before appending *x*. Defaults to True.
                loop (int): If *place* is False, *loop* must be specified. *x* will be appended to 
                    :attr:`self.parentInp._delayedPlaceBlocks[loop] <inpRW.inpRW._delayedPlaceBlocks>`."""

        if place:
            self._placeInpItemsToUpdate(x)
        else:
            self._delayedPlaceBlocks[loop].append(x)
        return super().append(x)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def extend(self, iterable, place=True, loop=None):
        """extend(iterable, place=True, loop=None)
        
            Extends the :class:`inpKeywordSequence` by appending all the items from *iterable*.
            
            If *place* = True, will call :func:`self._placeInpItemsToUpdate(x) for x in iterable <_placeInpItemsToUpdate>` before running 
            list.extend. If *place* = False, each item in *iterable* will be appended to :attr:`self.parentInp._delayedPlaceBlocks[loop] <inpRW.inpRW._delayedPlaceBlocks>`,
            and they will also be inserted into the :class:`inpKeywordSequence`. 
            
            Args:
                iterable (list): A sequence of :class:`inpKeyword` instances with which to extend the :class:`inpKeywordSequence`.
                place (bool): If True, call :func:`_placeInpItemsToUpdate` before inserting iterable. Defaults to True.
                loop (int): If *place* is False, *loop* must be specified. Each item in *iterable* will be appended to 
                    :attr:`self.parentInp._delayedPlaceBlocks[loop] <inpRW.inpRW._delayedPlaceBlocks>`."""

        if place:
            for item in iterable:
                self._placeInpItemsToUpdate(item)
        else:
            for item in iterable:
                self._delayedPlaceBlocks[loop].append(iterable)
        return super().extend(iterable)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def insert(self, i, x, place=True, loop=None):
        """insert(i, x, place=True, loop=None)
        
            Inserts *x* into the :class:`inpKeywordSequence` at position *i*. 
            
            If *place* = True, will call :func:`self._placeInpItemsToUpdate(x) <_placeInpItemsToUpdate>` before running 
            list.insert. If *place* = False, *x* will be appended to :attr:`self.parentInp._delayedPlaceBlocks[loop] <inpRW.inpRW._delayedPlaceBlocks>`,
            and it will also be inserted into the :class:`inpKeywordSequence`. 
            
            Args:
                i (int): The index of the element before which to insert.
                x (inpKeyword): The :class:`inpKeyword` instance to insert.
                place (bool): If True, call :func:`_placeInpItemsToUpdate` before inserting *x*. Defaults to True.
                loop (int): If *place* is False, *loop* must be specified. *x* will be appended to 
                    :attr:`self.parentInp._delayedPlaceBlocks[loop] <inpRW.inpRW._delayedPlaceBlocks>`."""

        if place:
            self._placeInpItemsToUpdate(x)
        else:
            self._delayedPlaceBlocks[loop].append(x)
        return super().insert(i, x)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mergeSuboptionsGlobalData(self):
        """mergeSuboptionsGlobalData()
            
            This function will add the contents of :attr:`_nd`, :attr:`_ed`, :attr:`_pd`, :attr:`_namedRefs`,
            and :attr:`_delayedPlaceBlocks` from the :attr:`~inpKeyword.inpKeyword.suboptions` of every block in
            the :class:`inpKeywordSequence` recursively."""
        
        gcb = self._grandchildBlocks
        gcb.clear()
        gcbapp = gcb.append
        for block in self:
            suboptions = block.suboptions
            for subblock in suboptions:
                subblock.suboptions.mergeSuboptionsGlobalData()
            block.suboptions.mergeSuboptionsGlobalData()
            gcbapp(sum(suboptions._grandchildBlocks) + len(suboptions))
            self._namedRefs.mergeSubItems(suboptions._namedRefs)
            self._delayedPlaceBlocks.mergeSubItems(suboptions._delayedPlaceBlocks)
            self._nd.update(suboptions._nd)
            self._ed.update(suboptions._ed)
            self._pd.update(suboptions._pd)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _placeInpItemsToUpdate(self, block):
        """_placeInpItemsToUpdate(block)
        
            This function will place all items from :attr:`block._inpItemsToUpdate <inpKeyword.inpKeyword._inpItemsToUpdate>` into 
            the appropriate attribute of the :class:`inpKeywordSequence`.
            
            This currently will place data into :attr:_namedRefs`, :attr:_ed`, :attr:_nd`,
            and :attr:_pd`.
            
            Args:
                block (inpKeyword)"""

        #self._inpItemsToUpdate = {'ed': self.ed, 'namedRefs': self.namedRefs, 'nd_ed': self.nd}: example for *ELEMENT keyword blocks
        try:
            for k, v in block._yieldInpRWItemsToUpdate():
                if k == 'namedRefs':
                    obj = self._namedRefs
                    obj.mergeSubItems(v)
                elif k in {'nd', 'ed', 'pd'}:
                    obj = eval(f'self._{k}')
                    obj.update(v)
                elif k == 'nd_ed':
                    obj = self._nd
                    obj.setNodesConnectedElements(v)
                else:
                    print(f'Unhandled data block {k}')
        except ValueError:
            print(block)
            print(block._inpItemsToUpdate.items())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        """__str__
            
            Generates a string of the objects in the :class:`inpKeywordSequence`. If :attr:`printSubBlocks` = False,
            this will only print the :class:`inpKeyword` blocks in the :class:`inpKeywordSequence`, but no sub-blocks.
            If :attr:`printSubBlocks` = True, all sub-blocks for blocks contained in the :class:`inpKeywordSequence` will
            also be included. This could print a huge amount of data, depending on how many keyword blocks are in the 
            input file.
            
            Example formatting with :attr:`printSubBlocks`=True:
            
*STEP, NLGEOM, UNSYMM=YES                                                        path: self.keywords[24]
    *STATIC                                                                          path: self.keywords[24].suboptions[0]
    *OUTPUT, FIELD, VARIABLE=PRESELECT, FREQ=10                                      path: self.keywords[24].suboptions[1]
        *ELEMENT OUTPUT                                                                  path: self.keywords[24].suboptions[1].suboptions[0]
        
            Returns:
                str:"""

        def formatKWLine(block, offset=0):
            subout = []
            suboutapp = subout.append
            out_tmp = block.formatKeywordLine()
            if len(out_tmp) > 80:
                out_tmp = f'{out_tmp[:77]}...'
            offset_s = ' ' * offset
            out = f'\n{offset_s}{out_tmp[1:]:<80} path: {block.path}'
            if block.suboptions and self.printSubBlocks:
                for subBlock in block.suboptions:
                    suboutapp(formatKWLine(subBlock, offset=offset + 4))
            out = ''.join(flatten([out] + subout))
            return out
        out = ''.join(formatKWLine(block) for block in self)
        return out

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __repr__(self):
        """__repr__()
        
            Generates a concise summary of the :class:`inpKeywordSequence`.
            
            Example outputs:
            
            inpKeywordSequence(num child keywords: 27, num descendant keywords: 27, path: self.keywords)
            
            inpKeywordSequence(num child keywords: 1, num descendant keyword: 1, path: self.keywords[24].suboptions[2].suboptions)
            
            Returns:
                str:"""

        if self.parentBlock != None:
            path = f'{self.parentBlock.path}.suboptions'
        else:
            path = 'self.keywords'
        numChildKWs = len(self)
        out = f'inpKeywordSequence(num child keywords: {numChildKWs}, num descendant keywords: {numChildKWs + sum(self._grandchildBlocks)}, path: {path})'
        return out