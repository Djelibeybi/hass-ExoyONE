"""ExoyONE light entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
    LightEntityFeature,
)

from .entity import ExoyOneEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ExoyOneDataUpdateCoordinator
    from .data import ExoyOneConfigEntry

ENTITY_DESCRIPTIONS = (
    LightEntityDescription(
        key="exoyone",
        icon="mdi:hexagon",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ExoyOneConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        ExoyOneLight(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ExoyOneLight(ExoyOneEntity, LightEntity):
    """Exoy ONE light class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ExoyOneDataUpdateCoordinator,
        entity_description: LightEntityDescription,
    ) -> None:
        """Initialize the light class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

        self.entity_id = f"light.{self.coordinator.exoyone.state.mdnsName}_exoyOne"
        self._attr_unique_id = f"{self.coordinator.exoyone.state.mdnsName}_light"
        self._attr_color_mode = ColorMode.HS
        self._attr_name = None
        self._attr_supported_color_modes = {ColorMode.HS}
        self._attr_supported_features = LightEntityFeature.EFFECT
        self._attr_effect_list = self.coordinator.mp.effects

    @property
    def is_on(self) -> bool:
        """Return the state of the light."""
        return self.coordinator.exoyone.state.fadingOff

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self.coordinator.exoyone.state.brightness

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the hs color value."""
        return (
            self.coordinator.exoyone.state.hue,
            self.coordinator.exoyone.state.saturation,
        )

    @property
    def color_mode(self) -> ColorMode:
        """Return current color mode."""
        return (
            ColorMode.BRIGHTNESS
            if self.coordinator.state.lockColorWheel is True
            else ColorMode.HS
        )

    @property
    def effect(self) -> str:
        """Return the current effect."""
        return self.coordinator.mp.get_effect_name_from_index(
            self.coordinator.state.currentModpack, self.coordinator.state.modeIndex
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if ATTR_EFFECT in kwargs:
            effect = kwargs[ATTR_EFFECT]
            pi, ei = self.coordinator.mp.get_indices_from_effect_name(effect)
            await self.coordinator.exoyone.set_effect((pi, ei))

        if ATTR_HS_COLOR in kwargs:
            hue, saturation = kwargs[ATTR_HS_COLOR]
            hue = int((hue / 360) * 255)
            await self.coordinator.exoyone.set_color((hue, saturation, self.brightness))

        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            await self.coordinator.exoyone.set_brightness(brightness)

        await self.coordinator.exoyone.toggle_power("on")

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Turn the light off."""
        await self.coordinator.exoyone.toggle_power("off")
