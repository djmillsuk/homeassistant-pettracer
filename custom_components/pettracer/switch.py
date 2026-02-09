"""Switches for controlling PetTracer collar LED and buzzer."""
from __future__ import annotations

import logging
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PetTracerCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PetTracer switches."""
    coordinator: PetTracerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for dev_id in coordinator.data:
        entities.append(PetTracerLEDSwitch(coordinator, dev_id))
        entities.append(PetTracerBuzzerSwitch(coordinator, dev_id))
    
    async_add_entities(entities)

class PetTracerLEDSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control the collar LED."""
    
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._dev_id = dev_id
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_led"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} LED"

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        data = self.coordinator.data.get(self._dev_id, {})
        # Assuming 'led' matches the state in getccs
        return data.get("led") is True

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.set_led(self._dev_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.set_led(self._dev_id, False)


class PetTracerBuzzerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control the collar buzzer."""
    
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._dev_id = dev_id
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_buzzer"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} Buzzer"

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        data = self.coordinator.data.get(self._dev_id, {})
        # Assuming 'buz' matches the state in getccs
        return data.get("buz") is True

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.set_buzzer(self._dev_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.set_buzzer(self._dev_id, False)
