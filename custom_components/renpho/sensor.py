"""Renpho sensor platform."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RenphoCoordinator

# Fields where 0.0 means "not measured by this scale model" rather than a real value.
# Weight is excluded because it always has a real measurement.
_ZERO_MEANS_UNAVAILABLE = {
    "bodyfat", "water", "muscle", "bone", "bmr", "bodyage",
    "protein", "visfat",
}


@dataclass(frozen=True, kw_only=True)
class RenphoSensorEntityDescription(SensorEntityDescription):
    """Describes a Renpho sensor."""

    data_key: str


SENSORS: tuple[RenphoSensorEntityDescription, ...] = (
    RenphoSensorEntityDescription(
        key="weight",
        data_key="weight",
        name="Weight",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    RenphoSensorEntityDescription(
        key="bmi",
        data_key="bmi",
        name="BMI",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:human",
        suggested_display_precision=1,
    ),
    RenphoSensorEntityDescription(
        key="body_fat",
        data_key="bodyfat",
        name="Body Fat",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        suggested_display_precision=1,
    ),
    RenphoSensorEntityDescription(
        key="body_water",
        data_key="water",
        name="Body Water",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water",
        suggested_display_precision=1,
    ),
    RenphoSensorEntityDescription(
        key="muscle_mass",
        data_key="muscle",
        name="Muscle Mass",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:arm-flex",
        suggested_display_precision=1,
    ),
    RenphoSensorEntityDescription(
        key="bone_mass",
        data_key="bone",
        name="Bone Mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bone",
        suggested_display_precision=2,
    ),
    RenphoSensorEntityDescription(
        key="bmr",
        data_key="bmr",
        name="BMR",
        native_unit_of_measurement="kcal",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
        suggested_display_precision=0,
    ),
    RenphoSensorEntityDescription(
        key="body_age",
        data_key="bodyage",
        name="Body Age",
        native_unit_of_measurement="years",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-heart",
        suggested_display_precision=0,
    ),
    RenphoSensorEntityDescription(
        key="protein",
        data_key="protein",
        name="Protein",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:food-steak",
        suggested_display_precision=1,
    ),
    RenphoSensorEntityDescription(
        key="visceral_fat",
        data_key="visfat",
        name="Visceral Fat",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:stomach",
        suggested_display_precision=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Renpho sensors from a config entry."""
    coordinator: RenphoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        RenphoSensor(coordinator, description, entry) for description in SENSORS
    )


class RenphoSensor(CoordinatorEntity[RenphoCoordinator], SensorEntity):
    """Represents a single Renpho body measurement sensor."""

    entity_description: RenphoSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RenphoCoordinator,
        description: RenphoSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Renpho Scale",
            manufacturer="Renpho",
            model="Smart Scale",
        )

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self.entity_description.data_key)
        if value is None:
            return None
        # Treat zero as unavailable for body composition fields — the scale
        # didn't perform that measurement (e.g. basic scale without bio-impedance).
        if value == 0 and self.entity_description.data_key in _ZERO_MEANS_UNAVAILABLE:
            return None
        return value
