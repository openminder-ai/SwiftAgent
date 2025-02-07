import json
from typing import List, Optional


class Task:
    def __init__(
        self,
        instruction: str,
        agent: str,
        unique_id: str,
        accepts_inputs_from: Optional[List[str]] = None,
    ):
        """
        Initializes a Task instance.

        :param instruction: The instruction for the task.
        :param agent: The agent responsible for the task.
        :param unique_id: A unique identifier for the task.
        :param accepts_inputs_from: A list of unique_ids from which this task accepts inputs.
        """
        self.instruction = instruction
        self.agent = agent
        self.unique_id = unique_id
        self.accepts_inputs_from = (
            accepts_inputs_from if accepts_inputs_from is not None else []
        )

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Task.
        """
        return {
            "instruction": self.instruction,
            "agent": self.agent,
            "unique_id": self.unique_id,
            "accepts_inputs_from": self.accepts_inputs_from,
        }

    def __repr__(self):
        return (
            f"Task(instruction={self.instruction!r}, agent={self.agent!r}, "
            f"unique_id={self.unique_id!r}, accepts_inputs_from={self.accepts_inputs_from!r})"
        )


class Tier:
    def __init__(self, tier_id: int, tasks: Optional[List[Task]] = None):
        """
        Initializes a Tier instance.

        :param tier_id: An integer representing the tier level.
        :param tasks: A list of Task objects associated with this tier.
        """
        self.tier_id = tier_id
        self.tasks = tasks if tasks is not None else []

    def add_task(self, task: Task):
        """
        Adds a new Task to the tier.

        :param task: The Task object to be added.
        """
        self.tasks.append(task)

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Tier.
        """
        return {
            "tier_id": self.tier_id,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    def __repr__(self):
        return f"Tier(tier_id={self.tier_id}, tasks={self.tasks})"


class RouterOutput:
    def __init__(self, pipeline: dict):
        """
        Initializes a RouterOutput instance by parsing the pipeline dictionary.

        :param pipeline: A dictionary containing tier and task information.
        """
        self.tiers = {}
        tiers_data = pipeline.get("tiers", {})

        # Iterate over each tier in the pipeline
        for tier_key, tasks_list in tiers_data.items():
            # Convert tier_key to integer (if needed)
            tier_id = int(tier_key)
            tasks = []
            # Create Task objects from each task dict in the list
            for task_data in tasks_list:
                task = Task(
                    instruction=task_data["instruction"],
                    agent=task_data["agent"],
                    unique_id=task_data["unique_id"],
                    accepts_inputs_from=task_data.get(
                        "accepts_inputs_from", []
                    ),
                )
                tasks.append(task)
            # Create a Tier object and store it in the tiers dictionary
            self.tiers[tier_id] = Tier(tier_id=tier_id, tasks=tasks)

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the RouterOutput.
        Note: The tier keys are converted to strings since JSON keys must be strings.
        """
        return {
            "tiers": {
                str(tier_id): tier.to_dict()
                for tier_id, tier in self.tiers.items()
            }
        }

    def __repr__(self):
        return f"RouterOutput(tiers={self.tiers})"
