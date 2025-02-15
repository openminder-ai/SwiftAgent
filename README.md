# SwiftAgent

<div align="center">

![Logo of Openminder AI](./docs/openminder_logo.jpeg)

# **SwiftAgent**

🦅 **SwiftAgent**: Build scalable & production-ready agents.

<h3>

</div>

## Table of contents

- [What is SwiftAgent?](#what-is-swiftagent)

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Key Concepts](#key-concepts)
  - [Agents]
  - [Actions]
  - [Memory]
  - [Suites]
- [Comparisons](#comparisons)



## What is SwiftAgent?
In today’s rapidly evolving tech landscape, AI agents have moved far beyond experimental research—they are now set to become an integral part of everyday development. Agentic systems are not just about early-stage prototypes; they’re about delivering robust, production-grade solutions that power real-world applications. SwiftAgent is the pioneering, scalable agent framework that transforms this vision into reality. It provides developers with an out-of-the-box, production-ready infrastructure that meets the demands of modern enterprise environments, ensuring high performance and seamless integration from concept to deployment.


## Installation

```bash
pip install swiftagent
```

## Getting Started

Let's build a real-time Weather Agent!

### Step 1: Install dependencies

We rely on the `python_weather` package to get real time weather for a city, so download it using

```bash
python -m pip install python_weather
```

### Step 2: Create an Agent Instance

Start by importing and instantiating a SwiftAgent.

```python
from swiftagent import SwiftAgent
import python_weather # for later action
import asyncio # for running async functions directly

weather_agent = SwiftAgent(name="WeatherAgent")
```

### Step 3: Define Actions

Actions are the core functionality of your agent, providing external abilities to agents. Use the `@SwiftAgent.action` decorator around any function to define what your agent can do:

```python
@weather_agent.action(description="get weather for a city")
async def get_weather_for_city(city: str) -> None:
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(city)
        return weather.temperature
```

### Step 4: Run the Agent

Agents are asynchronous since it allows for high scalability and performance. To directly run an asynchronous function, we use the built-in Python `asyncio` module.

```python
async def main():
    await agent.run('What is the weather in boston?')

asyncio.run(main())
```

## Key Concepts

### Agents

SwiftAgent's core is the *agent*—an autonomous unit designed to reason, act, and learn. Each agent is stateful and persistent, storing its own memory, action registry, and reasoning parameters. This makes them inherently “human-like” in that they can remember past interactions and adapt over time.

## Actions
Actions are the building blocks of an agent’s functionality. You can:

Decorate Functions: Register them as actions with clear descriptions and parameter metadata.
Group Actions: Use action sets to bundle related functionalities (e.g., finance actions, search tools).

## Memory & Persistence
SwiftAgent is the first framework where agents come equipped with:

Working Memory: For short-term storage and immediate context.
Long-Term Memory: Persistently stores important interactions, actions, and insights.
Semantic Memory: Uses vector storage (e.g., ChromaDB) to recall contextually relevant information.
Persistent Profiles: AgentRegistry ensures that all agent configurations, actions, and memories are saved and reloaded seamlessly.

## Multi-Agent Collaboration
Complex tasks often require multiple agents. SwiftAgent supports:

Tiered Execution Pipelines: Using the SwiftRouter and SwiftExecutor, agents can execute tasks in parallel or sequentially, passing outputs between tiers.
Hosted Mode via SwiftSuite: Agents and clients can interact in real time over websockets, enabling rich, distributed workflows.

## Reasoning & Orchestration
At the heart of every agent is its reasoning engine. SwiftAgent provides:

BaseReasoning: A fundamental LLM-driven reasoning module.
SalientMemoryReasoning: A specialized variant that retains only essential tool calls and final responses, reducing noise while preserving key insights.
LLM Integration: Out-of-the-box support for OpenAI’s API (and other LLM adapters) to power dynamic, multi-step reasoning.


## How SwiftAgent Compares



## Contributing

Contributions are always welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for more information.

## License

CrewAI is released under the [MIT License](./LICENSE).

