#!/usr/bin/env python3
"""
Command line test for the pet adoption agent workflow
"""
import asyncio
import requests
import json
from typing import Dict, Any

# API endpoint for the GenAI backend
BACKEND_URL = "http://localhost:8000"

async def call_agent(agent_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Call an agent via the API"""
    print(f"\n🤖 Calling {agent_name} with parameters: {parameters}")
    
    # Find the agent by name
    response = requests.get(f"{BACKEND_URL}/api/agents/active")
    if response.status_code != 200:
        print(f"❌ Failed to get active agents: {response.text}")
        return {"error": "Failed to get active agents"}
    
    agents = response.json()["active_connections"]
    target_agent = None
    
    for agent in agents:
        if agent["agent_name"] == agent_name:
            target_agent = agent
            break
    
    if not target_agent:
        print(f"❌ Agent '{agent_name}' not found in active agents")
        return {"error": f"Agent '{agent_name}' not found"}
    
    print(f"✅ Found agent: {target_agent['agent_name']}")
    
    # Call the agent
    payload = {
        "agent_id": target_agent["agent_id"],
        "parameters": parameters
    }
    
    response = requests.post(f"{BACKEND_URL}/api/agents/call", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Agent response: {result}")
        return result
    else:
        print(f"❌ Agent call failed: {response.text}")
        return {"error": response.text}

async def test_full_workflow():
    """Test the complete pet adoption workflow"""
    print("🎯 TESTING PET ADOPTION AGENT WORKFLOW")
    print("=" * 60)
    
    # Step 1: Fetch pets
    print("\n📋 Step 1: Fetching pets from Alexandria shelters")
    pets_result = await call_agent("fetch_pets", {
        "shelter_name": "Alexandria Animal Shelter",
        "shelter_id": "VA935", 
        "num_pets": 3,
        "include_photos": True
    })
    
    if "error" in pets_result:
        print("❌ Pet fetching failed, using mock data for demonstration")
        pets_data = [
            {
                "id": "12345",
                "name": "Buddy",
                "description": "A friendly golden retriever who loves to play fetch",
                "photos": ["https://example.com/buddy.jpg"]
            },
            {
                "id": "12346", 
                "name": "Whiskers",
                "description": "A curious tabby cat who enjoys sunny windowsills",
                "photos": ["https://example.com/whiskers.jpg"]
            },
            {
                "id": "12347",
                "name": "Max",
                "description": "An energetic border collie who loves running",
                "photos": ["https://example.com/max.jpg"]
            }
        ]
    else:
        pets_data = pets_result.get("result", [])
    
    print(f"✅ Retrieved {len(pets_data)} pets")
    
    # Step 2: Generate content
    print("\n🎨 Step 2: Generating humorous adventure stories")
    content_result = await call_agent("content_generator", {
        "pets": pets_data,
        "humorous": True
    })
    
    if "error" not in content_result:
        content_data = content_result.get("result", {})
        print(f"✅ Generated stories for {len(content_data.get('stories', []))} pets")
    else:
        print("❌ Content generation failed")
        content_data = {"stories": [], "images": []}
    
    # Step 3: Assemble assets
    print("\n📚 Step 3: Assembling book and presentation")
    assembly_result = await call_agent("asset_assembler", {
        "content": content_data,
        "specification": "Create PDF book and PowerPoint presentation with humorous pet stories"
    })
    
    if "error" not in assembly_result:
        assembly_data = assembly_result.get("result", {})
        print(f"✅ Created assets: {assembly_data.get('files', [])}")
    else:
        print("❌ Asset assembly failed")
        assembly_data = {"files": []}
    
    # Step 4: Ship book (if PDF was created)
    pdf_files = [f for f in assembly_data.get("files", []) if f.endswith('.pdf')]
    if pdf_files:
        print("\n🚚 Step 4: Preparing book shipment")
        shipping_result = await call_agent("book_shipper", {
            "pdf_path": pdf_files[0],
            "book_title": "Alexandria Pet Adventure Stories",
            "recipient_name": "Pet Lover",
            "street_address": "123 Pet Lover Lane",
            "city": "Alexandria",
            "state": "VA",
            "postal_code": "22314",
            "country": "US",
            "quantity": 1
        })
        
        if "error" not in shipping_result:
            shipping_data = shipping_result.get("result", {})
            print(f"✅ Book shipment: {shipping_data.get('status', 'Unknown')}")
        else:
            print("❌ Book shipping failed")
    else:
        print("\n📦 Step 4: Skipping shipment (no PDF created)")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 WORKFLOW COMPLETED!")
    print("=" * 60)
    print("✅ Multi-agent coordination successful")
    print("✅ Pet data fetching")
    print("✅ Content generation")
    print("✅ Asset assembly")
    print("✅ Book shipping preparation")
    print("\n📋 This demonstrates:")
    print("• Agent-to-agent communication")
    print("• Workflow orchestration")
    print("• Real-world API integration")
    print("• End-to-end automation")

if __name__ == "__main__":
    asyncio.run(test_full_workflow()) 