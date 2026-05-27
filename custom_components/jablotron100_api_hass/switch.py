from __future__ import annotations
from homeassistant.components.switch import (
	SwitchDeviceClass,
	SwitchEntity,
)
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import JablotronConfigEntry
from .const import EntityType
from .api_runtime import Jablotron, JablotronProgrammableOutput, JablotronEntity
from .platform_setup import setup_entity_platform


async def async_setup_entry(hass: HomeAssistant, config_entry: JablotronConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
	setup_entity_platform(
		hass,
		config_entry,
		async_add_entities,
		(EntityType.PROGRAMMABLE_OUTPUT,),
		lambda jablotron, control, _entity_type: JablotronProgrammableOutputEntity(jablotron, control),
	)


class JablotronProgrammableOutputEntity(JablotronEntity, SwitchEntity):

	_control: JablotronProgrammableOutput

	_attr_device_class = SwitchDeviceClass.SWITCH
	_attr_name = None

	def __init__(
		self,
		jablotron: Jablotron,
		control: JablotronProgrammableOutput,
	) -> None:
		super().__init__(jablotron, control)
		self._attr_suggested_object_id = f"jablotron100_pg{self._control.pg_output_number}"

	def _update_attributes(self) -> None:
		super()._update_attributes()

		self._attr_is_on = self._get_state() == STATE_ON

	async def async_turn_on(self, **kwargs) -> None:
		await self._jablotron.async_toggle_pg_output(self._control.pg_output_number, STATE_ON)

	async def async_turn_off(self, **kwargs) -> None:
		await self._jablotron.async_toggle_pg_output(self._control.pg_output_number, STATE_OFF)
