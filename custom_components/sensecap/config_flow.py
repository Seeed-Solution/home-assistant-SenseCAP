# from copy import deepcopy
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN,CONF_USERNAME,CONF_PASSWORD,CONF_HOST,CONF_URL
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

import voluptuous as vol

from .const import CONF_COMMAND_TOPIC, DOMAIN

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COMMAND_TOPIC, default="application/#"): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string, 
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    topic: str  # 添加 topic 属性
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                mqtt_topic = user_input[CONF_COMMAND_TOPIC]
                mqtt_host = user_input[CONF_HOST]
                user_name = user_input.get(CONF_USERNAME)
                user_passwd = user_input.get(CONF_PASSWORD)

                data = {
                    CONF_COMMAND_TOPIC: mqtt_topic,
                    CONF_HOST: mqtt_host,
                    CONF_USERNAME: user_name,
                    CONF_PASSWORD: user_passwd,
                }

                return self.async_create_entry(title="SenseCAP", data=data)

            except Exception as e:
                # 处理异常，可以记录日志或者返回适当的错误信息给用户
                _LOGGER.error(f"An unexpected error occurred: {e}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=AUTH_SCHEMA,
            errors=errors or {},
<<<<<<< HEAD
        )
=======
        )
>>>>>>> 389cc92554972b6e46e93c86199f62e83fd5afa7
