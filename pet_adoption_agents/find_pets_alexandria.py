#!/usr/bin/env python3
"""
Standalone script to find pets near Alexandria, VA using Petfinder API
"""

import os
import asyncio
import aiohttp
import json
from typing import List, Dict, Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Set your API keys from environment variables
PETFINDER_API_KEY = os.getenv("PETFINDER_API_KEY")
PETFINDER_API_SECRET = os.getenv("PETFINDER_API_SECRET")

class PetfinderClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None
        self.base_url = "https://api.petfinder.com/v2"
    
    async def get_access_token(self) -> str:
        """Get OAuth access token from Petfinder API"""
        token_url = f"{self.base_url}/oauth2/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    return self.access_token
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get access token: {response.status} - {error_text}")
    
    async def search_pets(self, location: str = "Alexandria, VA", limit: int = 5) -> List[Dict[str, Any]]:
        """Search for pets near a location"""
        if not self.access_token:
            await self.get_access_token()
        
        search_url = f"{self.base_url}/animals"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "location": location,
            "limit": limit,
            "status": "adoptable",
            "sort": "distance"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("animals", [])
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to search pets: {response.status} - {error_text}")

def format_pet_info(pet: Dict[str, Any]) -> str:
    """Format pet information for display"""
    name = pet.get("name", "Unknown")
    species = pet.get("species", "Unknown")
    breed = pet.get("breeds", {}).get("primary", "Mixed")
    age = pet.get("age", "Unknown")
    gender = pet.get("gender", "Unknown")
    size = pet.get("size", "Unknown")
    
    # Get organization info
    org = pet.get("organization_id", "Unknown")
    
    # Get photos
    photos = pet.get("photos", [])
    photo_url = photos[0].get("large", "No photo") if photos else "No photo"
    
    # Get description
    description = pet.get("description", "No description available")
    if description and len(description) > 200:
        description = description[:200] + "..."
    
    # Get contact info
    contact = pet.get("contact", {})
    email = contact.get("email", "No email")
    phone = contact.get("phone", "No phone")
    
    # Get address
    address = contact.get("address", {})
    city = address.get("city", "Unknown")
    state = address.get("state", "Unknown")
    
    return f"""
🐾 {name} ({species})
   Breed: {breed}
   Age: {age} | Gender: {gender} | Size: {size}
   Location: {city}, {state}
   Organization ID: {org}
   Photo: {photo_url}
   Contact: {email} | {phone}
   Description: {description}
   
   Petfinder URL: https://www.petfinder.com/petdetail/{pet.get('id', '')}
"""

async def main():
    """Main function to find pets near Alexandria, VA"""
    print("🔍 Searching for pets near Alexandria, VA...")
    print("=" * 60)
    
    # Check if API keys are set
    if not PETFINDER_API_KEY or not PETFINDER_API_SECRET:
        print("❌ Please set your Petfinder API keys!")
        print("   Make sure your .env file contains:")
        print("   PETFINDER_API_KEY=your_key_here")
        print("   PETFINDER_API_SECRET=your_secret_here")
        print("\n   Or set environment variables:")
        print("   export PETFINDER_API_KEY='your_key_here'")
        print("   export PETFINDER_API_SECRET='your_secret_here'")
        return
    
    try:
        # Create client and search for pets
        client = PetfinderClient(PETFINDER_API_KEY, PETFINDER_API_SECRET)
        pets = await client.search_pets("Alexandria, VA", 5)
        
        if not pets:
            print("❌ No pets found near Alexandria, VA")
            return
        
        print(f"✅ Found {len(pets)} pets near Alexandria, VA:")
        print("=" * 60)
        
        for i, pet in enumerate(pets, 1):
            print(f"\n{i}. {format_pet_info(pet)}")
            print("-" * 60)
        
        # Also save to JSON file for reference
        with open("pets_alexandria_va.json", "w") as f:
            json.dump(pets, f, indent=2)
        
        print(f"\n💾 Full pet data saved to: pets_alexandria_va.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API keys are correct")
        print("2. Ensure you have internet connection")
        print("3. Verify your Petfinder API account is active")

if __name__ == "__main__":
    asyncio.run(main()) 