from __future__ import annotations

from collections import OrderedDict
import logging
import re

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector
import voluptuous as vol

from .api_client import JablotronApiClient, JablotronApiError
from .const import (
    CONF_API_TOKEN,
    CONF_CONTROL_CODE,
    CONF_DEVICE_TYPE_OVERRIDES,
    CONF_PARTIALLY_ARMING_MODE,
    CONF_REQUIRE_CODE_TO_ARM,
    CONF_REQUIRE_CODE_TO_DISARM,
    CONF_SERVER_URL,
    CONF_TLS_CA_CERT,
    CONF_TLS_CLIENT_CERT,
    CONF_TLS_CLIENT_KEY,
    DEFAULT_CONF_REQUIRE_CODE_TO_ARM,
    DEFAULT_CONF_REQUIRE_CODE_TO_DISARM,
    DOMAIN,
    DeviceType,
    PartiallyArmingMode,
)

LOGGER = logging.getLogger(__name__)

PASSWORD_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
)
URL_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
)
PARTIAL_ARMING_SELECTOR = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[mode.value for mode in PartiallyArmingMode],
        mode=selector.SelectSelectorMode.DROPDOWN,
        translation_key="partially_arming_mode",
    )
)
AUTOMATIC_DEVICE_TYPE = "automatic"
DEVICE_OVERRIDE_LABEL_PATTERN = re.compile(r"^(\d+): ")
DEVICE_TYPE_OPTION_LABELS = {
    AUTOMATIC_DEVICE_TYPE: "Automatic",
    DeviceType.KEYPAD.value: "Keypad",
    DeviceType.KEYPAD_WITH_DOOR_OPENING_DETECTOR.value: "Keypad with door opening detector",
    DeviceType.SIREN_OUTDOOR.value: "Outdoor siren",
    DeviceType.SIREN_INDOOR.value: "Indoor siren",
    DeviceType.MOTION_DETECTOR.value: "Motion detector",
    DeviceType.WINDOW_OPENING_DETECTOR.value: "Window opening detector",
    DeviceType.DOOR_OPENING_DETECTOR.value: "Door opening detector",
    DeviceType.GARAGE_DOOR_OPENING_DETECTOR.value: "Garage door opening detector",
    DeviceType.GLASS_BREAK_DETECTOR.value: "Glass break detector",
    DeviceType.SMOKE_DETECTOR.value: "Smoke detector",
    DeviceType.FLOOD_DETECTOR.value: "Flood detector",
    DeviceType.GAS_DETECTOR.value: "Gas detector",
    DeviceType.THERMOSTAT.value: "Thermostat",
    DeviceType.THERMOMETER.value: "Thermometer",
    DeviceType.LOCK.value: "Lock",
    DeviceType.TAMPER.value: "Tamper",
    DeviceType.BUTTON.value: "Button",
    DeviceType.KEY_FOB.value: "Key fob",
    DeviceType.ELECTRICITY_METER_WITH_PULSE_OUTPUT.value: "Electricity meter with pulse output",
    DeviceType.RADIO_MODULE.value: "Radio module",
    DeviceType.VALVE.value: "Valve",
    DeviceType.CUSTOM.value: "Custom",
    DeviceType.OTHER.value: "Other",
    DeviceType.EMPTY.value: "Empty",
}


def _connection_schema(*, data: dict[str, str], show_secret_defaults: bool) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_SERVER_URL, default=data.get(CONF_SERVER_URL, "")): URL_SELECTOR,
            vol.Required(
                CONF_API_TOKEN,
                default=data.get(CONF_API_TOKEN, "") if show_secret_defaults else "",
            ): PASSWORD_SELECTOR,
            vol.Optional(
                CONF_CONTROL_CODE,
                default=data.get(CONF_CONTROL_CODE, "") if show_secret_defaults else "",
            ): PASSWORD_SELECTOR,
            vol.Optional(CONF_TLS_CA_CERT, default=data.get(CONF_TLS_CA_CERT, "")): str,
            vol.Optional(CONF_TLS_CLIENT_CERT, default=data.get(CONF_TLS_CLIENT_CERT, "")): str,
            vol.Optional(CONF_TLS_CLIENT_KEY, default=data.get(CONF_TLS_CLIENT_KEY, "")): str,
        }
    )


def _merge_connection_data(user_input: dict, existing: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(existing or {})
    merged[CONF_SERVER_URL] = user_input[CONF_SERVER_URL]
    for key in (CONF_TLS_CA_CERT, CONF_TLS_CLIENT_CERT, CONF_TLS_CLIENT_KEY):
        merged[key] = user_input.get(key) or ""
    for key in (CONF_API_TOKEN, CONF_CONTROL_CODE):
        value = user_input.get(key)
        if isinstance(value, str) and value.strip():
            merged[key] = value.strip()
        elif existing is None:
            merged[key] = ""
    return merged


class JablotronConfigFlow(ConfigFlow, domain=DOMAIN):
    _config_entry: ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "JablotronOptionsFlow":
        return JablotronOptionsFlow(config_entry)

    async def _validate_connection(self, merged: dict[str, str]) -> dict:
        client = JablotronApiClient(
            self.hass,
            server_url=merged[CONF_SERVER_URL],
            api_token=merged[CONF_API_TOKEN],
            ca_cert=merged.get(CONF_TLS_CA_CERT) or None,
            client_cert=merged.get(CONF_TLS_CLIENT_CERT) or None,
            client_key=merged.get(CONF_TLS_CLIENT_KEY) or None,
        )
        return await client.get("/v1/system")

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                merged = _merge_connection_data(user_input)
                system = await self._validate_connection(merged)
                unique_id = system.get("panel_unique_id") or merged[CONF_SERVER_URL]
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=system.get("panel_model") or "jablotron100-api-HASS",
                    data=merged,
                )
            except JablotronApiError as err:
                if err.status in {401, 403}:
                    errors["base"] = "invalid_auth"
                else:
                    LOGGER.warning("Jablotron API server request failed during config flow: %s", err)
                    errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Jablotron API server connection test failed during config flow")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=_connection_schema(data={}, show_secret_defaults=True),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict | None = None) -> ConfigFlowResult:
        self._config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reconfigure_settings(user_input)

    async def async_step_reconfigure_settings(self, user_input: dict | None = None) -> ConfigFlowResult:
        assert self._config_entry is not None
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                merged = _merge_connection_data(user_input, dict(self._config_entry.data))
                system = await self._validate_connection(merged)
                return self.async_update_reload_and_abort(
                    self._config_entry,
                    title=system.get("panel_model") or self._config_entry.title,
                    data_updates=merged,
                    reason="reconfigure_successful",
                )
            except JablotronApiError as err:
                if err.status in {401, 403}:
                    errors["base"] = "invalid_auth"
                else:
                    LOGGER.warning("Jablotron API server request failed during reconfigure flow: %s", err)
                    errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Jablotron API server connection test failed during reconfigure flow")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="reconfigure_settings",
            data_schema=_connection_schema(data=dict(self._config_entry.data), show_secret_defaults=False),
            errors=errors,
        )


class JablotronOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry
        self._options = dict(config_entry.options)

    def _base_options(self) -> dict:
        options = dict(self._options)
        options.pop(CONF_API_TOKEN, None)
        options.pop(CONF_CONTROL_CODE, None)
        return options

    def _current_api_token(self) -> str:
        return self._config_entry.data.get(CONF_API_TOKEN, self._options.get(CONF_API_TOKEN, ""))

    def _device_override_field_key(self, device: dict) -> str:
        device_id = int(device["id"])
        name = str(device.get("name") or f"Device {device_id}")
        inferred = str(device.get("inferred_device_type") or "unknown")
        return f"{device_id:03d}: {name} ({inferred})"

    async def _load_catalog_devices(self) -> list[dict]:
        try:
            client = JablotronApiClient(
                self.hass,
                server_url=self._config_entry.data[CONF_SERVER_URL],
                api_token=self._current_api_token(),
                ca_cert=self._config_entry.data.get(CONF_TLS_CA_CERT) or None,
                client_cert=self._config_entry.data.get(CONF_TLS_CLIENT_CERT) or None,
                client_key=self._config_entry.data.get(CONF_TLS_CLIENT_KEY) or None,
            )
            catalog = await client.get("/v1/export/catalog")
        except Exception as err:
            LOGGER.warning("Could not load catalog for device-type override options: %s", err)
            return []

        device_last_id = ((catalog.get("initial_setup") or {}).get("devices") or {}).get("last_id")
        devices: list[dict] = []
        for device in catalog.get("devices", []):
            try:
                device_id = int(device.get("id"))
            except (TypeError, ValueError):
                continue
            if device_last_id is not None and device_id > int(device_last_id):
                continue
            devices.append(device)
        return sorted(devices, key=lambda item: int(item["id"]))

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="init", menu_options=["options", "device_types"])

    async def async_step_options(self, user_input: dict | None = None) -> ConfigFlowResult:
        options = self._base_options()
        if user_input is not None:
            updated = dict(options)
            updated.update(user_input)
            return self.async_create_entry(title="", data=updated)

        fields = OrderedDict()
        fields[
            vol.Required(
                CONF_PARTIALLY_ARMING_MODE,
                default=options.get(CONF_PARTIALLY_ARMING_MODE, PartiallyArmingMode.NIGHT_MODE.value),
            )
        ] = PARTIAL_ARMING_SELECTOR
        fields[
            vol.Required(
                CONF_REQUIRE_CODE_TO_ARM,
                default=options.get(CONF_REQUIRE_CODE_TO_ARM, DEFAULT_CONF_REQUIRE_CODE_TO_ARM),
            )
        ] = bool
        fields[
            vol.Required(
                CONF_REQUIRE_CODE_TO_DISARM,
                default=options.get(CONF_REQUIRE_CODE_TO_DISARM, DEFAULT_CONF_REQUIRE_CODE_TO_DISARM),
            )
        ] = bool
        return self.async_show_form(step_id="options", data_schema=vol.Schema(fields))

    async def async_step_device_types(self, user_input: dict | None = None) -> ConfigFlowResult:
        devices = await self._load_catalog_devices()
        options = self._base_options()
        current_overrides = dict(options.get(CONF_DEVICE_TYPE_OVERRIDES, {}))
        if user_input is not None:
            updated = dict(options)
            overrides: dict[str, str] = {}
            for field_key, selected_type in user_input.items():
                match = DEVICE_OVERRIDE_LABEL_PATTERN.match(field_key)
                if match is None or selected_type == AUTOMATIC_DEVICE_TYPE:
                    continue
                overrides[match.group(1)] = selected_type
            if overrides:
                updated[CONF_DEVICE_TYPE_OVERRIDES] = overrides
            else:
                updated.pop(CONF_DEVICE_TYPE_OVERRIDES, None)
            return self.async_create_entry(title="", data=updated)

        fields = OrderedDict()
        for device in devices:
            field_key = self._device_override_field_key(device)
            fields[
                vol.Optional(
                    field_key,
                    default=current_overrides.get(str(device["id"]), AUTOMATIC_DEVICE_TYPE),
                )
            ] = vol.In(DEVICE_TYPE_OPTION_LABELS)
        return self.async_show_form(step_id="device_types", data_schema=vol.Schema(fields))
