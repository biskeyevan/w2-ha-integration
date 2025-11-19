"""Energy Meter integration for Home Assistant."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EnergyMeterApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Energy Meter from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_client = EnergyMeterApiClient(entry.data["host"])

    async def async_update_data():
        """Fetch data from API endpoint."""
        _LOGGER.debug("Starting data update from coordinator")
        try:
            data = await api_client.async_get_data()
            _LOGGER.debug("Successfully fetched data: %s", data)
            
            # Validate data structure
            if not isinstance(data, dict):
                raise UpdateFailed("API returned invalid data format (not a dictionary)")
            
            # Ensure channels and cts keys exist (can be empty lists)
            if "channels" not in data:
                _LOGGER.warning("API response missing 'channels' key, adding empty list")
                data["channels"] = []
            
            if "cts" not in data:
                _LOGGER.warning("API response missing 'cts' key, adding empty list")
                data["cts"] = []
            
            return data
        except UpdateFailed:
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch data from API: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="energy_meter",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api_client": api_client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Clean up the API client session
        api_client = hass.data[DOMAIN][entry.entry_id]["api_client"]
        await api_client.async_close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok