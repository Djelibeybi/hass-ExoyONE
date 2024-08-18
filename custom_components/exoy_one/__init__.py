"""Custom integration to control ExoyONE with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from exoyone import ExoyOne
from homeassistant.const import CONF_HOST, Platform
from homeassistant.loader import async_get_loaded_integration

from .coordinator import ExoyOneDataUpdateCoordinator
from .data import ExoyOneData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import ExoyOneConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ExoyOneConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = ExoyOneDataUpdateCoordinator(hass)
    exoyone = ExoyOne(host=entry.data[CONF_HOST])
    await exoyone.async_get_data()

    entry.runtime_data = ExoyOneData(
        exoyone=exoyone,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ExoyOneConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ExoyOneConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
