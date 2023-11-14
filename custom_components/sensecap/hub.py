import json
import asyncio
import logging
import paho.mqtt.client as mqtt
from homeassistant.helpers import service
from homeassistant.components import persistent_notification
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MEASUREMENT_DICT
)

_LOGGER = logging.getLogger(__name__)


def process_mqtt_payload(payload):
    if "deviceInfo" and "object" not in payload:
        return [],[]

    dev_eui = payload["deviceInfo"]["devEui"]

    if len(payload["object"]["messages"]) > 1:
        messages = payload["object"]["messages"]
        dev_messages = [messages]
    elif len(payload["object"]["messages"]) == 1:
        dev_messages = payload["object"]["messages"]
    else:
        dev_messages = []

    return dev_eui, dev_messages



def flatten_nested_list(data):
    result = []
    if isinstance(data, list):
        for item in data:
            result.extend(flatten_nested_list(item))
    else:
        result.append(data)
    return result

