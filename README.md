# 🦅 **SwiftAgent**

<h3> ⚡Build scalable & production-ready agents. ⚡ </h3>

<h4>

[Documentation](https://docs.openminder.ai/) | [Community](https://discord.gg/TseVHQC6e4)

</h4>

[![Release Notes](https://img.shields.io/github/release/openminder-ai/SwiftAgent?style=flat-square)](https://github.com/openminder-ai/SwiftAgent/releases)
[![CI](https://github.com/openminder-ai/SwiftAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/openminder-ai/SwiftAgent/actions/workflows/ci.yml)
[![GitHub Repo stars](https://img.shields.io/github/stars/openminder-ai/SwiftAgent)](https://github.com/openminder-ai/SwiftAgent)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

## Table of contents

- [What is SwiftAgent?](#what-is-swiftagent)
- [A different paradigm](#a-different-paradigm)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Key Concepts](#key-concepts)
  - [Agents](#-agents)
  - [Actions](#-actions)
  - [Memory](#-memory)
  - [Multi-Agent Systems](#multi-agent-systems)
- [How SwiftAgent Compares](#how-swiftagent-compares)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## What is SwiftAgent?
In today’s rapidly evolving tech landscape, AI agents have moved far beyond experimental research — they are now set to become an integral part of everyday development. Agentic systems are not just about early-stage prototypes; they’re about delivering robust, production-grade solutions that power real-world applications. SwiftAgent is the pioneering, scalable agent framework that transforms this vision into a reality. 

SwiftAgent is a framework for building anthropomorphic (humanlike) agents that are easy to prototype and production-ready from day one, moving agents beyond experimental research and into everyday development for scalable, real-world applications. 

SwiftAgent brings the familiarity of web development to AI agent creation. If you've worked with Express.js routes or FastAPI, you'll feel right at home – but instead of building UIs or APIs, you're crafting stateful, human-like AI agents ready for production from day one.

```python
#example
@agent.action(description="Analyze market trends")
async def analyze_market(symbol: str):
    # Your complex logic here
    return insights
```

**If you can build a REST API, you can build an AI agent**
SwiftAgent adopts the patterns that made web frameworks successful, giving developers instant familiarity:

We've reimagined agent development through web-tested paradigms:
- Decorator-Driven Design: Annotate capabilities like API endpoints
- Async-First Architecture: Native support for concurrent operations
- Component Reusability: Share agents like npm packages (coming soon!)
- DevTools Ecosystem: CLI, debugger, and hot-reload (coming soon!)

This isn't just another AI toolkit - it's the FastAPI for Agent Development, combining the web's accessibility with AI's power.

> [!NOTE]  
> 🦅 **SwiftAgent**</span> is part of OpenMinder Labs’ larger vision of the **Internet of Agents**, where agents are commodified and become as universal as websites.

## A different paradigm
<h3> Agents That Remember. Learn. Evolve. </h3>

SwiftAgent introduces the first true biomimetic architecture in AI frameworks. SwiftAgent aims to reimagine AI agents as cognitive beings rather than code utilities. Where traditional frameworks treat agents as functions to accomplish tasks, we work to implement stateful continuity – agents retain experiences like humans, evolving their decision-making through layered memory systems (episodic snapshots and semantic knowledge) instead of flat RAG. Tools become actions, intentional behaviors refined through interaction, not isolated API calls. We envision collaboration to mirror organic teamwork, with agents debating ideas and redistributing roles mid-task, and reasoning adopts neuroplastic principles where frequently used skills strengthen over time. This isn’t just mimicking human traits architecturally; it’s building agents with cognitive fingerprints that learn, forget, and adapt – not because they’re programmed to, but because their design biologically compels them to.

## Installation

```bash
pip install swiftagent
```

## Getting Started

Let's build a real-time Weather Agent!

### Step 1: Install dependencies

We rely on the `python_weather` package to get real-time weather for a city, so download it using

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
    await weather_agent.run('What is the weather in boston?')

asyncio.run(main())
```

## Key Concepts

### 📃 Agents

SwiftAgent's core is the *agent*—an autonomous unit designed to reason, act, and learn. Each agent is stateful and persistent, storing its own memory, action registry, and reasoning parameters. This makes them inherently “human-like” in that they can remember past interactions and adapt over time.

### 📚 Actions
Actions are the fundamental building blocks that empower agents to interact with the external world. Much like how humans use tools and skills to accomplish tasks, Actions give agents the ability to execute specific operations—from simple data retrieval to complex API integrations. Actions transform agents from passive chatbots into proactive problem solvers. 

### 🧠 Memory 
SwiftAgent is the first framework that takes inspiration from how human brains process and store information. Modulating biomimicry, we feature two main memory components:

1. **Episodic Memory** - This system handles experience-based memories, similar to how humans remember specific events and situations:
    - *Working Memory*: Like our ability to hold and manipulate immediate information
    - *Long-term Memory*: Stores past experiences and interactions over time

2. **Semantic Memory** - This system mirrors how humans store factual knowledge and general understanding about the world, independent of specific experiences. It's like our mental database of concepts, facts, and general knowledge.

### Multi-Agent Systems
SwiftAgent revolutionizes collaborative AI by enabling true emergent teamwork between agents. Unlike most frameworks, SwiftAgent treats multi-agent interactions as a first-class citizen, mirroring how humans organize into teams, departments, and organizations to solve complex problems. Currently, only hierarchical collaboration (preset subdivisions) is supported, but support for dynamic collaboration (in the moment divisions and allocations) is coming soon!


## How SwiftAgent Compares

Swiftagent's advantage: **Swiftagent** eliminates the need for cumbersome setup and complex configurations while delivering production-grade control and performance by mimicking the unique inner workings of the human brain.

* **LangChain** - While LangChain provides the building blocks for agent workflows, it requires significant boilerplate and intricate state management. Its heavy abstraction layer can slow down operations that would be faster with direct API calls. This excessive complexity hinders flexibility, decreases time efficiency, and makes setup difficult, especially when seeking deep custom agent behaviors or unique external integrations. LangChain's deployments also lack production-level efficiency and require manual wrapping into a server (like FastAPI). 

* **AutoGen** - AutoGen's flexibility comes at the cost of efficiency. It lacks built-in process management and requires additional coding for orchestration, which doesn't scale efficiently. Furthermore, AutoGen's resource-hungry nature and excess overhead results in a degrading inference speed. Its approach is memory-intensive and has limited out-of-the-box applicability for larger-scale scenarios.

* **CrewAI** - CrewAI focuses on orchestrating agents through “Crews and Flows,” but its architecture can be complex to fully leverage. Setup is challenging, and its enterprise cloud option may feel clunky for smaller-scale use. Customization for production workflows often demands significant effort. CrewAI's orchestration uses LangChain under the hood, inheriting some of its overhead, resulting in resource bloat and hurting speed and cost efficiency.  

* **Agno AI** - Agno AI's speed efficiency affects agent initialization. The speed of the actual task execution is still bottlenecked by LLM inference latency, so end-to-end throughput doesn't always surpass rival frameworks. Large deployments also strain resources and require careful orchestration features that are not provided. 


Meanwhile, **SwiftAgent** is straightforward and simple to use while still providing more granular control than CrewAI or AgnoAI. While LangChain and Autogen provide similar levels of control, implementation is excessively complicated and difficult. Unlike our competitors, we are incredibly performance-efficient, with memory usage and speed comparable to AgnoAI.


**Benchmarks coming out soon in the coming weeks!**



## Documentation
Refer to our [Documentation](https://docs.openminder.ai) for a more comprehensive view of the framework.

## Contributing

Contributions are always welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for more information.

## License

SwiftAgent is released under the [MIT License](./LICENSE).

