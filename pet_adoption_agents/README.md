# Pet Adoption Promotion Workflow

This project implements a multi-agent AI workflow using the GenAI AgentOS framework to boost animal shelter adoptions. It creates humorous, personalized stories for adoptable pets using real pet data and photos, compiles them into books, generates dynamic videos, and ships physical books to donors.

## Overview

The workflow is orchestrated by a Master Agent that receives a plain text task (e.g., 'Promote 3 adoptable pets from ASPCA shelter NY114 with humorous adventure stories: Create a book, generate videos from real photos, and ship to donor at [address]') and coordinates 4 specialized agents:

1. **Data Fetcher**: Retrieves pet data and photos from Petfinder API.
2. **Content Generator**: Uses OpenAI (GPT, DALL-E, Sora placeholder) or Google Veo3 to generate stories, images, badges, and videos conditioned on real photos.
3. **Asset Assembler**: Compiles content into books (PDF), presentations (PPT).
4. **Book Shipper**: Ships physical books via Lulu API.

The agents are registered as GenAI Agents in the framework.

## Prerequisites

- GenAI AgentOS framework running (see main repo README).
- UV installed for dependency management.
- API Keys: Set as environment variables (e.g., in `.env`):
  - `OPENAI_API_KEY`
  - `PETFINDER_API_KEY` and `PETFINDER_API_SECRET` (from Petfinder.com)
  - `GOOGLE_PROJECT_ID` and `GOOGLE_LOCATION` (for Vertex AI / Veo3)
  - `LULU_API_KEY` (from Lulu.com developers)

## Setup

1. Navigate to the folder: `cd pet_adoption_agents/`
2. For each agent subdirectory (e.g., `master_orchestrator/`):
   - `uv venv` (create virtual environment)
   - `uv sync` (install dependencies from pyproject.toml)
3. Register agents using the CLI (from the repo's `cli/` directory):
   ```bash
   python cli.py register_agent --name master_orchestrator --description "Orchestrates the pet adoption promotion workflow by parsing tasks and calling specialized agents."
   python cli.py register_agent --name data_fetcher --description "Fetches pet data and photos from Petfinder API."
   python cli.py register_agent --name content_generator --description "Generates humorous stories, images, badges, videos using OpenAI (Sora) or Google Veo3, conditioned on real pet photos."
   python cli.py register_agent --name asset_assembler --description "Assembles stories and assets into books, PDFs, PPTs."
   python cli.py register_agent --name book_shipper --description "Ships physical books using Lulu API."
   ```
4. Replace `PLACEHOLDER_JWT` in each `main.py` with the JWT from registration.

## Running the Agents

In each agent's directory:
- Activate venv: `source .venv/bin/activate`
- Run: `uv run python main.py`

## Testing the Workflow

Invoke the master_orchestrator via the GenAI framework (e.g., through the frontend chat or API). Provide a task string as input.

## Notes
- Sora API is a placeholder (not publicly available); falls back to Google Veo3.
- Expand parsing logic in master_orchestrator for more complex tasks.
- Outputs (PDFs, PPTs, videos) are saved locally; shipping uses Lulu for physical books.

For issues, refer to the main GenAI AgentOS repo or extend the agents as needed. 