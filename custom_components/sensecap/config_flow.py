# """Config flow for Hello World integration."""
# from __future__ import annotations

# import logging
# from typing import Any

# import voluptuous as vol

# from homeassistant import config_entries, exceptions
# from homeassistant.core import HomeAssistant

# from .const import (
#     DOMAIN,
#     CONF_COMMAND_TOPIC
# )

# _LOGGER = logging.getLogger(__name__)

# DATA_SCHEMA = vol.Schema({("command_topic"): str},
# )


# async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:

#     return {"title": data["command_topic"]}


# class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
#     VERSION = 1
#     topic: str

#     CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

#     async def async_step_user(self, user_input=None):
#         errors = {}
#         if user_input is not None:
#             try:
#                 self.topic = user_input[CONF_COMMAND_TOPIC]

#                 data={
#                 CONF_COMMAND_TOPIC: self.topic,
#                 }

#                 return self.async_create_entry(title=self.topic, data=data)
            
#             except Exception as e:
#                 # 处理异常，可以记录日志或者返回适当的错误信息给用户
#                 _LOGGER.error(f"An unexpected error occurred: {e}")
#                 errors["base"] = "unknown"

#         return self.async_show_form(
#             step_id="user",
#             data_schema=vol.Schema(
#                 {
#                     vol.Required(CONF_COMMAND_TOPIC, default="application/#"): str,
#                 }
#             ),
#             errors=errors or {},
#         )

"""Config flow for Hello World integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_COMMAND_TOPIC
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({("command_topic"): str},
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    return {"title": data["command_topic"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    topic: str  # 添加 topic 属性

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                self.topic = user_input[CONF_COMMAND_TOPIC]

                data={
                    CONF_COMMAND_TOPIC: self.topic,
                }

                return self.async_create_entry(title=self.topic, data=data)
            
            except Exception as e:
                # 处理异常，可以记录日志或者返回适当的错误信息给用户
                _LOGGER.error(f"An unexpected error occurred: {e}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COMMAND_TOPIC, default="application/#"): str,
                }
            ),
            errors=errors or {},
            description_placeholders={"command_topic": getattr(self, 'topic', "")},
        )
