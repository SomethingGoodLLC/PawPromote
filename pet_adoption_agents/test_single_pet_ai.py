#!/usr/bin/env python3
"""
Test script to generate AI images for a single pet
Tests the OpenAI API and image generation with real pet photos
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not available")

# OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI not available")

def load_pets_data() -> List[Dict]:
    """Load pet data from the Alexandria pets JSON file"""
    json_path = Path("pets_alexandria_va.json")
    if not json_path.exists():
        return []
    
    with open(json_path, 'r') as f:
        pets = json.load(f)
    
    return pets[:1]  # Just first pet for testing

def extract_photo_url(photo_data) -> Optional[str]:
    """Extract photo URL from pet photo data structure"""
    if not photo_data:
        return None
    
    if isinstance(photo_data, str):
        return photo_data
    elif isinstance(photo_data, dict):
        for size in ['large', 'medium', 'small']:
            if size in photo_data and photo_data[size]:
                return photo_data[size]
        for key, value in photo_data.items():
            if isinstance(value, str) and value.startswith('http'):
                return value
    
    return None

def download_image(url: str, filename: str, temp_dir: Path) -> Optional[Path]:
    """Download an image from URL and save to temp directory"""
    if not url or not url.startswith('http'):
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            file_path = temp_dir / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename} ({len(response.content)} bytes)")
            return file_path
        else:
            print(f"❌ Failed to download {filename}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")
        return None

def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client using API key from .env file"""
    if not OPENAI_AVAILABLE:
        return None
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or len(api_key) < 20:
        print("❌ OpenAI API key not found")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created")
        return client
    except Exception as e:
        print(f"❌ Error with OpenAI client: {e}")
        return None

async def test_ai_generation(client: OpenAI, pet: Dict, temp_dir: Path, original_photo_path: Optional[Path] = None):
    """Test AI image generation with improved prompts"""
    pet_name = pet.get('name', 'Pet')
    pet_type = pet.get('type', 'animal')
    description = pet.get('description', 'A wonderful pet')
    
    # Get appearance details
    appearance_keywords = []
    if description:
        desc_lower = description.lower()
        colors = ['black', 'white', 'brown', 'gray', 'grey', 'orange', 'tabby', 'calico', 'tortoiseshell', 'tuxedo', 'siamese', 'russian blue']
        for color in colors:
            if color in desc_lower:
                appearance_keywords.append(color)
    
    breed = pet.get('breeds', {}).get('primary', '')
    if breed:
        appearance_keywords.append(breed.lower())
    
    appearance_desc = f"This specific {pet_type.lower()} has {', '.join(appearance_keywords)} coloring" if appearance_keywords else f"This {pet_type.lower()}"
    
    print(f"\n🎨 Testing AI generation for {pet_name}")
    print(f"📝 Appearance: {appearance_desc}")
    print(f"📝 Description: {description[:100]}...")
    
    # Test different approaches
    
    # Method 1: Try image variation if we have original photo
    if original_photo_path and original_photo_path.exists():
        print(f"\n🔄 Method 1: Image variation using original photo")
        try:
            with open(original_photo_path, 'rb') as image_file:
                response = client.images.create_variation(
                    image=image_file,
                    n=1,
                    size="1024x1024"
                )
                image_url = response.data[0].url
                filename = f"{pet_name.lower().replace(' ', '_')}_variation.png"
                result_path = download_image(image_url, filename, temp_dir)
                if result_path:
                    print(f"✅ Image variation successful: {filename}")
                    return result_path
        except Exception as e:
            print(f"❌ Image variation failed: {e}")
    
    # Method 2: Enhanced text prompt with appearance details
    print(f"\n📝 Method 2: Enhanced text generation")
    try:
        enhanced_prompt = f"""Create a beautiful, professional portrait of this specific {pet_type.lower()} named {pet_name}. 
        {appearance_desc}. 
        
        Description: {description}
        
        Style: High-quality digital art, professional pet photography style, warm lighting, 
        engaging and heartwarming. Perfect for a pet adoption book.
        
        Important: Keep the pet's exact coloring, markings, and distinctive features as described."""
        
        print(f"🎯 Prompt: {enhanced_prompt[:200]}...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            n=1,
            size="1024x1024",
            quality="hd"
        )
        
        image_url = response.data[0].url
        filename = f"{pet_name.lower().replace(' ', '_')}_enhanced.png"
        result_path = download_image(image_url, filename, temp_dir)
        if result_path:
            print(f"✅ Enhanced text generation successful: {filename}")
            return result_path
            
    except Exception as e:
        print(f"❌ Enhanced text generation failed: {e}")
    
    # Method 3: Simple generation as fallback
    print(f"\n🔄 Method 3: Simple generation fallback")
    try:
        simple_prompt = f"A beautiful portrait of {pet_name}, a {pet_type.lower()}. Professional pet photography style."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=simple_prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        filename = f"{pet_name.lower().replace(' ', '_')}_simple.png"
        result_path = download_image(image_url, filename, temp_dir)
        if result_path:
            print(f"✅ Simple generation successful: {filename}")
            return result_path
            
    except Exception as e:
        print(f"❌ Simple generation failed: {e}")
    
    return None

async def main():
    """Test AI generation for a single pet"""
    print("🧪 Testing AI Image Generation for Single Pet")
    print("=" * 50)
    
    # Load single pet
    pets = load_pets_data()
    if not pets:
        print("❌ No pet data available")
        return
    
    pet = pets[0]
    print(f"🐾 Testing with: {pet.get('name', 'Unknown')} ({pet.get('type', 'Unknown')})")
    
    # Create temp directory
    temp_dir = Path("output/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Get OpenAI client
    client = get_openai_client()
    if not client:
        print("❌ OpenAI client not available")
        return
    
    # Download original photo
    original_photo_path = None
    photos = pet.get('photos', [])
    if photos:
        photo_url = extract_photo_url(photos[0])
        if photo_url:
            filename = f"{pet.get('name', 'pet').lower().replace(' ', '_')}_original.jpg"
            original_photo_path = download_image(photo_url, filename, temp_dir)
    
    # Test AI generation
    result = await test_ai_generation(client, pet, temp_dir, original_photo_path)
    
    if result:
        print(f"\n✅ SUCCESS: AI image generated successfully!")
        print(f"📁 Generated image: {result}")
    else:
        print(f"\n❌ FAILED: Could not generate AI image")
    
    # List all files in temp directory
    print(f"\n📁 Files in temp directory:")
    for file in sorted(temp_dir.glob("*")):
        size = file.stat().st_size
        print(f"   - {file.name} ({size:,} bytes)")

if __name__ == "__main__":
    asyncio.run(main()) 