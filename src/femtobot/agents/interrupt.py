from typing import TypedDict, NotRequired


class InterruptValue(TypedDict):
    node: str
    message: str
    choices: NotRequired[list[str]]
    command: NotRequired[str]
