"""Binary sensor entities for PetTracer."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PetTracerCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PetTracer binary sensors."""
    coordinator: PetTracerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for dev_id, device_data in coordinator.data.items():
        entities.append(PetTracerBinarySensor(coordinator, dev_id, "home", "Home", BinarySensorDeviceClass.PRESENCE))
        entities.append(PetTracerBinarySensor(coordinator, dev_id, "led", "LED Status", None, "mdi:led-on"))
        entities.append(PetTracerBinarySensor(coordinator, dev_id, "buz", "Buzzer Status", None, "mdi:bell-ring"))
        entities.append(PetTracerBinarySensor(coordinator, dev_id, "chg", "Charging", BinarySensorDeviceClass.BATTERY_CHARGING))
    
    async_add_entities(entities)

class PetTracerBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a PetTracer binary sensor."""

    def __init__(
        self, 
        coordinator: PetTracerCoordinator, 
        dev_id: str, 
        key: str, 
        name_suffix: str, 
        device_class: BinarySensorDeviceClass | None = None,
        icon: str | None = None
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._dev_id = dev_id
        self._key = key
        self._name_suffix = name_suffix
        self._attr_device_class = device_class
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_{self._key}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} {self._name_suffix}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        data = self.coordinator.data.get(self._dev_id, {})
        val = data.get(self._key)
        
        if self._key == "chg":
            # chg is typically 0 or 1
            return bool(val)
        
        # For boolean fields (home, led, buz)
        return bool(val)
