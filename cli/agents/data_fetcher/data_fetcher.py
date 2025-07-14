import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZWQ0OTM1NS1jNzljLTRhZDAtOGIzYS1mMGI5ZTJiYmI1MDkiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.EX7gQXrRMFGdcZx_fTtxU4vLdmmyiXMGXAEiJ8dGL3Q" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="data_fetcher",
    description="Fetches pet data and photos from Petfinder API."
)
async def data_fetcher(
    agent_context: GenAIContext,
    test_arg: Annotated[
        str,
        "This is a test argument. Your agent can have as many parameters as you want. Feel free to rename or adjust it to your needs.",  # noqa: E501
    ],
):
    """Fetches pet data and photos from Petfinder API."""
    return "Hello, World!"


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
