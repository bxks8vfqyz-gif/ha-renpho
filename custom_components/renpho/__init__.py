"""Renpho Home Assistant integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import RenphoCoordinator
from .history_import import async_import_all_history

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

# Store key to track whether history has been imported for this entry.
_HISTORY_IMPORTED_KEY = "history_imported"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Renpho from a config entry."""
    coordinator = RenphoCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Import full history once per entry (not on every restart).
    if not entry.data.get(_HISTORY_IMPORTED_KEY):
        hass.async_create_task(_run_history_import(hass, entry))

    return True


async def _run_history_import(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Import history then mark the entry so we don't repeat on next restart."""
    try:
        await async_import_all_history(
            hass, entry.data["email"], entry.data["password"]
        )
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, _HISTORY_IMPORTED_KEY: True}
        )
    except Exception:
        _LOGGER.exception("Renpho history import failed — will retry on next restart")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
