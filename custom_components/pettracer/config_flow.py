"""Config flow for PetTracer."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, API_BASE_URL, API_ENDPOINT_LOGIN
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PetTracer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                # Validate credentials by attempting login
                url = f"{API_BASE_URL}{API_ENDPOINT_LOGIN}"
                payload = {
                    "login": user_input[CONF_EMAIL],
                    "password": user_input[CONF_PASSWORD],
                }
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # We don't need to store the token here, the coordinator will get a fresh one.
                        # We just need to know it works.
                        if "access_token" in data:
                             return self.async_create_entry(title=user_input[CONF_EMAIL], data=user_input)
                        else:
                             errors["base"] = "invalid_auth"
                    else:
                        errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL
                        )
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                }
            ),
            errors=errors,
        )
