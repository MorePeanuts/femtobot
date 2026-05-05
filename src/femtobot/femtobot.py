from femtobot.agents.commands import _builtin_commands
from femtobot.agents.interrupt import InterruptValue
from femtobot.providers.chatmodel import get_model_list as _get_model_list
from typing import Literal
from dataclasses import dataclass
from langchain.messages import AIMessageChunk
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command
from rich.console import Console
from rich.prompt import Prompt
from loguru import logger

from femtobot.agents.nodes import builtin_tools, chat_model_call, command_parse, user_input
from femtobot.agents.state import AgentState, get_initial_state


def create_agent():
    checkpointer = InMemorySaver()
    agent = (
        StateGraph(AgentState)  # type: ignore
        .add_node(user_input)
        .add_node(chat_model_call)
        .add_node(command_parse)
        .add_node(builtin_tools)
        .add_edge(START, 'user_input')
        .compile(checkpointer=checkpointer)
    )
    return agent, checkpointer


async def agent_loop():
    agent = FemtobotAgent()
    console = Console()
    command_list = list(agent.get_commands().keys())

    while True:
        async for output in agent.stream_response():
            if output.tp == 'token':
                console.print(output.content, style='blue', end='')
            elif output.tp == 'interrupt':
                break
            elif output.tp == 'exit':
                console.print(output.content, style='blue', end='')
                exit(0)
        console.print()
        interrupt = agent.handle_interrupt()
        match interrupt.goto:
            case 'chat_input':
                console.print(
                    f'Available Tools:\n\t{command_list}',
                    style='red',
                )
                user_in = Prompt.ask(interrupt.info['message'])
            case 'tool_check':
                user_in = Prompt.ask(
                    interrupt.info['message'],
                    choices=interrupt.info['choices'],
                )
        agent.resume_state(user_in)


@dataclass
class AgentOutput:
    tp: Literal['token', 'interrupt', 'message', 'exit']
    content: str | dict


@dataclass
class AgentInterrupt:
    goto: Literal['chat_input', 'tool_check', 'command_panel']
    info: InterruptValue


class FemtobotAgent:
    def __init__(self):
        self.running = False
        self.config: RunnableConfig = {
            'configurable': {
                'thread_id': 'default_thread',
            },
        }
        self._create_agent()
        self.state = self.agent.invoke(get_initial_state(), self.config)
        self.interrupts = self.state['__interrupt__']

    def handle_interrupt(self):
        for interrupt in self.interrupts:
            interrupt_info = interrupt.value
            match interrupt_info['node']:
                case 'user_input':
                    return AgentInterrupt('chat_input', interrupt_info)
                case 'builtin_tools':
                    return AgentInterrupt('tool_check', interrupt_info)
                case 'command_parse':
                    return AgentInterrupt('command_panel', interrupt_info)

    def resume_state(self, user_in):
        self.state = Command(resume=user_in)

    def get_commands(self) -> dict[str, str]:
        return _builtin_commands

    def get_model_list(self) -> list[str]:
        return _get_model_list()

    async def stream_response(self):
        async for chunk in self.agent.astream(
            self.state,
            stream_mode=['messages', 'updates'],
            config=self.config,
            version='v2',
        ):
            if chunk['type'] == 'messages':
                # Handle streaming message content
                msg, _ = chunk['data']
                if isinstance(msg, AIMessageChunk) and msg.content:
                    yield AgentOutput('token', msg.content)
            elif chunk['type'] == 'updates':
                for _, state in chunk['data'].items():
                    if state and 'static_message' in state:
                        yield AgentOutput('message', state['static_message'])
        snapshot = self.agent.get_state(self.config)
        self.state = snapshot.values
        self.interrupts = snapshot.interrupts
        if len(snapshot.next) == 0:
            yield AgentOutput('exit', 'See you again!\n')
        if len(self.interrupts) > 0:
            yield AgentOutput('interrupt', self.interrupts[0].value)

    def _create_agent(self):
        self.checkpointer = InMemorySaver()
        self.agent = (
            StateGraph(AgentState)  # type: ignore
            .add_node(user_input)
            .add_node(chat_model_call)
            .add_node(command_parse)
            .add_node(builtin_tools)
            .add_edge(START, 'user_input')
            .compile(checkpointer=self.checkpointer)
        )
