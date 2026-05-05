# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Femtobot is an LLM-driven conversational agent built with the LangChain ecosystem, inspired by OpenClaw. It features:
- Interactive Textual-based TUI with vim keybindings
- DeepSeek LLM integration (v4 Flash/Pro with optional thinking modes)
- Web search via Tavily API (with human-in-the-loop approval)
- LangGraph-based state machine workflow

## Architecture

The agent uses a LangGraph StateGraph with the following node flow:
```
START → user_input → [chat_model_call or command_parse]
                          ↓
                     builtin_tools ← (if tool_calls exist)
                          ↓
                     user_input (loop)
```

**Key Components:**
- `src/femtobot/femtobot.py`: Core `FemtobotAgent` and graph construction
- `src/femtobot/agents/nodes.py`: LangGraph node implementations
- `src/femtobot/agents/state.py`: `AgentState` definition
- `src/femtobot/cli/cli.py`: Textual TUI application
- `src/femtobot/providers/chatmodel.py`: DeepSeek model registry
- `src/femtobot/tools/builtin.py`: Built-in tools (WebSearch)

## Development Commands

**Installation:**
```bash
uv sync
```

**Run the Agent:**
```bash
# TUI mode
femtobot run
# or
uv run femtobot run
```

**Development Tools:**
```bash
# Plot state graph
python tools/plot_graph.py  # Output: imgs/graph.png

# Simple agent loop
python tools/run_agent_loop.py
```

**Install Dev Dependencies:**
```bash
uv sync --dev
```

## Key Dependencies

- `langchain` & `langgraph`: Core agent framework
- `langchain-deepseek`: LLM provider
- `textual`: Terminal UI
- `tavily-python`: Web search tool
- `typer`: CLI parsing
- `pytest`: Testing (dev dependency)

## Environment Variables

The agent requires API keys for:
- `DEEPSEEK_API_KEY`: LLM access
- `TAVILY_API_KEY`: Web search capability