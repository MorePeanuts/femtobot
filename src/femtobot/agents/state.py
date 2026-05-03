from femtobot.providers.chatmodel import get_default_model
import operator
from typing import Annotated, NotRequired, TypedDict

from langchain.messages import AnyMessage, SystemMessage

from femtobot.templates.agent import init_system_prompt


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    model_name: str
    user_last_prompt: NotRequired[str]
    model_last_response: NotRequired[str]


def get_initial_state() -> AgentState:
    system_prompt = init_system_prompt({})
    return {
        'messages': [SystemMessage(system_prompt)],
        'model_name': get_default_model(),
    }
