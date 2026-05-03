from langchain.messages import AIMessageChunk
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command
from rich.console import Console

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
    agent, _checkpointer = create_agent()
    default_config: RunnableConfig = {
        'configurable': {
            'thread_id': 'default_thread',
        },
    }
    console = Console()
    initial_state = get_initial_state()
    current_state = initial_state.copy()

    while True:
        async for chunk in agent.astream(
            current_state,
            stream_mode=['messages', 'updates'],
            # TODO: Temporarily using a temporary thread
            config=default_config,
            version='v2',
        ):
            if chunk['type'] == 'messages':
                # Handle streaming message content
                msg, _ = chunk['data']
                if isinstance(msg, AIMessageChunk) and msg.content:
                    console.print(msg.content, style='blue', end='')

            elif chunk['type'] == 'updates':
                # Check for interrupts in the updates data
                if '__interrupt__' in chunk['data']:
                    interrupt_info = chunk['data']['__interrupt__'][0].value
                    user_prompt = input('\n' + interrupt_info['message'])
                    if interrupt_info['action'] == 'user_input':
                        current_state = Command(resume=user_prompt)
                    elif interrupt_info['action'] == 'builtin_tools':
                        # TODO: User input validation, or TUI options
                        # Temporary solution:
                        current_state = Command(resume=user_prompt)
                    break

        goto = agent.get_state(default_config).next
        if len(goto) == 0:
            console.print('See you again!', style='blue')
            break
