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

    # Create sensors for each channel
    for channel in data.get("channels", []):
        ch = channel["ch"]
        channel_type = channel.get("type", f"Channel {ch}")
        label = channel.get("label", channel_type)

        # Power sensor
        entities.append(
            EnergyMeterSensor(
                coordinator,
                f"{label} Power",
                f"power_ch{ch}",
                channel["p_W"],
                SensorDeviceClass.POWER,
                SensorStateClass.MEASUREMENT,
                "W",
            )
        )

        # Energy Import sensor
        entities.append(
            EnergyMeterSensor(
                coordinator,
                f"{label} Energy Import",
                f"energy_import_ch{ch}",
                channel["eImp_Ws"] / 3600000,  # Convert Ws to kWh
                SensorDeviceClass.ENERGY,
                SensorStateClass.TOTAL_INCREASING,
                "kWh",
            )
        )

        # Energy Export sensor
        entities.append(
            EnergyMeterSensor(
                coordinator,
                f"{label} Energy Export",
                f"energy_export_ch{ch}",
                channel["eExp_Ws"] / 3600000,  # Convert Ws to kWh
                SensorDeviceClass.ENERGY,
                SensorStateClass.TOTAL_INCREASING,
                "kWh",
            )
        )

        # Voltage sensor
        entities.append(
            EnergyMeterSensor(
                coordinator,
                f"{label} Voltage",
                f"voltage_ch{ch}",
                channel["v_V"],
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
            EnergyMeterSensor(
                coordinator,
                f"CT {ct_num} Power",
                f"ct_power_ct{ct_num}",
                ct["p_W"],
                SensorDeviceClass.POWER,
                SensorStateClass.MEASUREMENT,
                "W",
            )
        )

        # CT Current sensor
        entities.append(
            EnergyMeterSensor(
                coordinator,
                f"CT {ct_num} Current",
                f"ct_current_ct{ct_num}",
                ct["i_A"],
                SensorDeviceClass.CURRENT,
                SensorStateClass.MEASUREMENT,
                "A",
            )
        )

        # CT Voltage sensor
        entities.append(
            EnergyMeterSensor(
                coordinator,
                f"CT {ct_num} Voltage",
                f"ct_voltage_ct{ct_num}",
                ct["v_V"],
                SensorDeviceClass.VOLTAGE,
                SensorStateClass.MEASUREMENT,
                "V",
            )
        )

    async_add_entities(entities)


class EnergyMeterSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Energy Meter sensor."""

    def __init__(
        self,
        coordinator,
        name,
        unique_id,
        initial_value,
        device_class,
        state_class,
        unit,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._unique_id = unique_id
        self._device_class = device_class
        self._state_class = state_class
        self._unit = unit
        self._value = initial_value

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class."""
        return self._state_class

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value

    def _update_value(self, data):
        """Update the sensor value from data."""
        # Extract value based on unique_id
        if "power" in self._unique_id:
            # Power sensors
            if "ch" in self._unique_id:
                ch = int(self._unique_id.split("ch")[1])
                for channel in data.get("channels", []):
                    if channel["ch"] == ch:
                        self._value = channel["p_W"]
                        break
            elif "ct" in self._unique_id:
                ct = int(self._unique_id.split("ct")[1])
                for ct_data in data.get("cts", []):
                    if ct_data["ct"] == ct:
                        self._value = ct_data["p_W"]
                        break
        elif "energy_import" in self._unique_id:
            ch = int(self._unique_id.split("ch")[1])
            for channel in data.get("channels", []):
                if channel["ch"] == ch:
                    self._value = channel["eImp_Ws"] / 3600000  # Ws to kWh
                    break
        elif "energy_export" in self._unique_id:
            ch = int(self._unique_id.split("ch")[1])
            for channel in data.get("channels", []):
                if channel["ch"] == ch:
                    self._value = channel["eExp_Ws"] / 3600000  # Ws to kWh
                    break
        elif "voltage" in self._unique_id:
            if "ch" in self._unique_id:
                ch = int(self._unique_id.split("ch")[1])
                for channel in data.get("channels", []):
                    if channel["ch"] == ch:
                        self._value = channel["v_V"]
                        break
            elif "ct" in self._unique_id:
                ct = int(self._unique_id.split("ct")[1])
                for ct_data in data.get("cts", []):
                    if ct_data["ct"] == ct:
                        self._value = ct_data["v_V"]
                        break
        elif "current" in self._unique_id:
            ct = int(self._unique_id.split("ct")[1])
            for ct_data in data.get("cts", []):
                if ct_data["ct"] == ct:
                    self._value = ct_data["i_A"]
                    break

    async def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Sensor %s received coordinator update", self._unique_id)
        if self.coordinator.data is None:
            _LOGGER.warning("Coordinator data is None for sensor %s", self._unique_id)
            return
        
        old_value = self._value
        self._update_value(self.coordinator.data)
        
        if old_value != self._value:
            _LOGGER.debug("Sensor %s value changed from %s to %s", self._unique_id, old_value, self._value)
        else:
            _LOGGER.debug("Sensor %s value unchanged: %s", self._unique_id, self._value)
            
        self.async_write_ha_state()
        _LOGGER.debug("Sensor %s state written to HA", self._unique_id)

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "energy_meter")},
            "name": "Energy Meter",
            "manufacturer": "Unknown",
            "model": "LAN Energy Meter",
        }