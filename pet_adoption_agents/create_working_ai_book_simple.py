#!/usr/bin/env python3
"""
Create AI-Enhanced Pet Adoption Book using core content generation logic
Simplified version without genai_session dependency
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime

# Check if OpenAI is available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI library not available. Install with: pip install openai")

def load_pets_data() -> List[Dict]:
    """Load real pet data from Alexandria, VA"""
    pets_file = Path(__file__).parent / "pets_alexandria_va.json"
    
    if not pets_file.exists():
        print(f"❌ Pets data file not found: {pets_file}")
        return []
    
    try:
        with open(pets_file, 'r') as f:
            data = json.load(f)
        
        pets = data.get('animals', [])
        if not pets:
            print("❌ No animals found in pets data")
            return []
        
        print(f"✅ Loaded {len(pets)} pets from Alexandria Animal Shelter")
        return pets
    
    except Exception as e:
        print(f"❌ Error loading pets data: {e}")
        return []

def create_session_directory() -> str:
    """Create a session directory for generated content"""
    output_dir = Path(__file__).parent / "output"
    session_dir = output_dir / "generated_content" / datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create subdirectories
    (session_dir / "original_photos").mkdir(parents=True, exist_ok=True)
    (session_dir / "enhanced_images").mkdir(parents=True, exist_ok=True)
    (session_dir / "story_images").mkdir(parents=True, exist_ok=True)
    (session_dir / "ghibli_images").mkdir(parents=True, exist_ok=True)
    (session_dir / "badges").mkdir(parents=True, exist_ok=True)
    
    return str(session_dir)

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

def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client if available"""
    if not OPENAI_AVAILABLE:
        return None
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"❌ Error creating OpenAI client: {e}")
        return None

def extract_photo_url(photo_data) -> Optional[str]:
    """Extract photo URL from photo data"""
    if isinstance(photo_data, dict):
        # Try different possible URL keys
        for key in ['large', 'medium', 'small', 'full']:
            if key in photo_data and photo_data[key]:
                return photo_data[key]
        # If no size-specific URL, try direct URL
        if 'url' in photo_data:
            return photo_data['url']
    elif isinstance(photo_data, str):
        return photo_data
    return None

async def generate_story(pet: Dict[str, Any], humorous: bool = False) -> Dict[str, Any]:
    """Generate a story for the pet"""
    name = pet.get('name', 'Pet')
    pet_type = pet.get('type', 'animal')
    breed = pet.get('breeds', {}).get('primary', 'Mixed')
    
    # Create a simple story structure
    story = {
        'header': f"Meet {name}!",
        'subheader': f"A wonderful {breed} {pet_type} looking for a loving home",
        'story': f"Once upon a time in Alexandria, there lived a special {pet_type} named {name}. "
                f"This {breed} had the most amazing personality and was waiting for someone special "
                f"to take them home. {name} loves to play, cuddle, and bring joy to everyone around. "
                f"Could you be the perfect match for {name}?"
    }
    
    return story

async def generate_enhanced_image_from_photo(pet: Dict[str, Any], photo_url: Optional[str], scene_description: str = "in a beautiful park setting") -> str:
    """Generate an enhanced image using the real photo as reference"""
    client = get_openai_client()
    if not client or not photo_url:
        return f"https://example.com/{pet['name'].lower()}_enhanced.jpg"
    
    pet_name = pet['name']
    pet_type = pet.get('type', 'pet').lower()
    breed = pet.get('breeds', {}).get('primary', 'mixed')
    
    # Create enhanced prompt
    prompt = f"""Create a beautiful, professional-quality image of {pet_name}, a {breed} {pet_type} {scene_description}. 
    The image should be vibrant, engaging, and perfect for a pet adoption book. 
    Style: High-quality digital art with photorealistic features, warm lighting, and a welcoming atmosphere."""
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        
        # Download and save the AI-generated image locally
        ai_image_url = response.data[0].url
        local_path = download_and_save_image(ai_image_url, pet_name, "enhanced")
        return local_path
        
    except Exception as e:
        print(f"❌ Error generating enhanced image for {pet_name}: {e}")
        return f"https://example.com/{pet_name.lower()}_enhanced.jpg"

async def generate_story_image(pet: Dict[str, Any], story: str, real_photo_url: Optional[str] = None) -> str:
    """Generate a story-specific image"""
    client = get_openai_client()
    if not client:
        return f"https://example.com/{pet['name'].lower()}_story.jpg"
    
    pet_name = pet['name']
    pet_type = pet.get('type', 'pet').lower()
    breed = pet.get('breeds', {}).get('primary', 'mixed')
    
    # Create story-specific prompt
    prompt = f"""Create a heartwarming storybook illustration of {pet_name}, a {breed} {pet_type} in a scene that matches this story context: {story[:200]}...
    Style: Warm, engaging storybook illustration with vibrant colors and a friendly atmosphere perfect for a pet adoption book."""
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        
        # Download and save the AI-generated image locally
        ai_image_url = response.data[0].url
        local_path = download_and_save_image(ai_image_url, pet_name, "story")
        return local_path
        
    except Exception as e:
        print(f"❌ Error generating story image for {pet_name}: {e}")
        return f"https://example.com/{pet_name.lower()}_story.jpg"

async def generate_ghibli_style_image(pet: Dict[str, Any], real_photo_url: Optional[str] = None) -> str:
    """Generate a Ghibli-style image"""
    client = get_openai_client()
    if not client:
        return f"https://example.com/{pet['name'].lower()}_ghibli.jpg"
    
    pet_name = pet['name']
    pet_type = pet.get('type', 'pet').lower()
    breed = pet.get('breeds', {}).get('primary', 'mixed')
    
    # Create Ghibli-style prompt
    prompt = f"""Create a Studio Ghibli-style illustration of {pet_name}, a {breed} {pet_type} in a magical, whimsical setting. 
    Style: Studio Ghibli animation - soft watercolor textures, dreamy lighting, magical atmosphere, 
    whimsical and heartwarming, perfect for a pet adoption storybook."""
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        
        # Download and save the AI-generated image locally
        ai_image_url = response.data[0].url
        local_path = download_and_save_image(ai_image_url, pet_name, "ghibli")
        return local_path
        
    except Exception as e:
        print(f"❌ Error generating Ghibli image for {pet_name}: {e}")
        return f"https://example.com/{pet_name.lower()}_ghibli.jpg"

async def generate_content_for_pets(pets: List[Dict[str, Any]], humorous: bool = False) -> Dict[str, Any]:
    """Generate content for all pets"""
    print(f"🎨 Generating content for {len(pets)} pets...")
    
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
        pet_name = pet.get('name', 'Pet')
        print(f"  Processing {pet_name}...")
        
        # Generate story first
        story_dict = await generate_story(pet, humorous)
        content["stories"].append({"pet": pet_name, "story": story_dict})

        # Get original photo
        photos = pet.get("photos", [])
        photo_url = None
        if photos:
            photo_url = extract_photo_url(photos[0])
        
        if photo_url:
            # Download and save original photo locally
            local_original_path = download_and_save_image(photo_url, pet_name, "original", "jpg")
            content["original_photos"].append({
                "pet": pet_name, 
                "image_url": local_original_path, 
                "type": "original_petfinder"
            })
            
            # Generate enhanced image
            enhanced_image_url = await generate_enhanced_image_from_photo(
                pet, photo_url, "in a creative, fun adventure scene"
            )
            content["enhanced_images"].append({
                "pet": pet_name, 
                "image_url": enhanced_image_url, 
                "type": "gpt_enhanced_creative"
            })
            
            # Generate story-specific image
            story_image_url = await generate_story_image(pet, str(story_dict), photo_url)
            content["story_images"].append({
                "pet": pet_name, 
                "image_url": story_image_url, 
                "type": "gpt_story_specific"
            })
            
            # Generate Ghibli-style image
            ghibli_image_url = await generate_ghibli_style_image(pet, photo_url)
            content["ghibli_images"].append({
                "pet": pet_name, 
                "image_url": ghibli_image_url, 
                "type": "gpt_ghibli_style"
            })
            
            # Add to general images for compatibility
            content["images"].append({
                "pet": pet_name, 
                "image_url": enhanced_image_url, 
                "type": "gpt_enhanced_photo"
            })
        
        # Add empty entries for badges and videos for compatibility
        content["badges"].append({"pet": pet_name, "badge_url": f"https://example.com/{pet_name.lower()}_badge.jpg"})
        content["videos"].append({"pet": pet_name, "video_url": f"https://example.com/{pet_name.lower()}_video.mp4"})
        content["petfinder_urls"].append({"pet": pet_name, "url": f"https://example.com/{pet_name.lower()}"})

    return content

# Import the asset assembler PDF creation function
sys.path.append(str(Path(__file__).parent / "asset_assembler"))
from asset_assembler.main import create_pdf_book

async def main():
    """Main function to create AI-enhanced book"""
    print("🎨 Creating AI-Enhanced Pet Adoption Book (Simplified)")
    print("=" * 55)
    
    # Load pet data
    pets = load_pets_data()
    if not pets:
        print("❌ No pet data available")
        return
    
    # Generate content with AI images
    content = await generate_content_for_pets(pets, humorous=True)
    
    print(f"\n✅ Content generation complete!")
    print(f"   📖 Stories: {len(content.get('stories', []))}")
    print(f"   📸 Original photos: {len(content.get('original_photos', []))}")
    print(f"   🎨 Enhanced images: {len(content.get('enhanced_images', []))}")
    print(f"   📚 Story images: {len(content.get('story_images', []))}")
    print(f"   🌸 Ghibli images: {len(content.get('ghibli_images', []))}")
    
    # Create PDF using asset assembler
    print(f"\n📚 Creating PDF book...")
    try:
        pdf_path = create_pdf_book(content)
        print(f"✅ PDF created: {pdf_path}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return
    
    print(f"\n✅ AI-Enhanced Book Creation Complete!")
    print(f"📖 Your book is ready: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(main()) 