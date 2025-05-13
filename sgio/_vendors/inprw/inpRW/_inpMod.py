#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains functions for modifying the data in :attr:`~inpRW.inpRW.keywords`."""

# cspell:includeRegExp comments

from ._importedModules import *
from functools import reduce
import sgio._vendors.inprw.inpRW as inpRW
# from . import inpRW

class Mod:
    """The :class:`~inpRW._inpMod.Mod` class contains functions modify data in the parsed input file structure."""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def calculateCentroid(self, elementID):
        """calculateCentroid(elementID)

            This function gets the nodal coordinates of an element and calls :func:`centroid.averageVertices`. 
            
            Args:
                elementID (int or inpInt): The label of an element.
                
            Returns:
                numpy.ndarray: A numpy array containing the coordinates of the element centroid."""
        
        nodeCoords = [self.nd[i].data[1:] for i in self.ed[elementID].data[1:]]
        c = centroid.averageVertices(nodeCoords)
        return c

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def convertOPnewToOPmod(self, startStep=0, finishStep=None, bStep=None):
        """convertOPnewToOPmod(startStep=0, finishStep=None, bStep=None)
        
            Converts keyword parameter OP=NEW to OP=MOD or OP=REPLACE and removes unnecessary keywords from steps.

            This function will first identify a baseStep from which to compare all steps between and including *startStep*
            and *finishStep*. baseStep can be specified via the *bStep* parameter, or it will be the 0th step. The function
            will first identify the keyword blocks in baseStep which use the "OP" parameter (the list of potential keywords
            is stored in :attr:`~config._opKeywords`). This will include implied "OP" parameters.
            
            Args:
                startStep (int or str): The beginning step for which to convert "OP" parameters. Defaults to 0.
                finishStep (int or str): The last step for which to convert "OP" parameters. If None, all steps after  
                    and including *startStep* will be converted. Defaults to None.
                bStep (int or str): The index or name of the step in :attr:`kwg['Step'] <inpRW.inpRW.kwg>` from which 
                    the other steps will be compared. If bStep = None, the 0th step will be baseStep. Defaults to None.

            .. warning::
                This function should not be used. It needs to be reworked, as it does not properly deactivate step features
                that are inactive in subsequent steps.

            .. todo::
               Read Boundary Conditions in model data as the initial baseStep."""
                           
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def findStepRelativeIndex(step):
            """findStepRelativeIndex(step)
            
                Finds the index of *step* in :attr:`~inpRW.inpRW.steps`.

                Args:
                    step (int or str): If *step* is an :class:`int`, return *step*. If *step* is a string, find the \*STEP 
                        keyword block with name *step* in :attr:`~inpRW.inpRW.steps` and return its relative index.
                Returns:
                    int"""

            if step==None:
                return None
            elif isinstance(step, int):
                step = step
                return step
            elif isinstance(step, str):
                step = self.findKeyword('STEP', 'name=%s' % step, printOutput=False)[0].parameter['name']
                if step in self.steps:
                    step = self.steps[step][0]
                    return step
                else:
                    print('Did not find a step with name %s.' % step)
                    return None
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        stepsSorted = self.sortKWs(self.kwg['STEP'])
        opkws = [self.findKeyword(keywordName = self._opKeywords, printOutput=False, parentBlock=i) for i in stepsSorted]
        opkws_strings = [] + [[ self.writeBlocks([kw]) for kw in i] for i in opkws] # convert kw objects to strings for comparison
        base_items = []
        base_strings = []
        unique_items = []
        startStep = findStepRelativeIndex(startStep)
        loopString = 'enumerate(opkws_strings[%s:])' % startStep
        if finishStep:
            finishStep = findStepRelativeIndex(finishStep)
            loopString = 'enumerate(opkws_strings[%s:%s])' % (startStep, finishStep)
        if bStep != None:
            baseStep = findStepRelativeIndex(bStep)
            base_items = [i.path for i in opkws[baseStep]]
            base_strings = opkws_strings[baseStep]
        for s_index, step in eval(loopString):
            if bStep == None:
                a = stepsSorted[s_index]._baseStep
                if a != None:
                    baseStep = findStepRelativeIndex(a.name)
                    base_items = [i.path for i in opkws[baseStep]]
                    base_strings = opkws_strings[baseStep]
            if s_index == 0:
                unique_items += base_items
            for k_index, kw in enumerate(step):
                if kw not in base_strings:
                    unique_items.append(opkws[s_index][k_index].path)
        opkws.reverse()
        for step in opkws:
            step.reverse()
            for kw in step:
                if kw.path not in unique_items:
                    self.deleteKeyword(path=kw.path, updateInpStructure=False, printstatus=False)
                else:
                    block = self.parsePath(kw.path)[0]
                    if block:
                        try:
                            if rsl(kw.name)=='output':
                                block.parameter['OP'] = 'REPLACE'
                            else:
                                block.parameter['OP'] = 'MOD'
                        except TypeError:
                            if rsl(a.name)=='output':
                                block.parameter = createParamDictFromString(self.formatParameterOutput(block.parameter) + ', OP=REPLACE')
                            else:
                                block.parameter = createParamDictFromString(self.formatParameterOutput(block.parameter) + ', OP=MOD')
        self.updateInp()

    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def _convertOPnewToOPmod2(self):
    #    """convertOPnewToOPmod2()
    #    
    #        Converts keyword parameter OP=NEW to OP=MOD or OP=REPLACE and removes unnecessary keywords from steps.
    #        
    #        Args:
    #
    #        .. todo::
    #           Read Boundary Conditions in model data as the initial baseStep."""
    #                       
    #    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #    def findStepRelativeIndex(step):
    #        """findStepRelativeIndex(step)
    #        
    #            Finds the index of *step* in :attr:`~inpRW.inpRW.steps`.
    #
    #            Args:
    #                step (int or str): If *step* is an :class:`int`, return *step*. If *step* is a string, find the \*STEP 
    #                    keyword block with name *step* in :attr:`~inpRW.inpRW.steps` and return its relative index.
    #            Returns:
    #                int"""
    #
    #        if step==None:
    #            return None
    #        elif isinstance(step, int):
    #            stepind = step
    #            return stepind
    #        elif isinstance(step, str):
    #            step = self.findKeyword('STEP', 'name=%s' % step, printOutput=False)[0].parameter['name']
    #            stepfound = self.steps.get(step)
    #            if stepfound:
    #                stepind = stepfound[0]
    #                return stepind
    #            else:
    #                print('Did not find a step with name %s.' % step)
    #                return None
    #        elif isinstance(step, inpKeyword):
    #            for key, inpStep in self.steps.items():
    #                if inpStep[1] == step:
    #                    stepind = key
    #                    return stepind
    #
    #    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #    #==================================================================================================================
    #    class opKW(inpKeyword):
    #        """This class stores a string reproduction of the keyword block generated by wbfunc along with the keyword
    #            block. The string reproduction is used for hashes of this class and for equality tests."""
    #
    #        def __init__(self, block, wbfunc):
    #
    #            self.block = block
    #            self.string = wbfunc([self.block])[0]
    #            self.path = self.block.path
    #            self.data = self.block.data
    #            self.comments = self.block.comments
    #            self.parameter = self.block.parameter
    #            self.suboptions = self.block.suboptions
    #            self.name = self.block.name
    #
    #        def __hash__(self):
    #            return hash(self.string)
    #        
    #        def __eq__(self, other):
    #            return self.string == other
    #
    #        def __repr__(self):
    #
    #           return super().__repr__()
    #    #==================================================================================================================
    #
    #    #Define local variables for performance
    #    steps = self.steps
    #    wb = self.writeBlocks
    #    gpb = self.getParentBlock
    #    findkw = self.findKeyword
    #    opkws_m = self._opKeywords
    #    delkw = self.deleteKeyword
    #    cpdfs = createParamDictFromString
    #    fpo = self.formatParameterOutput
    #    inskw = self.insertKeyword
    #
    #    opKWsModel = [opKW(block, wb) for block in findkw(keywordName=opkws_m, printOutput=False) if gpb(block, 'STEP')==None]
    #    #blockstrings, paths = zip(*[[wb([kw]), kw.path] for kw in opKWsModel])
    #    uniqueItems = {'modelBase': set(opKWsModel)}
    #    baseItems = {'modelBase': set(opKWsModel)}
    #    opNewKwNames = {}
    #    for stepName in steps:
    #        print(f'\nCurrent Step: {stepName}')
    #        step = steps[stepName][1]
    #        opkws_s = [opKW(block, wb) for block in findkw(keywordName = opkws_m, printOutput=False, parentBlock=step)]
    #        #opkwstrings, paths = zip(*[[wb([kw]), kw.path] for kw in opkws]) # convert kw objects to strings for comparison
    #        stepOpKws = set(opkws_s)
    #        baseStep = step._baseStep
    #        if baseStep == None:
    #            baseStepName = 'modelBase'
    #            baseStepItems = baseItems['modelBase']
    #        else:
    #            baseStepName = findStepRelativeIndex(baseStep)
    #            baseStepItems = baseItems[baseStepName]
    #        print(f' Base Step: {baseStepName}')
    #        removedFeatures = baseStepItems.difference(stepOpKws)
    #        print(f' Removed Features : {"".join(wb([i.block for i in removedFeatures]))}')
    #        #removedFeaturesPaths = [baseStepItems[2][baseStepItems[1].index(item)] for item in removedFeatures]
    #        newFeatures = stepOpKws.difference(baseStepItems)
    #        #print(f' New Features : {"".join(wb([i.block for i in newFeatures]))}')
    #        #newFeaturesPaths = [newFeatures[2][newFeatures[1].index(item)] for item in newFeatures]
    #        #kwNamesMustBeInStep = set([block.name for block in removedFeatures.union(newFeatures)])
    #        #print(removedFeatures)
    #        opNewKwNames[stepName] = set([block.name for block in removedFeatures])
    #        uniqueItems[stepName] = removedFeatures.union(newFeatures)
    #        #print(f'Unique Items:  {"".join(wb([i.block for i in uniqueItems[stepName]]))}')
    #        baseItems[stepName] = baseStepItems.union(uniqueItems[stepName])
    #        stepUniqueItems = uniqueItems[stepName]
    #        #changed item and original from basestep are both showing up in unique items; set baseItems after deleting items in step
    #        for stepOpKw in self.sortKWs(opkws_s, reverse=True):
    #            needBlankKWNames = set()
    #            stepOpKwName = stepOpKw.name
    #            stepOpKwstr = wb([stepOpKw])[0]
    #            if stepOpKwstr not in stepUniqueItems:
    #                if stepOpKwName not in opNewKwNames:
    #                    delkw(path=stepOpKw.path, updateInpStructure=False, printstatus=False)
    #                else:
    #                    if rsl(stepOpKwName) in needBlankKWNames:
    #                        needBlankKWNames.remove(rsl(stepOpKwName))
    #            else:
    #                if stepOpKwName not in opNewKwNames:
    #                    if stepOpKwstr not in baseStepItems:
    #                        try:
    #                            if rsl(stepOpKwName)=='output':
    #                                stepOpKw.parameter['OP'] = 'REPLACE'
    #                            else:
    #                                stepOpKw.parameter['OP'] = 'MOD'
    #                        except TypeError:
    #                            if rsl(stepOpKwName)=='output':
    #                                stepOpKw.parameter = cpdfs(fpo(stepOpKw.parameter) + ', OP=REPLACE')
    #                            else:
    #                                stepOpKw.parameter = cpdfs(fps(stepOpKw.parameter) + ', OP=MOD')
    #                    else:
    #                        delkw(path=stepOpKw.path, updateInpStructure=False, printstatus=False)
    #                else:
    #                    if stepOpKwName in removedFeatures:
    #                        needBlankKWNames.add(rsl(stepOpKwName))
    #            for blankKWName in needBlankKWNames:
    #                blankKW = inpKeyword(name=blankKWName, parameters='OP=NEW')
    #                inskw(object=blankKW, path=f'{step.path}.suboptions[1]', updateInpStructure=False)
    #
    #    self.updateInp()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def createManifest(self, lastBaseStep=None, stepGroupingIn=None, parameterString=''):
        """createManifest(lastBaseStep=None, stepGroupingIn=None, parameterString='')

            Creates a \*MANIFEST :class:`~inpRW.inpRW` instance and places the steps in the original file into sub-input files.

            This function will reorganize the steps in the input file per the user's specification. The new \*MANIFEST
            input file will look like the following::

                *MANIFEST,BASE STATE=YES, EVOLUTION TYPE=HISTORY
                model_and_basesteps.inp
                stepGrouping1.inp
                stepGrouping2.inp
                stepGrouping3.inp

            The first input file will contain the model data and any common base steps for the subsequent simulations.
            All subsequent input files contain independent simulation histories. See that Abaqus documentation for
            more information on `*MANIFEST <https://help.3ds.com/2023/English/DSSIMULIA_Established/SIMACAEKEYRefMap/simakey-r-manifest.htm?contextscope=all&id=548c10151d164474bff2a41c0e9821f4>`_.

            *lastBaseStep* is the last step in the input file that will be considered a base step for the analysis. It can be
            a 0-based integer corresponding to the step number, or it can be a case-insensitive string corresponding to a 
            step name. If *lastBaseStep* is not specified, all steps in the simulation will be used in nonlinear
            load cases.
        
            *stepGroupingIn* is a sequence of sequences, the first item is the input file name, and the second is a
            sequence of the steps to associate with that input file. The sequence can use step names or integers.
            
            For example::
        
                stepGroupingIn = [ ['LoadA.inp', ['Step-1', 'Step-2']], ['LoadB.inp', [3, 4]] ]
            
            If *stepGroupingIn* is not specified, all steps after *lastBaseStep* will be independent nonlinear load cases.
            There is no limit on how steps can be ordered, reused, etc. However, it is the analyst's responsibility to 
            build a working step order, as this function does not check the validity of the simulation.
            
            *parameterString* is a string that allows the user to specify the parameters for \*MANIFEST. Specify them as
            you would on the Abaqus keyword line. The "BASE STATE" parameter will be set based on the *lastBaseStep* input. 
            "EVOLUTION TYPE=HISTORY" is automatically included and should not be specified, as this is currently (as of 
            Abaqus 2022 GA) the only valid option. 
            
            Example::
            
                parameterString = 'MODEL CHANGE, RESULTS=new' 
                
            Args:
                lastBaseStep (int or str): Indicates which step should be considered the last base step for the
                    \*MANIFEST steps. Use 0-based indices.
                stepGroupingIn (list): A Sequence of sequences, the first item is the input file name, and the second 
                    is a sequence of the steps to associate with that input file. The sequence can use step names or integers.
                parameterString (str): Specifies additional parameters for the keyword line. The "BASE STATE" and
                    "EVOLUTION TYPE" parameters will automatically be included.
                    
            Returns:
                inpRW: A new :class:`~inpRW.inpRW` instance reorganized as a \*MANIFEST input file."""
        
        if parameterString != '':
            ps = 'BASE STATE=NO, EVOLUTION TYPE=HISTORY, ' + parameterString
        else:
            ps = 'BASE STATE=NO, EVOLUTION TYPE=HISTORY'
        manInpName = self.inpName.split('.')[0] + '_man.inp'
        manInp = inpRW.inpRW(manInpName, organize=self.organize, ss=self.ss, rmtrailing0=self.rmtrailing0, jobSuffix=self.jobSuffix, parseSubFiles=self.parseSubFiles, preserveSpacing=self.preserveSpacing, _debug=self._debug)
        manInp.__dict__.update(self.inpKeywordArgs)
        manInp.outputFolder = self.outputFolder
        mBlock = inpKeyword(f'*MANIFEST, {ps}')
        dummyBlock1 = inpKeyword(name=f'DUMMY-MANIFEST_{self.inpName}')
        dummyBlock1.suboptions.extend(self.keywords)
        baseInp = self
        mBlock._subinps.append(baseInp)
        mBlock.suboptions.append(dummyBlock1)
        manInp.keywords.append(mBlock)
        manInp.updateInp()
        steps = manInp.sortKWs(manInp.kwg['STEP'])
        if lastBaseStep == None:
            baseSteps = []
            manSteps = steps
        elif isinstance(lastBaseStep, int):
            try:
                baseSteps = steps[:lastBaseStep + 1]
                manSteps = steps[lastBaseStep + 1:]
                mBlock.parameter['BASE STATE'] = 'YES'
                manInp._manBaseStep = baseSteps[-1]
                print('Setting step %s\n  as the last base step' % steps[lastBaseStep].formatKeywordLine())
            except IndexError:
                print('Input file does not have a step %s' % lastBaseStep)
                return None
        elif isinstance(lastBaseStep, str):
            lBS = manInp.findKeyword('STEP', parameters='name=%s' % lastBaseStep)
            if lBS:
                lBSindex = steps.index(lBS[0])
                baseSteps = steps[:lBSindex+1]
                manSteps = steps[lBSindex+1:]
                mBlock.parameter['BASE STATE'] = 'YES'
                manInp._manBaseStep = baseSteps[-1]
                print('Setting step %s as the last base step' % steps[lBSindex].formatKeywordLine())
        else:
            print('lastBaseStep not specified correctly')
            return None
        
        #remove Orientation parameter from *Boundary in mansteps, if it exists
        for pBlock in manSteps:
            orientBoundKWs = manInp.findKeyword(keywordName='BOUNDARY', parameters='ORIENTATION', printOutput=False, parentBlock=pBlock)
            if orientBoundKWs:
                for block in orientBoundKWs:
                    del block.parameter['ORIENTATION']
        
        if stepGroupingIn == None:
            stepGrouping = csid([[i.parameter['name'].strip('"') + '.inp', [ind, i.parameter['name']]] if 'name' in i.parameter else ['Step-%s.inp' % ind, [ind, 'step-%s' % ind]] for ind,i in enumerate(manSteps)])
        else:
            stepGroupingIn = [[i[0], [ind] + i[1]] for ind,i in enumerate(stepGroupingIn)]
            stepGrouping = csid(stepGroupingIn)
        
        #Write manSteps to new input file(s)
        sort_keys = sorted(stepGrouping, key=stepGrouping.get)

        for inpN in sort_keys:
            step_list = []
            inpN = str(inpN)
            stepID = stepGrouping[inpN][1:]
            subKws = inpKeywordSequence(parentBlock=mBlock)
            subKwsapp = subKws.append
            subinp = inpRW.inpRW(inpN)
            subinp.__dict__.update(self.inpKeywordArgs)
            subinp.outputFolder = self.outputFolder
            subinp._leadingcomments = ''
            dummyBlock2 = inpKeyword(name=f'DUMMY-MANIFEST_{inpN}')
            mBlock._subinps.append(subinp)
            mBlock.suboptions.append(dummyBlock2)
            subinp.keywords.append(dummyBlock2)
            dummyBlock2.suboptions = subKws
            for ind2,ID in enumerate(stepID):
                if isinstance(ID, int):
                    step_list.append(steps[ID])
                elif isinstance(ID, str):
                    step_list.append(manInp.findKeyword('STEP', parameters=f'NAME={ID}', printOutput=False)[0])
                s = step_list[-1]
                proc = s.suboptions[0]
                if ind2 == 0:
                    manInp._curBaseStep = manInp._manBaseStep
                s._baseStep = manInp._curBaseStep
                if rsl(proc.name) in manInp._generalSteps:
                    manInp._curBaseStep = s
                subKwsapp(step_list[-1])

        #Delete manSteps from existing input file
        manSteps.reverse()
        for step in manSteps:
            manInp.deleteKeyword(path=step.path, updateInpStructure=False)
        
        #Find and delete manSteps from baseInp, inelegant workaround
        baseInp.updateInp()
        for mstep in manSteps:
            stepParamline = mstep.formatParameterOutput()
            stepBlock = baseInp.findKeyword('step', parameters=stepParamline, printOutput=False)[0]
            baseInp.deleteKeyword(path=stepBlock.path)
        
        #Write *Manifest data lines
        mBlock.data = [[self.inpName]] + [[inpN] for inpN in sort_keys]
        manInp.updateInp()
    
        #Write new Manifest input file and the appropriate child input files
        return manInp
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deleteItemReferences(self, labelD, inputType='other', deleteModCouplings=False, delNodesFromElsLevel1=False, _level=0, _limit=100):
        """deleteItemReferences(labelD, inputType='other', deleteModCouplings=False, delNodesFromElsLevel1=False, _level=0, _limit=100)
       
            This function will delete the item references in *labelD* throughout the input file. If an item that is 
            deleted also deletes a :attr:`named reference <inpRW.inpRW.namedRefs>`, this function will also find the 
            references to those new items and delete them.

            A thorough explanation of the *delNodesFromElsLevel1* option is needed.
                
                The user has a set of nodes to delete. The user generates *labelD* with "labelD = findNodeRefs(nlabels)". 
                He then deletes the nodes and all references to the nodes (contained in *labelD*) with 
                ``deleteItemReferences(labelD, 'node')``. :func:`deleteItemReferences` will call itself to handle chained 
                item references, and it will specify the *_level* parameter to track how many levels deep it is. When deleting 
                nodes, :func:`deleteItemReferences` will by default delete the nodes and their references, which will 
                include elements. It deletes the elements by calling ``deleteItemReferences(elementD, 'element', _level=1)``, 
                which also handles deleting all references to the elements. 
                
                ``deleteItemReferences(elementD, 'element', _level=0)`` behaves a bit differently. When elements are 
                deleted, any nodes that were formally parts of elements but are no longer referenced by any elements will 
                be deleted. This does not happen with ``deleteItemReferences(elementD, 'element', _level=1)`` unless 
                *delNodesFromElsLevel1=True* is also specified. 
                
                This option has some niche use cases (for example, deleting fastener constructs of the form 
                mesh - coupling - solid elements representing weld - coupling - mesh). In most cases, leaving 
                *delNodesFromElsLevel1=False* (default) is the desired choice.
            
            Args:
                labelD (csid): Contains the mapping between the item references (the keys), and the location of the reference
                    along with the region that should be deleted if the item is deleted (the value). *labelD* should 
                    be the return :class:`csid` from a function in :class:`~inpRW._inpFindRefs.FindRefs`.
                inputType (str): Indicates to what *labelD* refers. Valid options are 'node', 'element', and 'other'. 
                    'node' will handle node label and node set references, 'element' will handle element label
                    and element set references, and 'other' handles all other cases. Defaults to 'other'.
                deleteModCouplings (bool): If True, all \*COUPLING, \*KINEMATIC COUPLING, and \*DISTRIBUTING COUPLING
                    keywords with modified application regions (\*SURFACE, \*NSET, \*ELSET) will be deleted.
                    Defaults to False.
                delNodesFromElsLevel1 (bool): If True, nodes can be deleted when element references are deleted in _level=1.
                    See detailed explanation above. Defaults to False.
                _level (int): Tracks when :func:`deleteItemReferences` calls itself to handle certain reference chains.
                    The user should not need to specify this. Defaults to 0.
                _limit (int): A limit on how many iterations this function will perform when trying to identify and delete
                    chains of references. This check is performed in a while loop, which could create an infinite loop
                    if something unexpected happens, hence the limit. The iterations referred to is something like the
                    following: delete a node -> delete an element -> delete an element set -> delete a surface ->
                    delete a contact pair. This example had 5 iterations from deleting nodes to deleting a contact pair
                    using an element based surface. The default value of 100 should be much higher than necessary.
                    Defaults to 100."""

        #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
        def checkIfNewRef(block):
            """checkIfNewRef(block)
            
                Checks if *block.name* is in :attr:`~inpRW.inpRW.namedRefs`, and if so adds *block.name* to newRefs."""

            bname = block.name
            tmpb = tmpNR.get(bname)
            if tmpb:
                rslbname = rsl(bname)
                if block in tmpb:
                    if rslbname in ['node', 'nset']:
                        newName = block.parameter['NSET']
                    elif rslbname in ['element', 'elset']:
                        newName = block.parameter['ELSET']
                    elif rslbname == 'contactpair':
                        newName = block.parameter['CPSET']
                    elif rslbname == 'rebarlayer':
                        pass
                    elif rslbname == 'rigidbody':
                        newName = block.parameter['ANALYTICAL SURFACE']
                    else:
                        newName = block.parameter['NAME']
                    newRefsObj = newRefs.setdefault(bname, [])
                    newRefsObj.append(newName)
        #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

        groups = []
        groupsappend = groups.append
        newRefs = csid() #Example: {'nset': ['nodeset1', 'nodeset2']}
        type_rsl = rsl(inputType)
        dataLinesDelete = []
        dldappend = dataLinesDelete.append
        blocksToDelete = set()
        btda = blocksToDelete.add
        tmpModBlocks = set()
        delkw = self.deleteKeyword
        deleteItemReferences = self.deleteItemReferences
        findItemReferences = self.findItemReferences
        parsePath = self.parsePath
        cpfs = self.createPathFromSequence
        ktridd = self.ktridd
        nm = self.nd
        em = self.ed
        coupSurfNames = self._couplingSurfNames
        kinCoupNsetNames = self._kinCoupNsetNames
        distCoupElsetNames = self._distCoupElsetNames
        tmpNR = csid([ (key, set(flatten(value.values()))) for key, value in self.namedRefs.items()])
        getParentBlock = self.getParentBlock
        subBlockLoop = self.subBlockLoop
        pktricd = self.pktricd
        if len(pktricd) > 0:
            removeParentKWActive = True
        else:
            removeParentKWActive = False
        nuca = self.nodesUpdatedConnectivity.append

        if type_rsl == 'node':
            print('Deleting nodes.')
            for label, data in labelD.items():
                groupsappend([i[1] for i in data])                
                try:
                    del nm[label]
                except KeyError:
                    continue
            nm.removeEmptySubMeshes()
            for nodeBlock in self.sortKWs(self.kwg['NODE']):
                if len(nodeBlock.data) == 0:
                    btda(nodeBlock)
        elif type_rsl == 'element':
            print('Deleting elements.')
            effectedNodes = set()
            for label, data in labelD.items():
                nodes = em[label].data[1:]
                effectedNodes.update(nodes)
                groupsappend([i[1] for i in data])
                del em[label]
            em.removeEmptySubMeshes()
            for elBlock in self.sortKWs(self.kwg['ELEMENT']):
                if len(elBlock.data) == 0:
                    btda(elBlock)
        else:
            print('Setting miscellaneous items to be deleted')
            for label, data in labelD.items():
                for item in data:
                    groupsappend(item[1])

        flatGroups = set(flatten(groups))
        if type_rsl == 'node' and _level == 0:
            print('Searching for elements referenced by deleted nodes.')
            elGroups = set([i for i in flatGroups if i[:7] == 'self.ed'])
            nonElGroups = flatGroups - elGroups
            #el format: 'self.ed[79]'
            elLabels = [int(el.split('[')[1].split(']')[0]) for el in elGroups]
            tmpElementD = self.findElementRefs(elements=elLabels)
            tmpDataLinesDelete, tmpModBlocks, tmpBlocksToDelete, tmpNewRefs = deleteItemReferences(labelD=tmpElementD, inputType='element', deleteModCouplings=deleteModCouplings, _level=1, delNodesFromElsLevel1=delNodesFromElsLevel1)
            dataLinesDelete.extend(tmpDataLinesDelete)
            blocksToDelete.update(tmpBlocksToDelete)
            newRefs.update(tmpNewRefs)
        elif type_rsl == 'element' and _level == 0:
            print('Searching for nodes referenced by deleted elements.')
            tmpNodeD = self.findNodeRefs(nodes=effectedNodes)
            print('Searching for nodes which have updated connectivity.')
            for nlabel in list(tmpNodeD.keys()):
                referenced = nm[nlabel].updateElements(em)
                if referenced == 2:
                    del tmpNodeD[nlabel]
                elif referenced == 1:
                    nuca(nlabel)
                    del tmpNodeD[nlabel]
            tmpDataLinesDelete, tmpModBlocks, tmpBlocksToDelete, tmpNewRefs = deleteItemReferences(labelD=tmpNodeD, inputType='node', deleteModCouplings=deleteModCouplings, _level=1)
            dataLinesDelete.extend(tmpDataLinesDelete)
            blocksToDelete.update(tmpBlocksToDelete)
            newRefs.update(tmpNewRefs)
            nonElGroups = flatGroups
        elif type_rsl == 'element' and _level == 1 and delNodesFromElsLevel1:
            print('Searching for nodes referenced by deleted elements.')
            nm.updateNodesConnectedElements(em)
            tmpNodeD = self.findNodeRefs(nodes=effectedNodes)
            print('Searching for nodes which have updated connectivity.')
            for nlabel in list(tmpNodeD.keys()):
                try:
                    referenced = nm[nlabel].updateElements(em) #MIGHT BE BETTER TO UPDATE NODE.ELEMENTS INSTEAD OF THIS
                except KeyError:
                    continue
                if referenced == 2:
                    del tmpNodeD[nlabel]
                elif referenced == 1:
                    nuca(nlabel)
                    del tmpNodeD[nlabel]
            tmpDataLinesDelete, tmpModBlocks, tmpBlocksToDelete, tmpNewRefs = deleteItemReferences(labelD=tmpNodeD, inputType='node', deleteModCouplings=deleteModCouplings, _level=1)
            dataLinesDelete.extend(tmpDataLinesDelete)
            blocksToDelete.update(tmpBlocksToDelete)
            newRefs.update(tmpNewRefs)
            nonElGroups = flatGroups
        elif type_rsl == 'element' and _level >= 1:
            print('Searching for nodes which have updated connectivity.')
            for nlabel in list(nm.keys()):
                referenced = nm[nlabel].updateElements(em)
                if referenced == 1:
                    nuca(nlabel)
            elGroups = set([i for i in flatGroups if i[:7] == 'self.ed'])
            nonElGroups = flatGroups - elGroups
        else:
            elGroups = set([i for i in flatGroups if i[:7] == 'self.ed'])
            nonElGroups = flatGroups - elGroups

        #print(f'_level: {_level}, len(groups): {len(groups)}, len(flatGroups): {len(flatGroups)}')
        modBlocksSet = set([i.split('.data[')[0] for i in nonElGroups])
        modBlocksIndices = [parsePath(i)[1] for i in modBlocksSet]
        modBlocks = nestedSort(modBlocksIndices, _level=1, reverse=True)
        modBlocks = set([parsePath(self.createPathFromSequence(i))[0] for i in modBlocks])
        if None in modBlocks:
            modBlocks.remove(None)
        nonElGroupsList = [parsePath(i)[1] for i in nonElGroups if parsePath(i)]
        nonElGroupsListS0 = nestedSort(nonElGroupsList, _level=2, reverse=True)
        del nonElGroupsList, modBlocksSet, modBlocksIndices
        print('Examining items slated for deletion. Keyword blocks will be deleted later, data items will be deleted now, and any now empty datalines will be tracked for deletion.')
        #print(f'inputType: {inputType}, _level: {_level}')
        for item in nonElGroupsListS0: #delete references
            path = self.createPathFromSequence(item)
            block = eval(path)
            if isinstance(block, inpKeyword):
                checkIfNewRef(block)
                btda(block)
            else:
                exec(f'del {path}')
            if 'data' in path:
                itemParent = path.rsplit('[', 1)[0]
                if len(eval(itemParent)) == 0:
                    dldappend(parsePath(itemParent)[1])
        
        if _level != 0:
            return dataLinesDelete, modBlocks, blocksToDelete, newRefs
        
        #print(f'inputType: {inputType}')
        c = 0
        while True:
            #print(f'c={c}')
            if len(dataLinesDelete) > 0:
                print('Deleting empty data lines.')
                dataLinesDelete = nestedSort(iterable=dataLinesDelete, _level=2, reverse=True)
                for line in dataLinesDelete:
                    try:
                        exec(f'del {self.createPathFromSequence(line)}')
                    except IndexError:
                        print(line)
                dataLinesDelete.clear()
                self.updateInp(gkw=False)

            if len(blocksToDelete) > 0:
                print('Sorting and deleting keyword blocks marked for deletion.')
                iterable = []
                iterapp = iterable.append
                mbr = modBlocks.remove
                tmbr = tmpModBlocks.remove
                
                def mbr_and_tmbr(block):
                    try:
                        mbr(block)
                    except KeyError:
                        pass
                    try:
                        tmbr(block)
                    except KeyError:
                        pass

                if removeParentKWActive:
                    for block in blocksToDelete:
                        parentKWName = self.pktricd.get(block)
                        if parentKWName:
                            parentBlock = getParentBlock(item=block, parentKWName=parentKWName)
                            iterapp(parsePath(parentBlock)[1])
                            parentSubBlocks = subBlockLoop(parentBlock, mbr_and_tmbr)
                        else:
                            iterapp(parsePath(block.path)[1])
                        mbr_and_tmbr(block)
                else:
                    for block in blocksToDelete:
                        iterapp(parsePath(block.path)[1])
                        mbr_and_tmbr(block)
                blocksToDeleteL = nestedSort(iterable=iterable, _level=1, reverse=True)
                for blockInd in blocksToDeleteL:
                    try:
                        delkw(positionl=blockInd, updateInpStructure=False, printstatus=False)
                    except KeywordNotFoundError:
                        print(blockInd)
                blocksToDelete.clear()
                self.updateInp(gkw=False)
            
            modBlocks.update(set(tmpModBlocks))
            if len(modBlocks) > 0:
                print('Examining modified keyword blocks and deleting empty blocks.')
                modBlocksReversed = nestedSort(iterable=[parsePath(block.path)[1] for block in modBlocks if parsePath(block.path)[0]], _level=1, reverse=True)
                try:
                    kinCoupD = csid([ [block.parameter['ref node'], block] for block in self.kwg['kinematic coupling'] ]) #WRONG, need to get nset from datalines, not parameter
                except KeyError:
                    pass
                try:
                    distCoupD = csid([ [block.parameter['elset'], block] for block in self.kwg['distributing coupling'] ])
                except KeyError:
                    pass
                try:
                    coupD = csid([ [block.parameter['surface'], block] for block in self.kwg['coupling'] ])
                except KeyError:
                    pass
                for blockIndices in modBlocksReversed: #deleting keyword blocks which now have empty data
                    block = parsePath(path=cpfs(seq=blockIndices))[0]
                    if block == None:
                        continue
                    if hasattr(block, 'data'):
                        lbdata = len(block.data)
                    else:
                        lbdata = 0
                    rslbname = rsl(block.name)
                    if rslbname == 'nset':
                        nsetvalue = block.parameter['nset']
                        if nsetvalue in kinCoupNsetNames:
                            if deleteModCouplings or lbdata < 2:
                                kinCoupBlock = kinCoupD.get(nsetvalue)
                                if kinCoupBlock:
                                    btda(kinCoupBlock)
                    elif rslbname == 'elset':
                        elsetvalue = block.parameter['elset']
                        if elsetvalue in distCoupElsetNames:
                            if deleteModCouplings or lbdata < 2:
                                distCoupBlock = distCoupD.get(elsetvalue)
                                if distCoupBlock:
                                    btda(distCoupBlock)
                    elif rslbname == 'surface':
                        surfvalue = block.parameter['name']
                        if surfvalue in coupSurfNames:
                            if deleteModCouplings or lbdata < 2:
                                coupBlock = coupD.get(surfvalue)
                                if coupBlock:
                                    btda(coupBlock)
                    if not hasattr(block, 'data') or rslbname in ktridd or lbdata == 0:
                        checkIfNewRef(block)
                        if removeParentKWActive:
                            parentKWName = pktricd.get(block)
                            if parentKWName:
                                parentblock = getParentBlock(item=block, parentKWName=parentKWName)
                                print(f'block {block.formatKeywordLine()} is set to be deleted. This triggers block {parentblock.formatKeywordLine()} and all its suboptions to be deleted due to these keyword names being included in inpRW.pktricd.')
                                block = parentblock
                        try:
                            delkw(path=block.path, updateInpStructure=False, printstatus=False)
                        except IndexError:
                            print(f'{block.path}')
                            raise IndexError
                    elif rslbname == 'distribution' and lbdata == 1:
                        checkIfNewRef(block)
                        try:
                            delkw(path=block.path, updateInpStructure=False, printstatus=False)
                        except IndexError:
                            print(f'{block.path}')
                            raise IndexError
                modBlocks.clear()
                tmpModBlocks.clear()
                self.updateInp()
            nri = list(newRefs.items())
            newRefs.clear()
            if len(nri) > 0:
                print('Blocks were deleted that defined named references. Searching for and deleting references to these blocks.')
                for kwName, refs in nri:
                    newLabelD = findItemReferences(kwName, refs)
                    if newLabelD:
                        tmpDataLinesDelete, tmpModBlocks, tmpBlocksToDelete, tmpNewRefs = deleteItemReferences(labelD = newLabelD, deleteModCouplings=deleteModCouplings, _level=2)
                        dataLinesDelete.extend(tmpDataLinesDelete)
                        modBlocks.update(tmpModBlocks)
                        blocksToDelete.update(tmpBlocksToDelete)
                        newRefs.update(tmpNewRefs)
            elif len(blocksToDelete) > 0:
                pass # this will call the loop again to clear out blocksToDelete
            else:
                break # nothing left to delete, break out of the function
            c += 1
            if c >= _limit:
                print('breaking to avoid potential infinite loop')
                break
        nm.updateNodesConnectedElements(em)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deleteKeyword(self, path='', positionl=None, updateInpStructure=True, printstatus=True):
        """deleteKeyword(path='', positionl=None, updateInpStructure=True, printstatus=True)

            Deletes the keyword block at the indicated location and updates the data structure.
        
            Either *path* or *positionl* is required. Set *updateInpStructure* to False if you need to delete many keyword 
            blocks from a large input file, as those update operations can be slow. If *updateInpStructure* == True,
            this function will call :func:`~inpRW.inpRW.updateInp`, but only update :class:`keyword block <.inpKeyword>`
            paths after (and including) the position of the deleted block, and it will not call 
            :func:`~inpRW._inpR.Read._groupKeywordBlocks`, as this function will automatically delete the entry from 
            :attr:`~inpRW.inpRW.kwg`.
            
            .. note::
            
                When deleting a list of keywords, deleting one keyword will change the indices of all subsequent keywords.
                However, the list of :attr:`inpKeyword.paths <inpKeyword.inpKeyword.path>` or position indices of keywords 
                to delete will not update automatically. For this reason, the user should always sort the list of keywords 
                to delete so that they are deleted from the end of the .inp towards the front. Deleting a keyword object 
                at the end of the list will not affect the indices of keywords prior to it. The sorting is more easily 
                handled when using *positionl* (which is a list of integers) than with *path*, which is a list of strings. 
                If the input file was parsed with organize=True, the user will need to perform a multi-level sort to account 
                for the keyword and suboption indices. Use :func:`.nestedSort` for this task. Example::
            
                    oldBlockPaths = list(flatten(oldBlockPaths))
                    #gets a flattened list of keyword paths to delete
                    
                    oldBlockPositionls = [self.parsePath(i)[1:] for i in oldBlockPaths] 
                    #gets the positionL from each path i.e. [1,[0]] will be keyword block 1, suboption 0
                
                    oldBlockPositionls1 = nestedSort(iterable=oldBlockPositionls, reverse=True)
                    #sorts oldBlockPositionls in reverse order. This will account for nested suboptions.
                
                Alternately, the user can account for the change of indices when deleting keywords. However, sorting
                and reversing the list of keywords to delete should be simpler in most cases.
            
            Args:
                path (str): A string indicating the path to the :class:`.inpKeyword` to delete. Defaults to ''.
                positionl (list): A sequence of sequences with the indices to the :class:`.inpKeyword` block
                    to delete. A path string will be generated from this via :func:`~inpRW._inpR.Read.createPathFromSequence`. 
                    Defaults to None.
                updateInpStructure (bool): If True, will call :func:`~inpRW.inpRW.updateInp` after deleting
                    the keyword block. Defaults to True.
                printstatus (bool): If True, print which keyword block is deleted. Defaults to True."""

        if path and positionl == None:
            tmp = self.parsePath(path)
        elif positionl and not path:
            tmp = self.parsePath(self.createPathFromSequence(positionl))
        else:
            print('Error! Exactly one of path or positionl is required. ')
            return None
        if not tmp[0]:
            if path!='':
                out = path
            elif positionl!=None:
                out = positionl
            print(f'No block at {out}.')
            raise KeywordNotFoundError
        obj, (keywpos, subpos, datapos) = tmp
        oldkwname = obj.name
        path = obj.path
        self.kwg[oldkwname].remove(obj)
        exec(f'del {path}')
        if updateInpStructure:
            self.updateInp(gkw=False, startIndex=keywpos)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getLabelsFromSet(self, blocks):
        """getLabelsFromSet(blocks)
        
            Returns a flat list of all the labels from the set defined in *block*. 

            Args:
                blocks (list): A list of \*NSET or \*ELSET keyword blocks.
               
            Returns:
                list: A flat list containing the labels in the sets. If more than one set is passed to this function,
                the output list will be sorted and contain only unique entries. If only one set is used, the output
                will not be sorted, and any duplicate entries will not be removed."""

        tmpdata = []
        tde = tmpdata.extend
        for block in blocks:
            if not 'generate' in block.parameter:
                tde(block.data)
            else:
                tde([list(range(line[0], line[1], line[2])) for line in block.data])
        if len(blocks) > 1:
            labels = list(set(flatten(tmpdata)))
            labels.sort()
        else:
            labels = list(flatten(tmpdata))
        return labels
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def insertKeyword(self, obj, path='', positionl=None, updateInpStructure=True):
        """insertKeyword(obj, path='', positionl=None, updateInpStructure=True)
            
            Inserts a new keyword object in the :class:`inpKeywordSequence` at the location specified by *path* or *positionl*.
            
            *obj* is required, and either *path* or *positionl* is required. Set *updateInpStructure* to False if you need to 
            insert many keyword blocks into a large input file, as those update operations can be slow. If *updateInpStructure* == True,
            this function will call :func:`~inpRW.inpRW.updateInp`, but only update :class:`keyword block <.inpKeyword>`
            paths after (and including) the position of the inserted block. :attr:`~inpRW.inpRW.kwg` will only have the
            new block added.

            .. note::
                Inserting multiple keywords should be done in reverse order. See the note in :func:`deleteKeyword` for
                a detailed explanation.
            
            Args:
                obj (inpKeyword): The new keyword block to insert.
                path (str): A string indicating the path to the :class:`.inpKeyword` to delete. Defaults to ''.
                positionl (list): A sequence of sequences with the indices to the :class:`.inpKeyword` block
                    to delete. A path string will be generated from this via :func:`~inpRW._inpR.Read.createPathFromSequence`.
                    Defaults to None.
                updateInpStructure (bool): If True, will call :func:`~inpRW.inpRW.updateInp` after deleting
                    the keyword block. Defaults to True."""
        
        if path and positionl==None:
            tmp = self.parsePath(path)
        elif positionl and not path:
            path = self.createPathFromSequence(positionl)
            tmp = self.parsePath(path)
        else:
            print('Error! Exactly one of path or positionl is required.')
            return None
        oldobj, (keywpos, subpos, datapos) = tmp
        if subpos == []:
            self.keywords.insert(keywpos, obj)
        else:
            pathtmp = path.rsplit('.', 1)[0]
            eval(f'{pathtmp}.suboptions.insert({subpos[-1]}, obj)')
        if updateInpStructure:
            self.updateInp(b=[obj], startIndex=keywpos)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mergeNodes(self, dupNodeDict):
        """mergeNodes(dupNodeDict)
        
            Merges pairs of nodes into one node. The node labels referred to by the keys in *dupNodeDict* will be replaced
            with the node labels in values.

            *dupNodeDict* should be a one-to-one mapping of node labels. The key will be replaced by the value. In most 
            cases, this dictionary should be created by using :func:`~inpRW._inpFind.Find.findCloseNodes`.

            For every pair of nodes in *dupNodeDict*, this function will first find every element connected to the old
            node (the key). Each of these elements will have their references to the node label in key replaced with the 
            node label in value. Then, the old node will have its :attr:`mesh.Node.elements` attribute cleared. Finally,
            :func:`deleteItemReferences` will be called to delete the old nodes and remove all remaining references to 
            them. Thus, the only locations in the input file where the old node labels will be replaced with the new
            node labels is in \*ELEMENT keyword blocks; all other references will simply be deleted.

            Args:
                dupNodeDict (dict): A dictionary which maps the node label to be removed with the node label with which
                    it should be replaced.
        """

        nd = self.nd
        ed = self.ed
        print(f'Merging {len(dupNodeDict)} duplicate nodes')
        for oldnode, goodnode in dupNodeDict.items():
            elements = nd[oldnode].elements
            for elementlabel in elements:
                element = ed[elementlabel]
                eldata = element.data
                node_index = eldata.index(oldnode)
                eldata[node_index] = goodnode
            nd[oldnode].elements.clear()
        print('Deleting old node labels and removing all references to them')
        oldNodeLabelD = self.findNodeRefs(dupNodeDict)
        self.deleteItemReferences(oldNodeLabelD, inputType='node')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reduceStepSubKWs(self, removeComments=False):
        """reduceStepSubKWs(removeComments=False)
        
            Consolidates keywords in a particular step that can have the "OP" parameter. 
            
            This function can also group some sub-keywords if the parent keywords are identical. This function is 
            limited to keyword blocks in 3 different groupings: :attr:`~config._mergeDatalineKeywordsOP`, 
            :attr:`~config._appendDatalineKeywordsOP`, and :attr:`~config._dofXtoYDatalineKeywordsOP`.

            If a keyword block to be removed has comments in its data, those comments will be included with the consolidated
            keyword block if removeComments=False. They will be immediately after the associated dataline if the 
            keyword is in :attr:`~config._appendDatalineKeywordsOP`, or they will all be appended to the end of the
            data if the keyword is in :attr:`~config._dofXtoYDatalineKeywordsOP`.
        
            Example::
            
                *BOUNDARY, OP=NEW, ORIENTATION="Orientation48"
                "Fixed Displacement24", 2, 2, 0.
                *BOUNDARY, OP=NEW, ORIENTATION="Orientation48"
                "Fixed Displacement24", 3, 3, 0.
                *BOUNDARY, OP=NEW, ORIENTATION="Orientation48"
                "Fixed Displacement24", 4, 4, 0.
                *OUTPUT, FIELD, FREQUENCY=1
                *ELEMENT OUTPUT
                S
                *OUTPUT, FIELD, FREQUENCY=1
                *ELEMENT OUTPUT
                E
                *OUTPUT, FIELD, FREQUENCY=1
                *ELEMENT OUTPUT
                PE
                *OUTPUT, FIELD, FREQUENCY=1
                *ELEMENT OUTPUT
                PEEQ
            
            will become::
            
                *BOUNDARY, OP=NEW, ORIENTATION="Orientation48"
                "Fixed Displacement24", 2, 4, 0.
                *OUTPUT, FIELD, FREQUENCY=1
                *ELEMENT OUTPUT
                S, E, PE, PEEQ

            Args:
                removeComments (bool): If True, any comments associated with keyword blocks that are now consolidated will
                                       be deleted. Defaults to False.
            
            .. todo::

                Add support for keywords in :attr:`~config._mergeDatalineKeywordsOP`."""
        
        if not self.organize:
            print('This function needs to work on an organized input file, otherwise keywords from different steps might be combined.')
        else:
            oldBlockPaths = []
            self._newKWs = []
            kwstoinsert = []
            kwstiapp = kwstoinsert.append
            for step in [self.parsePath(i)[0] for i in self.step_paths]:
                sBlocks = [block for block in step.suboptions]
                blockGroups = csid()
                for block in sBlocks:
                    if not block.name in blockGroups:
                        blockGroups[block.name] = csid()
                    kwline = block.formatKeywordLine()[1:] #[1:] leaves out the leading *
                    try:
                        blockGroups[block.name][kwline].append([block.path, block.data])
                    except (AttributeError, KeyError):
                        blockGroups[block.name][kwline] = [[block.path, block.data]]
                    if block.suboptions:
                        for sb in block.suboptions:
                            k = sb.name
                            k2 = block.formatKeywordLine(sb)[1:]
                            v = [[sb.path,sb.data]]
                            try:
                                blockGroups[block.name][kwline][0][2][k2].append(v)
                            except IndexError:
                                blockGroups[block.name][kwline][0].insert(2, csid())
                                blockGroups[block.name][kwline][0][2][k2] = [v]
                            except (TypeError, AttributeError, KeyError):
                                blockGroups[block.name][kwline][0][2][k2] = [v]
                for kwName, kw in list(blockGroups.items()):
                    for bgKWLine in sorted(kw, key=kw.get):
                        case=0
                        tmp = rsl(kwName)
                        if tmp in self._mergeDatalineKeywordsOP:
                            case = 1
                        elif tmp in self._appendDatalineKeywordsOP:
                            case = 2
                        elif tmp in self._dofXtoYDatalineKeywordsOP:
                            case = 3
                        elif tmp == 'boundary':
                            maxDataLen = max([len(i) for j in kw[bgKWLine] for i in j[1]])
                            if maxDataLen <= 2:
                                case = 2
                            else:
                                case = 3
                        
                        if case==1:
                            pass #low priority case, will handle later
                        
                        elif case==2:
                            newKW = inpKeyword()
                            self._parseKWLine(newKW, bgKWLine)
                            z = kw[bgKWLine]
                            p = [j[0] for j in z]
                            oldBlockPaths.append(p[1:])
                            newKW.path = p[0]
                            try:
                                if removeComments:
                                    datalist = [i for j in z for i in j[1] if not isinstance(i, str)] #nested list comprehension example
                                else:
                                    datalist = [i for j in z for i in j[1]]
                                newKW.data = datalist
                            except TypeError:
                                pass
                            if len(z[0])==3:
                                subD = z[0][2]
                                for subKWLine in sorted(subD, key=subD.get):
                                    subKW = inpKeyword()
                                    subKWLine = subKWLine
                                    self._parseKWLine(subKW, subKWLine)
                                    subkw = subD[subKWLine]
                                    subpaths = [i[0] for j in subkw for i in j]
                                    subpaths.sort()
                                    oldBlockPaths.append(subpaths[1:])
                                    if removeComments:
                                        subdata = reduce(lambda x,y: x+y, [k for j in subkw for i in j for k in i[1] if not isinstance(k, str)])
                                    else:
                                        subdata = reduce(lambda x,y: x+y, [k for j in subkw for i in j for k in i[1]])
                                    subKW.data = makeDataList(subdata)
                                    subKW.path = subpaths[0]
                                    newKW.suboptions.append(subKW)
                            self._newKWs.append(newKW)
                        
                        elif case==3:
                            xtoykw = inpKeyword()
                            self._parseKWLine(xtoykw, bgKWLine)
                            z = kw[bgKWLine]
                            p = [j[0] for j in z]
                            oldBlockPaths.append(p[1:])
                            xtoykw.path = p[0]
                            labelkw = xtoykw.cloneKW()
                            if removeComments:
                                datalist = [i for j in z for i in j[1] if not isinstance(i, str)]
                            else:
                                datalist = [i for j in z for i in j[1]]
                            dofXtoYdatalines, labelDatalines, comments = self._consolidateDofXtoYDatalines(datalist, removeComments)
                            xtoykw.data = dofXtoYdatalines
                            labelkw.data = labelDatalines
                            kwtoadd = [i for i in [labelkw, xtoykw] if len(i.data) > 0] #labelkw and xtoykw have the same path, so we want labelkw inserted first so xtoykw will push it back
                            if len(kwtoadd) == 0:
                                continue
                            else:
                                kwtoadd[0].comments = comments
                                self._newKWs.append(kwtoadd[0])
                                if len(kwtoadd) > 1:
                                    for nkw in kwtoadd[1:]:
                                        kwstiapp([nkw, kwtoadd[0]])
                            
            self._newKWs = list(flatten(self._newKWs))
            oldBlockPaths = list(flatten(oldBlockPaths))
            for a in self._newKWs:
                obd = [oldBlockPaths.index(i) for i in oldBlockPaths if a.path in i]
                obd.sort(reverse=True)
                for k in obd:
                    del oldBlockPaths[k]
            oldBlockPositionls = [self.parsePath(i)[1] for i in oldBlockPaths]
            oldBlockPositionls = nestedSort(oldBlockPositionls,  reverse=True)
            for kwn in self._newKWs:
                self.replaceKeyword(kwn, path=kwn.path, updateInpStructure=False)
            for oldkw in oldBlockPositionls:
                self.deleteKeyword(positionl=oldkw, updateInpStructure=False, printstatus=False)
            self.updateInp()
            for kwi in kwstoinsert:
                kwReftmp = kwi[1]
                kwRefParent = self.getParentBlock(item=kwReftmp, parentKWName='Step')
                tmpout = []
                self.writeBlocks(iterable=[kwReftmp], output=tmpout)
                kwRefpath = self.findKeyword(keywordName=kwReftmp.name, parameters=kwReftmp.parameter, data=kwReftmp.data, parentBlock=kwRefParent)[0].path
                self.insertKeyword(obj=kwi[0], path=kwRefpath)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def removeGenerate(self, generateBlocks=None):
        """removeGenerate(generateBlocks=None)
        
            Removes the GENERATE parameter from keyword blocks and expands the datalines.    

            This function will loop through the keyword blocks as specified in *generateBlocks* or it will search the entire 
            :class:`.inpKeywordSequence` for the appropriate blocks. It will remove the "GENERATE" parameter from blocks 
            such as \*NSET, and fully expand the datalines. It will ignore \*TIME POINTS, \*NODAL THICKNESS, and 
            \*NODAL ENERGY RATE keywords if *generateBlocks* == None.
            
            Args:
                generateBlocks (list): A list containing :class:`.inpKeyword` blocks. Defaults to None.
                
            .. todo::
               Test on latest version of inpRW."""
        
        if generateBlocks == None:
            try:
                generateBlocks = [i for i in self.findKeyword(parameters='GENERATE') if rsl(i.name) not in ['timepoints', 'nodalthickness', 'nodalenergyrate']]
            except TypeError:
                print(' removeGenerate command did not find anything to remove')
        else:
            for block in generateBlocks:
                if 'generate' in block.parameter:
                    newBlock = copy.copy(block)
                    del newBlock.parameter['generate']
                    newDataList = list(range(block.data[0][0], block.data[0][1] + block.data[0][2], block.data[0][2]))
                    newData = makeDataList(newDataList, 16)
                    newBlock.data = newData
                    self.replaceKeyword(obj=newBlock, path=newBlock.path)
                else:
                    print(' Skipping block %s, as it does not include the GENERATE parameter' % block.formatKeywordLine())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def replaceKeyword(self, obj, path='', positionl=None, updateInpStructure=True):
        """replaceKeyword(obj, path='', positionl=None, updateInpStructure=True)

            Deletes the keyword at the position designated by *path* or *positionl*, and then inserts the 
            new keyword object at the same location.

            *obj* is required, and either *path* or *positionl* is required. Set *updateInpStructure* to False if you need to 
            insert many keyword blocks into a large input file, as those update operations can be slow. If *updateInpStructure* == True,
            this function will call :func:`~inpRW.inpRW.updateInp`, but only update :class:`keyword block <.inpKeyword>`
            paths after (and including) the position of the inserted block. :attr:`~inpRW.inpRW.kwg` will only have the
            old block deleted and the new block added.
            
            Args:
                obj (inpKeyword): The new keyword block to insert.
                path (str): A string indicating the path to the :class:`.inpKeyword` to delete. Defaults to ''.
                positionl (list): A sequence of sequences with the indices to the :class:`.inpKeyword` block
                                  to delete. A path string will be generated from this via 
                                  :func:`~inpRW._inpR.Read.createPathFromSequence`. Defaults to None.
                updateInpStructure (bool): If True, will call :func:`~inpRW.inpRW.updateInp` after deleting
                                           the keyword block. Defaults to True."""
        
        if path and positionl == None:
            tmp = self.parsePath(path)
        elif positionl and not path:
            tmp = self.parsePath(self.createPathFromSequence(positionl))
        else:
            print('Error! Exactly one of path or positionl is required. ')
            return None
        oldobj, (keywpos, subpos, datapos) = tmp
        oldkwname = oldobj.name
        path = oldobj.path
        self.kwg[oldkwname].remove(oldobj)
        exec(f'{path} = obj')
        if updateInpStructure:
            self.updateInp(b=[obj], startIndex=keywpos) 

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateKTRIDD(self, keywordNames):
        """updateKTRIDD(keywordNames)
        
            Short for "update Keywords To Remove If Data Deleted", this function will update :attr:`~inpRW.inpRW.ktridd`.

            Args:
                keywordNames (list): A sequence of keyword names."""

        self.ktridd.update(set(keywordNames))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updatePKTRICD(self, mapping):
        """updatePKTRICD(mapping)
       
            Updates :attr:`~inpRW.inpRW.pktricd` with the items in mapping.

            Each key in :attr:`~inpRW.inpRW.pktricd` will be an :class:`inpKeyword` block. The value will be parent
            keyword name which should be deleted if the :class:`inpKeyword` contained in the key is deleted.
            
            Args:
                mapping (list): A sequence of sequences of the form [[[:class:`inpKeyword`, :class:`inpKeyword`, ...], parentKWName (str)]]."""

        for item in mapping:
            blocks, parentKWName = item
            temp = [[block, parentKWName] for block in blocks]
        self.pktricd.update(temp)
  
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _consolidateDofXtoYDatalines(self, datalist, removeComments=False):
        """_consolidateDofXtoYDatalines(datalist, removeComments=False)

            Examines *datalist* to determine the DOF ranges that are constrained. Returns a consolidated list.
        
            This should be specific to the \*ADAPTIVE MESH CONSTRAINT and \*BOUNDARY (with certain dataline lengths) keywords.
            The function will group the datalines by application region and by applied load, and will consolidate the applicable
            DOFs. This will return new dataline(s) as applicable. 
            
            The first grouping is via the application region, which is the 0th field in the dataline. This should be a 
            node label or node set name. This function just uses the item in the field as the key; so if one \*BOUNDARY
            applies to node 1, and another applies to nset1, which contains only node 1, the BCs will not be consolidated
            together.
            
            The items in datalist should all correspond to identical keyword lines, as it would be inappropriate to group
            items that are use different parameters. That must be handled before calling this function. Thus, the preferred
            method for calling this function is through :func:`reduceStepSubKWs`, as this will perform the necessary 
            operations prior to calling this function.
            
            Example::

                In: datalist = [["Fixed Displacement24", 2, 2, 0.], ["Fixed Displacement24", 3, 3, 0.], ["Fixed Displacement24", 4, 4, 0.]]
                In: self._consolidateDofXtoYDatalines(datalist)
                Out: ["Fixed Displacement24", 2, 4, 0.]

            Args:
                datalist (list): This should be a sequence of parsed datalines, not a list of strings.
                removeComments (bool): If True, comments included in datalist will be discarded. If False, they will be
                                       appended to the output.

            Returns:
                list: A list of the consolidated datalines."""

        dataD = csid()
        outputlist1 = []
        ol1app = outputlist1.append
        outputlist2 = []
        ol2app = outputlist2.append
        comments = []
        capp = comments.append
        for line in datalist:
            if isinstance(line, str) and not removeComments:
                capp(line)
                continue
            if len(line) == 4:
                try:
                    dataD[line[0]][line[3]].append(list(range(line[1], line[2]+1)))
                except (AttributeError, TypeError, KeyError):
                     dataD[line[0]] = {line[3]: [list(range(line[1], line[2]+1))]}
                except IndexError:
                    continue
            else:
                ol2app(line)
        for item in list(dataD.items()):
            for subitem in list(item[1].items()):
                dof = list(ranges(list(flatten(subitem[1]))))
                ol1app([[item[0], i[0], i[1], subitem[0]] for i in dof])
        try:
            outputlist1 = reduce(lambda x,y: x+y, outputlist1)
        except TypeError:
            pass
        return outputlist1, outputlist2, comments
    
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _convertSystem(self, node):
        """convertSystem(node)
        module: _inpMod.py
        
            .. warning::
               
               THIS FUNCTION HAS NOT BEEN TESTED WITH THE inpRW MODULE.
               IT NEEDS TO BE REWORKED BEFORE IT SHOULD BE USED.
        
            Pass in node data as (X, Y, Z, cos1, cos2, cos3, ActiveSystem tuple): 
            
            Example::

                (1, 10.0, 0.0, 20.0, 0.0, 0.0, 0.0, ((0.0, 0.0, 0.0, 1.0, 0.0, 0.0),))

            Returns the X,Y,Z coordinates of the node in the global CSYS.
            
            .. todo::
               Convert to inpRW."""
        
        Base = node[:3]
        A = node[-1][0][:3]
        B = node[-1][0][3:]
        Bl = tuple(map(lambda x,y: x-y, B, A))
        Bln = normalize(Bl)
        
        if len(node[-1])==1:
            theta11 = math.atan(Bln[1]/Bln[0])
            Cln = (-math.sin(theta11), math.cos(theta11), 0.0)
        elif len(node[-1])==2:
            C = node[-1][1][:3]
            Cl = tuple(map(lambda x,y: x-y, C, A))
            Cln = normalize(Cl)
            
        P = tuple(map(lambda x,y: x+y, Base, A))
        row1 = [Bln[0], Bln[1], Bln[2]]
        row2 = [Cln[0], Cln[1], Cln[2]]
        row3 = list(np.cross(row1, row2))
        matrix = np.array([row1, row2, row3], dtype='float')
        RHS = np.array([Base[0], Base[1], Base[2]], dtype='float')
        tmpout = np.linalg.solve(matrix, RHS)
        x2, y2, z2 = list(map(lambda x,y: x + y, tmpout, A))
        
        return (x2,y2,z2)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _isolateNodesToKeep(self, dup_node_dict, nodesToKeep):
        """_isolateNodesToKeep(dup_node_dict, nodesToKeep)
        
            .. warning::
               
               THIS FUNCTION HAS NOT BEEN TESTED WITH THE inpRW MODULE.
               IT NEEDS TO BE REWORKED BEFORE IT SHOULD BE USED.
        
            dup_node_dict is the duplicate nodes dictionary produced by _findCloseNodes, and nodesToKeep is a sequence of
            nodes. This function will remove all nodes in nodesToKeep from dup_node_dict."""
        
        c=0
        for node in nodesToKeep:
            try:
                del dup_node_dict[node]
                c+=1
            except KeyError:
                pass
        print('Removed %s nodes from the duplicate node dictionary' % c)
        return dup_node_dict
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _removeSystem(self):
        """_removeSystem()
        
            Finds the active system at all points of the input file, converts all node definitions to global coordinates, 
            then deletes the \*SYSTEM keywords.
            
            .. warning::
               
               THIS FUNCTION HAS NOT BEEN TESTED WITH THE inpRW MODULE.
               IT NEEDS TO BE REWORKED BEFORE IT SHOULD BE USED."""
        
        self._findActiveSystem()
        for block in self.sortKWs(self.kwg['NODE']):
            path = block.path
            nl = [(i[0], i[1], i[2], i[3], i[4], i[5], i[6], self._activeSystem[self.parsePath(path)[1]]) for i in block.data]
            print(nl[0])
            newData = tuple([(j[0],) + self._convertSystem(j[1:]) + j[4:] for j in nl])
            block.data = newData
        for systemBlock in self.sortKWs(self.kwg['SYSTEM']):
            self.deleteKeyword(systemBlock.path)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _replaceStarParameter(self):
        """_replaceStarParameter()
        module: _inpMod.py
        
            This function will delete \*PARAMETER keyword lines, and substitute the appropriate values into the input file.
            
            .. warning::
               
               THIS FUNCTION HAS NOT BEEN TESTED WITH THE inpRW MODULE.
               IT NEEDS TO BE REWORKED BEFORE IT SHOULD BE USED."""
    
        paramBlocks = self.sortKWs(self.kwg['PARAMETER'])
        paramData = reduce(lambda x,y: x + y,[j.data for j in paramBlocks])
        paramd = {i[0].split('=')[0].strip(' '): i[0].split('=')[-1].strip(' ')[1:-1] for i in paramData}
        for block in paramBlocks:
            self.deleteKeyword(block.path)
        tmpInp = 'tmp.inp'
        self.writeInp(output=tmpInp)
        f = open(tmpInp, 'r', newline='', encoding=self._openEncoding)
        nl = f.newlines
        data = f.read()
        f.close()
        os.remove('tmp.inp')
        for pair in list(paramd.items()):
            data = data.replace('<%s>' % (pair[0]), pair[1])
        f2 = open('%s_noparam.inp' % (tmpInp), 'w', newline=nl, encoding=self._openEncoding)
        print('writing %s_noparam.inp' % (tmpInp))
        f2.write(data)
        f2.close()
