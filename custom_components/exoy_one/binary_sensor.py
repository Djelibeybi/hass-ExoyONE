"""Binary sensor platform for ExoyOne."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import ExoyOneEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ExoyOneDataUpdateCoordinator
    from .data import ExoyOneConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="forceMusicSync",
        name="Music sync",
        icon="mdi:lock-reset",
        device_class=BinarySensorDeviceClass.LOCK,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    BinarySensorEntityDescription(
        key="lockColorWheel",
        name="Color wheel",
        icon="mdi:lock-reset",
        device_class=BinarySensorDeviceClass.LOCK,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ExoyOneConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        ExoyOneBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ExoyOneBinarySensor(ExoyOneEntity, BinarySensorEntity):
    """ExoyONE binary_sensor class."""

    def __init__(
        self,
        coordinator: ExoyOneDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self.entity_id = f"binary_sensor.{self.coordinator.exoyone.state.mdnsName}_{entity_description.key}"
        self._attr_unique_id = f"{self.coordinator.exoyone.state.mdnsName}_binary_sensor_{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return false if the corresponding ExoyOne state is true."""
        return not self.coordinator.async_is_on(self.entity_description.key)
