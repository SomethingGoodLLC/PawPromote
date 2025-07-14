import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkMGZkMjQ4MC0yMTQxLTQxYTAtOGY0My05OTkwNTc3ZjY3MmEiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.IPtSYWAY7Qh8LM_1Q2egcA05AoeBBU60eSSkze3BiCk" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="book_shipper",
    description="Ships physical books using Lulu API."
)
async def book_shipper(
    agent_context: GenAIContext,
    test_arg: Annotated[
        str,
        "This is a test argument. Your agent can have as many parameters as you want. Feel free to rename or adjust it to your needs.",  # noqa: E501
    ],
):
    """Ships physical books using Lulu API."""
    return "Hello, World!"


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
