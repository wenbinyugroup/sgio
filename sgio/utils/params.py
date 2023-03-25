# from scipy import interpolate
import csv
import msgd.utils.function as muf


class Parameter():
    def __init__(self, name='', value=None, type='float'):
        self.name = name
        self.value = value
        self.type = type

        self.distr_func = None

        return

    def __str__(self):
        s = '{} ({}): {} function: {}'.format(
            self.name, self.type, self.value, str(self.distr_func)
        )
        return s

    def __call__(self, x=0):
        v = None
        try:
            v = self.distr_func(x)
        except TypeError:
            v = self.value

        if self.type == 'float':
            v = float(v)
        elif self.type == 'int':
            v = int(v)

        return v


# class Distribution():
#     def __init__(self, data_indv, data_depv, func, form='linear', grid=False):

#         return


class TabularData():
    def __init__(self):
        self.name = ''
        self.columns = []
        self.nx = 1
        self.data = []
        return

    def printData(self, fmt='csv'):
        print(', '.join(self.columns))
        for row in self.data:
            print(', '.join(list(map(str, row))))
        return









def parseTabularDataToString(lines):
    str_data = []
    lines = lines.splitlines()
    for row in lines:
        if row.strip().startswith('#'):
            continue
        temp = row.split(',')
        str_data.append([v.strip() for v in temp])

    return str_data









def loadDataCSV(fn, ndimx, header=1, ynames=[], function='', kind='linear', delimiter=','):
    data = {}
    x = []
    ys = {}

    with open(fn, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        for i in range(header):
            names = next(reader)
            ynames = names[ndimx:]
        for yname in ynames:
            ys[yname] = []

        for row in reader:
            nums = list(map(float, row))
            x.append(nums[:ndimx])
            for i, yname in enumerate(ynames):
                ys[yname].append(nums[ndimx+i])

    # print(x)
    # print(ys)

    for yname, ydata in ys.items():
        f = muf.InterpolationFunction(x, ydata, kind=kind)
        data[yname] = f

    return data









def substituteParams(inputs, params):
    r"""Substitute quantities in inputs using values given in params.

    inputs can have a nested structure of {} and []
    - Go through every key:value pairs
    - If value is a string, then check if key exists
      in params as well. If yes, then do the substitution
    """
    if isinstance(inputs, dict):
        for k, v in inputs.items():
            if isinstance(v, dict) or isinstance(v, list):
                substituteParams(v, params)
            elif isinstance(v, str):
                try:
                    inputs[k] = params[v]
                except KeyError:
                    pass

    elif isinstance(inputs, list):
        for i, v in enumerate(inputs):
            if isinstance(v, dict) or isinstance(v, list):
                substituteParams(v, params)

    return




def substituteParamsOld(inputs, params):
    r"""Substitute quantities in inputs using values given in params.

    inputs can have a nested structure of {} and []
    - Go through every key:value pairs
    - If value is a scalar (number, string), then check if key exists
      in params as well. If yes, then do the substitution
    """
    if isinstance(inputs, dict):
        for k, v in inputs.items():
            # print('k:', k)
            # print('v:', v)
            if isinstance(v, dict) or isinstance(v, list):
                substituteParamsOld(v, params)
            else:
                try:
                    # print('v =', v)
                    inputs[k] = params[k]
                    # print('inputs[k] =', inputs[k])
                    # print('params[k] =', params[k])
                except KeyError:
                    pass

    elif isinstance(inputs, list):
        for i, v in enumerate(inputs):
            if isinstance(v, dict) or isinstance(v, list):
                substituteParamsOld(v, params)

    return
