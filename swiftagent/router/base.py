from swiftagent.core.prompts import AGENT_ROUTER_SYSTEM, AGENT_ROUTER_USER

from swiftagent import SwiftAgent

from swiftagent.llm.adapter import LLMAdapter

import json


class SwiftRouter:
    def __init__(self, agents=[]):
        self.agents: list[SwiftAgent] = agents

    def add_agents(self, agents: list[SwiftAgent]):
        self.agents.extend(agents)

    def _format_agents(self) -> str:
        return "\n".join(
            [f"{agent.name}: {agent.description}" for agent in self.agents]
        )

    async def route(self, query: str, llm: str = "gpt-4o-mini"):
        _messages = [
            {
                "role": "system",
                "content": AGENT_ROUTER_SYSTEM.substitute(
                    agent_info_list=self._format_agents(),
                ),
            },
            {
                "role": "user",
                "content": AGENT_ROUTER_USER.substitute(query=query),
            },
        ]

        completion = await LLMAdapter.inference(
            model=llm,
            messages=_messages,
            response_format={"type": "json_object"},
            max_tokens=4096,
        )

        response = json.loads(completion.choices[0].message.content)

        return response
