# This file contains the model registry for the application.

from enum import Enum


class ChatModelRegistry(Enum):
    DEEPSEEK_V4_FLASH = {
        'model': 'deepseek-v4-flash',
        'model_provider': 'deepseek',
        'extra_body': {'thinking': {'type': 'disabled'}},
    }
    DEEPSEEK_V4_FLASH_THINKING = {
        'model': 'deepseek-v4-flash',
        'model_provider': 'deepseek',
        'reasoning_effort': 'high',
        'extra_body': {'thinking': {'type': 'enabled'}},
    }
    DEEPSEEK_V4_PRO = {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'extra_body': {'thinking': {'type': 'disabled'}},
    }
    DEEPSEEK_V4_PRO_THINKING = {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'reasoning_effort': 'high',
        'extra_body': {'thinking': {'type': 'enabled'}},
    }
    DEEPSEEK_V4_PRO_MAX = {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'reasoning_effort': 'max',
        'extra_body': {'thinking': {'type': 'enabled'}},
    }

    def __iter__(self):
        return iter(self.value.items())

    def keys(self):
        return self.value.keys()

    def __getitem__(self, key):
        return self.value[key]


_default_model = 'DEEPSEEK_V4_FLASH'
_chat_model_map = {}
for _model in ChatModelRegistry:
    _chat_model_map[_model.name] = _model.value


def get_model_config(model_name: str):
    return _chat_model_map[model_name]


def get_default_model() -> str:
    return _default_model
