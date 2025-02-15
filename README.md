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

Agents are the core of any agentic system, representing a (semi-)autonomous unit that is capable of reasoning and taking actions to accomplish a goal. Agents are capable of using actions, having memory, and utilizing reasoning patterns.

### Actions

Actions are utilities or functionalities that an agent can perform. Much like we carry out everyday tasks — such as walking, talking, or using a computer—agents can execute actions like checking the weather, writing a Google Doc, or retrieving current stock prices.

SwiftAgent provides two primary methods to define actions:

---

#### 1. Using the `SwiftAgent.action` Decorator

This method allows you to register an action directly by decorating a function with the agent's own `action` decorator. Here’s how you can do it:

```python
from swiftagent import SwiftAgent

# Initialize your agent
agent = SwiftAgent()

# Define and register an action using the agent's decorator
@agent.action(description="Description her")
def sample_action(param1: str):
    # Implementation of your action here
    pass
```

---

#### 2. Using the Standalone `action` Decorator with `add_action`

Alternatively, you can create an action using the standalone `action` decorator and then register it with your agent by calling the `add_action` method. This approach offers flexibility, especially if you prefer to separate the action definition from the agent's configuration, or want to create reusable actions.

```python
from swiftagent import SwiftAgent
from swiftagent.actions import action

# Initialize your agent
agent = SwiftAgent()

# Define the action using the standalone decorator
@action(description="Description here")
def sample_action(param1: str):
    # Implementation of your action here
    pass

# Add the action to your agent
agent.add_action(sample_action)
```

---

Both methods are fully supported in SwiftAgent! 

### Persistence & State

A key differentiator of SwiftAgent is that it's agents by default are capable of being both persistent and stateful out of the box.

### Multi Agent Collaboration

SwiftAgent also features SwiftSuites,

## How SwiftAgent Compares



## Contributing

Contributions are always welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for more information.

## License

CrewAI is released under the [MIT License](./LICENSE).

