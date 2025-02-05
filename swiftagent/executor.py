import asyncio

from swiftagent import SwiftAgent


# The SwiftExecutor class that builds and runs the pipeline.
class SwiftExecutor:
    def __init__(self, agent_mapping: dict[str, SwiftAgent]):
        """
        :param agent_mapping: A dictionary mapping agent names (str) to agent instances.
        """
        self.agent_mapping = agent_mapping
        self.outputs = (
            {}
        )  # This will store outputs keyed by each agent's unique_id

    async def execute_pipeline(self, pipeline: dict) -> dict:
        """
        Execute the pipeline of agent tasks. Tasks in the same tier run concurrently.

        :param pipeline: Dictionary describing the pipeline.
                         Expected format:
                         {
                             'tiers': {
                                 '0': [ { ... task details ... }, ... ],
                                 '1': [ { ... task details ... }, ... ],
                                 ...
                             }
                         }
        :return: A dictionary mapping each task's unique_id to its output.
        """
        tiers: dict = pipeline.get("tiers", {})

        # Process tiers in ascending order (assuming tier keys can be cast to int)
        for tier_key in sorted(tiers.keys(), key=int):
            tasks = []
            for task_info in tiers[tier_key]:
                # Schedule each task in the current tier concurrently
                tasks.append(asyncio.create_task(self.execute_task(task_info)))
            # Wait for all tasks in the current tier to finish before moving to the next tier
            await asyncio.gather(*tasks)
        return self.outputs

    async def execute_task(self, task_info: dict) -> str:
        """
        Execute a single agent task.

        :param task_info: Dictionary with keys 'agent', 'instruction',
                          'unique_id', and optionally 'accepts_inputs_from'.
        :return: The output from the agent's run method.
        """
        agent_name = task_info["agent"]
        unique_id = task_info["unique_id"]
        instruction = task_info["instruction"]
        accepts_inputs_from = task_info.get("accepts_inputs_from", [])

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
        output = await agent.run(input_text)

        # Save the output under its unique_id.
        self.outputs[unique_id] = output
        return output
