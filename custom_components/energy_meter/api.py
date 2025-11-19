"""API client for Energy Meter."""
from __future__ import annotations

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

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint) as response:
                if response.status != 200:
                    _LOGGER.error("Error fetching data: %s", response.status)
                    raise Exception(f"HTTP {response.status}")
                return await response.json()