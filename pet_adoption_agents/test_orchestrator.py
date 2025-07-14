#!/usr/bin/env python3
"""
Test the Master Orchestrator with natural language input
"""
import asyncio
import requests
import json

# API endpoint for the GenAI backend
BACKEND_URL = "http://localhost:8000"

async def test_orchestrator():
    """Test the master orchestrator with natural language input"""
    print("🎯 TESTING MASTER ORCHESTRATOR")
    print("=" * 50)
    
    # Natural language task
    task = "Find 3 pets from Alexandria shelters and create adventure stories with videos and ship books"
    
    print(f"📋 Task: {task}")
    print("\n🤖 Calling Master Orchestrator...")
    
    # Find the orchestrator agent
    response = requests.get(f"{BACKEND_URL}/api/agents/active")
    if response.status_code != 200:
        print(f"❌ Failed to get active agents: {response.text}")
        return
    
    agents = response.json()["active_connections"]
    orchestrator = None
    
    for agent in agents:
        if "orchestrat" in agent["agent_name"].lower():
            orchestrator = agent
            break
    
    if not orchestrator:
        print("❌ Master orchestrator not found in active agents")
        print("Available agents:")
        for agent in agents:
            print(f"  - {agent['agent_name']}")
        return
    
    print(f"✅ Found orchestrator: {orchestrator['agent_name']}")
    
    # Call the orchestrator
    payload = {
        "agent_id": orchestrator["agent_id"],
        "parameters": {
            "task_description": task,
            "priority": "high"
        }
    }
    
    print("📤 Sending request to orchestrator...")
    response = requests.post(f"{BACKEND_URL}/api/agents/call", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ ORCHESTRATOR RESPONSE:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
        # Check if workflow was successful
        if "workflow_state" in result:
            state = result["workflow_state"]
            print(f"\n📋 Workflow Status: {state.get('status', 'Unknown')}")
            print(f"📋 Task ID: {state.get('task_id', 'Unknown')}")
            print(f"📋 Completed Steps: {state.get('completed_steps', [])}")
            if state.get('failed_steps'):
                print(f"❌ Failed Steps: {state.get('failed_steps', [])}")
    else:
        print(f"❌ Orchestrator call failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_orchestrator()) 