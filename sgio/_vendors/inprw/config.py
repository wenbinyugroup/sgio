#Copyright © 2023 Dassault Systemès Simulia Corp.

r"""In addition, it sets several groupings of keyword names and other similar items that are 
constant and need to be referenced throughout :mod:`~inpRW`.
See `How do I share global variables across modules? <https://docs.python.org/3/faq/programming.html#how-do-i-share-global-variables-across-modules>`_
for more information."""

# cspell:includeRegExp comments

from .csid import *
import sys
import os
from .elType import elType

if sys.platform=='win32':
    _slash = '\\' 
    """Stores slash or backslash depending on the OS; this will be inserted into all file paths and makes the script OS independent.

    :meta hide-value:
    :type: str
    """
elif sys.platform=='linux' or sys.platform=='darwin':
    _slash = '/'
_openEncoding = 'utf-8' 
"""Indicates the encoding used to open and write text files. Can be changed if needed before the user calls :func:`~inpRW.inpRW.parse`.

:meta hide-value:
:type: str
"""

#Define special keyword groupings
_supFilePath = os.path.realpath(__file__).rsplit(_slash,1)[0]
"""Supplemental file path, specifies the location of the additional files :mod:`inpRW` needs to read from. Defaults to the directory of :mod:`inpRW` and should not be changed.

:meta hide-value:
:type: str
"""

_elinfopath = os.path.join(_supFilePath,  f'inpRW{_slash}elInfoDict.txt')
with open(_elinfopath, 'r', encoding=_openEncoding) as f:
    _elementTypeDictionary = eval(f.read())
_elementTypeDictionary = csid(_elementTypeDictionary) 
"""A case- and space-insensitive dictionary that contains information for each element type. The element type labels are the keys, and :class:`~elType.elType` instances are the values.

:meta hide-value:
:type: csid
"""

#Merge dataline keywords
_mergeDatalineKeywordsOP = {'adaptivemeshconstraint, constrainttype=lagrangian': 16, 'fluidexchangeactivation': 8, 'fluidinflatoractivation': 8} 
"""Keywords whose data items can be consolidated by merging them into new datalines with up to X items per line.

:meta hide-value:
:type: dict
"""

#Append dataline keywords
_appendDatalineKeywordsOP = {'cecharge', 'cecurrent', 'cfilm', 'cflow', 'cflux', 'cload', 'connectorload', 'connectormotion', 'contactinterference', 
                           'contactpair', 'cradiate', 'creepstrainratecontrol', 'dempotential', 'decharge', 'decurrent', 'dflux', 'dload', 'dsecharge', 'dsecurrent', 'dsflow', 'dsload', 
                           'eulerianboundary', 'film', 'flow', 'massflowrate', 'output', 'pressurepenetration', 'pressurestress', 'radiate', 'sfilm', 'sflow', 'sload', 'sradiate'} 
"""Keywords whose datalines can be consolidated by appending them one after another.

:meta hide-value:
:type: set
"""

#DOF x to y
_dofXtoYDatalineKeywordsOP = {'adaptivemeshconstraint'}
"""Keywords that can be consolidated as DoF X to DoF Y. Boundary is not included here as it requires special handling.

:meta hide-value:
:type: set
"""

#_opKeywords = list(flatten(['boundary'] + [i for j in _mergeDatalineKeywordsOP for i in j if type(i)==type('')] + _appendDatalineKeywordsOP + _dofXtoYDatalineKeywordsOP)) 
_opKeywords = {'boundary', 'temperature'} | set(_mergeDatalineKeywordsOP.keys()) | _appendDatalineKeywordsOP | _dofXtoYDatalineKeywordsOP 
"""Keywords that can have the OP parameter.

:meta hide-value:
:type: set
"""

_subBlockKWspath =  os.path.join(_supFilePath, f'inpRW{_slash}keyword_sub.txt')
with open(_subBlockKWspath, 'r', encoding=_openEncoding) as f:
    _subBlockKWs = eval(f.read())
_subBlockKWs = csid(_subBlockKWs) 
"""Dictionary that uses a keyword name as the key, and a list of all keywords that are valid suboptions for that block as the value.

:meta hide-value:
:type: csid
"""

_keywordNamespath = os.path.join(_supFilePath, f'inpRW{_slash}keyword_names.txt')
with open(_keywordNamespath, 'r', encoding=_openEncoding) as f2:
    _allKwNames = set(eval(f2.read())) 
    """Contains all keyword names. Currently not used.
    
    :meta hide-value:
    :type: set
    """

_EoFKWs = {'include','manifest'} 
"""Keywords that read until the end of a file.

:meta hide-value:
:type: set
"""

_dataKWs = {'amplitude', 'clearance', 'correlation', 'element', 'equation', 'eventseries', 'field', 'impedanceproperty', 'initialconditions', 
            'massflowrate', 'matrixinput', 'mpc', 'nodalenergyrate', 'nodalthickness', 'node', 'parametershapevariation', 'pressurestress', 
            'psd-definition', 'release', 'spectrum', 'surfaceflaw', 'temperature', 'timepoints', 'wave'} 
"""Keywords that can read their data from another file.

:meta hide-value:
:type: set
"""

_EndKWs = {'assembly', 'instance', 'loadcase', 'part', 'step'} 
r"""Keywords that have an associated \*END KEYWORD.

:meta hide-value:
:type: set
"""

_generalSteps = {'coupledtemperature-displacement', 'coupledthermal-electrical', 'coupledthermal-electrochemical', 'directcyclic',
                 'dynamic', 'dynamictemperature-displacement', 'geostatic', 'heattransfer', 'massdiffusion', 'soils', 'static', 'visco'}  
"""Keywords that are general procedures.

:meta hide-value:
:type: set
"""

_perturbationSteps = {'buckle', 'frequency', 'static', 'steadystatedynamics', 'substructuregenerate'} 
"""Keywords that are linear perturbation procedures.

:meta hide-value:
:type: set
"""

_keywordsDelayPlacingData = csid([['parameter', 0], ['element', 2]]) #: :csid: Keywords in this list will not have their data parsed until loop X. This is for specific keywords that need to operate on other parsed data; for example, \*ELEMENT needs :attr:`~inpRW.inpRW.nd` to be fully populated, which requires waiting until all node blocks have been parsed. If a keyword is not in this dictionary, it will be parsed at 1.
_maxParsingLoops = 2 #: :int: The maximum number of loops to parse keyword data. This should match the highest number in the :attr:`_keywordsDelayPlacingData`. The initial loop will use an integer value of 0.

#_nodeCreationKWs = set(['node', 'ngen', 'nfill', 'ncopy'])
#_elementCreationKWs = set(['element', 'elgen', 'elcopy'])
#_ignoreNameKWs = set(['enrichmentactivation'])