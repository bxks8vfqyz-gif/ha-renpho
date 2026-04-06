"""Data update coordinator for Renpho."""
from __future__ import annotations

import logging
from datetime import timedelta

from renpho import RenphoClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, POLL_INTERVAL_MINUTES
from .girth_client import GirthClient

_LOGGER = logging.getLogger(__name__)


class RenphoCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that fetches the latest Renpho measurement every hour."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=POLL_INTERVAL_MINUTES),
        )
        self._email: str = entry.data["email"]
        self._password: str = entry.data["password"]

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(f"Error fetching Renpho data: {err}") from err

    def _fetch(self) -> dict:
        """Synchronous fetch — runs in executor thread."""
        # Scale measurements
        scale_client = RenphoClient(self._email, self._password)
        scale_client.login()
        data: dict = dict(scale_client.get_all_measurements())
        _LOGGER.debug("Renpho scale data: %s", data)

        # Girth (tape measure) measurements
        try:
            girth = GirthClient(self._email, self._password).fetch()
            _LOGGER.debug("Renpho girth data: %s", girth)
            data.update(girth)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Could not fetch Renpho girth data: %s", err)

        return data
