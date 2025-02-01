# SwiftAgent

<div align="center">

![Logo of Openminder AI](./docs/openminder_logo.jpeg)

# **SwiftAgent**

🦅 **SwiftAgent**: Build scalable & production-ready agents.

<h3>

<!-- TODO -->
<!-- [Homepage](https://www.crewai.com/) | [Documentation](https://docs.crewai.com/) | [Chat with Docs](https://chatg.pt/DWjSBZn) | [Examples](https://github.com/crewAIInc/crewAI-examples) | [Discourse](https://community.crewai.com) -->

</h3>

<!-- TODO -->
<!-- [![GitHub Repo stars](https://img.shields.io/github/stars/joaomdmoura/crewAI)](https://github.com/crewAIInc/crewAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) -->

</div>

## Table of contents

- [Why SwiftAgent?](#why-swiftagent)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Key Features](#key-features)
- [Understanding Suites](#understanding-suites)
- [Examples](#examples)
  - [Weather Agent](#weather-agent)
<!-- - [Connecting Your Crew to a Model](#connecting-your-crew-to-a-model)
- [How CrewAI Compares](#how-crewai-compares)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
- [Contribution](#contribution)
- [Telemetry](#telemetry)
- [License](#license) -->

## Why SwiftAgent?
SwiftAgent is designed to be truly simple yet remarkably flexible, offering a streamlined experience unlike more complex alternatives such as CrewAI or Autogen. With a minimal learning curve, SwiftAgent lets you get started quickly, enabling you to build robust agents without the overhead of unnecessary complexity. Its clear, concise API is inspired by popular web frameworks like FastAPI and Flask, making it especially accessible for web developers and software engineers alike.

One of SwiftAgent’s core strengths is its persistence by design. Unlike standard, function-based solutions, SwiftAgent’s agents are built to remain active over time and handle multiple queries in parallel. This design ensures that your agents are not only responsive but also capable of managing ongoing interactions and complex workflows without requiring additional scaffolding.

Furthermore, SwiftAgent supports multi-agent collaboration, allowing multiple agents to work together seamlessly to tackle intricate tasks. Combined with its integrated detailed analytics and replay capabilities, you can monitor every interaction, gain deep insights into your agents’ decision processes, and even replay queries for debugging or performance optimization.

## Installation

```bash
pip install swiftagent
```

## Getting Started

### Step 1: Create an Agent Instance

Start by importing and instantiating a SwiftAgent. You can create either a named or unnamed agent:

```python
from swiftagent import SwiftAgent

# Unnamed agent (for simple use cases)
agent = SwiftAgent()

# Named agent (required for persistent/suite modes)
agent = SwiftAgent(name="MyCustomAgent")
```

### Step 2: Define Actions

Actions are the core functionality of your agent. Use the `@agent.action` decorator to define what your agent can do:

```python
@agent.action(description="A human-readable description of what this action does")
async def my_custom_action(param1: str, param2: int) -> str:
    # Your action logic here
    return result
```

### Step 3: Choose a Running Mode

SwiftAgent supports three running modes, each suited for different use cases:

#### Standard Mode (One-off Tasks)
```python
await agent.run(task="Your task description here")
```

#### Persistent Mode (Long-running Service)
```python
from swiftagent.application.types import ApplicationType
await agent.run(type_=ApplicationType.PERSISTENT)
```

#### Suite Mode (Multiple Agents)
```python
from swiftagent.suite import SwiftSuite
suite = SwiftSuite(name="MySuite", agents=[agent1, agent2])
await suite.setup(host="localhost", port=8001)
```

### Step 4: Connect to Your Agent

For standard mode, the agent processes the task immediately and returns.

For persistent or suite modes, use SwiftClient to send tasks:

```python
from swiftagent.client import SwiftClient

client = SwiftClient()
await client.send(
    "Your task description",
    agent_name="MyCustomAgent"
)
```


## Key Features

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

## Understanding Suites
TBD

## Examples

### Weather Agent
