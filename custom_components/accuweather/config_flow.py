"""Adds config flow for AccuWeather."""
import asyncio

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from accuweather import AccuWeather, ApiError, InvalidApiKeyError
from aiohttp import ClientError
from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN  # pylint:disable=unused-import


class AccuWeatherFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for AccuWeather."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Optional(
                    CONF_LATITUDE, default=self.hass.config.latitude
                ): cv.latitude,
                vol.Optional(
                    CONF_LONGITUDE, default=self.hass.config.longitude
                ): cv.longitude,
                vol.Optional(CONF_NAME, default=self.hass.config.location_name): str,
            }
        )

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            websession = async_get_clientsession(self.hass)
            try:
                with timeout(10):
                    accuweather = AccuWeather(
                        user_input[CONF_API_KEY],
                        websession,
                        latitude=user_input[CONF_LATITUDE],
                        longitude=user_input[CONF_LONGITUDE],
                    )
                    await accuweather.async_get_location()
            except (ApiError, ClientConnectorError, asyncio.TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except InvalidApiKeyError:
                errors[CONF_API_KEY] = "invalid_api_key"
            else:
                await self.async_set_unique_id(
                    accuweather.location_key, raise_on_progress=False
                )

                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
