import asyncio
import os
from typing import Annotated, Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

import requests
from openai import OpenAI
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    # If python-dotenv is not installed, try to load manually
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "placeholder")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", None)  # Set if using Azure
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "placeholder")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

print(f"🔑 OpenAI API Key loaded: {'✅ Valid' if OPENAI_API_KEY != 'placeholder' and len(OPENAI_API_KEY) > 20 else '❌ Invalid/Missing'}")
print(f"🔑 Key length: {len(OPENAI_API_KEY)} characters")

# Global session directory for storing images
CURRENT_SESSION_DIR = None

def create_session_directory() -> str:
    """Create a unique session directory for storing generated images"""
    global CURRENT_SESSION_DIR
    if CURRENT_SESSION_DIR is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = f"pet_story_session_{timestamp}"
        CURRENT_SESSION_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_content", session_name)
        
        # Create the directory structure
        Path(CURRENT_SESSION_DIR).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(CURRENT_SESSION_DIR, "images")).mkdir(exist_ok=True)
        Path(os.path.join(CURRENT_SESSION_DIR, "original_photos")).mkdir(exist_ok=True)
        Path(os.path.join(CURRENT_SESSION_DIR, "enhanced_images")).mkdir(exist_ok=True)
        Path(os.path.join(CURRENT_SESSION_DIR, "story_images")).mkdir(exist_ok=True)
        Path(os.path.join(CURRENT_SESSION_DIR, "ghibli_images")).mkdir(exist_ok=True)
        Path(os.path.join(CURRENT_SESSION_DIR, "badges")).mkdir(exist_ok=True)
        
        print(f"📁 Created session directory: {CURRENT_SESSION_DIR}")
    
    return CURRENT_SESSION_DIR

def download_and_save_image(image_url: str, pet_name: str, image_type: str, file_extension: str = "png") -> str:
    """Download an image from URL and save it locally, returning the local path"""
    if not image_url or image_url.startswith("https://example.com"):
        return image_url  # Return placeholder as-is
    
    session_dir = create_session_directory()
    
    try:
        # Create safe filename
        safe_pet_name = "".join(c for c in pet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_pet_name = safe_pet_name.replace(' ', '_').lower()
        filename = f"{safe_pet_name}_{image_type}.{file_extension}"
        
        # Determine subdirectory based on image type
        if image_type == "original":
            subdir = "original_photos"
        elif image_type == "enhanced":
            subdir = "enhanced_images"
        elif image_type == "story":
            subdir = "story_images"
        elif image_type == "ghibli":
            subdir = "ghibli_images"
        elif image_type == "badge":
            subdir = "badges"
        else:
            subdir = "images"
        
        local_path = os.path.join(session_dir, subdir, filename)
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 Downloaded {image_type} image for {pet_name}: {local_path}")
            return local_path
        else:
            print(f"❌ Failed to download {image_type} image for {pet_name}: HTTP {response.status_code}")
            return image_url  # Return original URL as fallback
            
    except Exception as e:
        print(f"❌ Error downloading {image_type} image for {pet_name}: {e}")
        return image_url  # Return original URL as fallback


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
    response = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024", quality="hd")
    # Download and save the AI-generated image locally
    ai_image_url = response.data[0].url
    local_path = download_and_save_image(ai_image_url, pet['name'], "basic")
    return local_path


async def generate_enhanced_image_from_photo(pet: Dict[str, Any], photo_url: Optional[str], scene_description: str = "in a beautiful park setting") -> str:
    """Generate an enhanced image using GPT-Image-1 with the real Petfinder photo as input"""
    if not photo_url:
        return await generate_image(pet, "promotional image")
    
    # Download the Petfinder photo
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(photo_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return await generate_image(pet, "promotional image")
        
        image_data = response.content
        
        # Upload to GPT-Image-1 for creative transformation
        client = get_openai_client()
        
        # Create fun, creative transformation prompts based on pet characteristics
        pet_type = pet.get('type', 'pet').lower()
        pet_name = pet['name']
        breed = pet.get('breeds', {}).get('primary', 'mixed')
        
        # Generate creative scene ideas based on pet characteristics
        creative_scenes = []
        
        if pet_type == 'dog':
            creative_scenes = [
                f"Transform {pet_name} into a superhero dog flying through the city skyline, cape flowing in the wind",
                f"Place {pet_name} as a chef in a gourmet kitchen, wearing a chef's hat and apron, surrounded by fancy ingredients",
                f"Show {pet_name} as an astronaut floating in space with Earth in the background, wearing a space helmet",
                f"Transform {pet_name} into a detective with a magnifying glass and deerstalker hat in a mysterious library",
                f"Place {pet_name} as a surfer riding a giant wave at sunset, showing incredible balance and joy"
            ]
        elif pet_type == 'cat':
            creative_scenes = [
                f"Transform {pet_name} into a wizard cat with a pointed hat and magical sparkles, casting spells in an enchanted forest",
                f"Place {pet_name} as a scientist in a laboratory, wearing tiny goggles and surrounded by colorful bubbling beakers",
                f"Show {pet_name} as a pirate captain on a ship deck, wearing an eye patch and standing proudly at the helm",
                f"Transform {pet_name} into a ninja cat sneaking through a moonlit Japanese garden with throwing stars",
                f"Place {pet_name} as a rock star on stage with a tiny guitar, spotlights, and an enthusiastic crowd"
            ]
        else:
            creative_scenes = [
                f"Transform {pet_name} into an adventurer exploring a magical forest with glowing mushrooms and fairy lights",
                f"Place {pet_name} as an artist in a colorful studio, surrounded by paintbrushes and vibrant artwork",
                f"Show {pet_name} as a time traveler in a steampunk setting with gears, clockwork, and vintage machinery"
            ]
        
        # Select a random creative scene
        import random
        selected_scene = random.choice(creative_scenes)
        
        # Create detailed prompt for transformation
        enhanced_prompt = f"""{selected_scene}

        Keep the pet's distinctive features, coloring, and breed characteristics clearly recognizable.
        Style: High-quality digital art with photorealistic pet features, vibrant colors, dynamic composition, 
        professional lighting, and whimsical storytelling elements. The transformation should be fun and engaging 
        while maintaining the pet's natural charm and personality.
        
        Technical specs: Magazine-quality resolution, sharp focus on the pet, balanced composition suitable for print."""
        
                        # Use the image editing endpoint to transform the photo
        try:
            image_response = client.images.edit(
                image=image_data,
                prompt=enhanced_prompt,
                n=1,
                size="1024x1024"
            )
            # Download and save the AI-generated image locally
            ai_image_url = image_response.data[0].url
            local_path = download_and_save_image(ai_image_url, pet_name, "enhanced")
            return local_path
        except Exception as edit_error:
            # If edit fails, try generation with the scene description
            try:
                fallback_prompt = f"Create a fun, creative image: {selected_scene}. Style: High-quality digital art, vibrant colors, whimsical and engaging."
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=fallback_prompt,
                    n=1,
                    size="1024x1024",
                    quality="hd"
                )
                # Download and save the AI-generated image locally
                ai_image_url = image_response.data[0].url
                local_path = download_and_save_image(ai_image_url, pet_name, "enhanced")
                return local_path
            except:
                return await generate_image(pet, "promotional image")
        
    except Exception as e:
        # Fallback to generating a new image if enhancement fails
        return await generate_image(pet, "promotional image")


async def generate_badge(pet: Dict[str, Any], badge_text: Optional[str] = None) -> str:
    prompt_suffix = f"fun pet-related badge with text '{badge_text}'" if badge_text else "status badge in a humorous style"
    client = get_openai_client()
    prompt = f"Generate a {prompt_suffix} for pet {pet['name']} based on: {pet['description']}"
    response = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024", quality="hd")
    # Download and save the AI-generated image locally
    ai_image_url = response.data[0].url
    local_path = download_and_save_image(ai_image_url, pet['name'], "badge")
    return local_path


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
    """Generate a story-specific image using GPT-Image-1 that incorporates the story context and real pet photo"""
    client = get_openai_client()
    
    # Extract key story elements for creative scene generation
    pet_name = pet['name']
    pet_type = pet.get('type', 'pet').lower()
    
    # Analyze story content to create contextual scenes
    story_lower = story.lower()
    creative_story_scenes = []
    
    if "detective" in story_lower or "mystery" in story_lower or "investigate" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} as a brilliant detective in a noir-style office, wearing a fedora and examining clues with a magnifying glass",
            f"Place {pet_name} in a mysterious library at night, surrounded by floating books and glowing clues",
            f"Transform {pet_name} into a sherlock holmes-style detective in Victorian London, complete with pipe and deerstalker hat"
        ]
    elif "adventure" in story_lower or "explorer" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} as an intrepid explorer in a jungle temple, wearing an adventure hat and carrying a torch",
            f"Place {pet_name} on a mountain peak at sunrise, wearing climbing gear and looking triumphant",
            f"Transform {pet_name} into a treasure hunter in an ancient cave filled with glittering gems"
        ]
    elif "heist" in story_lower or "criminal" in story_lower or "mastermind" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} as a suave cat burglar in a black suit, tiptoeing across rooftops under moonlight",
            f"Place {pet_name} in a high-tech vault surrounded by laser security beams, wearing cool sunglasses",
            f"Transform {pet_name} into a master thief planning the perfect heist with blueprints and gadgets"
        ]
    elif "tea party" in story_lower or "retirement" in story_lower or "elegant" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} hosting an elegant tea party in a Victorian garden, wearing a fancy hat and bow tie",
            f"Place {pet_name} in a cozy library by a fireplace, wearing reading glasses and surrounded by books",
            f"Transform {pet_name} into a distinguished gentleman/lady in a luxurious mansion setting"
        ]
    elif "greeter" in story_lower or "jumping" in story_lower or "enthusiastic" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} as an enthusiastic theme park mascot, wearing a colorful costume and greeting visitors",
            f"Place {pet_name} as a cheerful hotel concierge, wearing a uniform and welcoming guests with a big smile",
            f"Transform {pet_name} into a carnival performer, juggling colorful balls under bright circus lights"
        ]
    elif "security" in story_lower or "patrol" in story_lower or "guard" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} as a superhero guardian flying over the city, wearing a cape and mask",
            f"Place {pet_name} as a medieval knight in shining armor, standing guard at a castle gate",
            f"Transform {pet_name} into a space patrol officer on a futuristic space station"
        ]
    elif "food" in story_lower or "critic" in story_lower or "dining" in story_lower:
        creative_story_scenes = [
            f"Show {pet_name} as a renowned chef in a gourmet kitchen, wearing a chef's hat and creating culinary masterpieces",
            f"Place {pet_name} as a food critic at a fancy restaurant, wearing a monocle and tasting exquisite dishes",
            f"Transform {pet_name} into a cooking show host on a colorful TV kitchen set"
        ]
    else:
        # Default creative scenes based on pet type
        if pet_type == 'dog':
            creative_story_scenes = [
                f"Show {pet_name} as a magical fairy tale character in an enchanted forest with sparkling lights",
                f"Place {pet_name} as a brave knight on a quest, wearing armor and carrying a noble banner",
                f"Transform {pet_name} into a wise wizard with a staff and flowing robes in a mystical tower"
            ]
        elif pet_type == 'cat':
            creative_story_scenes = [
                f"Show {pet_name} as a mysterious sorceress in a magical workshop filled with potions and crystals",
                f"Place {pet_name} as an elegant duchess in a grand ballroom, wearing a jeweled collar",
                f"Transform {pet_name} into a ninja master in a moonlit Japanese garden with cherry blossoms"
            ]
        else:
            creative_story_scenes = [
                f"Show {pet_name} as a magical creature in a fantasy realm with rainbow colors and sparkles",
                f"Place {pet_name} as an adventurer in a whimsical storybook setting"
            ]
    
    # Select a random creative scene
    import random
    selected_scene = random.choice(creative_story_scenes)
    
    # If we have a real photo, try to use it for transformation
    if real_photo_url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(real_photo_url, headers=headers, timeout=30)
            if response.status_code == 200:
                image_data = response.content
                
                # Create transformation prompt
                transformation_prompt = f"""{selected_scene}
                
                Keep the pet's distinctive features, coloring, and breed characteristics clearly recognizable.
                Style: High-quality digital art with photorealistic pet features, vibrant colors, dynamic composition, 
                professional lighting, and whimsical storytelling elements that match the story context.
                
                Story context: {story[:300]}...
                
                Technical specs: Magazine-quality resolution, sharp focus on the pet, balanced composition suitable for print."""
                
                # Try image editing first
                try:
                    image_response = client.images.edit(
                        image=image_data,
                        prompt=transformation_prompt,
                        n=1,
                        size="1024x1024"
                    )
                    # Download and save the AI-generated image locally
                    ai_image_url = image_response.data[0].url
                    local_path = download_and_save_image(ai_image_url, pet_name, "story")
                    return local_path
                except:
                    pass  # Fall through to generation
        except:
            pass  # Fall through to generation
    
    # Fallback to image generation
    try:
        generation_prompt = f"Create a fun, creative image: {selected_scene}. Style: High-quality digital art, vibrant colors, whimsical and engaging, perfect for a pet adoption storybook."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=generation_prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        # Download and save the AI-generated image locally
        ai_image_url = response.data[0].url
        local_path = download_and_save_image(ai_image_url, pet_name, "story")
        return local_path
    except Exception as e:
        # Final fallback
        simple_prompt = f"A heartwarming, creative image of {pet_name}, a {pet_type} in a fun, story-appropriate setting"
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=simple_prompt,
                n=1,
                size="1024x1024"
            )
            # Download and save the AI-generated image locally
            ai_image_url = response.data[0].url
            local_path = download_and_save_image(ai_image_url, pet_name, "story")
            return local_path
        except:
            return f"https://example.com/{pet_name.lower()}_story_image.jpg"


async def generate_ghibli_style_image(pet: Dict[str, Any], real_photo_url: Optional[str] = None) -> str:
    """Generate a Studio Ghibli-style image using GPT-Image-1 with the real pet photo"""
    client = get_openai_client()
    
    pet_name = pet['name']
    pet_type = pet.get('type', 'pet').lower()
    breed = pet.get('breeds', {}).get('primary', 'mixed')
    
    # Create Ghibli-style transformation prompts
    ghibli_scenes = []
    
    if pet_type == 'dog':
        ghibli_scenes = [
            f"Transform {pet_name} into a Studio Ghibli character: a magical forest spirit dog with glowing eyes, surrounded by floating spirits and ancient trees in a mystical woodland",
            f"Show {pet_name} as a Ghibli-style companion flying on a magical airship through cloudy skies, with wind flowing through fur and a sense of wonder",
            f"Place {pet_name} in a Ghibli countryside scene: running through rolling green hills with wildflowers, under a dreamy sky with soft clouds",
            f"Transform {pet_name} into a Ghibli castle guardian: a noble dog with ethereal qualities standing at the entrance of a floating castle"
        ]
    elif pet_type == 'cat':
        ghibli_scenes = [
            f"Transform {pet_name} into a Studio Ghibli magical cat: sitting in a moonlit garden with glowing fireflies, mysterious and enchanting with sparkling eyes",
            f"Show {pet_name} as a Ghibli-style witch's familiar: perched on a broomstick flying over a quaint village at sunset with magical sparkles",
            f"Place {pet_name} in a Ghibli forest scene: a mystical cat walking through a bamboo forest with dappled sunlight and floating dust motes",
            f"Transform {pet_name} into a Ghibli spirit cat: translucent and glowing, sitting on a torii gate in a sacred forest clearing"
        ]
    else:
        ghibli_scenes = [
            f"Transform {pet_name} into a Studio Ghibli magical creature in an enchanted forest with soft lighting and floating spirits",
            f"Show {pet_name} in a Ghibli-style pastoral scene with rolling hills, wildflowers, and a dreamy atmosphere"
        ]
    
    # Select a random Ghibli scene
    import random
    selected_scene = random.choice(ghibli_scenes)
    
    # If we have a real photo, try to use it for transformation
    if real_photo_url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(real_photo_url, headers=headers, timeout=30)
            if response.status_code == 200:
                image_data = response.content
                
                # Create Ghibli transformation prompt
                ghibli_prompt = f"""{selected_scene}
                
                Keep the pet's distinctive features, coloring, and breed characteristics clearly recognizable.
                Style: Studio Ghibli animation style - soft watercolor textures, dreamy lighting, magical atmosphere,
                gentle colors, ethereal quality, hand-drawn animation aesthetic, whimsical and heartwarming.
                
                Technical specs: High-quality digital art, soft focus, magical lighting, suitable for storybook illustration."""
                
                # Try image editing with GPT-Image-1
                try:
                    image_response = client.images.edit(
                        image=image_data,
                        prompt=ghibli_prompt,
                        n=1,
                        size="1024x1024"
                    )
                    return image_response.data[0].url
                except:
                    pass  # Fall through to generation
        except:
            pass  # Fall through to generation
    
    # Fallback to image generation with GPT-Image-1
    try:
        generation_prompt = f"Create a Studio Ghibli-style image: {selected_scene}. Style: Studio Ghibli animation - soft watercolor textures, dreamy lighting, magical atmosphere, whimsical and heartwarming."
        
        response = client.images.generate(
            model="dall-e-3",  # Using DALL-E 3 as GPT-Image-1 equivalent
            prompt=generation_prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        # Download and save the AI-generated image locally
        ai_image_url = response.data[0].url
        local_path = download_and_save_image(ai_image_url, pet_name, "ghibli")
        return local_path
    except Exception as e:
        # Final fallback
        return f"https://example.com/{pet_name.lower()}_ghibli_image.jpg"


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

    content = {
        "stories": [], 
        "images": [], 
        "original_photos": [],
        "enhanced_images": [],
        "story_images": [], 
        "ghibli_images": [],
        "badges": [], 
        "videos": [], 
        "petfinder_urls": []
    }

    for pet in pets:
        # Generate story first
        story_dict = await generate_story(pet, humorous)
        content["stories"].append({"pet": pet["name"], "story": story_dict})

        # Get original Petfinder photo
        photo_url = pet.get("photos", [None])[0] if "photos" in pet else None
        if photo_url:
            # Download and save original photo locally
            local_original_path = download_and_save_image(photo_url, pet["name"], "original", "jpg")
            content["original_photos"].append({
                "pet": pet["name"], 
                "image_url": local_original_path, 
                "type": "original_petfinder"
            })
            
            # Generate enhanced image using GPT-Image-1
            enhanced_image_url = await generate_enhanced_image_from_photo(
                pet, photo_url, "in a creative, fun adventure scene"
            )
            content["enhanced_images"].append({
                "pet": pet["name"], 
                "image_url": enhanced_image_url, 
                "type": "gpt_enhanced_creative"
            })
            
            # Generate story-specific image using GPT-Image-1
            story_image_url = await generate_story_image(pet, str(story_dict), photo_url)
            content["story_images"].append({
                "pet": pet["name"], 
                "image_url": story_image_url, 
                "type": "gpt_story_specific"
            })
            
            # Generate Ghibli-style image using GPT-Image-1
            ghibli_image_url = await generate_ghibli_style_image(pet, photo_url)
            content["ghibli_images"].append({
                "pet": pet["name"], 
                "image_url": ghibli_image_url, 
                "type": "gpt_ghibli_style"
            })
            
            # Also add to general images array for backward compatibility
            content["images"].append({
                "pet": pet["name"], 
                "image_url": enhanced_image_url, 
                "type": "gpt_enhanced_photo"
            })
        else:
            # Generate basic pet images if no real photo
            basic_image_url = await generate_image(pet)
            content["images"].append({
                "pet": pet["name"], 
                "image_url": basic_image_url, 
                "type": "generated_basic"
            })
            content["enhanced_images"].append({
                "pet": pet["name"], 
                "image_url": basic_image_url, 
                "type": "generated_basic"
            })

        # Generate badge using badge text from story
        badge_url = await generate_badge(pet, story_dict.get("badge"))
        content["badges"].append({"pet": pet["name"], "badge_url": badge_url})

        # Skip video generation to avoid Vertex AI issues
        # video_url = await generate_video_from_photo(pet, photo_url, humorous)
        content["videos"].append({"pet": pet["name"], "video_url": "no_video_generated"})

        # Add Petfinder URL
        content["petfinder_urls"].append({"pet": pet["name"], "url": pet.get("url", "")})

    return content


async def main():
    print("Content Generator agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 