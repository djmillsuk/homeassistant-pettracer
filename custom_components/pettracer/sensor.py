"""Sensor entities for PetTracer."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential
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
    """Set up PetTracer sensors."""
    coordinator: PetTracerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for dev_id, device_data in coordinator.data.items():
        entities.append(PetTracerBatterySensor(coordinator, dev_id))
        entities.append(PetTracerVoltageSensor(coordinator, dev_id))
    
    async_add_entities(entities)

class PetTracerBatterySensor(CoordinatorEntity, SensorEntity):
    """Representation of a PetTracer battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._dev_id = dev_id

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_battery"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} Battery"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self._dev_id, {})
        val = data.get("bat")
        if val is not None:
            try:
                mv = int(val)
                pct = int((mv - 3600) / 6)
                return max(0, min(100, pct))
            except (ValueError, TypeError):
                pass
        return None

class PetTracerVoltageSensor(CoordinatorEntity, SensorEntity):
    """Representation of a PetTracer battery voltage sensor."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._dev_id = dev_id

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_voltage"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} Voltage"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self._dev_id, {})
        return data.get("bat")
