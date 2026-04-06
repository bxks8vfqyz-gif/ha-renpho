"""One-time historical data import from Renpho into HA long-term statistics."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from renpho import RenphoClient

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_import_statistics,
    statistics_during_period,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .girth_client import GirthClient
from .sensor import SENSORS, _ZERO_MEANS_UNAVAILABLE

_LOGGER = logging.getLogger(__name__)

# Statistic IDs use the pattern "renpho:<sensor_key>"
def statistic_id(key: str) -> str:
    return f"{DOMAIN}:{key}"


def _fetch_all_history(email: str, password: str) -> tuple[list[dict], list[dict]]:
    """Fetch complete measurement + girth history (runs in executor)."""
    client = RenphoClient(email, password)
    client.login()
    measurements = client.get_all_measurements()

    try:
        girth_client = GirthClient(email, password)
        girths = girth_client._fetch_all_girths()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not fetch girth history: %s", err)
        girths = []

    return measurements, girths


async def async_import_all_history(
    hass: HomeAssistant, email: str, password: str
) -> None:
    """Import all available Renpho history as HA long-term statistics."""
    _LOGGER.info("Starting Renpho historical data import")

    measurements, girths = await hass.async_add_executor_job(
        _fetch_all_history, email, password
    )

    recorder = get_instance(hass)

    for desc in SENSORS:
        stats: list[StatisticData] = []

        # Scale measurements (newest-first → reverse for chronological)
        for m in reversed(measurements):
            value = m.get(desc.data_key)
            if value is None:
                continue
            if value == 0 and desc.data_key in _ZERO_MEANS_UNAVAILABLE:
                continue
            ts = m.get("timeStamp")
            if not ts:
                continue
            dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            converted = round(value * desc.conversion_factor, 4)
            stats.append(StatisticData(start=dt, state=converted, mean=converted))

        # Girth measurements
        for g in reversed(girths):
            value = g.get(desc.data_key)
            if value is None or value == 0:
                continue
            ts = g.get("time_stamp")
            if not ts:
                continue
            dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            converted = round(value * desc.conversion_factor, 4)
            stats.append(StatisticData(start=dt, state=converted, mean=converted))

        if not stats:
            continue

        # De-duplicate by start time (keep last) then sort
        by_time: dict[datetime, StatisticData] = {s.start: s for s in stats}
        stats = sorted(by_time.values(), key=lambda s: s.start)

        metadata = StatisticMetaData(
            has_mean=True,
            has_sum=False,
            name=f"Renpho {desc.name}",
            source=DOMAIN,
            statistic_id=statistic_id(desc.key),
            unit_of_measurement=desc.native_unit_of_measurement,
        )

        async_import_statistics(hass, metadata, stats)
        _LOGGER.info(
            "Imported %d historical records for Renpho %s", len(stats), desc.name
        )

    _LOGGER.info("Renpho historical data import complete")
