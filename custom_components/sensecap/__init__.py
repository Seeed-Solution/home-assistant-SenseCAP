from __future__ import annotations

import json
from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    mqtt_topic = entry.data["command_topic"]
    host = entry.data["host"]
    user_name = entry.data["username"]
    user_passwd = entry.data["password"]


    hass.data.setdefault(DOMAIN, {})["mqtt_topic"] = mqtt_topic
    hass.data.setdefault(DOMAIN, {})["user_name"] = user_name
    hass.data.setdefault(DOMAIN, {})["user_passwd"] = user_passwd
    hass.data.setdefault(DOMAIN, {})["mqtt_host"] = host

    hass.data.setdefault(DOMAIN, {})["dev_eui"] = []
    hass.data.setdefault(DOMAIN, {})["entities"] = {}


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop("mqtt_topic", None)
        hass.data[DOMAIN].pop("user_name", None)
        hass.data[DOMAIN].pop("user_passwd", None)
        hass.data[DOMAIN].pop("mqtt_host", None)
        hass.data[DOMAIN].pop("dev_eui", None)
        hass.data[DOMAIN].pop("entities", None)

    return unload_ok

