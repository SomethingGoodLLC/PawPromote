import asyncio
import os
import time
from typing import Annotated, Any, List, Dict

import requests
import impala.dbapi as impala
from bs4 import BeautifulSoup
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
    name="fetch_pets",
    description="Fetches pet data and photos from Petfinder API."
)
async def fetch_pets(
    agent_context: GenAIContext,
    shelter_name: Annotated[str, "Name of the shelter (e.g., ASPCA)"],
    shelter_id: Annotated[str, "Shelter ID (e.g., NY114)"],
    num_pets: Annotated[int, "Number of pets to fetch"],
    include_photos: Annotated[bool, "Whether to include photos"] = True,
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
        photos = [photo["large"] for photo in animal.get("photos", []) if "large" in photo]
        if include_photos and not photos:
            # fallback scrape
            resp = requests.get(animal["url"])
            soup = BeautifulSoup(resp.text, 'html.parser')
            photo_tags = soup.find_all('img', alt=lambda x: x and 'photo' in x.lower())
            if photo_tags:
                photos = [tag['src'] for tag in photo_tags if 'large' in tag.get('src', '')]
        pets.append({
            "id": animal["id"],
            "name": animal["name"],
            "description": animal["description"],
            "photos": photos
        })

    # Cloudera Impala integration
    host = os.getenv("IMPALA_HOST", "localhost")
    port = int(os.getenv("IMPALA_PORT", "21050"))
    conn = impala.connect(host=host, port=port)
    cursor = conn.cursor()
    pet_ids = [p["id"] for p in pets]
    if pet_ids:
        cursor.execute(f"SELECT id, name, description, photos, status FROM pet_data WHERE id IN ({','.join(map(str, pet_ids))})")
        for row in cursor.fetchall():
            for p in pets:
                if p["id"] == row[0]:
                    p["name"] = row[1]
                    p["description"] = row[2]
                    p["photos"] = row[3].split(',') if row[3] else []
                    p["status"] = row[4]

    # Setup real-time updates
    last_fetch_time = time.time()
    agents = await get_active_agents()
    master_id = get_agent_id(agents, "master_orchestrator")

    async def poll_updates():
        nonlocal last_fetch_time
        while True:
            await asyncio.sleep(60)
            cursor.execute(f"SELECT id, name, description, photos, status FROM pet_data WHERE last_updated > {last_fetch_time}")
            updates = [dict(zip(["id", "name", "description", "photos", "status"], row)) for row in cursor.fetchall()]
            for update in updates:
                update["photos"] = update["photos"].split(',') if update["photos"] else []
            if updates:
                await session.send(client_id=master_id, message={"type": "pet_updates", "updates": updates})
                last_fetch_time = time.time()

    asyncio.create_task(poll_updates())

    return pets


async def main():
    print("Data Fetcher agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 