"""Device tracker support for PetTracer."""
from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, API_BASE_URL, API_ENDPOINT_IMAGE
from .coordinator import PetTracerCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PetTracer device trackers."""
    coordinator: PetTracerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for dev_id, device_data in coordinator.data.items():
        entities.append(PetTracerTracker(coordinator, dev_id))
    
    async_add_entities(entities)

class PetTracerTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a PetTracer device."""

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator)
        self._dev_id = dev_id
        
    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_tracker"

    @property
    def check_details(self) -> dict:
        """Return the device data from coordinator."""
        return self.coordinator.data.get(self._dev_id, {})

    @property
    def name(self) -> str:
        """Return the name of the device."""
        details = self.check_details.get("details", {})
        return details.get("name") or f"Pet {self._dev_id}"

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        last_pos = self.check_details.get("lastPos", {})
        val = last_pos.get("posLat")
        return float(val) if val is not None else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        last_pos = self.check_details.get("lastPos", {})
        val = last_pos.get("posLong")
        return float(val) if val is not None else None

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        # 'bat' seems to be in mV (e.g., 4141).
        val = self.check_details.get("bat")
        if val is not None:
            try:
                mv = int(val)
                e = max(3000, min(mv, 4150))
                
                t = 0
                if e >= 4000:
                    t = (e - 4000) / 150 * 17 + 83
                elif e >= 3900:
                    t = (e - 3900) / 100 * 16 + 67
                elif e >= 3840:
                    t = (e - 3840) / 60 * 17 + 50
                elif e >= 3760:
                    t = (e - 3760) / 80 * 16 + 34
                elif e >= 3600:
                    t = (e - 3600) / 160 * 17 + 17
                else:
                    t = 0
                
                return round(t)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def source_type(self) -> str:
        """Return the source type."""
        return SourceType.GPS

    @property
    def entity_picture(self) -> str | None:
        """Return the entity picture to use in the frontend."""
        details = self.check_details.get("details", {})
        # API returns the image name
        image_name = details.get("image") or details.get("img")
        if image_name:
            return f"{API_BASE_URL}{API_ENDPOINT_IMAGE}{image_name}"
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return device specific attributes."""
        data = self.check_details
        last_pos = data.get("lastPos", {})
        
        attrs = {
            "battery_voltage": data.get("bat"),
            "battery_warn_level": data.get("accuWarn"),
            "last_contact": data.get("lastContact"),
            "led": data.get("led"),
            "buzzer": data.get("buz"),
            "home": data.get("home"),
            "safety_zone": data.get("safetyZone"),
            "software_version": data.get("sw"),
            "hardware_version": data.get("hw"),
            "mode": data.get("mode"),
            "gps_accuracy": last_pos.get("acc") or last_pos.get("horiPrec"),
            "satellites": last_pos.get("sat"),
        }
        return attrs
