from typer import Typer, Argument, Option
from typing import Annotated

app = Typer(
    name='FemtoBot',
    help='An LLM-driven agent built using the LangChain ecosystem, inspired by OpenClaw.',
)


@app.command()
def run():
    print('Hello from ChatBot!\n')


def main():
    app()
