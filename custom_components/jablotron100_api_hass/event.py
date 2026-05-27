from __future__ import annotations
from homeassistant.components.event import (
	EventEntity,
	EventEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from typing import Dict
from . import JablotronConfigEntry
from .const import (
	EntityType,
	EventLoginType,
)
from .api_runtime import Jablotron, JablotronControl, JablotronEntity
from .platform_setup import setup_entity_platform

EVENT_TYPES: Dict[EntityType, EventEntityDescription] = {
	EntityType.EVENT_LOGIN: EventEntityDescription(
		key=EntityType.EVENT_LOGIN,
		translation_key="login",
		icon="mdi:login",
		event_types=[EventLoginType.WRONG_CODE.value],
	),
}


async def async_setup_entry(hass: HomeAssistant, config_entry: JablotronConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
	setup_entity_platform(
		hass,
		config_entry,
		async_add_entities,
		EVENT_TYPES.keys(),
		lambda jablotron, control, entity_type: JablotronEventEntity(jablotron, control, EVENT_TYPES[entity_type]),
	)


class JablotronEventEntity(JablotronEntity, EventEntity):

	def __init__(
		self,
		jablotron: Jablotron,
		control: JablotronControl,
		description: EventEntityDescription,
	) -> None:
		self.entity_description = description

		super().__init__(jablotron, control)

	def trigger_event(self, event: EventLoginType) -> None:
		self._trigger_event(event.value)
		self.async_write_ha_state()
