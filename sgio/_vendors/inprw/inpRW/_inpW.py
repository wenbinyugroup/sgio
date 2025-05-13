#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains functions for writing a new input file from the information in :attr:`~inpRW.inpRW.keywords`."""

# cspell:includeRegExp comments

from ._importedModules import *

class Write:
    """The :class:`~inpRW._inpW.Write` class contains functions that write input files from the parsed data structure."""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def generateInpSum(self):
        """generateInpSum()
        
            Generates the .sum file, which includes the keyword line and :attr:`~inpKeyword.inpKeyword.path` for each
            keyword block.

            The file will be written to :attr:`~inpRW.inpRW._kwsumName`.
        """

        keywords = self.keywords
        keywordsPrintSubBlocks = keywords.printSubBlocks
        keywords.printSubBlocks = True
        with open(self._kwsumName, 'w') as inpSumFile:
            inpSumFile.write(str(keywords))
        keywords.printSubBlocks = keywordsPrintSubBlocks

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writeBlocks(self, iterable, output=None):
        """writeBlocks(iterable, output=None,)
        
            Generates strings from a sequence of :class:`.inpKeyword` objects. 
            
            This function generates strings from a sequence of :class:`.inpKeyword` objects. It will either write the
            strings to *output*, if *output* is a file, or it will append the strings to *output* if *output* is a list.

            This function will call itself recursively to handle suboptions.

            Args:
                iterable (list): Items in list should be :class:`.inpKeyword` blocks.
                output (:term:`file object` or :class:`list`): Output will be written to this object. Defaults to [].
                
            Returns:
                list: If output is a list, this function will return a list. If output is a file, there is no return."""
        
        if output == None:
            output = []
        for block in iterable:
            subout = False
            name = rsl(block.name)
            skipsuboptions = False

            if name == 'include':
                if self.parseSubFiles:
                    #k = [i for i in list(block.parameter.keys()) if rsl(i)=='input'][0]
                    k = 'input'
                    name, suffix = block.parameter[k].split('.')
                    block.parameter[k] = f'{name}{self.jobSuffix.split(".")[0]}.{suffix}'
                    subout = block.parameter[k]
                    try:
                        subinp = block._subinps[0]
                        subinp.writeInp(output=subout)
                    except IndexError:
                        print(f'Not writing {subout} of block {block.formatKeywordLine()}, as there is no parsed data for it.')
                    skipsuboptions = True
            elif name == 'manifest':
                if self.parseSubFiles:
                    data = block.data
                    block.data = [[item.split('.')[0] + self.jobSuffix for item in line] for line in data]
                    subout = [i for i in list(flatten(block.data))] #had data instead of block.data, but that seemed incorrect. Revert if errors arise.
                    if subout:
                        for index,sub in enumerate(subout):
                            subinp = block._subinps[index]
                            subinp.writeInp(output=sub)
                        skipsuboptions = True
                        #self._firstItem = True
            elif name in self._dataKWs:
                if hasattr(block, '_subdata'):
                    subblock = block._subdata
                    inputName, inputExt = block.parameter['input'].split('.')
                    if inputExt.lower() == 'inp':
                        if self._slash in inputName:
                            subinpName = self.outputFolder + inputName.split('.')[0].split(self._slash)[-1] + self.jobSuffix
                        else:
                            subinpName = inputName.split('.')[0] + self.jobSuffix
                        block.parameter['input'] = subinpName
                        self.writeInp([subblock], subinpName)

            if not 'dummy-manifest' in name:
                block._firstItem = self._firstItem
                if isinstance(output, IOBase):
                    output.writelines(block.__str__(includeSubData=False))
                elif type(output)==type([]):
                    output.append(''.join(block.__str__(includeSubData=False)))
                self._firstItem = False
            if block.suboptions and not skipsuboptions:
                self.writeBlocks(iterable=block.suboptions, output=output)
        if not isinstance(output, IOBase):
            return output
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writeInp(self, blocks=None, output=''):
        """writeInp(blocks=None, output='')
        
            This function writes out the contents of the input file structure (including any changes) to the file 
            indicated by *output*. 
            
            If *blocks* is not specified, every keyword block will be written. If *output* is
            not specified, the output .inp will be :attr:`~inpRW.inpRW.inpName` + :attr:`~inpRW.inpRW.jobSuffix`. 
            :attr:`~inpRW.inpRW.inpName` will have ".inp" removed before :attr:`~inpRW.inpRW.jobSuffix` is added.
            
            Args:
                blocks (list): The list of :class:`inpKeywords <.inpKeyword>` to write to output. Defaults to None, which 
                               will write out all keyword blocks.
                output (str): The name of the file to which the new input file will be written. Defaults to '', which
                              will write to :attr:`~inpRW.inpRW.inpName` + :attr:`~inpRW.inpRW.jobSuffix`."""
        
        self._firstItem = True
        if output=='':
            output = '.'.join(self.inpName.split('.')[:-1]) + self.jobSuffix
        if blocks==None:
            blocks = self.keywords
        outputfileName = self.outputFolder + output.split(self._slash)[-1]
        t1 = timing.time()
        print('Writing new file %s.' % outputfileName)
        with open(outputfileName, 'w', newline=self._nl, encoding=self._openEncoding) as f:
            if self._leadingcomments!=None:
                f.write(self._leadingcomments)
                #self._firstItem = False
            self.writeBlocks(blocks, f)
        print(' Wrote new file %s' % output)
        print('   time to write = %s' % (timing.time() - t1))

        
    