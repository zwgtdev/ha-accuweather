"""The AccuWeather component."""
import asyncio
import logging

from accuweather import AccuWeather, ApiError, InvalidApiKeyError, RequestsExceededError
from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
from homeassistant.const import CONF_API_KEY
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "weather"]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured AccuWeather."""
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    """Set up AccuWeather as config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    location_key = config_entry.unique_id

    _LOGGER.debug("Using location_key: %s", location_key)

    websession = async_get_clientsession(hass)

    coordinator = AccuWeatherDataUpdateCoordinator(
        hass, websession, api_key, location_key
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


class AccuWeatherDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AccuWeather data API."""

    def __init__(self, hass, session, api_key, location_key):
        """Initialize."""
        self.location_key = location_key
        self.accuweather = AccuWeather(api_key, session, location_key=self.location_key)

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=DEFAULT_UPDATE_INTERVAL
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            with timeout(10):
                current = await self.accuweather.async_get_current_conditions()
        except (
            ApiError,
            ClientConnectorError,
            InvalidApiKeyError,
            RequestsExceededError,
        ) as error:
            raise UpdateFailed(error)
        return current
