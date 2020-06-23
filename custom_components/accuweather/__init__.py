"""The AccuWeather component."""
import asyncio
import logging
from datetime import timedelta

from accuweather import AccuWeather, ApiError, InvalidApiKeyError
from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
from homeassistant.const import CONF_API_KEY
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_FORECAST, COORDINATOR, DOMAIN, UNDO_UPDATE_LISTENER

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "weather"]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured AccuWeather."""
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    """Set up AccuWeather as config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    location_key = config_entry.unique_id
    forecast = config_entry.options.get(CONF_FORECAST, False)

    _LOGGER.debug("Using location_key: %s, get forecast: %s", location_key, forecast)

    websession = async_get_clientsession(hass)

    coordinator = AccuWeatherDataUpdateCoordinator(
        hass, websession, api_key, location_key, forecast
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = config_entry.add_update_listener(update_listener)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

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

async def update_listener(hass, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class AccuWeatherDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AccuWeather data API."""

    def __init__(self, hass, session, api_key, location_key, forecast: bool):
        """Initialize."""
        self.location_key = location_key
        self.forecast = forecast
        self.accuweather = AccuWeather(api_key, session, location_key=self.location_key)

        # forecast download increases the number of requests with one data update
        update_interval = timedelta(minutes=60) if self.forecast else timedelta(minutes=30)

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=update_interval
        )

    async def _async_update_data(self):
        """Update data via library."""
        forecast = {}
        try:
            with timeout(10):
                current = await self.accuweather.async_get_current_conditions()
                if self.forecast:
                    forecast = await self.accuweather.async_get_forecast()
        except (ApiError, ClientConnectorError, InvalidApiKeyError) as error:
            raise UpdateFailed(error)
        _LOGGER.debug("Requests remaining: %s", self.accuweather.requests_remaining)
        return {**current, **forecast}
