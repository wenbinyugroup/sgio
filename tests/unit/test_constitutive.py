"""Tests for constitutive behavior seams introduced in phase 7."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from sgio.model.constitutive import (
    ConstitutiveBehaviorDescriptor,
    ConstitutiveBehaviorProtocol,
    HistoryDependentBehaviorProtocol,
    PhysicsChannel,
)
from sgio.model.query_types import ElasticInputType
from sgio.model.solid import CauchyContinuumModel


@dataclass(slots=True)
class DummyElectricalBehavior:
    """Small stateless behavior used to verify channel attachment."""

    payload: dict[str, Any]

    @property
    def descriptor(self) -> ConstitutiveBehaviorDescriptor:
        """Return a minimal stateless electrical descriptor."""

        return ConstitutiveBehaviorDescriptor(
            name="dummy_electrical",
            channels=(PhysicsChannel.ELECTRICAL,),
            is_stateful=False,
        )

    def export_payload(self) -> dict[str, Any]:
        """Return the wrapped payload."""

        return self.payload


@dataclass(slots=True)
class DummyViscoBehavior:
    """Small history-dependent behavior used to verify the future seam."""

    @property
    def descriptor(self) -> ConstitutiveBehaviorDescriptor:
        """Return a minimal stateful mechanical descriptor."""

        return ConstitutiveBehaviorDescriptor(
            name="dummy_visco",
            channels=(PhysicsChannel.MECHANICAL,),
            is_stateful=True,
            notes="History-dependent placeholder.",
        )

    def export_payload(self) -> dict[str, str]:
        """Return one placeholder payload."""

        return {"kind": "visco"}

    def initialize_history_state(self) -> dict[str, float]:
        """Return one initialized history state."""

        return {"creep_strain": 0.0}

    def describe_update_rule(self) -> str:
        """Return the placeholder update law description."""

        return "integrate history variables externally"

    def describe_consistent_tangent(self) -> str:
        """Return the placeholder tangent description."""

        return "algorithmic tangent defined by the future integrator"


@pytest.mark.unit
def test_default_constitutive_channels_expose_linear_mechanical_behavior():
    """Current materials should expose a stateless mechanical behavior by default."""

    solid = CauchyContinuumModel()
    solid.set_isotropy(0)
    solid.set_elastic([210e9, 0.3], input_type=ElasticInputType.ISOTROPIC)

    behavior = solid.get_behavior(PhysicsChannel.MECHANICAL)

    assert isinstance(behavior, ConstitutiveBehaviorProtocol)
    assert behavior is not None
    assert behavior.descriptor.name == "linear_elastic"
    assert behavior.descriptor.is_stateful is False
    assert behavior.export_payload().e1 == pytest.approx(210e9)


@pytest.mark.unit
def test_constitutive_channels_keep_thermal_properties_outside_mechanical_behavior():
    """Thermal payload should live in its own reserved channel slot."""

    solid = CauchyContinuumModel()
    solid.cte = [1e-6] * 6
    solid.specific_heat = 900.0

    channels = solid.constitutive_channels

    assert channels.mechanical.behavior is not None
    assert channels.thermal.behavior is None
    assert channels.thermal.properties is not None
    assert channels.thermal.properties.specific_heat == pytest.approx(900.0)


@pytest.mark.unit
def test_attach_behavior_allows_future_multiphysics_slots_without_flat_fields():
    """Future channel behaviors should attach without adding new outer fields."""

    solid = CauchyContinuumModel()
    behavior = DummyElectricalBehavior(payload={"sigma": 1.0})

    solid.attach_behavior(PhysicsChannel.ELECTRICAL, behavior)

    attached = solid.get_behavior(PhysicsChannel.ELECTRICAL)
    assert attached is behavior
    assert attached.export_payload()["sigma"] == pytest.approx(1.0)


@pytest.mark.unit
def test_stateful_protocol_placeholder_can_override_mechanical_slot():
    """History-dependent placeholders should fit the override seam cleanly."""

    solid = CauchyContinuumModel()
    visco = DummyViscoBehavior()

    solid.attach_behavior(PhysicsChannel.MECHANICAL, visco)

    behavior = solid.get_behavior(PhysicsChannel.MECHANICAL)
    assert isinstance(behavior, HistoryDependentBehaviorProtocol)
    assert behavior is visco
    assert behavior.descriptor.is_stateful is True
    assert behavior.initialize_history_state()["creep_strain"] == pytest.approx(0.0)


@pytest.mark.unit
def test_clear_behavior_restores_default_mechanical_behavior():
    """Clearing an override should fall back to the default linear view."""

    solid = CauchyContinuumModel()
    solid.set_isotropy(0)
    solid.set_elastic([200e9, 0.29], input_type="isotropic")
    solid.attach_behavior(PhysicsChannel.MECHANICAL, DummyViscoBehavior())

    solid.clear_behavior(PhysicsChannel.MECHANICAL)

    behavior = solid.get_behavior(PhysicsChannel.MECHANICAL)
    assert behavior is not None
    assert behavior.descriptor.name == "linear_elastic"
