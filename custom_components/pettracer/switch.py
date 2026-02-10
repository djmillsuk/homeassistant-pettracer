"""Switches for controlling PetTracer collar LED and buzzer."""
from __future__ import annotations

import logging
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

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
        
        # Initialize state from coordinator data
        data = self.coordinator.data.get(self._dev_id, {})
        self._last_contact = data.get("lastContact")
        self._attr_is_on = data.get("led") is True
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_led"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        name = details.get("name") or f"Pet {self._dev_id}"
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._dev_id))},
            name=name,
            manufacturer="PetTracer",
            model="GPS Collar",
            sw_version=self.coordinator.data.get(self._dev_id, {}).get("sw"),
            configuration_url="https://portal.pettracer.com/",
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} LED"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        # Optimistic update
        self._attr_is_on = True
        self.async_write_ha_state()
        
        await self.coordinator.set_led(self._dev_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        # Optimistic update
        self._attr_is_on = False
        self.async_write_ha_state()
        
        await self.coordinator.set_led(self._dev_id, False)

    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        data = self.coordinator.data.get(self._dev_id, {})
        new_contact = data.get("lastContact")
        
        # Only update state if lastContact has changed
        if new_contact != self._last_contact:
            self._last_contact = new_contact
            self._attr_is_on = data.get("led") is True
            self.async_write_ha_state()


class PetTracerBuzzerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control the collar buzzer."""
    
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._dev_id = dev_id
        
        # Initialize state from coordinator data
        data = self.coordinator.data.get(self._dev_id, {})
        self._last_contact = data.get("lastContact")
        self._attr_is_on = data.get("buz") is True
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_buzzer"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        name = details.get("name") or f"Pet {self._dev_id}"
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._dev_id))},
            name=name,
            manufacturer="PetTracer",
            model="GPS Collar",
            sw_version=self.coordinator.data.get(self._dev_id, {}).get("sw"),
            configuration_url="https://portal.pettracer.com/",
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} Buzzer"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        # Optimistic update
        self._attr_is_on = True
        self.async_write_ha_state()

        await self.coordinator.set_buzzer(self._dev_id, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        # Optimistic update
        self._attr_is_on = False
        self.async_write_ha_state()

        await self.coordinator.set_buzzer(self._dev_id, False)

    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        data = self.coordinator.data.get(self._dev_id, {})
        new_contact = data.get("lastContact")
        
        # Only update state if lastContact has changed
        if new_contact != self._last_contact:
            self._last_contact = new_contact
            self._attr_is_on = data.get("buz") is True
            self.async_write_ha_state()
