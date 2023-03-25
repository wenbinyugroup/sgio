# def updateDict(source:dict, target:dict, ignore:list=[]):
def updateDict(source, target, ignore=[]):

    for k, v in source.items():
        if not k in ignore:
            target[k] = v

    return



def getValueByKey(dictionary, key, match='start', recursive=False, which='first'):
    r"""
    """
    value = None

    if not isinstance(key, list):
        key = [key,]

    for _k, _v in dictionary.items():
        for k in key:
            if (match == 'start' and _k.startswith(k)) or (match == 'exact' and _k == k):
                value = _v


    return value
