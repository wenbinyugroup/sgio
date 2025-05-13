#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains functions for finding references to given names or labels in the input file.

    The functions here are not really meant to be used by the end-user; the designed entry point is through 
    :func:`~inpRW._inpFind.Find.findItemReferences`. All of the functions in this module are named like the following:
    "find[Abaquskeywordname]Refs". [Abaquskeywordname] should be an Abaqus keyword name, with the first word capitalized,
    no spaces, and all other words lower case. For example, if you wish to find references to a specific \*CONNECTOR BEHAVIOR,
    you would use findConnectorbehaviorRefs. Using  :func:`~inpRW._inpFind.Find.findItemReferences` will automatically format
    the provided keyword name.

    These functions are currently somewhat slow. The problem is that they need to search every location in the input file which
    could reference the desired items. The performance of these functions depends on the number of locations to check far 
    more than the number of items for which to search. For this reason, users should formulate their code so that these functions
    are called as few times as possible. For example, if the user wishes to search for references to nodes 1-5, they should not call 
    :func:`~inpRW._inpFindRefs.FindRefs.findNodeRefs` 5 times, once for each node label. Rather, they should pass in a sequence 
    or set of node labels. The function will check every possible location if the item in each location is in the input sequence.

    There are likely errors in these functions, as they are not fully tested and the Abaqus Keywords Guide is not always clear. 
    This class is also not yet complete; the initial focus was on items that can reference node or elements. Please report any 
    problems or new references that need to be addressed to erik.kane@3ds.com.
    
    These functions work (at least, once all the bugs are found), but they are slow. They will hopefully be eliminated in
    the future and replaced with an approach that can track references to specific items instead of needing to search for them."""

# cspell:includeRegExp comments

from ._importedModules import *

class FindRefs:
    """The :class:`~inpRW._inpFindRefs.FindRefs` class contains functions that find references to specific named entities
        in the parsed input file structure. For example, :func:`inp.findNodeRefs([1,2,3]) <inpRW._inpFindRefs.FindRefs.findNodeRefs>` 
        will find every location in the parsed input file structure which references node labels 1, 2, and 3."""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findAdaptivemeshcontrolsRefs(self, names):
        """findAdaptiveMeshControlsRefs(names)
       
            This function searches for keywords that can reference \*ADAPTIVE MESH CONTROLS.
            
            Args:
                names (list): A sequence of \*ADAPTIVE MESH CONTROLS names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *ADAPTIVE MESH CONTROLS name ref can be the value of the CONTROLS parameter
        kwGroup = ['ADAPTIVE MESH']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='CONTROLS')
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findClearanceRefs(self, names):
        """findClearanceRefs(names)
       
            This function searches for keywords that can reference \*CLEARANCE.
            
            Args:
                names (list): A sequence of \*CLEARANCE names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *CONTACT INITIALIZATION DATA, where the *CLEARANCE name ref can be the value of the INITIAL CLEARANCE parameter
        kwGroup = ['CONTACT INITIALIZATION DATA']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='INITIAL CLEARANCE')
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findConnectorbehaviorRefs(self, names):
        """findConnectorBehaviorRefs(names)
       
            This function searches for keywords that can reference \*CONNECTOR BEHAVIOR.
            
            Args:
                names (list): A sequence of \*CONNECTOR BEHAVIOR names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *CONNECTOR SECTION, where the *CONNECTOR BEHAVIOR name ref can be the value of the BEHAVIOR parameter
        kwGroup = ['CONNECTOR SECTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='BEHAVIOR')
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findContactclearanceRefs(self, names):
        """findContactClearanceRefs(names)
       
            This function searches for keywords that can reference \*CONTACT CLEARANCE.
            
            Args:
                names (list): A sequence of \*CONTACT CLEARANCE names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *CONTACT CLEARANCE ASSIGNMENT, where the *CONTACT CLEARANCE name ref can be p2 of all data lines
        kwGroup = ['CONTACT CLEARANCE ASSIGNMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=2)
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findContactinitializationdataRefs(self, names):
        """findContactInitializationRefs(names)
       
            This function searches for keywords that can reference \*CONTACT INITIALIZATION DATA.
            
            Args:
                names (list): A sequence of \*CONTACT INITIALIZATION DATA names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *CONTACT INITIALIZATION ASSIGNMENT, where the *CONTACT INITIALIZATION DATA name ref can be p2 of all data lines
        kwGroup = ['CONTACT INITIALIZATION ASSIGNMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=2)
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findContactpairRefs(self, names):
        """findContactpairRefs(names)
       
            This function searches for keywords that can reference the CPSET parameter of \*CONTACT PAIR.
            
            Args:
                names (list): A sequence of CPSET names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for blocks where the CPSet name ref can be the value of the CPSet parameter
        kwGroup = ['CLEARANCE', 'CONTACT CONTROLS', 'CONTACT OUTPUT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='CPSET')
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findDistributionRefs(self, names):
        """findDistributionRefs(names)
       
            This function searches for keywords that can reference \*DISTRIBUTION.
            
            Args:
                names (list): A sequence of \*DISTRIBUTION names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *ADJUST where the *DISTRIBUTION name ref can be the value of the DISTRIBUTION parameter
        kwGroup = ['ADJUST']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='DISTRIBUTION')

        #Looking for keywords where the *DISTRIBUTION name ref can be in p0 of all data lines
        kwGroup = ['DENSITY', 'SCALE MASS', 'SCALE STIFFNESS', 'SCALE STRESS DESIGN', 'SCALE THERMAL CONDUCTIVITY']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0)

        #Looking for *CONSTITUENT, where the *DISTRIBUTION name ref can be in all positions of all datalines if not DIRECTION=RANDOM3D
        kwGroup = ['CONSTITUENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='DIRECTION=RANDOM3D')

        #Looking for *ORIENTATION, Shell Section
        #Add this function
        #TODO


        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findDistributiontableRefs(self, names):
        """findDistributiontableRefs(names)
       
            This function searches for keywords that can reference \*DISTRIBUTION TABLE.
            
            Args:
                names (list): A sequence of \*DISTRIBUTION TABLE names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *ENRICHMENT ACTIVATION where the *ENRICHMENT name ref can be the value of the CRACK NAME parameter
        kwGroup = ['ENRICHMENT ACTIVATION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='NAME')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findElementprogressiveactivationRefs(self, names):
        """findElementprogressiveactivationRefs(names)
       
            This function searches for keywords that can reference \*ELEMENT PROGRESSIVE ACTIVATION.
            
            Args:
                names (list): A sequence of \*ELEMENT PROGRESSIVE ACTIVATION names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *ACTIVATE ELEMENTS where the *ELEMENT PROGRESSIVE ACTIVATION name ref can be the value of the ACTIVATION parameter
        kwGroup = ['ACTIVATE ELEMENTS']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ACTIVATION')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findElementRefs(self, elements, mode='labels'):
        """findElementRefs(elements, mode='labels')

            Finds all references in the input file to each element in elements.            
        
            Args:
                elements (list): A sequence of element labels or element set names (if *mode* == 'set').
                mode (str): Indicates which type of items for which the function searches. Valid choices:
                    'labels': indicates the function will search for element labels (default)
                    'set': indicates the function will search for element set names.
            
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        t1 = timing.time()
        _tmpD = {el: [] for el in elements}
        if self._debug:
            print(f'Time to generate blank _tmpD = {timing.time() - t1}')

        #############
        #DATA SECTION
        #############

        #Looking for keyword blocks where the element can be in the 0th field in every data line
        kwGroup = ['COMPOSITE MODAL DAMPING', 'CONNECTOR LOAD', 'CONNECTOR MOTION', 'D ADDED MASS', 'DECHARGE', 'DFLOW', 'DFLUX', 'DLOAD', 'FILM', 'FLOW', 'FOUNDATION', 'IMPEDANCE', 'MASS ADJUST', 'MULTIPHYSICS LOAD', 'PARTICLE OUTLET', 'PERIODIC MEDIA', 'RADIATE', 'RELEASE', 'SLOAD']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0)
            
        #Looking for *CO-SIMULATION REGION keyword blocks where the elset name can be in position 0 of all lines if not TYPE=NODE
        kwGroup = ['CO-SIMULATION REGION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=VOLUME', data_pos=0)

        #Looking for *CONTACT INTERFERENCE keyword blocks, where the elset name can be p0 of all lines if TYPE=ELEMENT
        kwGroup = ['CONTACT INTERFERENCE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=ELEMENT', data_pos=0)

        #Looking for *DISTRIBUTION keyword blocks, with LOCATION=ELEMENT or LOCATION=FACE
        t2 = timing.time()
        kwGroup = ['DISTRIBUTION']
        pars = ['LOCATION=ELEMENT', 'LOCATION=FACE']
        sub = list(flatten([j for j in [self.findKeyword(keywordName=kwGroup[0], parameters=i, printOutput=False) for i in pars] if j]))
        if sub:
            for block in sub:
                dlines = block.data[:3]
                lengths = [len(i) for i in dlines]
                if lengths == [8, 8, 6]:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0, linesToCheck='[3::3]', dataGroup='multiline')
                elif lengths == [8, 2, 8]:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0, linesToCheck='[2::2]', dataGroup='multiline')
                else:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0, linesToCheck='[1:]')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *DOMAIN DECOMPOSITION keyword blocks, where the elset can be in p0 of all lines if DEFINITION=ELSET or not ELSET, or in p0 of odd lines if DEFINITION=BOX
        t2 = timing.time()
        kwGroup = ['DOMAIN DECOMPOSITION']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            subDefBox = set([i for i in sub if rsl(i.parameter.get('DEFINITION', '')) == 'box'])
            if subDefBox:
                self._findData(labelD=_tmpD, kwNames=kwGroup[0], data_pos=0, linesToCheck='odd', dataGroup='multiline')
            sub2 = set([i for i in sub if not 'ELEMENT' in i.parameter or rsl(i.parameter.get('DEFINITION', '') == 'elset')]) - subDefBox
            if sub2:
                self._findData(labelD=_tmpD, kwNames=kwGroup[0], data_pos=0)
        
        #Looking for ELGEN keyword blocks
        t2 = timing.time()
        kwGroup = ['ELGEN'] 
        sub = self.findKeyword(keywordName=kwGroup[0], mode='all', printOutput=False)
        if sub:
            print('WARNING. *ELGEN keyword block detected in model. *ELGEN is not currently supported for element label operations.\
            Please generate a flattened input file if you need to operate on an element label contained in an *ELGEN command.')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')
                
        #Looking for *ELSET keyword blocks where the element label is in every position, unless the GENERATE parameter is included. If so, the GENERATE parameter will be removed and the ELSET expanded accordingly
        t2 = timing.time()
        kwGroup = ['ELSET']
        sub = self.findKeyword(keywordName=kwGroup[0], parameters='GENERATE', mode='all', printOutput=False)
        if sub:
            self.removeGenerate(sub)
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            self._findData(labelD=_tmpD, kwBlocks=sub, dataGroup='subline')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *EMBEDDED ELEMENT keyword blocks where the element label can be in all positions if the parameter EMBED NODES is not included
        kwGroup = ['EMBEDDED ELEMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='EMBED NODES', dataGroup='subline')
            
        #Looking for *EXTERNAL FIELD keyword blocks
        def externalFieldCustomSub(**kwargs):

            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])

        def externalFieldCustom(**kwargs):
            
            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if rsl(line[datano - 1]) != 'nodes' and item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
        
        t2 = timing.time()
        kwGroup = ['EXTERNAL FIELD']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            for block in sub:
                parent = self.getParentBlock(block)
                if rsl(parent.name) == 'fieldimport':
                    submodel = parent.parameter.get('submodel')
                    if submodel != None:
                        efcustom1 = externalFieldCustomSub
                        self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=4, custom=efcustom1)
                    else:
                        efcustom2 = externalFieldCustom
                        self._findData(labelD=_tmpD, kwBlocks=sub, data_pos='[1:5:3]', custom=efcustom2)

        #Looking for *IMPORT ELSET keyword blocks, where the element sets can be in every position of every line, but dataGroup is different based on the RENAME parameter
        kwGroup = ['IMPORT ELSET']
        suball = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        subRename = set([i for i in suball if i.parameter.get('RENAME') != None])
        subNoRename = set(suball) - subRename
        if subNoRename:
            self._findData(labelD=_tmpD, kwBlocks=subNoRename, dataGroup='subline')
        if subRename:
            self._findData(labelD=_tmpD, kwBlocks=subRename)
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *IMPORT keyword blocks, where the elset label can be in all positions of all lines if not RENAME, or in p0 of all lines if RENAME.
        t2 = timing.time()
        kwGroup = ['IMPORT']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        subRename = set([i for i in sub if not 'RENAME' in i.parameter])
        if subRename:
            self._findData(labelD=_tmpD, kwBlocks=subRename, data_pos=0)
        subNoRename = set(sub) - subRename
        if subNoRename:
            self._findData(labelD=_tmpD, kwBlocks=subRename, dataGroup='subline')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *INITIAL CONDITIONS
        t2 = timing.time()
        kwGroup = ['INITIAL CONDITIONS']
        case1pars = ['ACTIVATION', 'DAMAGE INITIATION', 'ENRICHMENT', 'INITIAL GAP', 'PLASTIC STRAIN', 'POROSITY', 'SPECIFIC ENERGY', 'SPUD EMBEDMENT', 'STRESS', 'VOLUME FRACTION']
        case2pars = ['ESDV', 'SOLUTION']
        case1blocks = list(flatten([j for j in [self.findKeyword(keywordName=kwGroup[0], parameters=f'TYPE={i}', printOutput=False) for i in case1pars] if j]))
        case2blocks = list(flatten([j for j in [self.findKeyword(keywordName=kwGroup[0], parameters=f'TYPE={i}', printOutput=False) for i in case2pars] if j]))
        case3blocks = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=HARDENING, NUMBER BACKSTRESSES', printOutput=False)
        case4blocks = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=REF COORDINATE', printOutput=False)
        if case1blocks:
            self._findData(labelD=_tmpD, kwBlocks=case1blocks, data_pos=0)
        if case2blocks:
            esdvblocks = self.findKeyword(keywordName='ELEMENT SOLUTION-DEPENDENT VARIABLES', printOutput=False)
            if esdvblocks:
                maxESDVLen = max([i.data[0][0] for i in esdvblocks])
                linestring = f'[::{math.ceil((maxESDVLen + 1) / 8)}]'
                self._findData(labelD=_tmpD, kwBlocks=case2blocks, data_pos=0, linesToCheck=linestring, dataGroup='multiline')
            else:
                print('Warning, found *INITIAL CONDITIONS, TYPE=ESDV or TYPE=SOLUTION block, but no corresponding *ELEMENT SOLUTION-DEPENDENT VARIABLEs block in input file. \
                Aborting search on these blocks.')
        if case3blocks:
            nbg1 = [block for block in case3blocks if block.parameter['NUMBER BACKSTRESSES'] > 1]
            nbe1 = list((set(case3blocks) - set(nbg1)))
            if nbg1:
                for block in nbg1:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0, linesToCheck=f'[::{block.parameter["NUMBER BACKSTRESSES"]}]', dataGroup='multiline')
            if nbe1:
                self._findData(labelD=_tmpD, kwBlocks=nbg1, data_pos=0)
        if case4blocks:
            self._findData(labelD=_tmpD, kwBlocks=case4blocks, data_pos=0, linesToCheck='even', dataGroup='multiline')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *MODEL CHANGE with the TYPE=ELEMENT parameters. The element label can be in all positions of all datalines in these blocks.
        kwGroup = ['MODEL CHANGE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=ELEMENT', dataGroup='subline')
        
        #Looking for *MOTION with the ELEMENT parameter. The element label can be in position 0 of all datalines in these blocks.
        kwGroup = ['MOTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='ELEMENT', data_pos=0)            
        
        #Looking for *NORMAL, and *SURFACE with the TYPE=ELEMENT parameters. The element label can be in position 0 of all datalines in these blocks.
        kwGroup = ['NORMAL', 'SURFACE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=ELEMENT', data_pos=0)

        #Looking for *SURFACE with the TYPE=CUTTING SURFACE parameter, where the element labels can be in all positions of datalines 1+
        kwGroup = ['SURFACE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=CUTTING SURFACE', linesToCheck='[1:]', dataGroup='subline')

        #Looking for *PARTICLE GENERATOR MIXTURE keyword blocks. The elset label can be in all positions of all datalines in these blocks.
        kwGroup = ['PARTICLE GENERATOR MIXTURE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, dataGroup='subline')

        #Looking for *REBAR keyword blocks where the element label can be in position 0 of even lines if the parameter GEOMETRY=SKEW, but not SINGLE is not included, else position 0 of all lines
        t2 = timing.time()
        kwGroup = ['REBAR']
        c1 = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        c2 = self.findKeyword(keywordName=kwGroup[0], parameters='GEOMETRY=SKEW', printOutput=False)
        if c2:
            c1 = list(set(c1) - set(c2))
            for block in c2:
                if 'SINGLE' not in block.parameter:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0, linesToCheck='even', dataGroup='multiline')
                else:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0)
        if c1:
            self._findData(labelD=_tmpD, kwBlocks=c1, data_pos=0)
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *SECTION POINTS keyword blocks, where the element label can be in position 1 of all lines if the parentblock is *BEAM SECTION GENERATE, or position 1 of even lines if parentblock is B*EAM GENERAL SECTION, SECTION=MESHED
        t2 = timing.time()
        kwGroup = ['SECTION POINTS']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        for block in sub:
            pb = self.getParentBlock(block)
            if rsl(pb.name) == 'beamsectiongenerate':
                self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=1)
            elif rsl(pb.name) == 'beamsectiongenerate' and 'section' in pb.parameter and rsl(pb.parameter['section'])=='meshed':
                self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=1, linesToCheck='even', dataGroup='multiline')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *TEMPERATURE keyword blocks. The elset label can be in all positions of all datalines in these blocks if FILE, INTERPOLATE and DRIVING ELSETS are included.
        kwGroup = ['TEMPERATURE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='FILE, INTERPOLATE, DRIVING ELSETS', data_pos=0)
            
        ##################
        #Parameter Section
        ##################

        #Looking for keyword blocks where the elset label can be the value of the ELSET parameter
        if mode=='set':
            kwGroup = ['ADAPTIVE MESH', 'ADAPTIVE MESH REFINEMENT', 'BEAM GENERAL SECTION', 'BEAM SECTION', 'CHANGE FRICTION', 'COHESIVE SECTION', 'CONNECTOR SECTION', 'CONTOUR INTEGRAL', 
                       'CREEP STRAIN RATE CONTROL', 'DASHPOT', 'DISCRETE SECTION', 'DISTRIBUTING COUPLING', 'DOMAIN DECOMPOSITION', 'DRAG CHAIN', 'EL FILE', 'EL PRINT', 'ELEMENT MATRIX OUTPUT',
                       'ELEMENT OPERATOR OUTPUT', 'ELEMENT OUTPUT', 'ELEMENT RECOVERY MATRIX', 'ELEMENT RESPONSE', 'ENERGY FILE', 'ENERGY OUTPUT', 'ENERGY PRINT', 'ENRICHMENT', 'EPJOINT',
                       'EULERIAN MESH MOTION', 'EULERIAN SECTION', 'EXTREME ELEMENT VALUE', 'FASTENER', 'FIXED MASS SCALING', 'FLUID PIPE CONNECTOR SECTION', 'FLUID PIPE SECTION', 'FRAME SECTION',
                       'GAP', 'GASKET SECTION', 'HEATCAP', 'INTEGRATED OUTPUT', 'INTERFACE', 'ITS', 'JOINT', 'MASS',  'MATRIX GENERATE', 'MEMBRANE SECTION', 'NONSTRUCTURAL MASS', 'NSET', 
                       'PERFECTLY MATCHED LAYER', 'PIPE-SOIL INTERACTION', 'RADIATION FILE', 'RADIATION OUTPUT', 'RADIATION PRINT', 'RIGID BODY', 'RIGID SURFACE', 'ROTARY INERTIA', 
                       'SHELL GENERAL SECTION', 'SHELL SECTION', 'SLIDE LINE', 'SOLID SECTION', 'SPRING', 'SUBCYCLING', 'SUBMODEL', 'SUBSTRUCTURE CHANGE', 'SUBSTRUCTURE GENERATE', 
                       'SUBSTRUCTURE OUTPUT', 'SUBSTRUCTURE PROPERTY', 'SURFACE SECTION', 'STEADY STATE DETECTION', 'STEADY STATE TRANSPORT', 'UEL PROPERTY', 'VARIABLE MASS SCALING'] 
            self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ELSET')

        #Looking for *ELCOPY keyword blocks where the elset label can be the value of the OLD SET parameter
        kwGroup = ['ELCOPY']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='OLD SET')

        #Looking for *EMBEDDED ELEMENT keyword blocks where the elset label can be the value of the HOST ELSET parameter
        kwGroup = ['EMBEDDED ELEMENT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='HOST ELSET')

        #Looking for *USER ELEMENT keyword blocks where the element label can be the value of the OLD ELEMENT parameter
        kwGroup = ['USER ELEMENT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='OLD ELEMENT')

        #Looking for *STATIC keyword blocks, where the elset name can be the value of the FULLY PLASTIC parameter
        kwGroup = ['STATIC']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='FULLY PLASTIC')

        #Looking for *SUBMODEL keyword blocks where the elset label can be the value of the GLOBAL ELSET parameter
        kwGroup = ['SUBMODEL']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='GLOBAL ELSET')

        #Looking for *SUBSTRUCTURE PATH keyword blocks where the element label can be the value of the ENTER ELEMENT parameter
        kwGroup = ['SUBSTRUCTURE PATH']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ENTER ELEMENT')

        #Looking for *PRE-TENSION SECTION keyword blocks where the element label can be the value of the ELEMENT parameter
        kwGroup = ['PRE-TENSION SECTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ELEMENT')

        if self._debug:
            print(f' Time to find all element refs = {timing.time() - t1}')
        return _tmpD
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findEnrichmentRefs(self, names):
        """findEnrichmentRefs(names)
       
            This function searches for keywords that can reference \*ENRICHMENT.
            
            Args:
                names (list): A sequence of \*ENRICHMENT names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *ENRICHMENT ACTIVATION where the *ENRICHMENT name ref can be the value of the CRACK NAME parameter
        kwGroup = ['ENRICHMENT ACTIVATION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='NAME')

        #Looking for *CONTOUR INTEGRAL where the *ENRICHMENT name ref can be the value of the CRACK NAME parameter
        kwGroup = ['CONTOUR INTEGRAL']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='CRACK NAME')

        #Looking for *SURFACE where the *ENRICHMENT name ref can be all positions of all lines if TYPE=XFEM
        kwGroup = ['SURFACE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=XFEM', dataGroup='subline')

        #Looking for *INITIAL CONDITIONS where the *ENRICHMENT name ref can be p2 of all lines if TYPE=ENRICHMENT
        kwGroup = ['INITIAL CONDITIONS']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=ENRICHMENT', data_pos=2)

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findFastenerpropertyRefs(self, names):
        """findFastenerpropertyRefs(names)
       
            This function searches for keywords that can reference \*FASTENER PROPERTY.
            
            Args:
                names (list): A sequence of \*FASTENER PROPERTY names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *FASTENER where the *FASTENER PROPERTY name ref can be the value of the PROPERTY parameter
        kwGroup = ['FASTENER']
        self._findParam(labelD=_tmpD, kwNames=kwGroup , parameterName='PROPERTY')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findFieldmappercontrolsRefs(self, names):
        """findFieldmappercontrolsRefs(names)
       
            This function searches for keywords that can reference \*FIELD MAPPER CONTROLS.
            
            Args:
                names (list): A sequence of \*FIELD MAPPER CONTROLS names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *EXTERNAL FIELD where the *FIELD MAPPER CONTROLS name ref can be in p6 of all lines
        kwGroup = ['EXTERNAL FIELD']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=6)

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findFluidbehaviorRefs(self, names):
        """findFluidbehaviorRefs(names)
       
            This function searches for keywords that can reference \*FLUID BEHAVIOR.
            
            Args:
                names (list): A sequence of \*FLUID BEHAVIOR names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *FLUID INFLATOR MIXTURE, where the fluid behavior name ref can be in the first set of datalines, 8 per line, up to NUMBER SPECIES entries.
        sub = self.findKeyword(keywordName='FLUID INFLATOR MIXTURE', printOutput=False)
        if sub:
            for block in sub:
                numFB = block.parameter['NUMBER SPECIES']
                linestring = f'[::{math.ceil((numFB + 1) / 8)}]'
                self._findData(labelD=_tmpD, kwBlocks=block, linesToCheck=linestring, dataGroup='alldata')
        
        #Looking for *FLUID CAVITY, where the fluid behavior name ref can be the value of the BEHAVIOR parameter
        kwGroup =['FLUID CAVITY']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='BEHAVIOR')

        #Looking for *DISCRETE SECTION, where the fluid behavior name ref can be the value of the FLUID BEHAVIOR parameter
        kwGroup = ['DISCRETE SECTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='FLUID BEHAVIOR')
    
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findGasketbehaviorRefs(self, names):
        """findGasketbehaviorRefs(names)
       
            This function searches for keywords that can reference \*GASKET BEHAVIOR.
            
            Args:
                names (list): A sequence of \*GASKET BEHAVIOR names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *GASKET SECTION, where the *GASKET BEHAVIOR name ref can be the value of the BEHAVIOR parameter
        kwGroup = ['GASKET SECTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='BEHAVIOR')
        return _tmpD    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findImpedancepropertyRefs(self, names):
        """findImpedancepropertyRefs(names)
       
            This function searches for keywords that can reference \*IMPEDANCE PROPERTY.
            
            Args:
                names (list): A sequence of \*IMPEDANCE PROPERTY names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *IMPEDANCE PROPERTY name ref can be the value of the PROPERTY parameter
        kwGroup = ['IMPEDANCE', 'SIMPEDANCE']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='PROPERTY')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findIncidentwaveinteractionpropertyRefs(self, names):
        """findIncidentwaveinteractionpropertyRefs(names)
       
            This function searches for keywords that can reference \*INCIDENT WAVE INTERACTION PROPERTY.
            
            Args:
                names (list): A sequence of \*INCIDENT WAVE INTERACTION PROPERTY names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *INCIDENT WAVE INTERACTION PROPERTY name ref can be the value of the PROPERTY parameter
        kwGroup = ['INCIDENT WAVE INTERACTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='PROPERTY')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findIncidentwavepropertyRefs(self, names):
        """findIncidentwavepropertyRefs(names)
       
            This function searches for keywords that can reference \*INCIDENT WAVE PROPERTY.
            
            Args:
                names (list): A sequence of \*INCIDENT WAVE PROPERTY names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *INCIDENT WAVE PROPERTY name ref can be the value of the PROPERTY parameter
        kwGroup = ['INDICENT WAVE']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='PROPERTY')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findIntegratedoutputsectionRefs(self, names):
        """findIntegratedoutputsectionRefs(names)
       
            This function searches for keywords that can reference \*INTEGRATED OUTPUT SECTION.
            
            Args:
                names (list): A sequence of \*INTEGRATED OUTPUT SECTION names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])
                
        #Looking for *INTEGRATED OUTPUT where the *INTEGRATED OUTPUT SECTION name ref can be the value of the SECTION parameter
        kwGroup = ['INTEGRATED OUTPUT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='SECTION')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findNodeRefs(self, nodes, mode='labels'):
        """findNodeRefs(nodes, mode='labels')

            Finds all references in the input file to each node in nodes.            
        
            Args:
                nodes (list): A sequence of node labels or node set names (if *mode* == 'set').
                mode (str): Indicates which type of items for which the function searches. Valid choices:
                    'labels': indicates the function will search for node labels (default)
                    'set': indicates the function will search for node set names.
            
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        t1 = timing.time()
        #_tmpD = {n: [] for n in nodes}
        _tmpD = csid([[n, []] for n in nodes])
        nd = self.nd
        if self._debug:
            print(f'Time to generate blank _tmpD = {timing.time() - t1}')

        #Find temperature lines based on temperature points for beam and shell elements
        maxTempPtsShell = 0
        maxTempPtsBeam = 0
        shellSec = self.findKeyword(keywordName='SHELL SECTION', parameters='TEMPERATURE', printOutput=False)
        if shellSec:
            maxTempPtsShell = max([block.parameter['TEMPERATURE'] for block in shellSec])
        beamSec = self.findKeyword(keywordName='BEAM SECTION', parameters='SECTION=ARBITRARY, TEMPERATURE=VALUES', printOutput=False)
        if beamSec:
            maxTempPtsBeam = max([block.data[0][0] for block in beamSec])
        maxTempPts = max([maxTempPtsShell, maxTempPtsBeam])
        temperatureLines = f'[::{math.ceil((maxTempPts + 1) / 8)}]'

        #############
        #Data Section
        #############

        #Looking for keyword blocks where the node label can be in the 0th field in every data line
        kwGroup = ['ACOUSTIC FLOW VELOCITY', 'ADAPTIVE MESH CONSTRAINT', 'BOND', 'BOUNDARY', 'CECHARGE', 'CECURRENT', 'CFILM', 
        'CFLOW', 'CFLUX', 'CLOAD', 'CRADIATE', 'DISPLAY BODY', 'DISTRIBUTING COUPLING', 'FLUID FLUX', 'FLUID INFLATOR',
        'KINEMATIC COUPLING', 'MASS FLOW RATE', 'MATRIX CHECK', 'NGEN', 'NODAL ENERGY RATE', 'PARAMETER SHAPE VARIATION', 
        'PRESSURE PENETRATION', 'PRESSURE STRESS', 'RETAINED NODAL DOFS', 'SURFACE FLAW', 'TRANSPORT VELOCITY']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0)
        
        #Looking for keyword blocks where the node label can be in the 1st field in every data line
        kwGroup = ['CFLOW', 'DISPLAY BODY', 'INCIDENT WAVE INTERACTION', 'NGEN', 'NORMAL', 'PERIODIC MEDIA', 'PRESSURE PENETRATION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=1)
        
        #Looking for keyword blocks where the node label can be in the 2nd field in every data line
        kwGroup = ['DIPLAY BODY', 'INCIDENT WAVE INTERACTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=2)

        #Looking for keyword blocks where the node label can be in the 4th field in every data line
        kwGroup = ['DIPLAY BODY', 'INCIDENT WAVE INTERACTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=4)

        #Looking for *BOUNDARY, PHANTOM=EDGE keyword blocks where the node label can be in position 1 of all data lines
        kwGroup = ['BOUNDARY']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='PHANTOM=EDGE', data_pos=1)
        
        #Looking for *C ADDED MASS keyword blocks where the node label can be in position 0 of even data lines
        kwGroup = ['C ADDED MASS']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0, linesToCheck='EVEN', dataGroup='multiline')

        #Looking for *CLEARANCE keyword blocks, where the node can be in p0 of all lines with TABULAR but not BOLT, or in p0 of datalines 1+ if BOLT
        kwGroup = ['CLEARANCE']
        sub1 = self.findKeyword(keywordName=kwGroup[0], parameters='TABULAR', printOutput=False)
        sub2 = set([i for i in sub1 if i.parameter.get('bolt') != None])
        sub = set(sub1) - sub2
        if sub:
            self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0)
        if sub2:
            self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0, linesToCheck='[1:]', dataGroup='multiline')

        #Looking for *CONTOUR INTEGRAL keyword blocks where the node label can be in odd positions of data lines 1+ with the CRACK TIP NODES and NORMAL parameters, or in the 1st position of all datalines if CRACK TIP NODES is included
        kwGroup = ['CONTOUR INTEGRAL']
        self._findData(labelD=_tmpD, kwNames=kwGroup[0], parameters='CRACK TIP NODES', excludeParameters='NORMAL, XFEM', data_pos='[0:2]')
        self._findData(labelD=_tmpD, kwNames=kwGroup[0], parameters='CRACK TIP NODES, NORMAL', excludeParameters='XFEM', linesToCheck='[1:]')
        self._findData(labelD=_tmpD, kwNames=kwGroup[0], excludeParameters='CRACK TIP NODES, NORMAL, XFEM', data_pos=0)
        self._findData(labelD=_tmpD, kwNames=kwGroup[0], parameters='NORMAL', excludeParameters='CRACK TIP NODES, XFEM', linesToCheck='[1:]')
        
        #Looking for *CO-SIMULATION REGION keyword blocks where the nset name can be in position 0 of all lines if TYPE=NODE
        kwGroup = ['CO-SIMULATION REGION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=NODE', data_pos=0)

        #Looking for *DISTRIBUTION keyword blocks where the node label can be in position 0 of all lines if LOCATION=NODE
        kwGroup = ['DISTRIBUTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='LOCATION=NODE', data_pos=0, linesToCheck='[1:]')

        #Looking for *DSLOAD keyword blocks where the node can be in position 5 of all lines if position 4 is WETTING ADVANCE
        def dsLoadCustom(**kwargs):
            
            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if len(line) > 4 and isinstance(line[4], str) and rsl(line[4]) == 'wettingadvance' and item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
        
        t2 = timing.time()
        kwGroup = ['DSLOAD']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            for block in sub:
                dscustom = dsLoadCustom
                self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=5, custom=dscustom)
        
        #Looking for node references in self.ed 
        if mode=='labels':
            t2 = timing.time()
            kwGroup = ['ELEMENT']
            if len(_tmpD) / len(nd) > 0.25:
                for elabel, value in self.ed.items():
                    data = value.data
                    for nlabel in data[1:]:
                        node = _tmpD.get(nlabel)
                        if node != None:
                            dataString = f'self.ed[{elabel}]'
                            node.append([f"{dataString}.data[{data.index(nlabel)}]", [dataString]])
            else:
                keys = _tmpD.keys()
                elabels = set(flatten([nd.get(i).elements for i in keys if nd.get(i)!=None]))
                for elabel in elabels:
                    try:
                        data = self.ed[elabel].data
                    except KeyError:
                        continue
                    for nlabel in data[1:]:
                        node = _tmpD.get(nlabel)
                        if node != None:
                            dataString = f'self.ed[{elabel}]'
                            node.append([f"{dataString}.data[{data.index(nlabel)}]", dataString])
            if self._debug:
                print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')
        
        
        #Looking for *EMBEDDED ELEMENT keyword blocks where the node label can be in all positions if the EMBED NODES parameter is included
        kwGroup = ['EMBEDDED ELEMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='EMBED NODES', dataGroup='subline')

        #Looking for *EQUATION keyword blocks where the node label is in every third position of datalines 1+
        kwGroup = ['EQUATION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos = '[::3]', linesToCheck='[1:]', dataGroup='alldata')

        #Looking for *EXTERNAL FIELD keyword blocks
        def externalFieldCustomSub(**kwargs):

            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])

        def externalFieldCustom(**kwargs):
            
            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if rsl(line[datano - 1]) == 'nodes' and item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
        
        t2 = timing.time()
        kwGroup = ['EXTERNAL FIELD']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            for block in sub:
                parent = self.getParentBlock(block)
                if rsl(parent.name) == 'fieldimport':
                    submodel = parent.parameter.get('submodel')
                    if submodel != None:
                        efcustom1 = externalFieldCustomSub
                        self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=1, custom=efcustom1)
                    else:
                        efcustom2 = externalFieldCustom
                        self._findData(labelD=_tmpD, kwBlocks=sub, data_pos='[1:5:3]', custom=efcustom2)

        #Looking for *FIELD keyword blocks where the node label can be in the 0th position of each data grouping, where the data grouping is determined by the number of temperature points for the element
        t2 = timing.time()
        kwGroup = ['FIELD']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0, linesToCheck=temperatureLines)
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')
        
        #Looking for *FLUID EXCHANGE keyword blocks where the node label is in the 0th and 1st position (all positions) of the 0th data line.
        kwGroup = ['FLUID EXCHANGE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, linesToCheck=0, dataGroup='alldata')

        #Looking for *IMPERFECTION keyword blocks where the node label is in the 0th position if the FILE and INPUT parameters are omitted.
        kwGroup = ['IMPERFECTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='FILE, INPUT', data_pos=0)
        
        #Looking for *IMPORT NSET keyword blocks, where the nodeset label is in position 0 of each dataline if the RENAME parameter is included, else in position 1
        t2 = timing.time()
        kwGroup = ['IMPORT NSET']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            subset = set(sub)
            rename = [i for i in sub if 'RENAME' in i.parameter]
            if rename:
                self._findData(labelD=_tmpD, kwBlocks=rename, data_pos=1)
                sub = list(subset - set(rename))
            self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0)
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')
        
        #Looking for *INITIAL CONDITIONS keyword blocks where the node label can be in various positions depending on the parameters')
        t2 = timing.time()
        kwGroup = ['INITIAL CONDITIONS']
        pos0typepars = ['TYPE=' + i  for i in ['ACOUSTIC STATIC PRESSURE', 'CONCENTRATION', 'FLUID PRESSURE', 'MASS FLOW RATE', 'NODE REF COORDINATE', 'PORE PRESSURE', 'PRESSURE STRESS', 'RATIO', 'RELATIVE DENSITY', 'SATURATION', 'VELOCITY']]
        pos0GroupSub = [j for j in [self.findKeyword(keywordName=kwGroup[0], parameters=i, mode='keyandone', printOutput=False) for i in pos0typepars] if j]
        if pos0GroupSub:
            pos0GroupSub = list(flatten(pos0GroupSub))
            self._findData(labelD=_tmpD, kwBlocks=pos0GroupSub, data_pos=0)
        pos0Special = [j for j in self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=FIELD, SECTION SPECIFICATION=UNIFORM', mode='all', printOutput=False) if j]
        if pos0Special:
            self._findData(labelD=_tmpD, kwBlocks=pos0Special, data_pos=0)
        typeContactGroupSub = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=CONTACT', mode='all', printOutput=False)
        if typeContactGroupSub:
            self._findData(labelD=_tmpD, kwBlocks=typeContactGroupSub, data_pos=2)
        typeFieldGroupSub = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=FIELD', mode='all', printOutput=False)
        if typeFieldGroupSub:
            typeFieldGroupSub = [i for i in typeFieldGroupSub if i not in pos0Special]
            for block in typeFieldGroupSub:
                pk = 'VARIABLE'
                if 'variable' in block.parameter:
                    v = block[pk][1]
                    if v<=7:
                        self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0)
                    else:
                        lines = eval('range(len(block.data))[::int(math.ceil((v-7)/8.))]')
                        self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=0, linesToCheck=lines, dataGroup='multiline')
        typeRotatingVelocitySub = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=ROTATING VELOCITY', mode='all', printOutput=False)
        typeRotatingVelocityDefNodesSub = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=ROTATING VELOCITY, DEFINITION=NODES', mode='all', printOutput=False)
        if typeRotatingVelocitySub:
            if typeRotatingVelocityDefNodesSub:
                self._findData(labelD=_tmpD, kwBlocks=typeRotatingVelocityDefNodesSub, data_pos=0, linesToCheck='ODD', dataGroup='multiline')
                self._findData(labelD=_tmpD, kwBlocks=typeRotatingVelocityDefNodesSub, data_pos='[0:2]', linesToCheck='EVEN', dataGroup='multiline')
                typeRotatingVelocitySub = list(set(typeRotatingVelocitySub) - set(typeRotatingVelocityDefNodesSub))
            self._findData(labelD=_tmpD, kwBlocks=typeRotatingVelocitySub, data_pos=0, linesToCheck='ODD', dataGroup='multiline')
        if maxTempPts > 7:
            self._findData(labelD=_tmpD, kwNames=kwGroup[0], parameters='TYPE=TEMPERATURE', data_pos=0, linesToCheck=temperatureLines, dataGroup='multiline')
        else:
            self._findData(labelD=_tmpD, kwNames=kwGroup[0], parameters='TYPE=TEMPERATURE', data_pos=0)
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *MOTION keyword blocks where the node label can be in position 0 if the ELEMENT parameter is omitted
        kwGroup = ['MOTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='ELEMENT', data_pos=0)
        
        #Looking for *MPC keyword blocks where the node label is in every position except the 0th
        kwGroup = ['MPC']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos='[1:]', dataGroup='subline')

        #Looking for *NCOPY keyword blocks where the node label is in the 0th position if the POLE parameter is specified
        kwGroup = ['NCOPY']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='POLE', data_pos=0)

        #Looking for *NODAL ENERGY RATE and NODAL THICKNESS keyword blocks where the node label can be in positions 0 and 1 if the GENERATE parameter is included, or in position 0 if it is omitted
        t2 = timing.time()        
        kwGroup = ['NODAL ENERGY RATE', 'NODAL THICKNESS']
        c1 = list(flatten([j for j in [self.findKeyword(keywordName=i, printOutput=False) for i in kwGroup] if j]))
        if c1:
            c2 = list(flatten([j for j in [self.findKeyword(keywordName=i, parameters='GENERATE', mode='all', printOutput=False) for i in kwGroup] if j]))
            c1 = list(set(c1) - set(c2))
            self._findData(labelD=_tmpD, kwBlocks=c1, data_pos=0)
            if c2:
                self._findData(labelD=_tmpD, kwBlocks=c2, data_pos='[0:2]')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')
            
        #Looking for *NSET, *SLIDE LINE, and *TRACER PARTICLE keyword blocks where the node label is in every position, unless the GENERATE parameter is included. If so, the GENERATE parameter will be removed and the NSET expanded accordingly
        t2 = timing.time()
        kwGroup = ['NSET', 'SLIDE LINE', 'TRACER PARTICLE']
        sub_gen = list(flatten([j for j in [self.findKeyword(keywordName=i, parameters='GENERATE', mode='all', printOutput=False) for i in kwGroup] if j]))
        if sub_gen:
            self.removeGenerate(sub_gen)
        sub = list(flatten([j for j in [self.findKeyword(keywordName=i, printOutput=False) for i in kwGroup] if j]))
        if sub:
            self._findData(labelD=_tmpD, kwBlocks=sub, dataGroup='subline')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *ORIENTATION keyword blocks where the node label can be in all positions of the 0th dataline if the DEFINITION=NODES parameter is included
        kwGroup = ['ORIENTATION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='DEFINITION=NODES', linesToCheck=0, dataGroup='alldata')

        #Looking for *SECTION FILE and *SECTION PRINT keyword blocks where the node label can be in position 0 of the 0th dataline and in positions 0 and 4 of the second dataline
        t2 = timing.time()        
        kwGroup = ['SECTION FILE', 'SECTION PRINT']
        sub = list(flatten([j for j in [self.findKeyword(keywordName=i, printOutput=False) for i in kwGroup] if j]))
        if sub:
            self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0, linesToCheck=0, dataGroup='alldata')
            self._findData(labelD=_tmpD, kwBlocks=sub, data_pos='[0:5:4]', linesToCheck=1, dataGroup='alldata')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *STATIC keyword blocks where the node label can be in position 5 of the dataline if the RIKS parameter is included
        kwGroup = ['STATIC']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='RIKS', data_pos=5)

        #Looking for *SUBMODEL keyword blocks where the node label can be in all positions if neither TYPE=SURFACE nor ACOUSTIC TO STRUCTURE are included
        kwGroup = ['SUBMODEL']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='TYPE=SURFACE, ACOUSTIC TO STRUCTURE', dataGroup='subline')
        
        #Looking for *SURFACE keyword blocks where the node label can be in position 0 of the dataline if the TYPE=NODE parameter is included, or positions 0 and 1 of line 0 if TYPE=CUTTING SURFACE and DEFINITION=NODES are included
        t2 = timing.time()
        kwGroup = ['SURFACE']
        c1 = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=NODE', mode='all', printOutput=False)
        c2 = self.findKeyword(keywordName=kwGroup[0], parameters='TYPE=CUTTING SURFACE, DEFINITION=NODES', mode='all', printOutput=False)
        if c1:
            self._findData(labelD=_tmpD, kwBlocks=c1, data_pos=0)
        if c2:
            self._findData(labelD=_tmpD, kwBlocks=c2, data_pos='[0:2]', linesToCheck=0, dataGroup='alldata')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *TEMPERATURE keyword blocks where the node label can be in position 0 of all datalines, but only specific datalines if applying temperature points in beams or shells and more than 7 temperature points are specified
        t2 = timing.time()
        kwGroup = ['TEMPERATURE']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            subSpecial = self.findKeyword(keywordName=kwGroup[0], parameters='FILE, INTERPOLATE, DRIVING ELSETS', printOutput=False)
            if subSpecial:
                self._findData(labelD=_tmpD, kwBlocks=subSpecial, data_pos=1)
                sub = list(set(sub) - set(subSpecial))
            if maxTempPts > 7:
                self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0, linesToCheck=temperatureLines, dataGroup='multiline')
            else:
                self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0)
            if self._debug:
                print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        ##################
        #Parameter Section
        ##################

        #Looking for keyword blocks where the node label can be the value of the REF NODE parameter
        kwGroup = ['COUPLING', 'DLOAD', 'DSLOAD', 'FLUID CAVITY', 'INTEGRATED OUTPUT SECTION', 'KINEMATIC COUPLING',
        'RIGID BODY', 'RIGID SURFACE', 'SOLID SECTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='REF NODE')

        #Looking for keyword blocks where the node label can be the value of the NODE parameter
        kwGroup = ['MONITOR', 'PRE-TENSION SECTION'] 
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='NODE')

        #Looking for keyword blocks where the nset label can be the value of the NSET parameter
        kwGroup = ['CONTACT FILE', 'CONTACT PRINT', 'CONTACT RESPONSE', 'CONTACT OUTPUT', 'ELEMENT RESPONSE', 'ENERGY OUTPUT', 'EXTREME NODE VALUE',
                  'FRACTURE CRITERION', 'FREQUENCY', 'IMPERFECTION', 'MATRIX ASSEMBLE', 'NMAP', 'NODE FILE', 'NODE OUTPUT', 'NODE PRINT', 'NODE RESPONSE', 'PARAMETER SHAPE VARIATION', 
                  'RADIATION VIEW FACTOR', 'SUBSTRUCTURE GENERATE', 'TRANSFORM'] 
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='NSET')

        #Looking for keyword blocks where the nset label can be the value of the NODE SET parameter
        kwGroup = ['ADJUST']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='NODE SET')

        #Looking for *ACOUSTIC CONTRIBUTION blocks where the nodeset can be the value of the ACOUSTIC NODES parameter
        kwGroup = ['ACOUSTIC CONTRIBUTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ACOUSTIC NODES')

        #Looking for *CONTACT CLEARANCE blocks where the nodeset can be the value of the SEARCH NSET parameter
        kwGroup = ['CONTACT CLEARANCE', 'CONTACT INITIALIZATION DATA']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='SEARCH NSET')

        #Looking for *CONTACT PAIR blocks where the nodeset can be the value of the ADJUST parameter
        kwGroup = ['CONTACT PAIR']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ADJUST')

        #Looking for *FASTENER blocks where the nodeset can be the value of the REFERENCE NODE SET parameter
        kwGroup = ['FASTENER']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='REFERENCE NODE SET')
        
        #Looking for *PARTICLE GENERATOR blocks where the nodeset can be the value of the FLUID CAVITY REFNODE parameter
        kwGroup = ['PARTICLE GENERATOR']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='FLUID CAVITY REFNODE')

        #Looking for *MATRIX GENERATE blocks where the nodeset can be the value of the INTERFACE NODES parameter
        kwGroup = ['MATRIX GENERATE']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='INTERFACE NODES')
        
        #Looking for *NCOPY blocks where the nodeset can be the value of the OLD SET parameter
        kwGroup = ['NCOPY']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='OLD SET')          

        #Looking for *PERIODIC keyword blocks where the node label can be the value of the INLET CONTROL NODE, OUTLET CONTROL NODE, or TRIGGER NODE parameters
        t2 = timing.time()
        kwGroup = ['PERIODIC MEDIA']
        parGroupSub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if parGroupSub:
            self._findParam(labelD=_tmpD, kwBlocks=parGroupSub, parameterName='INLET CONTROL NODE')
            self._findParam(labelD=_tmpD, kwBlocks=parGroupSub, parameterName='OUTLET CONTROL NODE')
            self._findParam(labelD=_tmpD, kwBlocks=parGroupSub, parameterName='TRIGGER NODE')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *RIGID BODY keyword blocks, where the node can be the value of PIN NSET or TIE NSET. REF NODE is handled previously.
        t2 = timing.time()
        kwGroup = ['RIGID BODY']
        parGroupSub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if parGroupSub:
            self._findParam(labelD=_tmpD, kwBlocks=parGroupSub, parameterName='PIN NSET')
            self._findParam(labelD=_tmpD, kwBlocks=parGroupSub, parameterName='TIE NSET')
        if self._debug:
            print(f'Time for block {kwGroup} = {timing.time() - t2:.8f}')

        #Looking for *TIE, where the node can be the value of the TIED NSET parameter
        kwGroup = ['TIE']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='TIED NSET')
        
        if self._debug:
            print(f' Time to find all node refs = {timing.time() - t1}')
        return _tmpD
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findOrientationRefs(self, names):
        """findOrientationRefs(names)
       
            This function searches for keywords that can reference \*ORIENTATION.
            
            Args:
                names (list): A sequence of \*ORIENTATION names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *SECTION CONTROLS, where the *ORIENTATION name can be in p1 of line 3 if ELEMENT CONVERSION=BACKGROUND GRID
        kwGroup = ['SECTION CONTROLS']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='ELEMENT CONVERSION=BACKGROUND GRID', data_pos=1)

        #Looking for keywords where the *ORIENTATION name can be in p2 of all lines
        kwGroup = ['CONTACT PAIR', 'EULERIAN SECTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=2)

        #Looking for keywords where the *ORIENTATION name can be in p3 of all lines
        kwGroup = ['CONTACT PAIR', 'D EM POTENTIAL']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=3)

        #Looking for keywords where the *ORIENTATION name can be in p3 of all lines if COMPOSITE
        kwGroup = ['SHELL SECTION', 'SOLID SECTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='COMPOSITE', data_pos=3)

        #Looking for *CONNECTOR SECTION, where the *ORIENTATION name can be in all positions of line 1
        kwGroup = ['CONNECTOR SECTION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, linesToCheck=1, dataGroup='alldata')

        #Looking for keywords where the *ORIENTATION name can be in all p6 of all lines
        kwGroup = ['DECURRENT', 'DSECURRENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=6)

        #Looking for *SURFACE PROPERTY ASSIGNMENT, where the *ORIENTATION name can be in p1 of all lines if PROPERTY=ORIENTATION
        kwGroup = ['SURFACE PROPERTY ASSIGNMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='PROPERTY=ORIENTATION', data_pos=1)

        #Looking for keyword blocks where the *ORIENTATION name ref can be the value of the ORIENTATION parameter
        kwGroup = ['ADJUST', 'BOUNDARY', 'COHESIVE SECTION', 'COUPLING', 'DASHPOT', 'DLOAD', 'DSLOAD', 'ELEMENT RESPONSE', 'EPJOINT', 'EULERIAN MESH MOTION', 'FASTENER', 
                   'GASKET SECTION', 'INERTIA RELIEF', 'INTEGRATED OUTPUT SECTION', 'JOINT', 'KINEMATIC COUPLING', 'MASS', 'MEMBRANE SECTION', 'NODE RESPONSE', 
                   'PERIODIC MEDIA', 'PIPE-SOIL INTERACTION', 'REBAR', 'REBAR LAYER', 'ROTARY INERTIA', 'SHELL GENERAL SECTION', 'SHELL SECTION', 'SOLID SECTION', 
                   'SPRING', 'UEL PROPERTY']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ORIENTATION')

        #Looking for *JOINTED MATERIAL, where the *ORIENTATION name ref can be the value of the JOINT DIRECTION parameter
        kwGroup = ['JOINTED MATERIAL']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='JOINT DIRECTION')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findPeriodicmediaRefs(self, names):
        """findPeriodicmediaRefs(names)
       
            This function searches for keywords that can reference \*PERIODIC MEDIA.
            
            Args:
                names (list): A sequence of \*PERIODIC MEDIA names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *MEDIA TRANSPORT, where the *PERIODIC MEDIA name ref can be in p0 of all lines
        kwGroup = ['MEDIA TRANSPORT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0)

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findRebarlayerRefs(self, names):
        """findRebarlayerRefs(names)
       
            This function searches for keywords that can reference \*REBAR LAYER.
            
            Args:
                names (list): A sequence of \*REBAR LAYER names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *ELEMENT OUTPUT, where the *REBAR LAYER name ref can be the value of the REBAR parameter
        kwGroup = ['ELEMENT OUTPUT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='REBAR')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findRebarRefs(self, names):
        """findRebarRefs(names)
       
            This function searches for keywords that can reference \*REBAR.
            
            Args:
                names (list): A sequence of \*REBAR names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *PRESTRESS HOLD, where the *REBAR name ref can be in p1 of all lines
        kwGroup = ['PRESTRESS HOLD']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=1)

        #Looking for *INITIAL CONDITIONS, where the *REBAR name ref can be in p1 if REBAR, but the lines to check varies
        kwNames = ['INITIAL CONDITIONS']
        case2blocks = self.findKeyword(keywordName=kwNames[0], parameters='TYPE=SOLUTION, REBAR', printOutput=False)
        if case2blocks:
            esdvblocks = self.findKeyword(keywordName='ELEMENT SOLUTION-DEPENDENT VARIABLES', printOutput=False)
            if esdvblocks:
                maxESDVLen = max([i.data[0][0] for i in esdvblocks])
                linestring = f'[::{math.ceil((maxESDVLen + 1) / 8)}]'
                self._findData(labelD=_tmpD, kwBlocks=case2blocks, data_pos=1, linesToCheck=linestring, dataGroup='multiline')
            else:
                print('Warning, found *INITIAL CONDITIONS, TYPE=ESDV or TYPE=SOLUTION block, but no corresponding *ELEMENT SOLUTION-DEPENDENT VARIABLEs block in input file. \
                Aborting search on these blocks.')
        case3blocks = self.findKeyword(keywordName=kwNames[0], parameters='TYPE=HARDENING, NUMBER BACKSTRESSES, REBAR', printOutput=False)
        if case3blocks:
            nbg1 = [block for block in case3blocks if block.parameter['NUMBER BACKSTRESSES'] > 1]
            nbe1 = list((set(case3blocks) - set(nbg1)))
            if nbg1:
                for block in nbg1:
                    self._findData(labelD=_tmpD, kwBlocks=[block], data_pos=1, linesToCheck=f'[::{block.parameter["NUMBER BACKSTRESSES"]}]', dataGroup='multiline')
            if nbe1:
                self._findData(labelD=_tmpD, kwBlocks=nbg1, data_pos=1)
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='REBAR', excludeParameters='TYPE=SOLUTION, TYPE=HARDENING', data_pos=1)

        #Looking for keywords where the *REBAR name ref can be the value of the REBAR parameter
        kwGroup = ['EL FILE', 'EL PRINT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='REBAR')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findRigidbodyRefs(self, names):
        """findRigidbodyRefs(names)
       
            This function searches for keywords that can reference \*RIGID BODY.
            
            Args:
                names (list): A sequence of \*RIGID BODY names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *SURFACE, where the *RIGID BODY surface ref name can be the value of the NAME parameter
        kwGroup = ['SURFACE']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='NAME')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findSectioncontrolsRefs(self, names):
        """findSectioncontrolsRefs(names)
       
            This function searches for keywords that can reference \*SECTION CONTROLS.
            
            Args:
                names (list): A sequence of \*SECTION CONTROLS names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *SECTION CONTROLS name ref can be the value of the CONTROLS parameter
        kwGroup = ['COHESIVE SECTION', 'CONNECTOR SECTION', 'DISCRETE SECTION', 'EULERIAN SECTION', 'MEMBRANE SECTION', 'SHELL GENERAL SECTION', 'SHELL SECTION', 'SOLID SECTION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='CONTROLS')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findSubstructureloadcaseRefs(self, names):
        """findSubstructureloadcaseRefs(names)
       
            This function searches for keywords that can reference \*SUBSTRUCTURE LOADCASE.
            
            Args:
                names (list): A sequence of \*SUBSTRUCTURE LOADCASE names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *SLOAD, where the *SUBSTRUCTURE LOAD CASE name ref can be in p1 of all lines
        kwGroup = ['SLOAD']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=1)

        return _tmpD
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findSurfaceRefs(self, names):
        """findSurfaceRefs(names)
       
            This function searches for keywords that can reference \*SURFACE.
            
            Args:
                names (list): A sequence of \*SURFACE names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        t1 = timing.time()
        _tmpD = csid([[s, []] for s in names])
        
        #############
        #Data Section
        #############

        #Looking for keyword blocks where the surface name can be in the 0th field in every data line
        kwGroup = ['CONTACT CLEARANCE ASSIGNMENT', 'CONTACT EXCLUSIONS', 'CONTACT FORMULATION', 'CONTACT INCLUSIONS', 'CONTACT INITIALIZATION ASSIGNMENT', 'CONTACT PAIR', 'D EM POTENTIAL', 'DSECHARGE', 'DSECURRENT', 'DSFLOW', 'DSFLUX', 'DSLOAD', 'EULERIAN BOUNDARY', 'INCIDENT WAVE', 'INCIDENT WAVE INTERACTION', 'SFILM', 'SFLOW', 'SHELL TO SOLID COUPLING', 'SIMPEDANCE', 'SRADIATE', 'SURFACE PROPERTY ASSIGNMENT', 'SURFACE SMOOTHING', 'TIE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0)
        
        #Looking for keyword blocks where the surface name can be in the 1st field in every data line
        kwGroup = ['CONTACT CLEARANCE ASSIGNMENT', 'CONTACT EXCLUSIONS', 'CONTACT FORMULATION', 'CONTACT INCLUSIONS', 'CONTACT INITIALIZATION ASSIGNMENT', 'CONTACT PAIR', 'SHELL TO SOLID COUPLING', 'SURFACE SMOOTHING', 'TIE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=1)

        #Looking for keyword blocks where the surface name can be in the 2nd field in every data line
        kwGroup = ['PERIODIC MEDIA']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=2)

        #Looking for keyword blocks where the surface name can be in the 3rd field in every data line
        kwGroup = ['PERIODIC MEDIA']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=3)

        #Looking for keyword blocks where the surface name can be in all field of all datalines.
        kwGroup = ['RADIATION VIEW FACTOR']
        self._findData(labelD=_tmpD, kwNames=kwGroup, dataGroup='subline')

        #Looking for *CAVITY DEFINITION, where the surface name ref can be in p0 of all lines if SET PROPERTY else all positions of all lines
        kwGroup = ['CAVITY DEFINITION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='SET PROPERTY', dataGroup='subline')
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='SET PROPERTY', data_pos=0)

        #Looking for *CONTACT CONTROLS ASSIGNMENT, where the surface name ref can be in p0 of all lines if TYPE=FOLD TRACKING or TYPE=FOLD INVERSION CHECK, or in p0 and p1 if AUTOMATIC OVERCLOSURE RESOLUTION or TYPE=SCALE PENALTY
        kwGroup = ['CONTACT CONTROLS ASSIGNMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='AUTOMATIC OVERCLOSURE RESOLUTION, TYPE=SCALE', mode='keyandany', data_pos='[:2]')
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=FOLD TRACKING, TYPE=FOLD INVERSION CHECK', mode='keyandany', data_pos=0)

        #Looking for *CONTACT INTERFERENCE, where the surface name ref can be in p0 and p1 of all lines if not TYPE=ELEMENT
        kwGroup = ['CONTACT INTERFERENCE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='TYPE=ELEMENT', data_pos='[:2]')

        #Looking for *CONTACT PROPERTY ASSIGNMENT, where the surface names can be in p0 and p1 if p3 and p4 are not "MATERIAL"
        def cpaCustom(**kwargs):
            
            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if rsl(line[indd + 3]) != 'material' and item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
        
        t2 = timing.time()
        kwGroup = ['CONTACT PROPERTY ASSIGNMENT']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            for block in sub:
                cpacustom = cpaCustom
                self._findData(labelD=_tmpD, kwBlocks=sub, data_pos='[:2]', custom=cpacustom)

        #Looking for *CONTACT STABILIZATION, where the surface name ref can be p0 and p1 if not RESET and not SCALE FACTOR=USER ADAPTIVE
        kwGroup = ['CONTACT STABILIZATION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='RESET, SCALE FACTOR=USER ADAPTIVE')

        #Looking for *CO-SIMULATION REGION, where the surface name ref can be p0 if TYPE!=[VOLUME or NODE]
        kwGroup = ['CO-SIMULATION REGION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='TYPE=VOLUME, TYPE=NODE', data_pos=0)

        #Looking for *EXTERNAL FIELD keyword blocks
        def externalFieldCustom(**kwargs):
            
            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if rsl(line[datano - 1]) == 'surface' and item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
        
        t2 = timing.time()
        kwGroup = ['EXTERNAL FIELD']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            for block in sub:
                parent = self.getParentBlock(block)
                if rsl(parent.name) == 'fieldimport':
                    submodel = parent.parameter.get('submodel')
                    if submodel == None:
                        efcustom = externalFieldCustom
                        self._findData(labelD=_tmpD, kwBlocks=sub, data_pos='[1:5:3]', custom=efcustom)

        #Looking for *FASTENER, where the surface name refs can be in all positions of lines 1+
        kwGroup = ['FASTENER']
        self._findData(labelD=_tmpD, kwNames=kwGroup, linesToCheck='[1:]', dataGroup='subline')

        #Looking for *IMPORT SURFACE keyword blocks, where the surface name ref can be in all positions if not RENAME, or in p0 if RENAME
        kwGroup = ['IMPORT SURFACE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, excludeParameters='RENAME', dataGroup='subline')
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='RENAME', data_pos=0)

        #Looking for *INITIAL CONDITIONS, where the surface name ref can be in p0 and p1 if TYPE=CONTACT
        kwGroup = ['INITIAL CONDITIONS']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=CONTACT', data_pos='[0:2]')

        #Looking for *MODEL CHANGE, where the surface name ref can be p0 and p1 if TYPE=CONTACT PAIR
        kwGroup = ['MODEL CHANGE']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=CONTACT PAIR')

        #Looking for *MULTIPHYSICS LOAD, where the surface names can be in p0 if p1 is "QS"
        def mplCustom(**kwargs):
            
            keys = ['data', 'ds', 'do', 'ls', 'lo', 'path', 'dstring', 'blockpathstring', 'labelD', 'calcFuncGroupString', 'dataGroup']
            data, ds, do, ls, lo, path, dstring, blockpathstring, labelD, calcFuncGroupString, dataGroup = [kwargs[i] for i in keys]
            for ind,line in enumerate(data):
                for indd,item in enumerate(eval(f'line{dstring}')):
                    datano = indd * ds + do
                    if rsl(line[1]) == 'qs' and item in labelD:
                        lineno = ind * ls + lo
                        labelD[item].append([blockpathstring.format(**locals()), calcFuncGroupString(path, lineno, ls, datano, ds, dataGroup)])
        
        t2 = timing.time()
        kwGroup = ['MULTIPHYSICS LOAD']
        sub = self.findKeyword(keywordName=kwGroup[0], printOutput=False)
        if sub:
            for block in sub:
                mplcustom = mplCustom
                self._findData(labelD=_tmpD, kwBlocks=sub, data_pos=0, custom=mplcustom)

        #Looking for *NORMAL, where the surface name ref can be in p0 if TYPE=CONTACT SURFACE
        kwGroup = ['NORMAL']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='TYPE=CONTACT SURFACE', data_pos=0)

        #Looking for *SUBMODEL, where the surface name ref can be in p0 if ACOUSTIC TO STRUCTURE or TYPE=SURFACE
        kwGroup = ['SUBMODEL']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='ACOUSTIC TO STRUCTURE, TYPE=SURFACE', mode='keyandany', data_pos=0)

        #Looking for *SURFACE keywords, where the surface name can be in varying positions
        kwGroup = 'SURFACE'
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='COMBINE=UNION', dataGroup='subline')
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='COMBINE=INTERSECTION, COMBINE=DIFFERENCE', mode='keyandone')
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='CROP', data_pos=0, linesToCheck=0, dataGroup='alldata')

        #Looking for *SYMMETRIC MODEL GENERATION, where the surface name can be in p0 of lines 2+ (this is approximate, the precise positioning is quite complicated, but nothing else that could be in p0 of lines 2+ is likely to be confused with a surface name)
        kwGroup = ['SYMMETRIC MODEL GENERATION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=0, linesToCheck='[2:]')

        ##################
        #Parameter Section
        ##################

        #Looking for keyword blocks where the surface name ref can be the value of the SURFACE parameter
        kwGroup = ['ADJUST', 'CONTACT OUTPUT', 'COUPLING', 'EULERIAN MESH MOTION', 'FLUID CAVITY', 'INTEGRATED OUTPUT', 'INTEGRATED OUTPUT SECTION', 'PARTICLE GENERATOR INLET' 'PARTICLE OUTLET', 'PRE-TENSION SECTION', 'RADIATION FILE', 'RADIATION OUTPUT', 'RADIATION PRINT', 'SECTION FILE', 'SECTION PRINT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='SURFACE')

        #Looking for keyword blocks where the surface name ref can be the value of the MAIN parameter
        kwGroup= ['CLEARANCE', 'CONTACT CONTROLS', 'CONTACT FILE', 'CONTACT PRINT', 'CONTACT RESPONSE', 'DEBOND', 'PRESSURE PENETRATION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='MAIN')

        #Looking for keyword blocks where the surface name ref can be the value of the SECONDARY parameter
        kwGroup = ['CLEARANCE', 'CONTACT CONTROLS', 'CONTACT FILE', 'CONTACT PRINT', 'CONTACT RESPONSE', 'DEBOND', 'PRESSURE PENETRATION']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='SECONDARY')

        #Looking for *RIGID BODY, where the surface name ref can be the value of the ANALYTICAL SURFACE parameter
        kwGroup = ['RIGID BODY']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='ANALYTICAL SURFACE')

        if self._debug:
            print(f'Time to generate blank _tmpD = {timing.time() - t1}')
        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findSurfaceinteractionRefs(self, names):
        """findSurfaceinteractionRefs(names)
       
            This function searches for keywords that can reference \*SURFACE INTERACTION.
            
            Args:
                names (list): A sequence of \*SURFACE INTERACTION names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *SURFACE INTERACTION name ref can be the value of the INTERACTION parameter
        kwGroup = ['CHANGE FRICTION', 'CONTACT PAIR', 'ENRICHMENT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='INTERACTION')

        #Looking for *CONTACT PROPERTY ASSIGNMENT, where the *SURFACE INTERACTION name ref can be in p2 of all lines
        kwGroup = ['CONTACT PROPERTY ASSIGNMENT']
        self._findData(labelD=_tmpD, kwNames=kwGroup, data_pos=2)

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findSurfacepropertyRefs(self, names):
        """findSurfacepropertyRefs(names)
       
            This function searches for keywords that can reference \*SURFACE PROPERTY.
            
            Args:
                names (list): A sequence of \*SURFACE PROPERTY names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *CAVITY DEFINITION, where the *SURFACE PROPERTY name ref can be in odd positions of all datalines if SET PROPERTY
        kwGroup = ['CAVITY DEFINITION']
        self._findData(labelD=_tmpD, kwNames=kwGroup, parameters='SET PROPERTY', data_pos='odd', dataGroup='subline')

        #Looking for *SURFACE, where the *SURFACE PROPERTY name ref can be the value of the PROPERTY parameter
        kwGroup = ['SURFACE']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='PROPERTY')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findSurfacesmoothingRefs(self, names):
        """findSurfacesmoothingRefs(names)
       
            This function searches for keywords that can reference \*SURFACE SMOOTHING.
            
            Args:
                names (list): A sequence of \*SURFACE SMOOTHING names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for *CONTACT PAIR, where the *SURFACE PROPERTY name ref can be the value of the GEOMETRIC CORRECTION parameter
        kwGroup = ['CONTACT PAIR']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='GEOMETRIC CORRECTION')

        return _tmpD

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def findTracerparticleRefs(self, names):
        """findTracerparticleRefs(names)
       
            This function searches for keywords that can reference \*TRACER PARTICLE.
            
            Args:
                names (list): A sequence of \*TRACER PARTICLE names.
                
            Returns:
                csid: Uses names as the keys, each value will be a list containing the exact location which references
                      the name and the region of the keyword effected by this reference."""

        _tmpD = csid([[name, []] for name in names])

        #Looking for keywords where the *TRACER PARTICLE name ref can be the value of the TRACER SET parameter
        kwGroup = ['ELEMENT OUTPUT', 'NODE OUTPUT']
        self._findParam(labelD=_tmpD, kwNames=kwGroup, parameterName='TRACER SET')

        return _tmpD
