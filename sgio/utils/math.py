# import abc
from math import *
import numpy as np
# from sympy import *


def tilde(v):
    """
    ~v_{ij} = -e_{ijk} * v_k

    :param v: 3x1 vector
    :type v: list or array-like
    """
    vtilde = np.zeros((3, 3))
    vtilde[0, 1] = -v[2, 0]
    vtilde[0, 2] = v[1, 0]
    vtilde[1, 0] = v[2, 0]
    vtilde[1, 2] = -v[0, 0]
    vtilde[2, 0] = -v[1, 0]
    vtilde[2, 1] = v[0, 0]

    return vtilde




def calcRotationTensorFromParameters(rp, method=''):
    """Calculate rotation tensor from rotation parameters.

    Parameters
    ----------
    rp : list of floats
        Rotation parameters (3x1).
    method : str
        Rotation parameter type.

        * `er` - Eular-Rodrigues
        * `wm` - Wiener-Milenkovic
    """
    C = np.zeros((3, 3))
    if method == 'er':
        # Eular-Rodrigues
        t = np.dot(rp.T, rp)[0, 0]
        nmr = (1 - t / 4.0) * np.eye(3) + np.dot(rp, rp.T) / 2.0 - tilde(rp)
        dnm = 1 + t / 4.0
        C = nmr / dnm
    elif method == 'wm':
        # Wiener-Milenkovic
        t = np.dot(rp.T, rp)[0, 0]
        c0 = 2 - t / 8.0
        nmr = (c0**2 - t) * np.eye(3) - 2.0 * c0 * tilde(rp) + 2.0 * np.dot(rp, rp.T)
        dnm = (4 - c0)**2
        C = nmr / dnm

    return C




def floorAbsolute(number):
    """Round the number such that the absolute value is smaller than the given number.

    Parameters
    ----------
    number : float
        Number to be rounded.

    Returns
    -------
    float
        Rounded number
    """
    if (number - 0.) > 1e-15:
        # Positive
        number = np.floor(number)
    elif (0. - number) > 1e-15:
        # Negative
        number = np.ceil(number)
    else:
        # Very close to 0
        number = 0.
    
    return number




def angleToCosine2D(angle):
    angle = radians(angle)
    c = [
        [cos(angle), -sin(angle)],
        [sin(angle),  cos(angle)]
    ]
    return c




def calcBasicRotation3D(angle, axis=1):
    c = np.array([
        [1.,            0.,             0.],
        [0., np.cos(angle), -np.sin(angle)],
        [0., np.sin(angle),  np.cos(angle)]
    ])
    if axis == 2:
        p = np.array([
            [0., 1., 0.],
            [0., 0., 1.],
            [1., 0., 0.]
        ])
        c = np.dot(p.T, np.dot(c, p))
    elif axis == 3:
        p = np.array([
            [0., 0., 1.],
            [1., 0., 0.],
            [0., 1., 0.]
        ])
        c = np.dot(p.T, np.dot(c, p))

    return c




def calcGeneralRotation3D(angles, order=[1, 2, 3]):
    ''' Calculate the general rotation matrix

    :param angles: Three rotation angles in radians
    :type angles: list

    :param order: The order of axis of the rotation operation
    :type order: list

    :return: The general rotation matrix
    :rtype: numpy.array
    '''
    c = np.eye(3)
    for angle, axis in zip(angles, order):
        ci = calcBasicRotation3D(angle, axis)
        c = np.dot(ci, c)
    return c




def rotateVectorByAngle2D(v2d, angle):
    c = angleToCosine2D(angle)
    vp = [
        c[0][0] * v2d[0] + c[0][1] * v2d[1],
        c[1][0] * v2d[0] + c[1][1] * v2d[1]
    ]
    return vp




def calcCab(a, b):
    '''Calculate the direction cosine matrix between frame a and b

    :math:`C_{ij} = a_i\ \cdot\ b_j`

    Parameters
    ----------
    a : list of floats
        List of three a basis (a_1, a_2, a_3).
    b : list of floats
        List of three b basis (b_1, b_2, b_3).

    Returns
    -------
    list of lists of floats
        3x3 matrix of the direction cosine.

    Examples
    --------
    >>> a = [
    ...     [1., 0., 0.],
    ...     [0., 1., 0.],
    ...     [0., 0., 1.]
    ... ]
    >>> b = [
    ...     [],
    ...     [],
    ...     []
    ... ]
    >>> utilities.calcCab(a, b)
    '''
    a = np.array(a)
    b = np.array(b)
    Cab = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            Cab[i][j] = np.dot(a[i], b[j])
    return Cab




def distance(p1, p2):
    s2 = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
    return sqrt(s2)




def ss(v1, v2, scale=None):
    if scale is None:
        scale = [1., ] * len(v1)
    assert len(scale) == len(v1)
    sumsqr = 0.0
    for i in range(len(v1)):
        sumsqr = sumsqr + (v1[i] * scale[i] - v2[i] * scale[i])**2
    return sumsqr




class Polynomial2DSP(object):
    def __init__(self, order, coeffs):
        self.order = order
        self.coeffs = np.asarray(coeffs)

    def __call__(self, x):
        basis = []
        for i in range(self.order+1):
            for j in range(i+1):
                basis.append(x[0]**(i-j) * x[1]**j)
        basis = np.asarray(basis)

        return np.dot(self.coeffs, basis)




class PolynomialFunction(object):
    def __init__(self, coefficients=[], x=[], y=[]):
        self.coefficients = coefficients
        self.points = {}
        if len(x) > 0:
            # points = np.asarray(points)
            ndof = len(x)
            A = np.zeros((ndof, ndof))
            for i in range(ndof):
                self.points[x[i]] = y[i]
                for j in range(ndof):
                    A[i, j] = x[i]**j
            # print(A)
            self.coefficients = np.linalg.solve(A, y)
            # print(self.coefficients)

    def __call__(self, x):
        f = 0.0
        if x in self.points.keys():
            f = self.points[x]
        else:
            for i, c in enumerate(self.coefficients):
                f += c * x**i
        return f

    def __str__(self):
        terms = []
        for i, c in enumerate(self.coefficients):
            # terms.append(f'({c})*x^{i}')
            terms.append('({})*x^{}'.format(c, i))
        
        return ' + '.join(terms)









def calcCoordsOnCylinder(X, r, axis=3):
    """[summary]

    Parameters
    ----------
    X : list
        Coordinates in the global inertial frame

    Returns
    -------
    list
        Coordinates on the cylindrical surface
    """
    x = [0, 0]

    x1 = r * atan2(X[1], X[0])
    x2 = X[2]

    x = [x1, x2]

    return x


class FrameTransCylinder():
    def __init__(self, r):
        self.r = r

    def __call__(self, X):
        x1 = self.r * atan2(X[1], X[0])
        x2 = X[2]

        x = [x1, x2]

        return x









def transformRigid3D(v0, R=None, t=None):
    r"""Transform a point/vector rigidly in 3D.

    Parameters
    ----------
    R : list of shape (3, 3)
        Rotation matrix.
    t : list of shape (3,)
        Translation vector.
    """
    v = np.asarray(v0)

    if not R:
        R = np.eye(3)
    else:
        R = np.asarray(R)
    if not t:
        t = np.zeros(3)
    else:
        t = np.asarray(t)

    v = np.dot(R, v) + t

    return v.tolist()
