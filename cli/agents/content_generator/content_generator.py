import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmYTVjMTRlMi00NWQ3LTQ3MjctOGFhZS02NDQ4YmQyZWUwMGQiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.ci1Irpoxt5RX5lqKDEf8k05Hi1uSngeR3OGbVWsailY" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="content_generator",
    description="Generates humorous stories, images, badges, videos using OpenAI (Sora) or Google Veo3, conditioned on real pet photos."
)
async def content_generator(
    agent_context: GenAIContext,
    test_arg: Annotated[
        str,
        "This is a test argument. Your agent can have as many parameters as you want. Feel free to rename or adjust it to your needs.",  # noqa: E501
    ],
):
    """Generates humorous stories, images, badges, videos using OpenAI (Sora) or Google Veo3, conditioned on real pet photos."""
    return "Hello, World!"


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
