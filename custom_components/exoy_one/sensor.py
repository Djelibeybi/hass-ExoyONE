"""Sensor platform for ExoyOne."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory

from .entity import ExoyOneEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ExoyOneDataUpdateCoordinator
    from .data import ExoyOneConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="currentModpack",
        name="Mode Pack",
        icon="mdi:package-variant",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="modeIndex",
        name="Effect",
        icon="mdi:magic-staff",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ExoyOneConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        ExoyOneSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ExoyOneSensor(ExoyOneEntity, SensorEntity):
    """ExoyOne Sensor class."""

    def __init__(
        self,
        coordinator: ExoyOneDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self.entity_id = (
            f"sensor.{self.coordinator.exoyone.state.mdnsName}_{entity_description.key}"
        )
        self._attr_unique_id = (
            f"{self.coordinator.exoyone.state.mdnsName}_sensor_{entity_description.key}"
        )

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.async_get_sensor_value(self.entity_description.key)
