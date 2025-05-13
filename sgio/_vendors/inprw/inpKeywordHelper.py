#Copyright © 2023 Dassault Systemès Simulia Corp.

"""This module contains functions meant to assist with creating :class:`~inpKeyword` blocks in parallel. This process is not currently providing 
much performance benefit (perhaps a 25% speedup when running with 4 cores vs. single core), so its usage is not recommended."""

# cspell:includeRegExp comments

from .inpKeyword import inpKeyword
import concurrent.futures as cf


def inpKeywordInit(rawstringsin, Args):
    """inpKeywordInit(rawstringsin, Args)
    
        Initializes variables needed in each process when parsing keywords in parallel.
        
        Args:
            rawstringsin (list): A list of strings. Each string should correspond to the text of an entire keyword block.
                The list will be turned into a global variable for the subprocesses.
            Args (dict): Each item in Args will be converted to a global variable. This should be set to :attr:`~inpRW.inpRW.inpKeywordArgs`
                in most cases."""

    global rawstrings
    rawstrings = rawstringsin
    for k,v in Args.items():
        if isinstance(v, str):
            vStr = f'"{v.encode("unicode_escape").decode()}"'
        else:
            vStr = f'{v}'
        exec(rf'{k} = {vStr}', globals())
    #global preserveSpacing, useDecimal, paramInInp, fastElementParsing, joinPS, parseSubFiles, delayParsingDataKws, inputFolder, nl, rmtrailing0, debug
    #for key, value in Args.items():
    #    if key == 'nl':
    #        nl = value
    #    elif key == 'joinPS':
    #        joinPS = value
    #    elif key == 'inputFolder':
    #        inputFolder = value
    #    elif key == 'delayParsingDataKws':
    #        delayParsingDataKws = value
    #    elif value == True:
    #        exec(f'{key} = True', globals())
    #    elif value == False:
    #        exec(f'{key} = False', globals())
    #print('called init', flush=True)

def inpKeywordHelper(num):
    """inpKeywordHelper(num)
        
        Creates an :class:`~inpKeyword.inpKeyword` for rawstrings[num], referencing the items passed to :func:`inpKeywordInit` via Args.
        
        Args:
            num (int): An integer representing the item from rawstrings on which to operate."""

    inpKWArgs = {'preserveSpacing': preserveSpacing, 'useDecimal': useDecimal, # type: ignore
                 '_ParamInInp': _ParamInInp, 'fastElementParsing': fastElementParsing, '_joinPS': _joinPS, # type: ignore
                 'parseSubFiles': parseSubFiles, 'delayParsingDataKws': delayParsingDataKws, # type: ignore
                 'inputFolder': inputFolder, '_nl': _nl, 'rmtrailing0': rmtrailing0, '_debug': _debug} # type: ignore
    #print(dir(globals), flush=True)
    tmp = inpKeyword(rawstrings[num], createSuboptions=False, **inpKWArgs)
    #print(f'useDecimal={tmp.useDecimal}, preserveSpacing={tmp.preserveSpacing}', flush=True)
    #tmp.rawstring = rawstring
    #tmp.lines = tmp._parseRawString()
    #dummy = tmp._parseKWData()
    #print(type(tmp.data[0][0]), flush=True)
    #print(tmp.formatKeywordLine(), flush=True)
    return tmp
    


    
if __name__ == '__main__':
    import time as timing
    rawstring = '''*NODE, nset=nset-{}
   1 ,  0.00,   0.00
   21, 70.00,   0.00
 2401,  0.00,  66.50
 2421, 19.25,  66.50
 3601,  0.00,  91.75
 3621, 16.17,  91.75
 3801,  0.00, 103.00
 3821, 14.80, 103.00'''
    rawstring2 = '''*CONCRETE TENSION STIFFENING, TYPE=DISPLACEMENT-{}
 2.9E+6         ,0
 1.94393E+6     ,0.000066185
 1.30305E+6     ,0.00012286
 0.873463E+6    ,0.000173427
 0.5855E+6      ,0.00022019
 0.392472E+6    ,0.000264718
 0.263082E+6    ,0.000308088
 0.176349E+6    ,0.00035105
 0.11821E+6     ,0.000394138
 0.0792388E+6   ,0.000437744
 0.0531154E+6   ,0.000482165'''
    x = 100000
    cpus = 4
    chunksize = int(x / cpus / 2)
    rawstrings = [rawstring2.format(s) for s in range(x)]
    inpKWArgs = {'preserveSpacing': True, 'useDecimal': True, '_ParamInInp': False, 'fastElementParsing': True, '_joinPS': ',', 'parseSubFiles': True, 'delayParsingDataKws': {}, 'inputFolder': '', '_nl': '\n', 'rmtrailing0': False, '_debug': False}
    l = []
    lapp = l.append
    t1 = timing.time()
    with cf.ProcessPoolExecutor(max_workers=cpus, initializer=inpKeywordInit, initargs=(inpKWArgs,)) as runner:
        #jobs = {ind: runner.submit(inpKeywordHelper, s) for ind, s in enumerate(rawstrings)}
        jobs = runner.map(inpKeywordHelper, rawstrings, chunksize=chunksize)
        #jobs_items = jobs.values()
        #cf.wait(jobs_items, return_when='ALL_COMPLETED')
    #for i in range(len(jobs)):
    for i in jobs:
        lapp(i)
    print(f' time to parse {x} keywords with {cpus} cores: {timing.time() - t1}')
    print(l[-1])
    t2 = timing.time()
    l2 = []
    l2app = l2.append
    jobs = [inpKeyword(rawstring, **inpKWArgs) for rawstring in rawstrings]
    for i in jobs:
        l2app(i)
    print(f' time to parse {x} keywords with 1 core: {timing.time() - t2}')
    print(l2[-1])
    #for block in l:
    #    print(block)