from swiftagent import SwiftAgent
from swiftagent.memory import SemanticMemory

from swiftagent.prebuilt.actions.exa import exa_actions

SemanticMemory("sm1").container_collection.clear()

memory = SemanticMemory("sm1").ingest(
    [
        "https://www.poshantracker.in/pdf/Awareness/MilletsRecipeBook2023_Low%20Res_V5.pdf",
        "https://www.cardiff.ac.uk/__data/assets/pdf_file/0003/123681/Recipe-Book.pdf",
    ]
)

recipe_agent = SwiftAgent(
    name="RecipeAgent",
    description="Agent that is able to build recipes",
    instruction=(
        "Search for recipes based on the ingredients and time available from your memory."
        + "Include the exact calories, preparation time, cooking instructions, and highlight allergens for the recommended recipes."
        + "Always search exa for recipe links or tips related to the recipes apart from knowledge base."
        + "Provide a list of recipes that match the user's requirements and preferences."
    ),
)

recipe_agent.add_actionset(exa_actions)
recipe_agent.add_semantic_memory_section(memory)

import asyncio


async def main():
    await recipe_agent.run(
        task="I have potatoes, tomatoes, onions, garlic, ginger, and chicken. Suggest me a quick recipe for dinner"
    )


asyncio.run(main())
