Timoshenko Beam Model
========================

Inertial
-----------

..  math::

    \begin{bmatrix}
    \mu & 0 & 0 & 0 & \mu x_{M3} & -\mu x_{M2} \\
    0 & \mu & 0 & -\mu x_{M3} & 0 & 0 \\
    0 & 0 & \mu & \mu x_{M2} & 0 & 0 \\
    0 & -\mu x_{M3} & \mu x_{M2} & i_{22}+i_{33} & 0 & 0 \\
    \mu x_{M3} & 0 & 0 & 0 & i_{22} & i_{23} \\
    -\mu x_{M2} & 0 & 0 & 0 & i_{23} & i_{33}
    \end{bmatrix}



Stiffness
-----------



Constitutive relation:

..  math::

    \begin{Bmatrix}
    F_1 \\ F_2 \\ F_3 \\ M_1 \\ M_2 \\ M_3
    \end{Bmatrix} =
    \begin{bmatrix}
    C^b_{11} & C^b_{12} & C^b_{13} & C^b_{14} & C^b_{15} & C^b_{16} \\
    C^b_{12} & C^b_{22} & C^b_{23} & C^b_{24} & C^b_{25} & C^b_{26} \\
    C^b_{13} & C^b_{23} & C^b_{33} & C^b_{34} & C^b_{35} & C^b_{36} \\
    C^b_{14} & C^b_{24} & C^b_{34} & C^b_{44} & C^b_{45} & C^b_{46} \\
    C^b_{15} & C^b_{25} & C^b_{35} & C^b_{45} & C^b_{55} & C^b_{56} \\
    C^b_{16} & C^b_{26} & C^b_{36} & C^b_{46} & C^b_{56} & C^b_{66} \\
    \end{bmatrix}
    \begin{Bmatrix}
    \gamma_{11} \\ \gamma_{12} \\ \gamma_{13} \\ \kappa_{11} \\ \kappa_{12} \\ \kappa_{13}
    \end{Bmatrix}

..  math::

    \begin{Bmatrix}
    \gamma_{11} \\ \gamma_{12} \\ \gamma_{13} \\ \kappa_{11} \\ \kappa_{12} \\ \kappa_{13}
    \end{Bmatrix} =
    \begin{bmatrix}
    S^b_{11} & S^b_{12} & S^b_{13} & S^b_{14} & S^b_{15} & S^b_{16} \\
    S^b_{12} & S^b_{22} & S^b_{23} & S^b_{24} & S^b_{25} & S^b_{26} \\
    S^b_{13} & S^b_{23} & S^b_{33} & S^b_{34} & S^b_{35} & S^b_{36} \\
    S^b_{14} & S^b_{24} & S^b_{34} & S^b_{44} & S^b_{45} & S^b_{46} \\
    S^b_{15} & S^b_{25} & S^b_{35} & S^b_{45} & S^b_{55} & S^b_{56} \\
    S^b_{16} & S^b_{26} & S^b_{36} & S^b_{46} & S^b_{56} & S^b_{66} \\
    \end{bmatrix}
    \begin{Bmatrix}
    F_1 \\ F_2 \\ F_3 \\ M_1 \\ M_2 \\ M_3
    \end{Bmatrix}


