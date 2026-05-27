from __future__ import annotations
from homeassistant.components.alarm_control_panel import (
	AlarmControlPanelEntity,
	AlarmControlPanelEntityFeature,
	AlarmControlPanelState,
	CodeFormat,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from . import JablotronConfigEntry
from .const import EntityType, PartiallyArmingMode
from .api_runtime import Jablotron, JablotronEntity, JablotronAlarmControlPanel
from .errors import ControlDenied
from .platform_setup import setup_entity_platform


async def async_setup_entry(hass: HomeAssistant, config_entry: JablotronConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
	setup_entity_platform(
		hass,
		config_entry,
		async_add_entities,
		(EntityType.ALARM_CONTROL_PANEL,),
		lambda jablotron, control, _entity_type: JablotronAlarmControlPanelEntity(jablotron, control),
	)


class JablotronAlarmControlPanelEntity(JablotronEntity, AlarmControlPanelEntity):
	_control: JablotronAlarmControlPanel
	_changed_by: str | None = None
	_code_required_for_disarm: bool = False
	_partially_arming_mode: PartiallyArmingMode

	_attr_name = None

	def __init__(
		self,
		jablotron: Jablotron,
		control: JablotronAlarmControlPanel,
	) -> None:
		super().__init__(jablotron, control)

	def _update_attributes(self) -> None:
		super()._update_attributes()

		self._partially_arming_mode = self._jablotron.partially_arming_mode()
		self._code_required_for_disarm = self._jablotron.is_code_required_for_disarm()
		self._attr_code_arm_required = self._jablotron.is_code_required_for_arm()
		self._attr_supported_features = self._detect_supported_features()
		self._attr_alarm_state = self._get_state()
		self._attr_changed_by = self._changed_by
		self._attr_code_format = self._detect_code_format()

	async def async_alarm_disarm(self, code: str | None = None) -> None:
		if self._get_state() == AlarmControlPanelState.DISARMED:
			return

		code = self._clean_code(code)
		code = self.code_or_default_code(code)

		if code is None and self._code_required_for_disarm:
			raise ControlDenied("Disarming requires a code.")

		await self._jablotron.async_modify_alarm_control_panel_section_state(
			self._control.section, AlarmControlPanelState.DISARMED, code
		)

	async def async_alarm_arm_away(self, code: str | None = None) -> None:
		await self._async_arm(AlarmControlPanelState.ARMED_AWAY, code, only_if_disarmed=True)

	async def async_alarm_arm_home(self, code: str | None = None) -> None:
		await self._async_arm(AlarmControlPanelState.ARMED_HOME, code, only_if_disarmed=False)

	async def async_alarm_arm_night(self, code: str | None = None) -> None:
		await self._async_arm(AlarmControlPanelState.ARMED_NIGHT, code, only_if_disarmed=False)

	def update_state(self, state: StateType) -> None:
		if self._get_state() != state:
			self._changed_by = self._jablotron.last_authorized_user_or_device()

		super().update_state(state)

	async def _async_arm(
		self,
		state: AlarmControlPanelState,
		code: str | None,
		*,
		only_if_disarmed: bool,
	) -> None:
		current = self._get_state()
		if current == state:
			return
		if not only_if_disarmed and current in (
			AlarmControlPanelState.ARMED_AWAY,
			AlarmControlPanelState.ARMED_HOME,
			AlarmControlPanelState.ARMED_NIGHT,
		):
			return

		code = self._clean_code(code)
		code = self.code_or_default_code(code)

		if code is None and self.code_arm_required:
			raise ControlDenied("Arming requires a code.")

		await self._jablotron.async_modify_alarm_control_panel_section_state(self._control.section, state, code)

	def _detect_supported_features(self) -> AlarmControlPanelEntityFeature:
		if self._partially_arming_mode == PartiallyArmingMode.NOT_SUPPORTED:
			return AlarmControlPanelEntityFeature.ARM_AWAY

		if self._partially_arming_mode == PartiallyArmingMode.HOME_MODE:
			return AlarmControlPanelEntityFeature.ARM_AWAY | AlarmControlPanelEntityFeature.ARM_HOME

		return AlarmControlPanelEntityFeature.ARM_AWAY | AlarmControlPanelEntityFeature.ARM_NIGHT

	def _detect_code_format(self) -> CodeFormat | None:
		if self._get_state() == AlarmControlPanelState.DISARMED:
			code_required = self._attr_code_arm_required
		else:
			code_required = self._code_required_for_disarm

		if not code_required:
			return None

		return CodeFormat.TEXT if self._jablotron.code_contains_asterisk() is True else CodeFormat.NUMBER

	@staticmethod
	def _clean_code(code: str | None) -> str | None:
		return None if code == "" else code
