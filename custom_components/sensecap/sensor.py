import json
import concurrent.futures
import logging
import re
import asyncio

from homeassistant.components import mqtt
import paho.mqtt.client as mqtt
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import service
from homeassistant.components import persistent_notification

measurement_pair = {
    '4097':'Air Temperature','4098':'Air Humidity','4099':'Light Intensity','4100':'CO2'
    ,'4200':'Event Status','4197':'Longitude','4198':'Latitude','4199':'Light','3000':'Battery','5100':'Wi-Fi Scan'
}
DEFAULT_PORT = 1883

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

    mqtt_host = hass.data.setdefault(DOMAIN, {})["mqtt_host"]
    username = hass.data.setdefault(DOMAIN, {})["user_name"]
    password = hass.data.setdefault(DOMAIN, {})["user_passwd"]

    message_queue = asyncio.Queue()

    def message_received(client, userdata, msg):
        """处理接收到的 MQTT 消息."""
        message_queue.put_nowait(msg.payload.decode("utf-8"))

    client = mqtt.Client()
    if username and password:
        client.username_pw_set(username, password)
    client.on_message = message_received

    # 连接到 MQTT broker
    client.connect(mqtt_host, DEFAULT_PORT)
    client.subscribe(mqtt_topic)

    # 开始循环以接收消息
    client.loop_start()
    # # MQTT数据处理

    # 创建异步任务，持续监听消息队列
    async def message_consumer():
        while True:
            payload = await message_queue.get()
            try:
                payload = json.loads(payload)
                existing_entities = await get_sensor_entity_ids(hass)
                # 判断payload关键字
                if "deviceInfo" not in payload:
                    return
                # # 根据devEui来判断设备是否来自SenseCAP
                # if payload["deviceInfo"]["devEui"][:6] != "2cf7f1":
                #     return 

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
                num_of_brackets = count_nested_lists(dev_messages)
                _LOGGER.info(num_of_brackets)
                if num_of_brackets == 1:
                    dev_messages = [dev_messages]


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
                        sensor_type = str(int(float(dev_messages[0][i]["measurementId"])))
                        sensor_type = measurement_pair.get(sensor_type)
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
                    sensor_type = str(int(float(dev_messages[0][i]["measurementId"])))
                    sensor_type = measurement_pair.get(sensor_type)
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

            except Exception as e:
                _LOGGER.error("处理 MQTT 消息时出错：%s", str(e))
            finally:
                message_queue.task_done()

    def count_nested_lists(data):
        if isinstance(data, list):
            return sum(count_nested_lists(item) for item in data)
        else:
            return 1


    async def get_sensor_entity_ids(hass):
        sensor_entity_ids = hass.states.async_entity_ids("sensor")
        return sensor_entity_ids

    asyncio.create_task(message_consumer())
    # await hass.components.mqtt.async_subscribe(mqtt_topic, message_received)

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
            "model": "SenseCAP",
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
            "model": "SenseCAP",
            "manufacturer": "SenseCAP",
        }



