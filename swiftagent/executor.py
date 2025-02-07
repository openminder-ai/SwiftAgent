import asyncio
from swiftagent import SwiftAgent

from swiftagent.router.output import RouterOutput, Task


class SwiftExecutor:
    def __init__(self, agent_mapping: dict[str, SwiftAgent]):
        """
        :param agent_mapping: A dictionary mapping agent names (str) to agent instances.
        """
        self.agent_mapping = agent_mapping
        self.outputs = (
            {}
        )  # This will store outputs keyed by each agent's unique_id

    async def execute_pipeline(self, router_output: "RouterOutput") -> dict:
        """
        Execute the pipeline of agent tasks. Tasks in the same tier run concurrently.

        :param router_output: A RouterOutput instance containing tiers and tasks.
        :return: A dictionary mapping each task's unique_id to its output.
        """
        # Process tiers in ascending order (assuming tier IDs are integers)
        for tier_id in sorted(router_output.tiers.keys()):
            tier = router_output.tiers[tier_id]
            tasks = []
            for task in tier.tasks:
                # Schedule each task in the current tier concurrently
                tasks.append(asyncio.create_task(self.execute_task(task)))
            # Wait for all tasks in the current tier to finish before moving to the next tier
            await asyncio.gather(*tasks)
        return self.outputs

    async def execute_task(self, task: "Task") -> str:
        """
        Execute a single agent task.

        :param task: A Task object with attributes 'agent', 'instruction',
                     'unique_id', and optionally 'accepts_inputs_from'.
        :return: The output from the agent's run method.
        """
        agent_name = task.agent
        unique_id = task.unique_id
        instruction = task.instruction
        accepts_inputs_from = task.accepts_inputs_from

        # Build the input string for the agent. Start with the instruction.
        # If the agent depends on other agents' outputs, append them.
        input_text = instruction
        if accepts_inputs_from:
            dependency_texts = []
            for dep_id in accepts_inputs_from:
                # It is assumed that these outputs are available from previous tiers.
                dependency_output = self.outputs.get(dep_id, "")
                dependency_texts.append(dependency_output)
            if dependency_texts:
                input_text += "\n" + "\n".join(dependency_texts)

        # Get the agent instance from the mapping.
        agent = self.agent_mapping.get(agent_name)
        if not agent:
            raise ValueError(
                f"Agent '{agent_name}' not found in agent mapping."
            )

        # Run the agent's task asynchronously.
        output = await agent.run(task=input_text)

        # Save the output under its unique_id.
        self.outputs[unique_id] = output
        return output
