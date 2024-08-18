"""DataUpdateCoordinator for ExoyONE."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from exoyone import ExoyOneException, ExoyOneTimeoutError, mode_packs
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .utils import get_method_for_attribute

if TYPE_CHECKING:
    from exoyone import ExoyOne, ExoyOneState
    from homeassistant.core import HomeAssistant

    from .data import ExoyOneConfigEntry


class ExoyOneDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Exoy ONE."""

    config_entry: ExoyOneConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=3),
            always_update=False,
        )
        self.mp = mode_packs

    @property
    def exoyone(self) -> ExoyOne:
        """Return the ExoyOne instance."""
        return self.config_entry.runtime_data.exoyone

    @property
    def state(self) -> ExoyOneState:
        """Return the state."""
        return self.config_entry.runtime_data.exoyone.state

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.exoyone.async_get_state()
        except ExoyOneTimeoutError as exception:
            raise UpdateFailed(exception) from exception
        except ExoyOneException as exception:
            raise UpdateFailed(exception) from exception

    def async_is_on(self, key: str) -> bool:
        """Return True if the key is on."""
        if key == "musicSync":
            return True if self.state.forceMusicSync is True else self.state.musicSync

        return getattr(self.state, key)

    def async_is_available(self, key: str) -> bool:
        """Return true if the key is available."""
        return not (
            (self.state.sceneGeneration is True and key in {"musicSync", "autoChange"})
            or (self.state.forceMusicSync is True and key == "musicSync")
        )

    def async_get_sensor_value(self, key: str) -> str | None:
        """Return the value of the sensor."""
        if key == "currentModpack":
            return self.mp.get_pack_name_from_index(self.state.currentModpack)
        if key == "modeIndex":
            return self.mp.get_effect_name_from_index(
                self.state.currentModpack, self.state.modeIndex
            )
        return None

    async def async_set_value(self, key: str, value: float) -> None:
        """Set a new value for the specified key."""
        method = getattr(self.exoyone, get_method_for_attribute(key))
        await method(value)

    async def async_turn_on(self, key: str) -> None:
        """Turn on the switch."""
        method = getattr(self.exoyone, get_method_for_attribute(key))
        await method("on")

    async def async_turn_off(self, key: str) -> None:
        """Turn off the switch."""
        method = getattr(self.exoyone, get_method_for_attribute(key))
        await method("off")

    def async_current_option(self, key: str) -> str:
        """Return the current selected option."""
        if key == "currentModpack":
            return self.mp.get_pack_name_from_index(self.state.currentModpack)
        if key == "modeIndex":
            return self.mp.get_effect_name_from_index(
                self.state.currentModpack, self.state.modeIndex
            )
        return ""

    def async_all_options(self, key: str) -> list[str]:
        """Return the list of available options."""
        if key == "currentModpack":
            return self.mp.mode_packs
        if key == "modeIndex":
            return self.mp.get_effects_by_index(self.state.currentModpack)
        return []

    async def async_select_option(self, key: str, option: str) -> None:
        """Select the option."""
        if key == "currentModpack":
            pi = self.mp.get_pack_index_from_name(option)
            if self.state.modeIndex <= len(self.mp.get_effects_by_index(pi)):
                await self.exoyone.set_effect((pi, self.state.modeIndex))
            else:
                await self.exoyone.set_effect((pi, 0))
        if key == "modeIndex":
            pi, ei = self.mp.get_indices_from_effect_name(option)
            await self.exoyone.set_effect((pi, ei))
