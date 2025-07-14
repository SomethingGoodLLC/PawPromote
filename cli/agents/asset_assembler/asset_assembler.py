import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTljZTU3NS0yMTMyLTQ3YjctOWIzYy1lZjdlMWE3NmZiY2YiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.HwKMqQoWTKjtfVHv5-TGanyYoK53hsScHEAbY-SR840" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="asset_assembler",
    description="Assembles stories and assets into books, PDFs, PPTs."
)
async def asset_assembler(
    agent_context: GenAIContext,
    test_arg: Annotated[
        str,
        "This is a test argument. Your agent can have as many parameters as you want. Feel free to rename or adjust it to your needs.",  # noqa: E501
    ],
):
    """Assembles stories and assets into books, PDFs, PPTs."""
    return "Hello, World!"


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
