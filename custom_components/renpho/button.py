"""Renpho button platform — manual refresh."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RenphoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RenphoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RenphoRefreshButton(coordinator, entry)])


class RenphoRefreshButton(ButtonEntity):
    """Button that triggers an immediate poll of the Renpho API."""

    _attr_has_entity_name = True
    _attr_name = "Refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: RenphoCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Renpho Scale",
            manufacturer="Renpho",
            model="Smart Scale",
        )

    async def async_press(self) -> None:
        """Fetch latest data from Renpho and update all sensors."""
        await self._coordinator.async_request_refresh()
