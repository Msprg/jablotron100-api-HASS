"""Constants for the API-backed Jablotron 100 integration."""

import logging
from enum import Enum, StrEnum
from typing import Final

LOGGER: Final = logging.getLogger(__package__)

DOMAIN: Final = "jablotron100_api_hass"
NAME: Final = "jablotron100-api-HASS"

EVENT_WRONG_CODE: Final = "{}_wrong_code".format(DOMAIN)

CONF_SERVER_URL: Final = "server_url"
CONF_API_TOKEN: Final = "api_token"
CONF_TLS_CA_CERT: Final = "tls_ca_cert"
CONF_TLS_CLIENT_CERT: Final = "tls_client_cert"
CONF_TLS_CLIENT_KEY: Final = "tls_client_key"
CONF_CONTROL_CODE: Final = "control_code"
CONF_DEVICE_TYPE_OVERRIDES: Final = "device_type_overrides"
CONF_REQUIRE_CODE_TO_ARM: Final = "require_code_to_arm"
CONF_REQUIRE_CODE_TO_DISARM: Final = "require_code_to_disarm"
CONF_PARTIALLY_ARMING_MODE: Final = "partially_arming_mode"

DEFAULT_CONF_REQUIRE_CODE_TO_ARM: Final = False
DEFAULT_CONF_REQUIRE_CODE_TO_DISARM: Final = True


class DeviceType(StrEnum):
    CENTRAL_UNIT = "central_unit"
    KEYPAD = "keypad"
    KEYPAD_WITH_DOOR_OPENING_DETECTOR = "keypad_with_door_opening_detector"
    SIREN_OUTDOOR = "outdoor_siren"
    SIREN_INDOOR = "indoor_siren"
    MOTION_DETECTOR = "motion_detector"
    WINDOW_OPENING_DETECTOR = "window_opening_detector"
    DOOR_OPENING_DETECTOR = "door_opening_detector"
    GARAGE_DOOR_OPENING_DETECTOR = "garage_door_opening_detector"
    GLASS_BREAK_DETECTOR = "glass_break_detector"
    SMOKE_DETECTOR = "smoke_detector"
    FLOOD_DETECTOR = "flood_detector"
    GAS_DETECTOR = "gas_detector"
    THERMOSTAT = "thermostat"
    THERMOMETER = "thermometer"
    LOCK = "lock"
    TAMPER = "tamper"
    BUTTON = "button"
    KEY_FOB = "key_fob"
    ELECTRICITY_METER_WITH_PULSE_OUTPUT = "electricity_meter_with_pulse_output"
    RADIO_MODULE = "radio_module"
    VALVE = "valve"
    CUSTOM = "custom"
    OTHER = "other"
    EMPTY = "empty"

    def get_name(self) -> str:
        name = self._value_.replace("_", " ")
        return name[0:1].upper() + name[1:]


class EntityType(StrEnum):
    ALARM_CONTROL_PANEL = "alarm_control_panel"
    BATTERY_LEVEL = "battery_level"
    BATTERY_PROBLEM = "battery_problem"
    BATTERY_LOAD_VOLTAGE = "battery_load_voltage"
    BATTERY_STANDBY_VOLTAGE = "battery_standby_voltage"
    BUS_DEVICES_CURRENT = "bus_devices_current"
    BUS_VOLTAGE = "bus_voltage"
    DEVICE_STATE_MOTION = "device_state_motion"
    DEVICE_STATE_WINDOW = "device_state_window"
    DEVICE_STATE_DOOR = "device_state_door"
    DEVICE_STATE_GARAGE_DOOR = "device_state_garage_door"
    DEVICE_STATE_GLASS = "device_state_glass"
    DEVICE_STATE_MOISTURE = "device_state_moisture"
    DEVICE_STATE_GAS = "device_state_gas"
    DEVICE_STATE_SMOKE = "device_state_smoke"
    DEVICE_STATE_LOCK = "device_state_lock"
    DEVICE_STATE_TAMPER = "device_state_tamper"
    DEVICE_STATE_THERMOSTAT = "device_state_thermostat"
    DEVICE_STATE_THERMOMETER = "device_state_thermometer"
    DEVICE_STATE_INDOOR_SIREN_BUTTON = "device_state_indoor_siren_button"
    DEVICE_STATE_BUTTON = "device_state_button"
    DEVICE_STATE_VALVE = "device_state_valve"
    DEVICE_STATE_CUSTOM = "device_state_custom"
    EVENT_LOGIN = "event_login"
    FIRE = "fire"
    GSM_SIGNAL = "gsm_signal"
    GSM_SIGNAL_STRENGTH = "gsm_signal_strength"
    LAN_CONNECTION = "lan_connection"
    LAN_IP = "lan_ip"
    # The string value below is a historical typo kept deliberately:
    # it is part of installed entities' identity and changing it would
    # break existing user installations.
    POWER_SUPPLY = "power_supple"
    PROBLEM = "problem"
    PULSES = "pulses"
    PROGRAMMABLE_OUTPUT = "programmable_output"
    SIGNAL_STRENGTH = "signal_strength"
    TEMPERATURE = "temperature"


DEVICE_TYPE_TO_ENTITY_TYPE: Final = {
    DeviceType.MOTION_DETECTOR: EntityType.DEVICE_STATE_MOTION,
    DeviceType.WINDOW_OPENING_DETECTOR: EntityType.DEVICE_STATE_WINDOW,
    DeviceType.DOOR_OPENING_DETECTOR: EntityType.DEVICE_STATE_DOOR,
    DeviceType.KEYPAD_WITH_DOOR_OPENING_DETECTOR: EntityType.DEVICE_STATE_DOOR,
    DeviceType.GARAGE_DOOR_OPENING_DETECTOR: EntityType.DEVICE_STATE_GARAGE_DOOR,
    DeviceType.GLASS_BREAK_DETECTOR: EntityType.DEVICE_STATE_GLASS,
    DeviceType.FLOOD_DETECTOR: EntityType.DEVICE_STATE_MOISTURE,
    DeviceType.GAS_DETECTOR: EntityType.DEVICE_STATE_GAS,
    DeviceType.SMOKE_DETECTOR: EntityType.DEVICE_STATE_SMOKE,
    DeviceType.LOCK: EntityType.DEVICE_STATE_LOCK,
    DeviceType.TAMPER: EntityType.DEVICE_STATE_TAMPER,
    DeviceType.THERMOSTAT: EntityType.DEVICE_STATE_THERMOSTAT,
    DeviceType.THERMOMETER: EntityType.DEVICE_STATE_THERMOMETER,
    DeviceType.SIREN_INDOOR: EntityType.DEVICE_STATE_INDOOR_SIREN_BUTTON,
    DeviceType.BUTTON: EntityType.DEVICE_STATE_BUTTON,
    DeviceType.KEY_FOB: EntityType.DEVICE_STATE_BUTTON,
    DeviceType.VALVE: EntityType.DEVICE_STATE_VALVE,
    DeviceType.CUSTOM: EntityType.DEVICE_STATE_CUSTOM,
}


class EventLoginType(StrEnum):
    WRONG_CODE = "wrong_code"


class PartiallyArmingMode(StrEnum):
    NOT_SUPPORTED = "not_supported"
    NIGHT_MODE = "night_mode"
    HOME_MODE = "home_mode"
