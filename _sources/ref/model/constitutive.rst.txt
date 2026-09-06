Constitutive Behavior
=====================

The constitutive layer describes *what a material does*, independently of the
structural model that uses it. A structural model holds a
:class:`~sgio.MaterialBehaviorMap` binding physics channels to behaviors.

.. currentmodule:: sgio.model


Protocols
---------

..  autoclass:: Model
    :members:

..  autoclass:: ConstitutiveBehaviorProtocol
    :members:

..  autoclass:: HistoryDependentBehaviorProtocol
    :members:


Behaviors and Descriptors
-------------------------

..  autoclass:: LinearElasticConstitutiveBehavior
    :members:
    :show-inheritance:

..  autoclass:: ConstitutiveBehaviorDescriptor
    :members:

..  autoclass:: MaterialBehaviorMap
    :members:

..  autoclass:: BehaviorVariable
    :members:

..  autoclass:: ChannelBehaviorSlot
    :members:

..  autoclass:: ChannelCouplingDescriptor
    :members:

..  autoclass:: TensorComponent
    :members:


Enumerations
------------

..  autoclass:: PhysicsChannel
    :members:
    :undoc-members:

..  autoclass:: BehaviorVariableRole
    :members:
    :undoc-members:

..  autoclass:: ElasticInputType
    :members:
    :undoc-members:

..  autoclass:: MatrixKind
    :members:
    :undoc-members:

..  autoclass:: SectionMatrixKind
    :members:
    :undoc-members:

..  autoclass:: SectionAxis
    :members:
    :undoc-members:

..  autoclass:: SectionCenter
    :members:
    :undoc-members:

..  autoclass:: LocationType
    :members:
    :undoc-members:


Helper Functions
----------------

..  autofunction:: getModelDim
