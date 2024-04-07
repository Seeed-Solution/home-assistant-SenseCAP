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

def process_chirpstack(payload):
    if "deviceInfo" and "object" not in payload:
        return [],[]

    eui = payload["deviceInfo"]["devEui"]
    msgs = payload["object"]["messages"]

    return eui, msgs

def process_ttn(payload):
    eui = payload["end_device_ids"]["dev_eui"]
    msgs = payload["uplink_message"]["decoded_payload"]["messages"]

    return eui, msgs




def process_mqtt_payload(payload):
    if "deviceInfo" and "object" in payload:
        dev_eui, raw_msgs = process_chirpstack(payload)
    elif "uplink_message" and "end_device_ids" in payload:
        dev_eui, raw_msgs = process_ttn(payload)
    else:
        return None, None

    if len(raw_msgs) > 1:
        messages = raw_msgs
        dev_messages = [messages]
    elif len(raw_msgs) == 1:
        dev_messages = raw_msgs
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

