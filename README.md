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
In today’s rapidly evolving tech landscape, AI agents have moved far beyond experimental research — they are now set to become an integral part of everyday development. Agentic systems are not just about early-stage prototypes; they’re about delivering robust, production-grade solutions that power real-world applications. SwiftAgent is the pioneering, scalable agent framework that transforms this vision into a reality. SwiftAgent provides developers with an out-of-the-box, production-ready infrastructure that meets the demands of modern enterprise environments, ensuring high performance and seamless integration from concept to deployment.

Human-Like Memory & Learning
Persistent Memory:
Just like humans remember past experiences, SwiftAgent’s agents store their interactions across sessions. They keep a record of recent events (working memory) as well as long-term memories, allowing them to recall and learn from past actions.

Semantic Understanding:
Our agents use semantic memory modules to extract and store contextually relevant information. This means they don’t just remember facts—they understand relationships, similar to how our brains abstract important details from our experiences.

Evolving Behavior:
By continuously ingesting new information and updating their memories, SwiftAgent agents evolve over time. They adapt their responses based on previous interactions, much like how people refine their opinions and strategies with experience.

Reflective Reasoning
Step-by-Step Thought Processes:
SwiftAgent’s reasoning engines (like the SalientMemoryReasoning module) simulate a reflective, chain-of-thought process. Instead of providing a one-shot answer, the agent iteratively refines its response, mimicking how humans deliberate before concluding.

Selective Memory Storage:
Not all interactions are preserved — agents only store key actions and final responses, much like how humans remember only the highlights of a conversation or decision-making process.

Contextual Awareness:
When facing a new task, an agent can recall relevant past experiences from its memory. This ability to integrate past knowledge with current context creates a more “human” and personalized interaction.

Collaborative & Social Interaction
Multi-Agent Communication:
SwiftAgent supports scenarios where multiple agents work together, sharing information and coordinating tasks. This collaboration mirrors how teams of humans interact, delegate tasks, and build on each other’s ideas.

Dynamic Personality:
Each agent can be seen as having its own “personality” through its instructions, action sets, and memory configurations. Over time, their behavior becomes tailored by their unique experiences, just like how individuals develop unique traits based on their life history.

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

Agents are asynchronous, allowing for high scalability and performance. To directly run an asynchronous function, we use the built-in Python `asyncio` module.

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

