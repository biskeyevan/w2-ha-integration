"""Sensor platform for Energy Meter integration."""
from __future__ import annotations
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    entities = []
    data = coordinator.data
    
    if not data:
        _LOGGER.warning("No data available from coordinator during setup")
        return

    # Create sensors for each channel
    for channel in data.get("channels", []):
        ch = channel["ch"]
        channel_type = channel.get("type", f"Channel {ch}")
        label = channel.get("label", channel_type)

        # Power sensor
        entities.append(
            EnergyMeterChannelSensor(
                coordinator,
                f"{label} Power",
                f"power_ch{ch}",
                ch,
                "p_W",
                SensorDeviceClass.POWER,
                SensorStateClass.MEASUREMENT,
                "W",
            )
        )

        # Energy Import sensor
        entities.append(
            EnergyMeterChannelSensor(
                coordinator,
                f"{label} Energy Import",
                f"energy_import_ch{ch}",
                ch,
                "eImp_Ws",
                SensorDeviceClass.ENERGY,
                SensorStateClass.TOTAL_INCREASING,
                "kWh",
                conversion_factor=1/3600000,  # Ws to kWh
            )
        )

        # Energy Export sensor
        entities.append(
            EnergyMeterChannelSensor(
                coordinator,
                f"{label} Energy Export",
                f"energy_export_ch{ch}",
                ch,
                "eExp_Ws",
                SensorDeviceClass.ENERGY,
                SensorStateClass.TOTAL_INCREASING,
                "kWh",
                conversion_factor=1/3600000,  # Ws to kWh
            )
        )

        # Voltage sensor
        entities.append(
            EnergyMeterChannelSensor(
                coordinator,
                f"{label} Voltage",
                f"voltage_ch{ch}",
                ch,
                "v_V",
                SensorDeviceClass.VOLTAGE,
                SensorStateClass.MEASUREMENT,
                "V",
            )
        )

    # Create sensors for each CT
    for ct in data.get("cts", []):
        ct_num = ct["ct"]

        # CT Power sensor
        entities.append(
            EnergyMeterCTSensor(
                coordinator,
                f"CT {ct_num} Power",
                f"ct_power_ct{ct_num}",
                ct_num,
                "p_W",
                SensorDeviceClass.POWER,
                SensorStateClass.MEASUREMENT,
                "W",
            )
        )

        # CT Current sensor
        entities.append(
            EnergyMeterCTSensor(
                coordinator,
                f"CT {ct_num} Current",
                f"ct_current_ct{ct_num}",
                ct_num,
                "i_A",
                SensorDeviceClass.CURRENT,
                SensorStateClass.MEASUREMENT,
                "A",
            )
        )

        # CT Voltage sensor
        entities.append(
            EnergyMeterCTSensor(
                coordinator,
                f"CT {ct_num} Voltage",
                f"ct_voltage_ct{ct_num}",
                ct_num,
                "v_V",
                SensorDeviceClass.VOLTAGE,
                SensorStateClass.MEASUREMENT,
                "V",
            )
        )

    async_add_entities(entities)


class EnergyMeterChannelSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Energy Meter channel sensor."""

    def __init__(
        self,
        coordinator,
        name,
        unique_id,
        channel_number,
        data_key,
        device_class,
        state_class,
        unit,
        conversion_factor=1,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        self._channel_number = channel_number
        self._data_key = data_key
        self._conversion_factor = conversion_factor

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        for channel in self.coordinator.data.get("channels", []):
            if channel.get("ch") == self._channel_number:
                value = channel.get(self._data_key)
                if value is not None:
                    return value * self._conversion_factor
                return None
        return None

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "energy_meter")},
            "name": "Energy Meter",
            "manufacturer": "Unknown",
            "model": "LAN Energy Meter",
        }


class EnergyMeterCTSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Energy Meter CT sensor."""

    def __init__(
        self,
        coordinator,
        name,
        unique_id,
        ct_number,
        data_key,
        device_class,
        state_class,
        unit,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        self._ct_number = ct_number
        self._data_key = data_key

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        for ct in self.coordinator.data.get("cts", []):
            if ct.get("ct") == self._ct_number:
                return ct.get(self._data_key)
        return None

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "energy_meter")},
            "name": "Energy Meter",
            "manufacturer": "Unknown",
            "model": "LAN Energy Meter",
        }