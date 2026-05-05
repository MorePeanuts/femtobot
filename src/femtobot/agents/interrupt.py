from typing import TypedDict


class InterruptValue(TypedDict):
    node: str
    message: str
    choices: list[str]
