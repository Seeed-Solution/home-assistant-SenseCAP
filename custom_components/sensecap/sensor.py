import json
import concurrent.futures
import logging
import re

from homeassistant.components import mqtt
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import service
from homeassistant.components import persistent_notification

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    mqtt_topic = hass.data.setdefault(DOMAIN, {})["mqtt_topic"]
    entities = hass.data.setdefault(DOMAIN, {})["entities"]
    devices_eui = hass.data.setdefault(DOMAIN, {})["dev_eui"]

    # MQTT数据处理
    async def message_received(msg: mqtt.ReceiveMessage) -> None:
        existing_entities = await get_sensor_entity_ids(hass)
        payload = json.loads(msg.payload)
        # 判断payload关键字
        if "deviceInfo" not in payload:
            return
        # 根据devEui来判断设备是否来自SenseCAP
        if payload["deviceInfo"]["devEui"][:6] != "2cf7f1":
            return 

        dev_eui = payload["deviceInfo"]["devEui"]
        _LOGGER.info(len(payload["object"]["messages"]))

        if len(payload["object"]["messages"]) > 1:
            messages = payload["object"]["messages"]
            dev_messages = [messages]
        elif len(payload["object"]["messages"]) == 1:
            dev_messages = payload["object"]["messages"]
        else:
            dev_messages = []

        _LOGGER.info(dev_messages)

        # 检查设备是否存在
        if dev_eui not in devices_eui:
            _LOGGER.info(f"Creating new device with dev_eui: {dev_eui}")
            #发送通知
            persistent_notification.async_create(
                hass,
                f"New devices discovered！ \n" +
                f"Device EUI： {dev_eui} \n" + 
                f"[Check it out](/config/integrations/integration/sensecap)",
                "SenseCAP"
                )
            new_device = MyDevice(hass, dev_eui)
            devices_eui.append(dev_eui)
            # 创建实体并状态赋值
            for i in range(len(dev_messages[0])):
                sensor_type = dev_messages[0][i]["type"]
                if("measurementValue" not in dev_messages[0][i]):
                    pass
                new_state = dev_messages[0][i]["measurementValue"]

                new_sensor = MySensor(hass, new_device, sensor_type)
                new_sensor._state = new_state

                if dev_eui not in entities:
                    entities[dev_eui] = {}

                # 将实体连同设备信息放入实体中，方便后续更新状态
                async_add_entities([new_sensor])
                entities[dev_eui][sensor_type] = new_sensor

        _LOGGER.info(f"entities:{entities}")
        _LOGGER.info(f"devices_eui:{devices_eui}")
        for i in range(len(dev_messages[0])):
            sensor_type = dev_messages[0][i]["type"]
            if("measurementValue" not in dev_messages[0][i]):
                pass
            new_state = dev_messages[0][i]["measurementValue"]
            
            for dev_eui in devices_eui:
                if dev_eui not in entities:
                    devices_eui.remove(dev_eui)
                    pass

                if sensor_type in entities[dev_eui]:
                    entity = entities[dev_eui][sensor_type]
                    entity._state = new_state
                    entity.async_schedule_update_ha_state()



    async def get_sensor_entity_ids(hass):
        sensor_entity_ids = hass.states.async_entity_ids("sensor")
        return sensor_entity_ids


    await hass.components.mqtt.async_subscribe(mqtt_topic, message_received)

    return True


class MyDevice(Entity):
    def __init__(self, hass, dev_eui):
        """初始化设备."""
        super().__init__()
        self.hass = hass
        self._id = dev_eui
        self._name = f"{dev_eui}"
        self._state = {}

    @property
    def unique_id(self):
        """返回用于此设备的唯一ID."""
        return self._id

    @property
    def name(self):
        """返回设备的名称."""
        return self._name

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._name,
            "sw_version": "1.0",
            "model": "IAG Model",
            "manufacturer": "SenseCAP",
        }

class MySensor(Entity):
    _attr_icon = "mdi:devices"
    def __init__(self, hass, device, sensor_type):
        """初始化传感器."""
        super().__init__()
        self.hass = hass
        self.device = device
        self._id = f"{device._id}_{sensor_type}"
        self._name = f"{device._id}_{sensor_type}"
        self._state = None

    @property
    def unique_id(self):
        """返回用于此传感器的唯一ID."""
        return self._id

    @property
    def name(self):
        """返回传感器的名称."""
        return self._name

    @property
    def state(self):
        """返回传感器的状态."""
        return self._state
    
    async def async_update(self):
        pass

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self.device._id)},
            "name": self.device._name,
            "sw_version": "1.0",
            "model": "IAG Model",
            "manufacturer": "SenseCAP",
        }



