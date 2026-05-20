from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from .material_components import LinearElasticBehavior, ThermalProperties


class PhysicsChannel(str, Enum):
    """Supported constitutive physics channels."""

    MECHANICAL = "mechanical"
    THERMAL = "thermal"
    ELECTRICAL = "electrical"
    MAGNETIC = "magnetic"
    OPTICAL = "optical"


class BehaviorVariableRole(str, Enum):
    """Role of one constitutive variable within a behavior descriptor."""

    INPUT = "input"
    OUTPUT = "output"
    STATE = "state"
    TANGENT = "tangent"


@dataclass(frozen=True, slots=True)
class BehaviorVariable:
    """One named constitutive variable used by a behavior descriptor.

    Parameters
    ----------
    name : str
        Variable name.
    channel : PhysicsChannel
        Owning physics channel.
    role : BehaviorVariableRole
        Variable role.
    description : str, optional
        Human-readable description.
    """

    name: str
    channel: PhysicsChannel
    role: BehaviorVariableRole
    description: str = ""


@dataclass(frozen=True, slots=True)
class ChannelCouplingDescriptor:
    """Descriptor for one cross-channel coupling relation.

    Parameters
    ----------
    source : PhysicsChannel
        Driving channel.
    target : PhysicsChannel
        Driven channel.
    description : str, optional
        Human-readable description of the coupling.
    """

    source: PhysicsChannel
    target: PhysicsChannel
    description: str = ""


@dataclass(frozen=True, slots=True)
class ConstitutiveBehaviorDescriptor:
    """Static descriptor of one constitutive behavior family.

    Parameters
    ----------
    name : str
        Behavior family name.
    channels : tuple[PhysicsChannel, ...]
        Physics channels covered by the behavior.
    is_stateful : bool
        Whether the behavior carries history variables.
    inputs : tuple[BehaviorVariable, ...], optional
        Input variables.
    outputs : tuple[BehaviorVariable, ...], optional
        Output variables.
    tangent_outputs : tuple[BehaviorVariable, ...], optional
        Tangent outputs or linearization products.
    state_variables : tuple[BehaviorVariable, ...], optional
        History variables used by the behavior.
    notes : str, optional
        Additional notes about the behavior boundary.
    """

    name: str
    channels: tuple[PhysicsChannel, ...]
    is_stateful: bool
    inputs: tuple[BehaviorVariable, ...] = ()
    outputs: tuple[BehaviorVariable, ...] = ()
    tangent_outputs: tuple[BehaviorVariable, ...] = ()
    state_variables: tuple[BehaviorVariable, ...] = ()
    notes: str = ""


@runtime_checkable
class ConstitutiveBehaviorProtocol(Protocol):
    """Protocol for stateless or stateful constitutive behaviors."""

    @property
    def descriptor(self) -> ConstitutiveBehaviorDescriptor:
        """Return the static behavior descriptor."""

    def export_payload(self) -> Any:
        """Return the payload currently backing this behavior."""


@runtime_checkable
class HistoryDependentBehaviorProtocol(ConstitutiveBehaviorProtocol, Protocol):
    """Protocol for future history-dependent constitutive behaviors."""

    def initialize_history_state(self) -> dict[str, Any]:
        """Return one initialized history-state payload."""

    def describe_update_rule(self) -> str:
        """Describe the update law boundary used by the behavior."""

    def describe_consistent_tangent(self) -> str:
        """Describe the tangent quantity exposed by the behavior."""


_LINEAR_ELASTIC_DESCRIPTOR = ConstitutiveBehaviorDescriptor(
    name="linear_elastic",
    channels=(PhysicsChannel.MECHANICAL,),
    is_stateful=False,
    inputs=(
        BehaviorVariable(
            name="strain",
            channel=PhysicsChannel.MECHANICAL,
            role=BehaviorVariableRole.INPUT,
            description="Generalized mechanical strain-like input.",
        ),
    ),
    outputs=(
        BehaviorVariable(
            name="stress",
            channel=PhysicsChannel.MECHANICAL,
            role=BehaviorVariableRole.OUTPUT,
            description="Generalized mechanical stress-like output.",
        ),
    ),
    tangent_outputs=(
        BehaviorVariable(
            name="stiffness",
            channel=PhysicsChannel.MECHANICAL,
            role=BehaviorVariableRole.TANGENT,
            description="Constant linear tangent represented by the stiffness matrix.",
        ),
    ),
    notes="Stateless mechanical behavior represented by one constant stiffness/compliance pair.",
)


@dataclass(slots=True)
class LinearElasticConstitutiveBehavior:
    """Adapter exposing current linear elasticity through the generic behavior seam.

    Parameters
    ----------
    payload : LinearElasticBehavior
        Linear-elastic payload snapshot.
    """

    payload: LinearElasticBehavior

    @property
    def descriptor(self) -> ConstitutiveBehaviorDescriptor:
        """Return the linear-elastic behavior descriptor."""

        return _LINEAR_ELASTIC_DESCRIPTOR

    def export_payload(self) -> LinearElasticBehavior:
        """Return the wrapped linear-elastic payload."""

        return self.payload


@dataclass(slots=True)
class ChannelBehaviorSlot:
    """One extensibility slot for a single physics channel.

    Parameters
    ----------
    channel : PhysicsChannel
        Slot channel.
    behavior : ConstitutiveBehaviorProtocol or None, optional
        Attached behavior implementation.
    properties : object or None, optional
        Auxiliary channel properties not yet promoted to full behaviors.
    """

    channel: PhysicsChannel
    behavior: ConstitutiveBehaviorProtocol | None = None
    properties: Any | None = None


@dataclass(slots=True)
class MaterialBehaviorMap:
    """Container reserving per-channel constitutive behavior slots.

    Parameters
    ----------
    mechanical, thermal, electrical, magnetic, optical : ChannelBehaviorSlot
        Per-channel slots.
    couplings : tuple[ChannelCouplingDescriptor, ...], optional
        Cross-channel couplings carried alongside the slots.
    """

    mechanical: ChannelBehaviorSlot = field(
        default_factory=lambda: ChannelBehaviorSlot(PhysicsChannel.MECHANICAL)
    )
    thermal: ChannelBehaviorSlot = field(
        default_factory=lambda: ChannelBehaviorSlot(PhysicsChannel.THERMAL)
    )
    electrical: ChannelBehaviorSlot = field(
        default_factory=lambda: ChannelBehaviorSlot(PhysicsChannel.ELECTRICAL)
    )
    magnetic: ChannelBehaviorSlot = field(
        default_factory=lambda: ChannelBehaviorSlot(PhysicsChannel.MAGNETIC)
    )
    optical: ChannelBehaviorSlot = field(
        default_factory=lambda: ChannelBehaviorSlot(PhysicsChannel.OPTICAL)
    )
    couplings: tuple[ChannelCouplingDescriptor, ...] = ()

    def get_slot(self, channel: PhysicsChannel) -> ChannelBehaviorSlot:
        """Return one channel slot by enum key."""

        slot_map = {
            PhysicsChannel.MECHANICAL: self.mechanical,
            PhysicsChannel.THERMAL: self.thermal,
            PhysicsChannel.ELECTRICAL: self.electrical,
            PhysicsChannel.MAGNETIC: self.magnetic,
            PhysicsChannel.OPTICAL: self.optical,
        }
        return slot_map[channel]


def build_default_behavior_map(
    elastic: LinearElasticBehavior,
    thermal: ThermalProperties,
) -> MaterialBehaviorMap:
    """Build the default stateless behavior map for current material models.

    Parameters
    ----------
    elastic : LinearElasticBehavior
        Current linear-elastic payload.
    thermal : ThermalProperties
        Current thermal-property payload.

    Returns
    -------
    MaterialBehaviorMap
        Default behavior map with mechanical behavior and thermal properties populated.
    """

    return MaterialBehaviorMap(
        mechanical=ChannelBehaviorSlot(
            channel=PhysicsChannel.MECHANICAL,
            behavior=LinearElasticConstitutiveBehavior(elastic),
        ),
        thermal=ChannelBehaviorSlot(
            channel=PhysicsChannel.THERMAL,
            properties=thermal,
        ),
    )


__all__ = [
    "BehaviorVariable",
    "BehaviorVariableRole",
    "ChannelBehaviorSlot",
    "ChannelCouplingDescriptor",
    "ConstitutiveBehaviorDescriptor",
    "ConstitutiveBehaviorProtocol",
    "HistoryDependentBehaviorProtocol",
    "LinearElasticConstitutiveBehavior",
    "MaterialBehaviorMap",
    "PhysicsChannel",
    "build_default_behavior_map",
]
