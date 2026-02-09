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
    API_ENDPOINT_LOGIN,
    CONF_API_KEY,
    CONF_EMAIL,
    CONF_PASSWORD,
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
        # Support legacy API key or new email/password
        self.api_key = entry.data.get(CONF_API_KEY)
        self.email = entry.data.get(CONF_EMAIL)
        self.password = entry.data.get(CONF_PASSWORD)
        
        # If we have an API key, treat it as the access token initially
        self.access_token = self.api_key
        self.session = async_get_clientsession(hass)

    async def _ensure_token(self):
        """Ensure we have an access token."""
        if self.access_token:
            return

        if not self.email or not self.password:
            raise UpdateFailed("No credentials available for PetTracer")

        try:
            url = f"{API_BASE_URL}{API_ENDPOINT_LOGIN}"
            payload = {
                "login": self.email,
                "password": self.password,
            }
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                self.access_token = data.get("access_token")
                if not self.access_token:
                    raise UpdateFailed("Login successful but no access token found")
        except Exception as err:
            raise UpdateFailed(f"Login failed: {err}")

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        # Wrap the update logic to handle 401 retry
        try:
            return await self._fetch_data()
        except UpdateFailed as err:
            # If it looks like an auth error? 
            # Depending on how raise_for_status raises errors (ClientResponseError with status)
            # We can catch 401 specifically.
            if "401" in str(err):
                # Clear token and retry once
                self.access_token = None
                return await self._fetch_data()
            raise err
        except Exception as err:
             raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_data(self):
        """Internal fetch data logic."""
        await self._ensure_token()
        
        try:
            async with async_timeout.timeout(30):
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
                
                # Fetch list of collars
                url = f"{API_BASE_URL}{API_ENDPOINT_GET_CCS}"
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 401:
                        raise UpdateFailed("401 Unauthorized")
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
        # Try once
        try:
            await self._set_collar_mode_request(dev_id, mode_cmd)
        except Exception as err:
            if "401" in str(err):
                self.access_token = None
                await self._set_collar_mode_request(dev_id, mode_cmd)
            else:
                raise err
        
        # Trigger an immediate refresh/update
        await self.async_request_refresh()

    async def _set_collar_mode_request(self, dev_id: str, mode_cmd: int):
        await self._ensure_token()
        
        url = f"{API_BASE_URL}{API_ENDPOINT_SET_MODE}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "devType": 0,
            "devId": int(dev_id),
            "cmdNr": mode_cmd
        }
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 401:
                raise Exception("401 Unauthorized")
            response.raise_for_status()

    async def set_led(self, dev_id: str, turn_on: bool):
        """Set the collar LED state."""
        # 1 = On, 2 = Off
        state_cmd = 1 if turn_on else 2
        await self._set_led_request(dev_id, state_cmd)
        await self.async_request_refresh()

    async def _set_led_request(self, dev_id: str, state_cmd: int):
        await self._ensure_token()
        # /api/map/setccled/{collarId}/{1/0} - user specified 1/2 in request text
        url = f"{API_BASE_URL}/map/setccled/{dev_id}/{state_cmd}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        
        async with self.session.post(url, headers=headers) as response:
            if response.status == 401:
                self.access_token = None
                await self._ensure_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                async with self.session.post(url, headers=headers) as retry_resp:
                    retry_resp.raise_for_status()
            else:
                response.raise_for_status()

    async def set_buzzer(self, dev_id: str, turn_on: bool):
        """Set the collar buzzer state."""
        # 1 = On, 2 = Off
        state_cmd = 1 if turn_on else 2
        await self._set_buzzer_request(dev_id, state_cmd)
        await self.async_request_refresh()

    async def _set_buzzer_request(self, dev_id: str, state_cmd: int):
        await self._ensure_token()
        # /api/map/setccbuz/{collarId}/{1/0} - user specified 1/2 in request text
        url = f"{API_BASE_URL}/map/setccbuz/{dev_id}/{state_cmd}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        
        async with self.session.post(url, headers=headers) as response:
            if response.status == 401:
                self.access_token = None
                await self._ensure_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                async with self.session.post(url, headers=headers) as retry_resp:
                    retry_resp.raise_for_status()
            else:
                response.raise_for_status()
