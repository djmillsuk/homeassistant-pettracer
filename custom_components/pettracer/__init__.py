"""The PetTracer integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PetTracerCoordinator

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER, Platform.SENSOR, Platform.SELECT, Platform.BINARY_SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PetTracer from a config entry."""
    _LOGGER.info("Setting up PetTracer integration for entry: %s", entry.entry_id)
    coordinator = PetTracerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Start WebSocket connection - after platforms to ensure listeners might be ready if needed, 
    # but more importantly after first refresh so we have device IDs.
    _LOGGER.debug("Starting PetTracer WebSocket...")
    await coordinator.start_websocket()

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        # Ensure we stop the websocket connection
        await coordinator.stop_websocket()

    return unload_ok
