"""Custom types for ExoyONE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from exoyone import ExoyOne
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import ExoyOneDataUpdateCoordinator


type ExoyOneConfigEntry = ConfigEntry[ExoyOneData]


@dataclass
class ExoyOneData:
    """Data for the ExoyONE integration."""

    exoyone: ExoyOne
    coordinator: ExoyOneDataUpdateCoordinator
    integration: Integration
