"""ExoyONE entity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ExoyOneDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import ExoyOneConfigEntry


class ExoyOneEntity(CoordinatorEntity[ExoyOneDataUpdateCoordinator]):
    """ExoyOneEntity class."""

    config_entry: ExoyOneConfigEntry
    _attr_has_entity_name = True

    def __init__(self, coordinator: ExoyOneDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.runtime_data.exoyone.state.mdnsName,
                ),
            },
            manufacturer="Exoy BV",
            name=coordinator.exoyone.state.userDefinedName,
            model="Exoy(tm) ONE",
            model_id=coordinator.exoyone.device_type,
            serial_number=coordinator.exoyone.state.mdnsName,
            sw_version=coordinator.exoyone.state.firmwareVersion,
        )
