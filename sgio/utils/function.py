from typing import Iterable
# import numpy as np
from scipy.interpolate import interp1d


class MSGDFunction():
    def __init__(self):
        self.return_type = 'float'




class LinearFunction(MSGDFunction):
    """A simple class for 1D linear function

    f(x) = (b - a) * (x + d) / c + a
    """
    def __init__(self, a, b, c, d=None, axis=1, n=None):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.axis = axis
        self.n = n  # rounding number of digits

    def __str__(self):
        # s = f'f(x) = ({self.b} - {self.a}) * (x + {self.d}) / {self.c} + {self.a}'
        s = 'f(x) = ({b} - {a}) * (x + {d}) / {c} + {a}'.format(
            a=self.a, b=self.b, c=self.c, d=self.d
        )
        return s

    def __call__(self, x):
        try:
            xd = [ (x[i] + self.d[i]) for i in range(len(x)) ]
        except:
            xd = x

        f = (self.b - self.a) * xd[self.axis-1] / self.c + self.a

        if self.n:
            f = round(f, self.n)

        return f









class SymLinearFunction(MSGDFunction):
    """A simple class for symmetric linear function

    f(x) = 2 * (b - a) * | (x + d)  / c| + a
    """
    def __init__(self, a, b, c, d=None, axis=1):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.axis = axis

    def __str__(self):
        # s = f'f(x) = 2 * ({self.b} - {self.a}) * |x / {self.c}| + {self.a}'
        s = 'f(x) = 2 * ({b} - {a}) * |x / {c}| + {a}'.format(
            a=self.a, b=self.b, c=self.c
        )
        return s

    def __call__(self, x):
        try:
            xd = [ (x[i] + self.d[i]) for i in range(len(x)) ]
        except:
            xd = x

        # print('x =', x)
        # print('xd =', xd)

        return 2.0 * (self.b - self.a) * abs( xd[self.axis-1] / self.c) + self.a









class ScriptFunction(MSGDFunction):
    """[summary]

    Parameters
    ----------
    Function : [type]
        [description]
    """
    def __init__(self, func, coef):
        super().__init__()
        self.func = func
        self.coef = coef

    def __str__(self):
        s = self.func.__name__
        s += '(x, y, z'
        for k, v in self.coef.items():
            s += ', {}={}'.format(k, v)
        s += ')'
        return s

    def __call__(self, x):
        return self.func(x, self.coef)









class InterpolationFunction(MSGDFunction):
    def __init__(self, data_indv, data_depv, kind='linear', fill_value='extrapolate', ytype='float') -> None:
        """[summary]

        Parameters
        ----------
        data_indv : [type]
            Independent variables. np x nx
        data_depv : [type]
            Dependent variables. np x ny
        form : str, optional
            [description], by default 'linear'
        grid : bool, optional
            [description], by default False
        """
        super().__init__()

        self.data_indv = data_indv
        self.data_depv = data_depv
        self.ytype = ytype
        self.np = len(data_indv)

        try:
            self.nx = len(data_indv[0])
        except:
            self.nx = 1

        try:
            self.ny = len(data_depv[0])
        except:
            self.ny = 1

        self.kind = kind
        self.fill_value = fill_value

        self.func = None

        if self.nx == 1:
            if isinstance(self.data_indv[0], list):
                self.data_indv = [i[0] for i in self.data_indv]
            # print(interpolate.__dict__)
            if self.ytype != 'str':
                self.func = interp1d(
                    self.data_indv, self.data_depv, axis=0,
                    kind=self.kind, fill_value=self.fill_value
                )


    def __call__(self, x):
        if self.ytype == 'str':
            if self.kind == 'previous':
                for i, px in enumerate(self.data_indv):
                    if px > x:
                        break
                    y = self.data_depv[i]
            elif self.kind == 'next':
                pass
        else:
            y = self.func(x)

        if self.ny == 1 and isinstance(y, list):
            y = y[0]

        if self.ytype == 'int':
            y = round(y)

        return y









try:
    from sympy import *

    class CustomFunction(MSGDFunction):
        r"""Custom function created by a string of expression.

        Parameters
        ----------
        Function : [type]
            [description]
        """
        # def __init__(self, expr, coef_strs):
        def __init__(self, expr='', coef_strs=[], var_strs=['x', 'y', 'z'], return_type='float'):
            super().__init__()
            self.var_sym = symbols(' '.join(var_strs))
            self.expr_str = expr
            self.coef_strs = coef_strs
            self.coef_sym = []
            for cs in self.coef_strs:
                s = symbols(cs)
                self.coef_sym.append(s)
            self.expr_sym = sympify(self.expr_str)
            self.expr_lmd = None
            self.return_type = return_type

        def __str__(self):
            return self.expr_sym.__str__()

        def implement(self, coef_val={}):
            # print('implement')
            self.coef_rep = []
            for s in self.coef_sym:
                v = coef_val[s.__str__()]
                self.coef_rep.append((s, v))
            self.expr_sym = self.expr_sym.subs(self.coef_rep)
            self.expr_lmd = lambdify(self.var_sym, self.expr_sym, 'math')

        def __call__(self, x=0, y=0, z=0):
            # print('__call__')
            if not self.expr_lmd:
                return

            if isinstance(x, Iterable):
                f = self.expr_lmd(x[0], x[1], x[2])
            else:
                f = self.expr_lmd(x, y, z)

            if self.return_type.lower().startswith('i'):
                f = round(f)

            return f


except ModuleNotFoundError:
    # print('sympy module not found.')
    pass
except:
    # print('other exceptions.')
    pass

