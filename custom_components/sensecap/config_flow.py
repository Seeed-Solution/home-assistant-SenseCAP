from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_USERNAME,CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_COMMAND_TOPIC,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({("command_topic"): str},
)



class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    topic: str  # 添加 topic 属性

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH
    # data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                mqtt_topic = user_input[CONF_COMMAND_TOPIC]
                user_name = user_input.get(CONF_USERNAME)
                user_passwd = user_input.get(CONF_PASSWORD)

                data = {
                    CONF_COMMAND_TOPIC: mqtt_topic,
                    CONF_USERNAME: user_name,
                    CONF_PASSWORD: user_passwd,
                }

                return self.async_create_entry(title=mqtt_topic, data=data)

            except Exception as e:
                # 处理异常，可以记录日志或者返回适当的错误信息给用户
                _LOGGER.error(f"An unexpected error occurred: {e}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COMMAND_TOPIC, default="application/#"): str,
                    vol.Optional(CONF_USERNAME): str,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
            errors=errors or {},
        )
