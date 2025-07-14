import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjNDgwODI1OS03Y2ViLTQxOWEtYTQ2Ni0yMjlkN2IyNGEwMmIiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.31xNxTxZ2TZbcdXWJ0nWaucHTqnsdz7WQwoGy_nhDHI" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="master_orchestrator",
    description="Orchestrates the pet adoption promotion workflow by parsing tasks and calling specialized agents."
)
async def master_orchestrator(
    agent_context: GenAIContext,
    test_arg: Annotated[
        str,
        "This is a test argument. Your agent can have as many parameters as you want. Feel free to rename or adjust it to your needs.",  # noqa: E501
    ],
):
    """Orchestrates the pet adoption promotion workflow by parsing tasks and calling specialized agents."""
    return "Hello, World!"


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
