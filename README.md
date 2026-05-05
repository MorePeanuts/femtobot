# Femtobot

[![uv](https://img.shields.io/badge/uv-Package%20Manager-blueviolet)](https://docs.astral.sh/uv)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.1.10-blue)](https://langchain-ai.github.io/langgraph/)
[![Textual](https://img.shields.io/badge/Textual-8.2.5-green)](https://textual.textualize.io/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-Docs-orange)](https://platform.deepseek.com/docs)
[![Tavily](https://img.shields.io/badge/Tavily-Docs-purple)](https://docs.tavily.com/)

An LLM-driven agent built using the LangChain ecosystem, inspired by OpenClaw.

## Features

- Interactive Textual-based TUI with vim keybindings
- DeepSeek LLM integration (v4 Flash/Pro with optional thinking modes)
- Web search via Tavily API (with human-in-the-loop approval)
- LangGraph-based state machine workflow

## Installation

```bash
git clone https://github.com/MorePeanuts/femtobot.git
cd femtobot
uv sync
```

## Configuration

Set the following environment variables:

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export TAVILY_API_KEY="your-tavily-api-key"
```

## Usage

```bash
# Run the TUI
femtobot run
```

## Roadmap

- [ ] Add more built-in tools
- [ ] Support additional LLM providers
- [ ] Persistent conversation history
- [ ] Plugin system for extensibility

## License

MIT License. See [LICENSE](LICENSE) for details.