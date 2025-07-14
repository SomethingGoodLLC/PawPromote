import asyncio
import os
from typing import Annotated, Any, Dict, List, Optional

import requests
from openai import OpenAI
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "placeholder")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", None)  # Set if using Azure
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "placeholder")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")


def get_openai_client() -> OpenAI:
    if AZURE_OPENAI_ENDPOINT:
        return OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=AZURE_OPENAI_ENDPOINT,  # Configure for Azure if using Sora via Azure
            api_version="2023-05-01"  # Example Azure API version; adjust for Sora
        )
    return OpenAI(api_key=OPENAI_API_KEY)


async def generate_story(pet: Dict[str, Any], humorous: bool = False) -> str:
    client = get_openai_client()
    base_prompt = f"Create a heartwarming adventure story for {pet['name']} using real description: {pet['description']}. Include adoption CTA."
    if humorous:
        base_prompt = f"Create a funny, heartwarming adventure story for {pet['name']} using real description: {pet['description']}. Include puns, silly situations, and adoption CTA."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": base_prompt}]
    )
    return response.choices[0].message.content


async def generate_image(pet: Dict[str, Any], prompt_suffix: str = "promotional image") -> str:
    client = get_openai_client()
    prompt = f"Generate a {prompt_suffix} for pet {pet['name']} based on: {pet['description']}"
    response = client.images.generate(model="gpt-image-1", prompt=prompt, n=1, size="1024x1024")
    return response.data[0].url


async def generate_enhanced_image_from_photo(pet: Dict[str, Any], photo_url: Optional[str], scene_description: str = "in a beautiful park setting") -> str:
    """Generate an enhanced image using GPT-Image-1 with detailed description based on real photo"""
    if not photo_url:
        return await generate_image(pet, "promotional image")
    
    # Download and analyze the photo to create a detailed description
    try:
        response = requests.get(photo_url)
        if response.status_code != 200:
            return await generate_image(pet, "promotional image")
        
        # Create a detailed prompt that describes what we want based on the pet's appearance
        # Since gpt-image-1 is text-to-image only, we enhance the description
        enhanced_prompt = f"""Create a high-quality promotional image of a {pet.get('type', 'pet')} named {pet['name']} {scene_description}. 
        Based on this description: {pet['description']}. 
        Style: Professional pet photography, warm lighting, engaging pose, suitable for adoption promotion.
        The {pet.get('type', 'pet')} should look friendly and adoptable."""
        
        client = get_openai_client()
        image_response = client.images.generate(
            model="gpt-image-1", 
            prompt=enhanced_prompt, 
            n=1, 
            size="1024x1024"
        )
        return image_response.data[0].url
        
    except Exception as e:
        # Fallback to regular image generation
        return await generate_image(pet, "promotional image")


async def generate_badge(pet: Dict[str, Any]) -> str:
    return await generate_image(pet, "status badge in a humorous style")


async def generate_video_from_photo(pet: Dict[str, Any], photo_url: Optional[str], humorous: bool = False) -> str:
    if not photo_url:
        return "no_video_generated"  # Fallback if no photo

    # Download photo
    response = requests.get(photo_url)
    if response.status_code != 200:
        return "failed_to_download_photo"
    image_data = response.content

    client = get_openai_client()
    theme = "adventure" if not humorous else "scene, e.g., chasing butterflies comically"
    prompt = f"Animate this real {pet.get('type', 'pet')} in a humorous {theme} based on: {pet['description']}."

    try:
        # Assume Sora image-to-video endpoint (not public yet; placeholder)
        video_response = client.videos.generate(  # Hypothetical call
            model="sora",
            prompt=prompt,
            input_image=image_data,  # Assume binary image data upload
            duration="short"  # Short video clip
        )
        return video_response.data[0].url
    except Exception as e:
        # Fallback to Veo3 via Vertex AI
        vertexai.init(project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)
        model = GenerativeModel("gemini-1.5-pro")  # Use Gemini with Veo integration; adjust for actual Veo3
        image_part = Part.from_data(mime_type="image/jpeg", data=image_data)
        video_response = model.generate_content([image_part, prompt])
        # Assume response provides a GCS URI or downloadable URL
        return video_response.candidates[0].content.parts[0].file_data.file_uri


@session.bind(
    name="content_generator",
    description="Generates humorous stories, images, badges, videos using OpenAI (Sora) or Google Veo3, conditioned on real pet photos."
)
async def content_generator(
    agent_context: GenAIContext,
    pets: Annotated[List[Dict[str, Any]], "List of pet data with names, descriptions, and photo URLs"],
    humorous: Annotated[bool, "Whether to generate humorous content"] = False
) -> Dict[str, Any]:
    agent_context.logger.info(f"Generating content for {len(pets)} pets with humorous={humorous}")

    content = {"stories": [], "images": [], "badges": [], "videos": []}

    for pet in pets:
        story = await generate_story(pet, humorous)
        content["stories"].append({"pet": pet["name"], "story": story})

        # Use enhanced image generation if photo is available
        photo_url = pet.get("photos", [None])[0] if "photos" in pet else None
        if photo_url:
            image_url = await generate_enhanced_image_from_photo(pet, photo_url, "in a cozy home setting ready for adoption")
        else:
            image_url = await generate_image(pet)
        content["images"].append({"pet": pet["name"], "image_url": image_url})

        badge_url = await generate_badge(pet)
        content["badges"].append({"pet": pet["name"], "badge_url": badge_url})

        photo_url = pet.get("photos", [None])[0] if "photos" in pet else None
        video_url = await generate_video_from_photo(pet, photo_url, humorous)
        content["videos"].append({"pet": pet["name"], "video_url": video_url})

    return content


async def main():
    print("Content Generator agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 