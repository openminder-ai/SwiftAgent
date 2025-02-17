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
- [Anthropomorphism]
- [Key Concepts](#key-concepts)
  - [Agents]
  - [Actions]
  - [Memory]
  - [Suites]
- [Comparisons](#comparisons)

## What is SwiftAgent?
In today’s rapidly evolving tech landscape, AI agents have moved far beyond experimental research — they are now set to become an integral part of everyday development. Agentic systems are not just about early-stage prototypes; they’re about delivering robust, production-grade solutions that power real-world applications. SwiftAgent is the pioneering, scalable agent framework that transforms this vision into a reality. 

SwiftAgent is a framework for building anthropomorphic (humanlike) agents that are easy to prototype and production-ready from day one, moving agents beyond experimental research and into everyday development for scalable, real-world applications. 

> [!NOTE]  
> 🦅 **SwiftAgent**</span> is part of OpenMinder Labs’ larger vision of the Internet of Agents, where agents are commodified and become as universal as websites.

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

### 📃 Agents

SwiftAgent's core is the *agent*—an autonomous unit designed to reason, act, and learn. Each agent is stateful and persistent, storing its own memory, action registry, and reasoning parameters. This makes them inherently “human-like” in that they can remember past interactions and adapt over time.

## 📚 Actions
Actions are the fundamental building blocks that empower agents to interact with the external world. Much like how humans use tools and skills to accomplish tasks, Actions give agents the ability to execute specific operations—from simple data retrieval to complex API integrations. Actions transform agents from passive chatbots into proactive problem solvers. 

## 🧠 Memory 
SwiftAgent is the first framework that takes inspiration from how human brains process and store information. Modulating biomimicry, we feature two main memory components:

1. **Episodic Memory** - This system handles experience-based memories, similar to how humans remember specific events and situations:
    - *Working Memory*: Like our ability to hold and manipulate immediate information
    - *Long-term Memory*: Stores past experiences and interactions over time

2. **Semantic Memory** - This system mirrors how humans store factual knowledge and general understanding about the world, independent of specific experiences. It's like our mental database of concepts, facts, and general knowledge.

## Multi-Agent Systems
SwiftAgent revolutionizes collaborative AI by enabling true emergent teamwork between agents. Unlike most frameworks, SwiftAgent treats multi-agent interactions as a first-class citizen, mirroring how humans organize into teams, departments, and organizations to solve complex problems. Currently, only hierarchical collaboration (preset subdivisions) is supported, but support for dynamic collaboration (in the moment divisions and allocations) is coming soon!


## How SwiftAgent Compares


## Documentation
Refer to our [Documentation](https://docs.openminder.ai) for a more comprehensive view of the framework.

## Contributing

Contributions are always welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for more information.

## License

SwiftAgent is released under the [MIT License](./LICENSE).

