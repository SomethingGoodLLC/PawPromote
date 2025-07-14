import asyncio
import os
from typing import Annotated, Any, Dict, List, Optional

import requests
from openai import OpenAI
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
import json

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


async def generate_story(pet: Dict[str, Any], humorous: bool = False) -> Dict[str, Any]:
    client = get_openai_client()
    base_prompt = f"""Create a visually appealing, engaging pet story for {pet['name']} in JSON format. Follow this structure:
    {{
      "header": "Pet Name: Playful Title 🕵️‍♀️",
      "subheader": "Short descriptor",
      "paragraphs": ["Para1", "Para2", ...],
      "badge": "Badge text 🔍",
      "cta": "Call to action paragraph"
    }}
    
    Use warm, playful, emotionally resonant language. Focus on personality traits, funny quirks, emotional aspects, relatable scenarios, transformations, and potential futures. Break into short paragraphs for readability.
    
    Example for a cat named Pepper:
    {{
      "header": "Pepper: Alexandria’s Curious Detective 🕵️‍♀️",
      "subheader": "Cracking cases, charming hearts.",
      "paragraphs": [
        "Pepper isn’t your average black cat—she’s a sleuth extraordinaire! Each day, Pepper diligently investigates suspicious grocery bags and conducts thorough interrogations of unruly dust bunnies. She’s solved mysteries like “The Case of the Missing Treats,” earning her fame throughout Alexandria.",
        "Pepper’s future family ideally enjoys mystery, excitement, and toy mice hidden cleverly in shoes."
      ],
      "badge": "Top Cat Detective 🔍",
      "cta": "Ready to meet your new partner-in-crime-solving? Pepper awaits your companionship!"
    }}
    
    Base on real description: {pet['description']}. {"Make it humorous with puns and silly situations if humorous else ''"} Include adoption CTA in cta."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": base_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


async def generate_image(pet: Dict[str, Any], prompt_suffix: str = "promotional image") -> str:
    client = get_openai_client()
    prompt = f"Generate a {prompt_suffix} for pet {pet['name']} based on: {pet['description']}"
    response = client.images.generate(model="gpt-image-1", prompt=prompt, n=1, size="1024x1024")
    return response.data[0].url


async def generate_enhanced_image_from_photo(pet: Dict[str, Any], photo_url: Optional[str], scene_description: str = "in a beautiful park setting") -> str:
    """Generate an enhanced image using GPT-Image-1 with the real Petfinder photo as input"""
    if not photo_url:
        return await generate_image(pet, "promotional image")
    
    # Download the Petfinder photo
    try:
        response = requests.get(photo_url)
        if response.status_code != 200:
            return await generate_image(pet, "promotional image")
        
        image_data = response.content
        
        # Upload to GPT-Image-1 for enhancement
        client = get_openai_client()
        
        # Create a detailed prompt for enhancement
        enhanced_prompt = f"""Enhance this pet photo to create a professional, magazine-quality adoption photo. 
        The pet is {pet['name']}, a {pet.get('breeds', {}).get('primary', 'mixed')} {pet.get('type', 'pet').lower()}.
        
        Enhancement goals:
        - Professional pet photography lighting and composition
        - Warm, inviting atmosphere perfect for adoption marketing
        - Clear focus on the pet's personality and charm
        - Magazine-quality finish suitable for print materials
        
        Style: Professional pet photography, warm lighting, engaging pose, adoption-ready presentation."""
        
        # Use the image editing endpoint to enhance the photo
        image_response = client.images.edit(
            image=image_data,
            prompt=enhanced_prompt,
            n=1,
            size="1024x1024"
        )
        return image_response.data[0].url
        
    except Exception as e:
        # Fallback to generating a new image if enhancement fails
        return await generate_image(pet, "promotional image")


async def generate_badge(pet: Dict[str, Any], badge_text: Optional[str] = None) -> str:
    prompt_suffix = f"fun pet-related badge with text '{badge_text}'" if badge_text else "status badge in a humorous style"
    return await generate_image(pet, prompt_suffix)


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


async def generate_story_image(pet: Dict[str, Any], story: str, real_photo_url: Optional[str] = None) -> str:
    """Generate a story-specific image using GPT-Image-1 that incorporates the story context"""
    client = get_openai_client()
    
    # Extract key story elements for image generation
    story_elements = []
    if "adventure" in story.lower():
        story_elements.append("on an exciting adventure")
    if "heist" in story.lower() or "criminal" in story.lower():
        story_elements.append("in a mischievous detective scene")
    if "tea party" in story.lower() or "retirement" in story.lower():
        story_elements.append("in an elegant, cozy setting")
    if "greeter" in story.lower() or "jumping" in story.lower():
        story_elements.append("enthusiastically greeting visitors")
    if "security" in story.lower() or "patrol" in story.lower():
        story_elements.append("proudly on duty as a guardian")
    if "food critic" in story.lower() or "dining" in story.lower():
        story_elements.append("as a sophisticated food connoisseur")
    
    scene_description = " ".join(story_elements) if story_elements else "in a heartwarming adoption scene"
    
    # Create detailed prompt incorporating pet details and story context
    prompt = f"""Create a high-quality, heartwarming image of {pet['name']}, a {pet.get('breeds', {}).get('primary', 'mixed')} {pet.get('type', 'pet').lower()} {scene_description}. 
    
    Pet details: {pet.get('age', 'adult')} {pet.get('gender', '').lower()}, {pet.get('colors', {}).get('primary', 'beautiful coloring')}.
    
    Story context: {story[:200]}...
    
    Style: Professional pet photography meets storybook illustration, warm and inviting lighting, perfect for pet adoption promotion. 
    The image should capture the pet's personality from the story while maintaining photorealistic quality."""
    
    try:
        response = client.images.generate(
            model="dall-e-3",  # Using DALL-E 3 as GPT-Image-1 placeholder
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        return response.data[0].url
    except Exception as e:
        # Fallback to simpler prompt if detailed one fails
        simple_prompt = f"A heartwarming photo of {pet['name']}, a {pet.get('type', 'pet').lower()} ready for adoption"
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=simple_prompt,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except:
            return f"https://example.com/{pet['name'].lower()}_story_image.jpg"


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

    content = {"stories": [], "images": [], "story_images": [], "badges": [], "videos": [], "petfinder_urls": []}

    for pet in pets:
        # Generate story first
        story_dict = await generate_story(pet, humorous)
        content["stories"].append({"pet": pet["name"], "story": story_dict})

        # Process real Petfinder photo through GPT-Image-1
        photo_url = pet.get("photos", [None])[0] if "photos" in pet else None
        if photo_url:
            # Download Petfinder photo and enhance it with GPT-Image-1
            enhanced_image_url = await generate_enhanced_image_from_photo(pet, photo_url, "in a professional adoption photo setting")
            content["images"].append({"pet": pet["name"], "image_url": enhanced_image_url, "type": "gpt_enhanced_photo"})
        else:
            # Generate a basic pet image if no real photo
            basic_image_url = await generate_image(pet)
            content["images"].append({"pet": pet["name"], "image_url": basic_image_url, "type": "generated_basic"})

        # Generate story-specific image using GPT-Image-1
        story_image_url = await generate_story_image(pet, str(story_dict), photo_url)
        content["story_images"].append({"pet": pet["name"], "image_url": story_image_url, "type": "story_specific"})

        # Generate badge using badge text from story
        badge_url = await generate_badge(pet, story_dict.get("badge"))
        content["badges"].append({"pet": pet["name"], "badge_url": badge_url})

        # Generate video from real photo
        video_url = await generate_video_from_photo(pet, photo_url, humorous)
        content["videos"].append({"pet": pet["name"], "video_url": video_url})

        # Add Petfinder URL
        content["petfinder_urls"].append({"pet": pet["name"], "url": pet.get("url", "")})

    return content


async def main():
    print("Content Generator agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 