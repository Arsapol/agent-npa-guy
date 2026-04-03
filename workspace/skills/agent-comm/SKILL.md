---
name: agent-comm
description: Inter-agent communication for nanobot. Sends a message to another nanobot agent running in a different workspace and returns its response. Use when NPA-guy needs a second opinion, financial analysis from Ada, or wants to delegate a task to a specialized agent.
---

# Agent Communication Skill

## Overview

Enables NPA-guy to communicate with other nanobot agents in different workspaces. Each agent has its own persona (SOUL.md), memory, and skills. Communication is synchronous — the caller sends a message, waits for the response, and gets clean text back.

## How It Works

```
NPA-guy (this agent)                    Target Agent
    |                                        |
    |-- call ask_agent(message, ...)  ------>|
    |                                        |-- Loads its own SOUL.md, memory
    |                                        |-- Processes the message
    |                                        |-- Uses its own tools/skills
    |   <------------------------------ result |
    |-- Receives clean response text         |
    |-- Continues with the result            |
```

Uses `nanobot agent -m "<message>" -w <workspace> -c <config> --no-markdown` under the hood.

## Tool: `ask_agent`

Use via `scripts/ask_agent.sh` through the `shell` tool.

### Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `message` | Yes | The message/task to send to the target agent |
| `target_workspace` | Yes | Absolute path to target agent's workspace directory |
| `target_config` | Yes | Absolute path to target agent's config.json |
| `timeout` | No | Timeout in seconds (default: 120) |

### Usage

```bash
bash scripts/ask_agent.sh \
  "<message>" \
  "<target_workspace>" \
  "<target_config>" \
  [timeout_seconds]
```

### Example: Ask Ada for financial analysis

```bash
bash scripts/ask_agent.sh \
  "What is the current rental yield benchmark for condos near BTS Ari? Any macro factors affecting Bangkok condo prices?" \
  "/Users/arsapolm/.nanobot-stocks/workspace" \
  "/Users/arsapolm/.nanobot-stocks/config.json" \
  120
```

## Registered Target Agents

| Agent | Workspace | Config | Purpose |
|-------|-----------|--------|---------|
| Ada | `~/.nanobot-stocks/workspace` | `~/.nanobot-stocks/config.json` | Financial analysis, macro context, market data |
| Sentinel | `~/.nanobot-sentinel/workspace` | `~/.nanobot-sentinel/config.json` | News monitoring, KB curation, market scanning |
| Reviewer | `~/.nanobot-reviewer/workspace` | `~/.nanobot-reviewer/config.json` | Critical review of investment theses |

## When to Use

- **Financial context**: Ask Ada about macro conditions affecting real estate (interest rates, THB strength, economic outlook)
- **News check**: Ask Sentinel about recent news that might affect a specific area or property type
- **Second opinion**: Get independent analysis on a property deal
- **Market data**: Ask Ada for comparable financial analysis

## Limitations

- **Synchronous**: Caller blocks until response arrives (up to timeout)
- **Single-message**: No multi-turn conversation — each call is stateless
- **No streaming**: Response arrives all at once after completion
- **Shell timeout**: nanobot's 60s shell timeout applies — for longer tasks, use the `spawn` tool to run `ask_agent.sh` in the background
- **Session isolation**: Target agent does NOT see caller's conversation history
