# Constitutive Behavior

The constitutive layer describes *what a material does*, independently of the
structural model that uses it. A structural model holds a
{class}`~sgio.MaterialBehaviorMap` binding physics channels to behaviors.

```{eval-rst}
.. currentmodule:: sgio.model
```

## Protocols

```{eval-rst}
.. autoclass:: Model
   :members:
```

```{eval-rst}
.. autoclass:: ConstitutiveBehaviorProtocol
   :members:
```

```{eval-rst}
.. autoclass:: HistoryDependentBehaviorProtocol
   :members:
```

## Behaviors and Descriptors

```{eval-rst}
.. autoclass:: LinearElasticConstitutiveBehavior
   :members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: ConstitutiveBehaviorDescriptor
   :members:
```

```{eval-rst}
.. autoclass:: MaterialBehaviorMap
   :members:
```

```{eval-rst}
.. autoclass:: BehaviorVariable
   :members:
```

```{eval-rst}
.. autoclass:: ChannelBehaviorSlot
   :members:
```

```{eval-rst}
.. autoclass:: ChannelCouplingDescriptor
   :members:
```

```{eval-rst}
.. autoclass:: TensorComponent
   :members:
```

## Enumerations

```{eval-rst}
.. autoclass:: PhysicsChannel
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: BehaviorVariableRole
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: ElasticInputType
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: MatrixKind
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: SectionMatrixKind
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: SectionAxis
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: SectionCenter
   :members:
   :undoc-members:
```

```{eval-rst}
.. autoclass:: LocationType
   :members:
   :undoc-members:
```

## Helper Functions

```{eval-rst}
.. autofunction:: getModelDim
```
