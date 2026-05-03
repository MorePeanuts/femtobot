import asyncio
from typing import Annotated

from typer import Argument, Option, Typer

from femtobot.femtobot import agent_loop

app = Typer(
    name='FemtoBot',
    help='An LLM-driven agent built using the LangChain ecosystem, inspired by OpenClaw.',
)


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
    print('Hello from ChatBot!\n')
    asyncio.run(agent_loop())


def main():
    app()
