from typing import Literal

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command, interrupt

from femtobot.agents.commands import check_command
from femtobot.agents.interrupt import InterruptValue
from femtobot.agents.state import AgentState
from femtobot.providers.chatmodel import get_model_config, get_model_list
from femtobot.tools.builtin import get_builtin_tool, get_builtin_tool_list

_chat_model = None


def user_input(
    state: AgentState,
) -> Command[Literal['chat_model_call', 'command_parse']]:
    user_prompt: str = interrupt(
        {
            'node': 'user_input',
            'message': 'User',
        }
    )
    if check_command(user_prompt):
        return Command(
            update={
                'user_last_prompt': user_prompt,
            },
            goto='command_parse',
        )
    else:
        # TODO: User data security verification
        return Command(
            update={
                'messages': [HumanMessage(user_prompt)],
                'user_last_prompt': user_prompt,
            },
            goto='chat_model_call',
        )


async def chat_model_call(
    state: AgentState,
) -> Command[Literal['builtin_tools', 'user_input']]:
    global _chat_model
    if _chat_model is None:
        _chat_model = init_chat_model(**get_model_config(state['model_name']))
        assert isinstance(_chat_model, BaseChatModel)
        _chat_model = _chat_model.bind_tools(get_builtin_tool_list())

    ai_msg = await _chat_model.ainvoke(state['messages'])

    if hasattr(ai_msg, 'tool_calls') and len(ai_msg.tool_calls) > 0:
        goto = 'builtin_tools'
    else:
        goto = 'user_input'

    return Command(
        update={
            'messages': [ai_msg],
            'model_last_response': ai_msg.content,
        },
        goto=goto,
    )


def command_parse(
    state: AgentState,
) -> Command[Literal['user_input', '__end__']]:
    if state['user_last_prompt'] == '/exit':
        return Command(goto='__end__')
    elif state['user_last_prompt'] == '/model':
        user_response = interrupt(
            {
                'node': 'command_parse',
                'message': f'Choose a model: (current model is {state["model_name"]})',
                'choices': get_model_list(),
                'command': '/model',
            }
        )
        if user_response != '<|remain|>':
            _chat_model = init_chat_model(**get_model_config(user_response))
            return Command(update={'model_name': user_response}, goto='user_input')
        else:
            return Command(goto='user_input')
    elif state['user_last_prompt'] == '/usage':
        # TODO: get model usage
        return Command(update={'static_message': 'todo!'}, goto='user_input')
    # TODO: More command parsing
    else:
        # TODO: If the command parsing fails, an error message
        # must be output and fall back to the user input.
        return Command(goto='user_input')


async def builtin_tools(
    state: AgentState,
) -> Command[Literal['chat_model_call']]:
    ai_msg = state['messages'][-1]
    assert isinstance(ai_msg, AIMessage), (
        'The last message entering the tool call node does not come from AI.'
    )
    tool_msgs = []
    for tool_call in ai_msg.tool_calls:
        user_response = interrupt(
            {
                'node': 'builtin_tools',
                'message': (
                    f'ChatBot wants to use builtin tool {tool_call["name"]}.\n'
                    f'Args:\n\t{tool_call["args"]}\n'
                    'Do you allow this operation?'
                ),
                'choices': ['Allow', 'Reject', 'Always (TODO)', 'Reject with reason (TODO)'],
            }
        )
        if user_response == 'Allow':
            tool_msg = await get_builtin_tool(tool_call['name']).ainvoke(tool_call)
            tool_msgs.append(tool_msg)
        elif user_response == 'Reject':
            tool_msgs.append(
                ToolMessage(
                    content='The tool call was rejected by the user.',
                    tool_call_id=tool_call['id'],
                )
            )
        else:
            raise NotImplementedError
    return Command(update={'messages': tool_msgs}, goto='chat_model_call')
