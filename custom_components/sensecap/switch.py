# import json
# import concurrent.futures
# import logging
# import re
# import asyncio

# from homeassistant.components import mqtt
# import paho.mqtt.client as mqtt
# from homeassistant.components.switch import SwitchEntity
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.helpers import service
# from homeassistant.components import persistent_notification
# from homeassistant.components.sensor import SensorDeviceClass

# from .hub import process_mqtt_payload, flatten_nested_list

# from homeassistant.const import (
#     DEVICE_CLASS_TEMPERATURE,
#     DEVICE_CLASS_HUMIDITY,
#     DEVICE_CLASS_ILLUMINANCE,
#     DEVICE_CLASS_CO2,
#     DEVICE_CLASS_BATTERY,
#     STATE_ON,
#     STATE_OFF
# )

# DEFAULT_PORT = 1883

# from .const import (
#     DOMAIN,
#     MEASUREMENT_DICT
# )

# _LOGGER = logging.getLogger(__name__)

# async def async_setup_entry(
#     hass: HomeAssistant,
#     config_entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback,
# ) -> None:
#     data = hass.data[DOMAIN][config_entry.entry_id]
#     mqtt_topic = data.get("command_topic")
#     mqtt_host = data.get("host")
#     username = data.get("username")
#     password = data.get("password")

#     entities = {}
#     devices_eui = []

#     message_queue = asyncio.Queue()

#     def message_received(client, userdata, msg):
#         """处理接收到的 MQTT 消息."""
#         message_queue.put_nowait(msg.payload.decode("utf-8"))

#     client = mqtt.Client()
#     if username and password:
#         client.username_pw_set(username, password)
#     client.on_message = message_received

#     # 连接到 MQTT broker
#     client.connect(mqtt_host, DEFAULT_PORT)
#     client.subscribe(mqtt_topic)

#     # 开始循环以接收消息
#     client.loop_start()
#     # # MQTT数据处理

#     # 创建异步任务，持续监听消息队列
#     async def message_consumer():
#         while True:
#             payload = await message_queue.get()
#             try:
#                 payload = json.loads(payload)
#                 existing_entities = await get_sensor_entity_ids(hass)
#                 # 判断payload关键字
#                 if "deviceInfo" not in payload:
#                     continue
#                 dev_eui, dev_messages = process_mqtt_payload(payload)
#
#                 dev_messages = flatten_nested_list(dev_messages)
#                 _LOGGER.info(len(dev_messages))
#                 _LOGGER.info((dev_messages))
#                 # # 检查设备是否存在
#                 if dev_eui not in devices_eui:
#                     _LOGGER.info(f"Creating new device with dev_eui: {dev_eui}")
#                     #发送通知
#                     persistent_notification.async_create(
#                         hass,
#                         f"New devices discovered！ \n" +
#                         f"Device EUI： {dev_eui} \n" + 
#                         f"[Check it out](/config/integrations/integration/sensecap)",
#                         "SenseCAP"
#                         )
#                     devices_eui.append(dev_eui)
#                     # 创建实体并状态赋值
#                     for i in range(len(dev_messages)):
#                         if("measurementId" not in dev_messages[i]):
#                             continue
#                         sensor_id = str(int(float(dev_messages[i]["measurementId"])))
#                         measurement_info = MEASUREMENT_DICT[sensor_id]
#                         sensor_type = measurement_info[0]
#                         sensor_unit = measurement_info[1]
#                         sensor_icon = measurement_info[2]
#                         if("measurementValue" not in dev_messages[i]):
#                             continue
#                         new_state = dev_messages[i]["measurementValue"]

#                         new_sensor = MySwitch(hass, dev_eui, sensor_id, sensor_type, sensor_unit, sensor_icon)
#                         new_sensor._state = new_state

#                         if dev_eui not in entities:
#                             entities[dev_eui] = {}

#                         # 将实体连同设备信息放入实体中，方便后续更新状态
#                         async_add_entities([new_sensor], update_before_add=True)
#                         entities[dev_eui][sensor_type] = new_sensor

#                 _LOGGER.info(f"entities:{entities}")
#                 _LOGGER.info(f"devices_eui:{devices_eui}")
#                 for i in range(len(dev_messages)):
#                     if("measurementId" not in dev_messages[i]):
#                         continue
#                     sensor_id = str(int(float(dev_messages[i]["measurementId"])))
#                     measurement_info = MEASUREMENT_DICT[sensor_id]
#                     sensor_type = measurement_info[0]
#                     if("measurementValue" not in dev_messages[i]):
#                         continue
#                     new_state = dev_messages[i]["measurementValue"]
                    
#                     for dev in entities:
#                         if dev == dev_eui:
#                             if sensor_type in entities[dev_eui]:
#                                 entity = entities[dev_eui][sensor_type]
#                                 if new_state > 50 :
#                                     entity._state = STATE_ON
#                                 else : 
#                                     entity._state = STATE_OFF
#                                 entity.async_schedule_update_ha_state()

#                 if hass.data[DOMAIN]["mqtt_client"] == 0:
#                     client.loop_stop()

#             except Exception as e:
#                 _LOGGER.error("处理 MQTT 消息时出错：%s", str(e))
#             finally:
#                 message_queue.task_done()

#     def flatten_nested_list(data):
#         result = []
#         if isinstance(data, list):
#             for item in data:
#                 result.extend(flatten_nested_list(item))
#         else:
#             result.append(data)
#         return result



#     async def get_sensor_entity_ids(hass):
#         sensor_entity_ids = hass.states.async_entity_ids("sensor")
#         return sensor_entity_ids

#     asyncio.create_task(message_consumer())

#     return True


# class MySwitch(SwitchEntity):
#     def __init__(self, hass, dev_eui, sensor_id, sensor_type, sensor_unit, sensor_icon):
#         """初始化传感器."""
#         super().__init__()
#         self.hass = hass
#         self.device = dev_eui
#         self._id = f"{self.device}_{sensor_type}"
#         self._name = f"{self.device}_{sensor_type}"
#         self._state = STATE_OFF

#         self.sensor_id =sensor_id
        
#     async def async_turn_off(self, **kwargs):
#         """Turn the entity off."""
#         self._state = STATE_OFF
#         self.async_write_ha_state()
    
#     async def async_turn_on(self, **kwargs):
#         """Turn the entity on."""
#         self._state = STATE_ON
#         self.async_write_ha_state()

#     @property
#     def unique_id(self):
#         """返回用于此传感器的唯一ID."""
#         return self._id

#     @property
#     def name(self):
#         """返回传感器的名称."""
#         return self._name

#     @property
#     def state(self):
#         """返回传感器的状态."""
#         return self._state
    

#     @property
#     def device_info(self):
#         """Information about this entity/device."""
#         return {
#             "identifiers": {(DOMAIN, self.device)},
#             "name": self.device,
#             "sw_version": "1.0",
#             "model": "SenseCAP",
#             "manufacturer": "SenseCAP",
#         }
