"""Renpho sensor platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RenphoCoordinator

_CM_TO_IN = 1 / 2.54

# Fields where 0.0 means "not measured" rather than a real value.
_ZERO_MEANS_UNAVAILABLE = {
    "bodyfat", "water", "muscle", "bone", "bmr", "bodyage",
    "protein", "visfat",
    "neck_value", "shoulder_value", "chest_value", "waist_value",
    "hip_value", "abdomen_value", "arm_value", "thigh_value", "calf_value",
    "left_arm_value", "right_arm_value", "left_thigh_value", "right_thigh_value",
    "left_calf_value", "right_calf_value", "whr_value",
}


@dataclass(frozen=True, kw_only=True)
class RenphoSensorEntityDescription(SensorEntityDescription):
    """Describes a Renpho sensor."""

    data_key: str
    conversion_factor: float = field(default=1.0)


SENSORS: tuple[RenphoSensorEntityDescription, ...] = (
    # --- Scale sensors ---
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
    # --- Tape measure (girth) sensors ---
    # API returns centimeters; conversion_factor converts to inches natively.
    RenphoSensorEntityDescription(
        key="neck",
        data_key="neck_value",
        name="Neck",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="shoulder",
        data_key="shoulder_value",
        name="Shoulder",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="chest",
        data_key="chest_value",
        name="Chest",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="waist",
        data_key="waist_value",
        name="Waist",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="hip",
        data_key="hip_value",
        name="Hip",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="abdomen",
        data_key="abdomen_value",
        name="Abdomen",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="left_arm",
        data_key="left_arm_value",
        name="Left Arm",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="right_arm",
        data_key="right_arm_value",
        name="Right Arm",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="left_thigh",
        data_key="left_thigh_value",
        name="Left Thigh",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="right_thigh",
        data_key="right_thigh_value",
        name="Right Thigh",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="left_calf",
        data_key="left_calf_value",
        name="Left Calf",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="right_calf",
        data_key="right_calf_value",
        name="Right Calf",
        native_unit_of_measurement=UnitOfLength.INCHES,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:tape-measure",
        suggested_display_precision=1,
        conversion_factor=_CM_TO_IN,
    ),
    RenphoSensorEntityDescription(
        key="whr",
        data_key="whr_value",
        name="Waist-Hip Ratio",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:human-male",
        suggested_display_precision=2,
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
        if value == 0 and self.entity_description.data_key in _ZERO_MEANS_UNAVAILABLE:
            return None
        return round(value * self.entity_description.conversion_factor, 4)
