from femtobot.agents.commands import _builtin_commands
from femtobot.agents.interrupt import InterruptValue
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
    command_list = agent.get_command_list()

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
        goto, interrupt_info = agent.handle_interrupt()
        match goto:
            case 'chat_input':
                console.print(
                    f'Available Tools:\n\t{command_list}',
                    style='red',
                )
                user_in = Prompt.ask(interrupt_info['message'])
            case 'tool_check':
                user_in = Prompt.ask(
                    interrupt_info['message'],
                    choices=interrupt_info['choices'],
                )
        agent.resume_state(user_in)


@dataclass
class AgentOutput:
    tp: Literal['token', 'interrupt', 'exit']
    content: str | dict


class FemtobotAgent:
    def __init__(self):
        self.state = get_initial_state()
        self.interrupts = tuple()
        self.running = False
        self.config: RunnableConfig = {
            'configurable': {
                'thread_id': 'default_thread',
            },
        }
        self._create_agent()

    def handle_interrupt(self):
        for interrupt in self.interrupts:
            interrupt_info = interrupt.value
            match interrupt_info['node']:
                case 'user_input':
                    return 'chat_input', interrupt_info
                case 'builtin_tools':
                    return 'tool_check', interrupt_info
                case 'command_parse':
                    raise NotImplementedError

    def resume_state(self, user_in):
        self.state = Command(resume=user_in)

    def get_command_list(self) -> list[str]:
        return list(_builtin_commands)

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
        snapshot = self.agent.get_state(self.config)
        self.state = snapshot.values
        self.interrupts = snapshot.interrupts
        if len(snapshot.next) == 0:
            yield AgentOutput('exit', 'See you again!\n')
        else:
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
