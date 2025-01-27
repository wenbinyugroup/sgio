.. _guide_model_bm_euler:

Euler-Bernoulli Beam Model
============================


Inertial
---------


Stiffness
------------



Constitutive relation:

..  math::

    \begin{Bmatrix}
    F_1 \\ M_1 \\ M_2 \\ M_3
    \end{Bmatrix} =
    \begin{bmatrix}
    C^b_{11} & C^b_{12} & C^b_{13} & C^b_{14} \\
    C^b_{12} & C^b_{22} & C^b_{23} & C^b_{24} \\
    C^b_{13} & C^b_{23} & C^b_{33} & C^b_{34} \\
    C^b_{14} & C^b_{24} & C^b_{34} & C^b_{44}
    \end{bmatrix}
    \begin{Bmatrix}
    \gamma_{11} \\ \kappa_{11} \\ \kappa_{12} \\ \kappa_{13}
    \end{Bmatrix}

..  math::

    \begin{Bmatrix}
    \gamma_{11} \\ \kappa_{11} \\ \kappa_{12} \\ \kappa_{13}
    \end{Bmatrix} =
    \begin{bmatrix}
    S^b_{11} & S^b_{12} & S^b_{13} & S^b_{14} \\
    S^b_{12} & S^b_{22} & S^b_{23} & S^b_{24} \\
    S^b_{13} & S^b_{23} & S^b_{33} & S^b_{34} \\
    S^b_{14} & S^b_{24} & S^b_{34} & S^b_{44}
    \end{bmatrix}
    \begin{Bmatrix}
    F_1 \\ M_1 \\ M_2 \\ M_3
    \end{Bmatrix}


