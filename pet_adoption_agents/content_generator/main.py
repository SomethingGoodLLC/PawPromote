import asyncio
import os
from typing import Annotated, Any, Dict, List

from openai import OpenAI
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "placeholder")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "placeholder")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")


@session.bind(
    name="content_generator",
    description="Generates humorous stories, images, badges, videos using OpenAI (Sora) or Google Veo3, conditioned on real pet photos."
)
async def content_generator(
    agent_context: GenAIContext,
    pets: Annotated[List[Dict[str, Any]], "List of pet data with names, descriptions, and photo URLs"]
) -> Dict[str, Any]:
    agent_context.logger.info(f"Generating content for {len(pets)} pets")

    client = OpenAI(api_key=OPENAI_API_KEY)
    content = {"stories": [], "videos": []}

    for pet in pets:
        # Generate humorous story using GPT
        story_prompt = f"Create a humorous adventure story for a pet named {pet['name']} based on: {pet['description']}"
        story_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": story_prompt}]
        )
        story = story_response.choices[0].message.content
        content["stories"].append({"pet": pet["name"], "story": story})

        # Generate badge/image using DALL-E
        image_prompt = f"Humorous badge for pet {pet['name']} in adventure style"
        image_response = client.images.generate(model="dall-e-3", prompt=image_prompt, n=1)
        badge_url = image_response.data[0].url

        # Generate video: Placeholder for Sora (not public); fallback to Veo3
        video_url = "placeholder_sora_video.mp4"  # Sora integration: client.videos.generate(...) when available
        try:
            vertexai.init(project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)
            model = GenerativeModel("video-veo3")  # Assuming Veo3 model name
            video_prompt = f"Generate a dynamic video of {pet['name']} in a humorous adventure, conditioned on real photo: {pet['photos'][0] if pet['photos'] else ''}"
            video_response = model.generate_content(video_prompt)  # Simplified; adjust for actual API
            video_url = video_response.candidates[0].content.parts[0].file_data.file_uri
        except Exception as e:
            agent_context.logger.error(f"Veo3 fallback failed: {e}")

        content["videos"].append({"pet": pet["name"], "video_url": video_url, "badge_url": badge_url})

    return content


async def main():
    print("Content Generator agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 