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

## Getting Started

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
