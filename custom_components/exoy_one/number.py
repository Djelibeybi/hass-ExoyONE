"""Number entities for ExoyOne."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import ExoyOneEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ExoyOneDataUpdateCoordinator
    from .data import ExoyOneConfigEntry

ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="speed",
        name="Effect speed",
        icon="mdi:play-speed",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.SPEED,
        native_unit_of_measurement="%",
        native_max_value=100,
        native_min_value=0,
        native_step=1,
    ),
    NumberEntityDescription(
        key="cycleSpeed",
        name="Mode cycle speed",
        icon="mdi:timer-refresh-outline",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement="s",
        native_max_value=300,
        mode="box",
    ),
    NumberEntityDescription(
        key="shutdownTimer",
        name="Shutdown timer",
        icon="mdi:alarm",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement="min",
        native_max_value=480,
        native_min_value=0,
        mode="slider",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ExoyOneConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        ExoyOneNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ExoyOneNumber(ExoyOneEntity, NumberEntity):
    """Exoy ONE number class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ExoyOneDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self._attr_unique_id = (
            f"{self.coordinator.exoyone.state.mdnsName}_number_{entity_description.key}"
        )
        self.entity_id = (
            f"number.{self.coordinator.exoyone.state.mdnsName}_{entity_description.key}"
        )

    @property
    def native_value(self) -> float:
        """Return the value of the entity."""
        return self.coordinator.async_get_sensor_value(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        return await self.coordinator.async_set_value(
            self.entity_description.key, value
        )
