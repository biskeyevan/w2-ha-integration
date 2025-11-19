"""API client for Energy Meter."""
from __future__ import annotations

import asyncio
import aiohttp
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EnergyMeterApiClient:
    """API client for communicating with the energy meter."""

    def __init__(self, host: str) -> None:
        """Initialize the API client."""
        self.host = host
        self.endpoint = f"http://{host}/current-sample"
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))

    async def async_close(self) -> None:
        """Close the aiohttp session."""
        await self.session.close()

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        _LOGGER.debug("Making API request to: %s", self.endpoint)
        try:
            async with self.session.get(self.endpoint) as response:
                _LOGGER.debug("API responded with status: %s", response.status)
                if response.status != 200:
                    _LOGGER.error("Error fetching data: %s", response.status)
                    raise Exception(f"HTTP {response.status}")
                data = await response.json()
                _LOGGER.debug("API returned data with keys: %s", list(data.keys()) if isinstance(data, dict) else "non-dict")
                return data
        except Exception as err:
            _LOGGER.error("Exception in API request: %s", err, exc_info=True)
            raise