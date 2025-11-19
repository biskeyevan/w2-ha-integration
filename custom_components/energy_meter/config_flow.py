"""Config flow for Energy Meter integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .api import EnergyMeterApiClient
from .const import DOMAIN


class EnergyMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Meter."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the host
            api_client = EnergyMeterApiClient(user_input["host"])
            try:
                await api_client.async_get_data()
            except Exception:
                errors["host"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Energy Meter ({user_input['host']})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                }
            ),
            errors=errors,
        )