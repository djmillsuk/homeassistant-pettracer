"""Select entities for PetTracer."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_MAP, MODE_MAP_INV
from .coordinator import PetTracerCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PetTracer select entities."""
    coordinator: PetTracerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for dev_id, device_data in coordinator.data.items():
        entities.append(PetTracerModeSelect(coordinator, dev_id))
    
    async_add_entities(entities)

class PetTracerModeSelect(CoordinatorEntity, SelectEntity):
    """Representation of a PetTracer mode selector."""

    def __init__(self, coordinator: PetTracerCoordinator, dev_id: str) -> None:
        """Initialize the selector."""
        super().__init__(coordinator)
        self._dev_id = dev_id

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return f"{self._dev_id}_mode"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        details = self.coordinator.data.get(self._dev_id, {}).get("details", {})
        base_name = details.get("name") or f"Pet {self._dev_id}"
        return f"{base_name} Mode"

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return list(MODE_MAP.keys())

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        # Find the mode in the data
        data = self.coordinator.data.get(self._dev_id, {})
        # Assuming the API returns 'mode' as an integer matching the command number
        current_val = data.get("mode") or data.get("cmdNr")
        
        if current_val in MODE_MAP_INV:
            return MODE_MAP_INV[current_val]
        
        # Fallback if we can't find it or it's unknown
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        val = MODE_MAP.get(option)
        if val is not None:
            await self.coordinator.set_collar_mode(self._dev_id, val)

