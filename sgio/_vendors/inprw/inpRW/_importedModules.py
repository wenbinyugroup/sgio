"""This module contains all the module imports used by the submodules of :class:`inpRW`.
No module that is imported in :mod:`~inpRW._importedModules` should import :mod:`~inpRW._importedModules`,
or circular import errors will likely occur. """

# cspell:includeRegExp comments

#import sys
#import re
import traceback
import math
import numpy as np
import copy
import os
from scipy import spatial
import collections
from operator import itemgetter
import time as timing
#from math import acos, asin, atan, cos, log, log10, pi, sin, sqrt, tan
#import concurrent.futures
import multiprocessing as mp
#import concurrent.futures as cf
import logging
from pprint import pprint as pp
import decimal
from decimal import Decimal
from io import IOBase
from itertools import groupby, chain
#import pickle
#Do not change the order of the following modules, or else circular import problems are likely
from ..printer import Printer
from ..config_re import *
from ..inpDecimal import inpDecimal
from ..inpInt import inpInt
from ..inpKeywordSequence import inpKeywordSequence
from ..inpString import inpString
from ..inpRWErrors import *
from ..misc_functions import *
from ..eval2 import *
from ..csid import csid
from ..mesh import *
from ..inpKeyword import inpKeyword, createParamDictFromString, formatStringFromParamDict
from ..centroid import *
from ..NoneSort import NoneSort