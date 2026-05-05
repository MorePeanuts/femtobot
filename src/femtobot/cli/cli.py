from rich.markdown import Markdown
from textual.message import Message
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Annotated

from loguru import logger
from rich.console import Console
from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.events import Key
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option as TOption
from typer import Argument, Option, Typer

from femtobot.femtobot import FemtobotAgent, agent_loop

app = Typer(
    name='FemtoBot',
    help='An LLM-driven agent built using the LangChain ecosystem, inspired by OpenClaw.',
)
console = Console()
_root_path = Path(__file__).parents[3]


class ChatInput(Input):
    """Custom chat input box"""

    def on_key(self, event: Key) -> None:
        if event.key == 'tab':
            # Get the completion list
            cmd_list = self.app.query_one('#cmd_list', OptionList)

            # If the completion menu is displayed and contains candidate commands
            if cmd_list.display and cmd_list.option_count > 0:
                # Get the first item and complete it
                first_cmd_id = cmd_list.get_option_at_index(0).id
                self.value = f'{first_cmd_id}'

                # Move the cursor to the end of the input box.
                self.cursor_position = len(self.value)

                # Prevent the event from continuing to propagate and thus
                # triggering a focus switch.
                event.prevent_default()
                event.stop()


class ChatMessage(Static):
    """Single Chat Message Component"""

    def __init__(self, title, text='', **kwargs):
        super().__init__(**kwargs)
        self._raw_content = text
        self.border_title = title

    def on_mount(self) -> None:
        self.update(Markdown(self._raw_content))

    def append_text(self, text) -> None:
        self._raw_content += text
        self.update(Markdown(self._raw_content))

    def set_text(self, text) -> None:
        self._raw_content = text
        self.update(Markdown(self._raw_content))


class VimVerticalScroll(VerticalScroll):
    """VerticalScroll with vim key bindings."""

    BINDINGS = [
        ('j', 'scroll_down', 'Scroll down'),
        ('k', 'scroll_up', 'Scroll up'),
        ('ctrl+d', 'scroll_half_page_down', 'Scroll half page down'),
        ('ctrl+u', 'scroll_half_page_up', 'Scroll half page up'),
        ('ctrl+f', 'scroll_page_down', 'Scroll page down'),
        ('ctrl+b', 'scroll_page_up', 'Scroll page up'),
        ('G', 'scroll_bottom', 'Scroll to bottom'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._g_pressed = False

    def on_key(self, event: Key) -> None:
        """Handle key press for gg combination."""
        if event.key == 'g':
            if self._g_pressed:
                self.scroll_home(animate=False)
                self._g_pressed = False
                event.stop()
            else:
                self._g_pressed = True
                event.stop()
        else:
            self._g_pressed = False

    def action_scroll_down(self) -> None:
        """Scroll down one line."""
        self.scroll_relative(y=1)

    def action_scroll_up(self) -> None:
        """Scroll up one line."""
        self.scroll_relative(y=-1)

    def action_scroll_half_page_down(self) -> None:
        """Scroll down half page (ctrl+d)."""
        scroll_amount = max(1, self.content_size.height // 3)
        self.scroll_relative(y=scroll_amount)

    def action_scroll_half_page_up(self) -> None:
        """Scroll up half page (ctrl+u)."""
        scroll_amount = max(1, self.content_size.height // 3)
        self.scroll_relative(y=-scroll_amount)

    def action_scroll_page_down(self) -> None:
        """Scroll down one page (ctrl+f)."""
        self.scroll_page_down()

    def action_scroll_page_up(self) -> None:
        """Scroll up one page (ctrl+b)."""
        self.scroll_page_up()

    def action_scroll_bottom(self) -> None:
        """Scroll to bottom (G)."""
        self.scroll_end(animate=False)


class HumanInTheLoop(OptionList):
    """Human in the loop component, such as tool call."""

    BINDINGS = [
        ('j', 'cursor_down', 'Move down'),
        ('k', 'cursor_up', 'Move up'),
    ]

    class Decision(Message):
        """
        Custom event, sent to the parent component when the user makes a selection.
        """

        def __init__(self, user_in: str, hitl_widget: 'HumanInTheLoop'):
            self.user_in = user_in
            self.hitl_widget = hitl_widget
            super().__init__()

    def __init__(self, prompt: str, choices: list[str], **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompt
        self.choices = choices
        self.border_title = 'Tool Call Request'

    def on_mount(self) -> None:

        for option in self.choices:
            self.add_option(TOption(option, id=option))

        if self.option_count > 0:
            self.highlighted = 0

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        user_in = event.option.id
        assert isinstance(user_in, str)
        self.post_message(self.Decision(user_in, self))
        self.disabled = True
        self.border_title = 'Tool Call Request (done)'


class FemtobotCLI(App):
    """Femtobot command line interface"""

    CSS = """
    Screen {
        layout: vertical;
    }
    HumanInTheLoop {
        height: auto;
        border: round $warning;
        background: $panel;
        margin: 1 0;
    }
    HumanInTheLoop:disabled {
        border: round $success;
        opacity: 0.7;
    }
    #chat_container {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }
    #cmd_list {
        display: none; height: auto; max-height: 6;
        background: $panel; border: tall $accent; margin: 0 1;
    }
    #chat_input {
        dock: bottom;
        background: $boost;
    }
    .user-message {
        color: $success;
        border: round $success;
        margin: 1 0;
        padding: 0 1;
    }
    .bot-message {
        color: $error;
        border: round $error;
        margin: 1 0;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield VimVerticalScroll(id='chat_container')
        yield OptionList(id='cmd_list')
        yield ChatInput(
            placeholder='Please enter your message (type / to view available commands)...',
            id='chat_input',
        )

    def on_ready(self) -> None:
        self.query_one('#chat_input').focus()
        self._add_message('Hello from ChatBot!\n', 'bot-message', 'System')
        self.agent = FemtobotAgent()

    @on(Input.Changed, '#chat_input')
    def handle_input_changed(self, event: Input.Changed) -> None:
        """
        Monitor input box changes, dynamically show/hide the completion menu
        """
        cmd_list = self.query_one('#cmd_list', OptionList)

        if event.value.startswith('/'):
            commands = self.agent.get_commands()
            matches = {
                k: v for k, v in commands.items() if k.startswith(event.value.lower().strip())
            }
            if matches:
                cmd_list.clear_options()
                for cmd, desc in matches.items():
                    cmd_list.add_option(
                        TOption(
                            f'[bold cyan]{cmd}[/]  [dim]{desc}[/]',
                            id=cmd,
                        )
                    )
                cmd_list.display = True
            else:
                cmd_list.display = False
        elif event.value == '?':
            # TODO: Display help page
            pass
        elif event.value == ':':
            # TODO: Using a sandbox to process bash commands
            pass
        else:
            cmd_list.display = False

    @on(Input.Submitted, '#chat_input')
    async def handle_submit(self, event: Input.Submitted) -> None:
        """Process user input"""

        while True:
            interrupt = self.agent.handle_interrupt()
            if interrupt.goto == 'chat_input':
                break

        user_prompt = event.value.strip()
        if not user_prompt:
            return

        input_widget = self.query_one('#chat_input', ChatInput)
        self.query_one('#cmd_list').display = False
        input_widget.value = ''

        # Render the user's message immediately
        self._add_message(user_prompt, 'user-message', interrupt.info['message'])
        self.agent.resume_state(user_prompt)

        # Start the background asynchronous task to handle streaming
        # output and avoid blocking the UI.
        self.run_worker(self.render_bot_response())

    def _add_message(self, text: str, css_class: str, title: str) -> ChatMessage:
        """Add a new message to the container and return the component instance."""
        container = self.query_one('#chat_container', VimVerticalScroll)

        # Create a new message component that supports rich syntax.
        msg_widget = ChatMessage(title, text, classes=css_class)

        # Mount the component into the container.
        container.mount(msg_widget)
        container.scroll_end(animate=False)

        return msg_widget

    async def render_bot_response(self) -> None:
        """Call the streaming output interface of FemtobotAgent."""
        container = self.query_one('#chat_container', VimVerticalScroll)
        widget = self._add_message('', 'bot-message', 'Femtobot')

        async for output in self.agent.stream_response():
            if output.tp == 'token':
                # current_text += output.content
                widget.append_text(output.content)

                # Dynamically update the content of the ChatMessage component.
                # widget.update(current_text)

                container.scroll_end(animate=False)

            elif output.tp == 'interrupt':
                interrupt = self.agent.handle_interrupt()
                if interrupt.goto == 'chat_input':
                    self.query_one('#chat_input').focus()
                elif interrupt.goto == 'tool_check':
                    hitl_widget = HumanInTheLoop(
                        interrupt.info['message'],
                        interrupt.info['choices'],
                    )
                    container.mount(hitl_widget)
                    container.scroll_end(animate=False)
                    hitl_widget.focus()
                break

            elif output.tp == 'exit':
                self.exit()

    @on(HumanInTheLoop.Decision)
    def handle_hitl_decision(self, event: HumanInTheLoop.Decision) -> None:
        """Intercept the Decision custom event emitted by the HITL component."""

        self.agent.resume_state(event.user_in)
        self.query_one('#chat_input').focus()
        self.query_one('#chat_container', VimVerticalScroll).scroll_end(animate=False)

        self.run_worker(self.render_bot_response())


@app.command()
def run(
    cont: Annotated[
        bool,
        Option(
            '--continue',
            '-c',
            help='Continue the most recent conversation in the current directory',
        ),
    ] = False,
    resume: Annotated[
        bool,
        Option(
            '--resume',
            '-r',
            help='Resume a conversation by session ID, or open interactive picker with optional search term',
        ),
    ] = False,
):
    # log_path = _root_path / f'logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    # logger.remove()
    # logger.add(log_path, level='DEBUG')
    cli = FemtobotCLI()
    cli.run()


def main():
    app()
