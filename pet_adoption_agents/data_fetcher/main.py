import asyncio
import os
from typing import Annotated, Any, List, Dict

import requests
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)

PETFINDER_API_KEY = os.getenv("PETFINDER_API_KEY", "placeholder")
PETFINDER_API_SECRET = os.getenv("PETFINDER_API_SECRET", "placeholder")
PETFINDER_BASE_URL = "https://api.petfinder.com/v2"


@session.bind(
    name="data_fetcher",
    description="Fetches pet data and photos from Petfinder API."
)
async def data_fetcher(
    agent_context: GenAIContext,
    shelter_name: Annotated[str, "Name of the shelter (e.g., ASPCA)"],
    shelter_id: Annotated[str, "Shelter ID (e.g., NY114)"],
    num_pets: Annotated[int, "Number of pets to fetch"]
) -> List[Dict[str, Any]]:
    agent_context.logger.info(f"Fetching {num_pets} pets from {shelter_name} ({shelter_id})")

    # Get access token
    token_response = requests.post(
        f"{PETFINDER_BASE_URL}/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": PETFINDER_API_KEY,
            "client_secret": PETFINDER_API_SECRET,
        }
    )
    token = token_response.json().get("access_token")

    # Fetch pets
    headers = {"Authorization": f"Bearer {token}"}
    params = {"organization": shelter_id, "limit": num_pets, "status": "adoptable"}
    response = requests.get(f"{PETFINDER_BASE_URL}/animals", headers=headers, params=params)
    animals = response.json().get("animals", [])

    # Extract data and photos
    pets = []
    for animal in animals:
        pets.append({
            "name": animal["name"],
            "description": animal["description"],
            "photos": [photo["large"] for photo in animal.get("photos", []) if "large" in photo]
        })

    return pets


async def main():
    print("Data Fetcher agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 