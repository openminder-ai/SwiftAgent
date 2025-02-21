from swiftagent.core.prompts import AGENT_ROUTER_SYSTEM, AGENT_ROUTER_USER

from swiftagent import SwiftAgent

from swiftagent.llm.base import LLM

from swiftagent.router.output import RouterOutput

import json


class SwiftRouter:
    def __init__(self, agents=[], llm: LLM = None):
        self.agents: list[SwiftAgent] = agents
        self.llm = llm

    def add_agents(self, agents: list[SwiftAgent]):
        self.agents.extend(agents)

    def _format_agents(self) -> str:
        return "\n".join(
            [f"{agent.name}: {agent.description}" for agent in self.agents]
        )

    async def route(self, query: str):
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

        completion = await self.llm.inference(
            model=self.llm,
            messages=_messages,
            response_format={"type": "json_object"},
            max_tokens=4096,
        )

        response = json.loads(completion.choices[0].message.content)

        return RouterOutput(response)
