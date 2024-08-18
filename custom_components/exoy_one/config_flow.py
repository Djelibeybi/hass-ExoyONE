"""Adds config flow for ExoyOne."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING

import voluptuous as vol
from exoyone import ExoyOne, ExoyOneTimeoutError
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_IP_ADDRESS
from homeassistant.helpers import selector

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.components.zeroconf import ZeroconfServiceInfo
    from homeassistant.config_entries import ConfigFlowResult


class ExoyOneFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for ExoyONE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_device: ExoyOne | None = None

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle discovery using hostname and IP address."""
        hostname = str(discovery_info.hostname)
        ip_address: str = str(discovery_info.ip_address)
        return await self._async_handle_discovery(
            hostname=hostname, ip_address=ip_address
        )

    async def _async_handle_discovery(
        self,
        hostname: str,
        ip_address: str,
    ) -> ConfigFlowResult:
        """Handle any discovery-based config flow."""
        self._async_abort_entries_match({CONF_HOST: hostname})
        self.context[CONF_HOST] = hostname

        for progress in self._async_in_progress():
            if any(
                (progress.get("context", {}).get(CONF_HOST) == hostname),
            ):
                return self.async_abort(reason="already_in_progress")

        if not (device := await _async_try_connect(ip_address)):
            LOGGER.debug("Failed to connect to %s (%s)", hostname, ip_address)
            return self.async_abort(reason="cannot_connect")

        if device is not None:
            self._discovered_device: ExoyOne = device

        await self.async_set_unique_id(self._discovered_device.state.mdnsName)
        self._abort_if_unique_id_configured(updates={CONF_HOST: ip_address})

        return await self.async_step_discovery_confirm(
            {
                "hostname": hostname,
                "ip_address": ip_address,
            }
        )

    async def async_step_discovery_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle confirmation of discovered device."""
        if user_input is not None:
            mdns_name = self._discovered_device.state.mdnsName
            return self.async_create_entry(
                title=mdns_name,
                data={CONF_HOST: user_input[CONF_IP_ADDRESS]},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"host": mdns_name},
        )

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            hostname = ip_address = user_input[CONF_IP_ADDRESS]
            return await self._async_handle_discovery(
                hostname=hostname, ip_address=ip_address
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=(user_input or {}).get(CONF_IP_ADDRESS, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )


async def _async_try_connect(ip_address: str) -> ExoyOne | None:
    """Try to connect to the ExoyONE."""
    try:
        exoyone = ExoyOne(host=ip_address)
        await exoyone.async_get_data()
    except socket.gaierror:
        return None
    except ExoyOneTimeoutError as exception:
        raise data_entry_flow.AbortFlow(reason="cannot_connect") from exception
    return exoyone
