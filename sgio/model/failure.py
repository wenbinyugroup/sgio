# Failure criteria

import numpy as np


class TsaiWuFailureCriterion:
    """Tsai-Wu failure criterion for anisotropic materials.

    Parameters
    ----------
    xt : float
        Tensile strength in x-direction.
    xc : float
        Compressive strength in x-direction.
    yt : float
        Tensile strength in y-direction.
    yc : float
        Compressive strength in y-direction.
    zt : float
        Tensile strength in z-direction.
    zc : float
        Compressive strength in z-direction.
    r : float
        Shear strength in yz-direction.
    t : float
        Shear strength in xz-direction.
    s : float
        Shear strength in xy-direction.
    """

    def __init__(self, xt, xc, yt, yc, zt, zc, r, t, s):
        self.xt = xt
        self.xc = xc
        self.yt = yt
        self.yc = yc
        self.zt = zt
        self.zc = zc
        self.r = r
        self.t = t
        self.s = s

        self.f1 = 1/xt - 1/xc
        self.f2 = 1/yt - 1/yc
        self.f3 = 1/zt - 1/zc
        self.f4 = 0
        self.f5 = 0
        self.f6 = 0

        self.f11 = 1 / (xt * xc)
        self.f22 = 1 / (yt * yc)
        self.f33 = 1 / (zt * zc)
        self.f44 = 1 / (r * r)
        self.f55 = 1 / (t * t)
        self.f66 = 1 / (s * s)

        self.f12 = (- self.f11 - self.f22 + self.f33) / 2
        self.f13 = (- self.f11 + self.f22 - self.f33) / 2
        self.f23 = (- self.f11 - self.f22 + self.f33) / 2
        self.f14 = 0
        self.f15 = 0
        self.f16 = 0
        self.f24 = 0
        self.f25 = 0
        self.f26 = 0
        self.f34 = 0
        self.f35 = 0
        self.f36 = 0
        self.f45 = 0
        self.f46 = 0
        self.f56 = 0

        self.A = np.array([
            [self.f11, self.f12, self.f13, self.f14, self.f15, self.f16],
            [self.f12, self.f22, self.f23, self.f24, self.f25, self.f26],
            [self.f13, self.f23, self.f33, self.f34, self.f35, self.f36],
            [self.f14, self.f24, self.f34, self.f44, self.f45, self.f46],
            [self.f15, self.f25, self.f35, self.f45, self.f55, self.f56],
            [self.f16, self.f26, self.f36, self.f46, self.f56, self.f66]
        ])

        self.b = np.array([
            self.f1, self.f2, self.f3, self.f4, self.f5, self.f6
        ])

    def failure_index(self, stress):
        """Calculate failure index for given stress vector(s).

        The Tsai-Wu failure index is calculated as:
        FI = b·σ + σᵀ·A·σ

        where:
        - b is the linear coefficient vector (6,)
        - A is the quadratic coefficient matrix (6, 6)
        - σ is the stress vector(s)

        Failure occurs when FI >= 1.0

        Parameters
        ----------
        stress : array_like
            Stress vector(s) in the form [σ11, σ22, σ33, σ23, σ13, σ12].
            Can be:
            - 1D array of shape (6,) for a single stress state
            - 2D array of shape (n, 6) for n stress states

        Returns
        -------
        failure_index : float or ndarray
            Failure index value(s).
            - float if input is 1D
            - ndarray of shape (n,) if input is 2D
        """
        stress = np.atleast_2d(stress)

        # Vectorized calculation: FI = b·σ + σᵀ·A·σ
        # Linear term: (n, 6) @ (6,) = (n,)
        linear_term = stress @ self.b

        # Quadratic term: (n, 6) @ (6, 6) @ (6, n) = (n,)
        # For each stress vector: σᵀ·A·σ
        quadratic_term = np.einsum('ij,jk,ik->i', stress, self.A, stress)

        failure_index = linear_term + quadratic_term

        # Return scalar if input was 1D
        if failure_index.shape[0] == 1:
            return failure_index[0]
        return failure_index

    def strength_ratio(self, stress):
        """Calculate strength ratio for given stress vector(s).

        The strength ratio (SR) is the factor by which the stress can be
        multiplied before failure occurs. It is found by solving:

        (σᵀ·A·σ)·SR² + (b·σ)·SR - 1 = 0

        The positive root of this quadratic equation gives the strength ratio.
        SR > 1 indicates the stress state is safe.
        SR < 1 indicates failure.

        Parameters
        ----------
        stress : array_like
            Stress vector(s) in the form [σ11, σ22, σ33, σ23, σ13, σ12].
            Can be:
            - 1D array of shape (6,) for a single stress state
            - 2D array of shape (n, 6) for n stress states

        Returns
        -------
        strength_ratio : float or ndarray
            Strength ratio value(s).
            - float if input is 1D
            - ndarray of shape (n,) if input is 2D
        """
        stress = np.atleast_2d(stress)

        # Quadratic equation: a·SR² + b·SR + c = 0
        # where a = σᵀ·A·σ, b = b·σ, c = -1

        # Coefficient a: (n, 6) @ (6, 6) @ (6, n) = (n,)
        a = np.einsum('ij,jk,ik->i', stress, self.A, stress)

        # Coefficient b: (n, 6) @ (6,) = (n,)
        b = stress @ self.b

        # Coefficient c
        c = -1.0

        # Solve quadratic equation: SR = (-b + sqrt(b² - 4ac)) / (2a)
        # We take the positive root
        discriminant = b**2 - 4*a*c

        # Handle edge cases
        strength_ratio = np.zeros_like(a)

        # For valid discriminant (should always be >= 0 for physical problems)
        valid = discriminant >= 0

        # Calculate strength ratio using the positive root
        strength_ratio[valid] = (-b[valid] + np.sqrt(discriminant[valid])) / (2*a[valid])

        # Handle cases where a is very small (nearly zero quadratic term)
        # In this case, solve linear equation: b·SR - 1 = 0 => SR = 1/b
        small_a = np.abs(a) < 1e-10
        if np.any(small_a):
            strength_ratio[small_a] = 1.0 / b[small_a]

        # Return scalar if input was 1D
        if strength_ratio.shape[0] == 1:
            return strength_ratio[0]
        return strength_ratio


