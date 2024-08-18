"""Switch platform for ExoyOne."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory

from .entity import ExoyOneEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ExoyOneDataUpdateCoordinator
    from .data import ExoyOneConfigEntry

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="musicSync",
        name="Music sync",
        icon="mdi:timer-music-outline",
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key="sceneGeneration",
        name="Scene generation",
        icon="mdi:auto-fix",
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key="autoChange",
        name="Mode cycle",
        icon="mdi:rotate-left",
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key="poweredByPowerbank",
        name="Powered by powerbank",
        icon="mdi:battery-high",
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key="direction",
        name="Direction",
        icon="mdi:directions-fork",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ExoyOneConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        ExoyOneSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ExoyOneSwitch(ExoyOneEntity, SwitchEntity):
    """ExoyONE switch class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ExoyOneDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        self.entity_id = (
            f"switch.{self.coordinator.state.mdnsName}_{entity_description.key}"
        )
        self._attr_unique_id = (
            f"{self.coordinator.state.mdnsName}_switch_{entity_description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.async_is_on(self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return true if the switch is available."""
        return self.coordinator.async_is_available(self.entity_description.key)

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self.coordinator.async_turn_on(self.entity_description.key)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self.coordinator.async_turn_off(self.entity_description.key)
