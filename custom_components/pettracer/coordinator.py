"""DataUpdateCoordinator for PetTracer."""
from __future__ import annotations

import logging
from datetime import timedelta
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    UPDATE_INTERVAL_SECONDS,
    API_BASE_URL,
    API_ENDPOINT_GET_CCS,
    API_ENDPOINT_SET_MODE,
    CONF_API_KEY,
)

_LOGGER = logging.getLogger(__name__)

class PetTracerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching PetTracer data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(30):
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                # Fetch list of collars
                url = f"{API_BASE_URL}{API_ENDPOINT_GET_CCS}"
                async with self.session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Convert list to dict keyed by ID for easier access
                    results = {}
                    if isinstance(data, list):
                        for device in data:
                            dev_id = device.get("id")
                            if not dev_id:
                                continue
                            
                            dev_id = str(dev_id)
                            results[dev_id] = device
                    
                    return results

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def set_collar_mode(self, dev_id: str, mode_cmd: int):
        """Set the tracking mode for a collar."""
        url = f"{API_BASE_URL}{API_ENDPOINT_SET_MODE}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "devType": 0,
            "devId": int(dev_id),
            "cmdNr": mode_cmd
        }
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            # Trigger an immediate refresh/update
            await self.async_request_refresh()
