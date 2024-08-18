"""Select platform for ExoyOne."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory

from .entity import ExoyOneEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ExoyOneDataUpdateCoordinator
    from .data import ExoyOneConfigEntry

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="currentModpack",
        name="Mode Pack",
        icon="mdi:package-variant",
        entity_category=EntityCategory.CONFIG,
    ),
    SelectEntityDescription(
        key="modeIndex",
        name="Effect",
        icon="mdi:magic-staff",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ExoyOneConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        ExoyOneSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ExoyOneSelect(ExoyOneEntity, SelectEntity):
    """ExoyOne Select class."""

    def __init__(
        self,
        coordinator: ExoyOneDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self.entity_id = (
            f"select.{self.coordinator.exoyone.state.mdnsName}_{entity_description.key}"
        )
        mdns_name = self.coordinator.exoyone.state.mdnsName
        key = entity_description.key
        self._attr_unique_id = f"{mdns_name}_selects_{key}"

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        return self.coordinator.async_current_option(self.entity_description.key)

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return self.coordinator.async_all_options(self.entity_description.key)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        return await self.coordinator.async_select_option(
            self.entity_description.key, option
        )
