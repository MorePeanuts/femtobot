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


_chat_model_registry = {
    'deepseek-v4-flash': {
        'model': 'deepseek-v4-flash',
        'model_provider': 'deepseek',
        'extra_body': {'thinking': {'type': 'disabled'}},
    },
    'deepseek-v4-pro': {
        'model': 'deepseek-v4-pro',
        'model_provider': 'deepseek',
        'extra_body': {'thinking': {'type': 'disabled'}},
    },
}

_default_model = 'deepseek-v4-flash'


def get_model_config(model_name: str | None) -> dict:
    if model_name:
        return _chat_model_registry[model_name]
    return _chat_model_registry[_default_model]


def get_model_list() -> list[str]:
    return sorted(_chat_model_registry.keys())


def get_default_model() -> str:
    return _default_model
