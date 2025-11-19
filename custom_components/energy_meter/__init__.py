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
            return data
        except Exception as err:
            _LOGGER.error("Failed to fetch data from API: %s", err, exc_info=True)
            # Do not raise UpdateFailed to allow coordinator to continue
            return None

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="energy_meter",
        update_method=async_update_data,
        update_interval=timedelta(seconds=1),
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
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok