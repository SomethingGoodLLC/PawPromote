# Pet Adoption Agents - End-to-End Guide

## 🚀 Quick Start: Find Pets Near Alexandria, VA

### Option 1: Simple Pet Search (Recommended for Testing)

1. **Set your API keys** (you mentioned they're "in there"):
   ```bash
   export PETFINDER_API_KEY="your_actual_key_here"
   export PETFINDER_API_SECRET="your_actual_secret_here"
   ```

2. **Install dependencies**:
   ```bash
   cd pet_adoption_agents
   uv add aiohttp python-dotenv
   ```

3. **Run the pet finder**:
   ```bash
   uv run python find_pets_alexandria.py
   ```

This will show you 5 real pets available for adoption near Alexandria, VA!

---

## 🏗️ Full System Setup (GenAI AgentOS Integration)

### Prerequisites

1. **GenAI AgentOS Backend Running**:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Environment Variables**:
   ```bash
   # Required for Petfinder API
   export PETFINDER_API_KEY="your_key"
   export PETFINDER_API_SECRET="your_secret"
   
   # Optional for Cloudera (if you have it)
   export IMPALA_HOST="your_impala_host"
   export IMPALA_PORT="21000"
   
   # GenAI AgentOS Backend
   export BACKEND_URL="http://localhost:8000"
   ```

### Step-by-Step Agent Setup

#### 1. Register All Agents

```bash
cd pet_adoption_agents

# Register Data Fetcher
cd data_fetcher
uv run python main.py &
DATA_FETCHER_PID=$!

# Register Master Orchestrator  
cd ../master_orchestrator
uv run python main.py &
MASTER_PID=$!

# Register Content Generator
cd ../content_generator
uv run python main.py &
CONTENT_PID=$!

# Register Asset Assembler
cd ../asset_assembler
uv run python main.py &
ASSET_PID=$!

# Register Book Shipper
cd ../book_shipper
uv run python main.py &
BOOK_PID=$!
```

#### 2. Verify Agents Are Running

```bash
curl http://localhost:8000/agents/active
```

You should see all 5 agents listed as active.

#### 3. Test the Full Workflow

**Option A: Via API Call**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find 3 pets from ASPCA shelter NY114 and create adventure stories with videos and ship books",
    "agent_id": "master_orchestrator"
  }'
```

**Option B: Via Frontend** (if running)
1. Open http://localhost:3000
2. Navigate to Chat
3. Select "Master Orchestrator" agent
4. Send message: "Find 3 pets from ASPCA shelter NY114 and create adventure stories with videos and ship books"

---

## 🔄 How the Full System Works

### Workflow Overview

```
User Request → Master Orchestrator → Data Fetcher → Content Generator → Asset Assembler → Book Shipper
```

### Detailed Flow

1. **Master Orchestrator** receives request and parses:
   - Number of pets needed
   - Shelter information
   - Content requirements (stories, videos, books)

2. **Data Fetcher** (`@session.bind 'fetch_pets'`):
   - Fetches pets from Petfinder API
   - Gets high-quality photos (with web scraping fallback)
   - Queries Cloudera Impala for real-time updates
   - Polls for status changes (adoptable → pending → adopted)

3. **Content Generator** creates:
   - Adventure stories for each pet
   - Video concepts and scripts

4. **Asset Assembler** combines:
   - Pet photos + stories + videos
   - Creates multimedia presentations

5. **Book Shipper** handles:
   - Physical book creation and shipping
   - Tracking and notifications

### Real-Time Updates

The Data Fetcher continuously monitors pet status changes:
- Polls Cloudera Impala every 30 seconds
- Sends updates to Master Orchestrator when status changes
- Triggers workflow adjustments (e.g., remove adopted pets)

---

## 🧪 Testing Options

### 1. Unit Testing
```bash
cd tests
python test_pet_adoption_standalone.py
```

### 2. Demo Simulation
```bash
cd tests
python demo_test.py
```

### 3. Live API Testing
```bash
cd pet_adoption_agents
python find_pets_alexandria.py
```

### 4. Integration Testing (requires full system)
```bash
cd tests
pytest TestAgents/test_data_fetcher.py -v
pytest TestAgents/test_master_orchestrator.py -v
```

---

## 📊 Monitoring and Debugging

### Check Agent Status
```bash
curl http://localhost:8000/agents/active | jq
```

### View Agent Logs
```bash
# Each agent logs to console when running
# Check the terminal where you started each agent
```

### Test Individual Agent Functions

**Test Data Fetcher**:
```python
import asyncio
from data_fetcher.main import fetch_pets

async def test():
    result = await fetch_pets("ASPCA", "NY114", 3, True)
    print(result)

asyncio.run(test())
```

**Test Master Orchestrator**:
```python
import asyncio
from master_orchestrator.main import master_orchestrator

async def test():
    result = await master_orchestrator("Find 3 pets from ASPCA shelter NY114 with adventure stories")
    print(result)

asyncio.run(test())
```

---

## 🚨 Troubleshooting

### Common Issues

1. **"No agents found"**:
   - Make sure GenAI AgentOS backend is running
   - Verify agents are registered (check active agents endpoint)

2. **"API key invalid"**:
   - Double-check your Petfinder API credentials
   - Ensure environment variables are set correctly

3. **"Connection refused"**:
   - Verify backend is running on correct port
   - Check firewall/network settings

4. **"No pets found"**:
   - Try different shelter IDs or locations
   - Check Petfinder API status

### Debug Mode

Add this to any agent's main.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📋 Quick Reference

### Key Files
- `find_pets_alexandria.py` - Simple pet search script
- `data_fetcher/main.py` - Main data fetching agent
- `master_orchestrator/main.py` - Workflow coordinator
- `tests/demo_test.py` - Complete workflow simulation

### Key Endpoints
- `GET /agents/active` - List active agents
- `POST /chat` - Send message to agent
- `GET /agents/{agent_id}` - Get agent details

### Environment Variables
```bash
PETFINDER_API_KEY=your_key
PETFINDER_API_SECRET=your_secret
IMPALA_HOST=your_impala_host
IMPALA_PORT=21000
BACKEND_URL=http://localhost:8000
```

---

## 🎯 Next Steps

1. **Start Simple**: Run `find_pets_alexandria.py` first
2. **Test Workflow**: Use `demo_test.py` to see the full simulation
3. **Go Live**: Set up the full agent system with GenAI AgentOS
4. **Customize**: Modify agents for your specific needs

Need help? Check the logs, verify your API keys, and ensure all services are running! 