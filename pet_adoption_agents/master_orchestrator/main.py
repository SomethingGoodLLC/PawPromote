import asyncio
import os
import re
from typing import Annotated, Any, Dict, List

import requests
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


async def get_active_agents():
    response = requests.get(
        f"{BACKEND_URL}/api/agents/active",
        headers={"X-API-KEY": AGENT_JWT},
        params={"agent_type": "genai"},
    )
    if response.status_code == 200:
        return response.json()["active_connections"]
    else:
        raise Exception(f"Failed to get active agents: {response.text}")


def get_agent_id(agents: list[Dict[str, Any]], name: str) -> str:
    for agent in agents:
        if agent["name"] == name:
            return agent["id"]
    raise Exception(f"Agent {name} not found")


@session.bind(
    name="master_orchestrator",
    description="Orchestrates the pet adoption promotion workflow by parsing tasks and calling specialized agents."
)
async def master_orchestrator(
    agent_context: GenAIContext,
    task: Annotated[str, "The plain text task description (e.g., 'Promote 3 adoptable pets from ASPCA shelter NY114 with humorous adventure stories: Create a book, generate videos from real photos, and ship to donor at [address]')"]
):
    agent_context.logger.info("Starting master_orchestrator with task: " + task)

    # Parse task
    match = re.match(r"Promote (\d+) adoptable pets from ([\w\s]+) shelter (\w+) with .* stories: .* ship to donor at ([\w\s\[\]]+)", task)
    if not match:
        return {"error": "Invalid task format"}
    num_pets, shelter_name, shelter_id, address = match.groups()
    num_pets = int(num_pets)
    humorous = "humorous" in task.lower()  # Detect humor option

    # Fetch active agents
    agents = await get_active_agents()

    # Get IDs
    fetcher_id = get_agent_id(agents, "data_fetcher")
    generator_id = get_agent_id(agents, "content_generator")
    assembler_id = get_agent_id(agents, "asset_assembler")
    shipper_id = get_agent_id(agents, "book_shipper")

    # Step 1: Fetch pet data (including photos for video generation)
    fetcher_input = {"shelter_name": shelter_name, "shelter_id": shelter_id, "num_pets": num_pets, "include_photos": True}
    pets_response = await session.send(client_id=fetcher_id, message=fetcher_input)
    pets = pets_response.response

    # Step 2: Generate content (delegate with humor option and real photos)
    generator_input = {"pets": pets, "humorous": humorous}
    content_response = await session.send(client_id=generator_id, message=generator_input)
    content = content_response.response

    # Step 3: Assemble assets
    assembler_input = {"content": content}
    assets_response = await session.send(client_id=assembler_id, message=assembler_input)
    book_file = assets_response.response.get("book_file")

    # Step 4: Ship book
    shipper_input = {"book_file": book_file, "address": address}
    shipping_response = await session.send(client_id=shipper_id, message=shipper_input)
    confirmation = shipping_response.response

    return {"status": "completed", "confirmation": confirmation}


@session.bind(
    name="pet_updates",
    description="Receives pet data updates."
)
async def pet_updates(
    agent_context: GenAIContext,
    updates: Annotated[List[Dict[str, Any]], "List of updated pet data"]
):
    agent_context.logger.info(f"Received pet updates: {updates}")
    # TODO: handle updates, perhaps trigger regeneration or notify


async def main():
    print("Master Orchestrator agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 