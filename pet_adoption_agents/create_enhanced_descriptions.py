#!/usr/bin/env python3
"""
Enhanced Pet Description Generator using GPT-4o Vision
Analyzes real pet photos to create detailed descriptions for better AI image generation
"""

import asyncio
import json
import os
import base64
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
    
    return pets[:5]  # First 5 pets

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

def encode_image_to_base64(image_path: Path) -> str:
    """Encode image to base64 for GPT-4o vision"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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

async def analyze_pet_photo_with_gpt4o(client: OpenAI, pet: Dict, image_path: Path) -> Dict[str, str]:
    """Use GPT-4o vision to analyze pet photo and create detailed descriptions"""
    pet_name = pet.get('name', 'Pet')
    pet_type = pet.get('type', 'animal')
    description = pet.get('description', 'A wonderful pet')
    
    print(f"🔍 Analyzing {pet_name}'s photo with GPT-4o vision...")
    
    try:
        # Encode image
        base64_image = encode_image_to_base64(image_path)
        
        # Create detailed analysis prompt
        analysis_prompt = f"""You are an expert pet photographer and animal behaviorist. Please analyze this photo of {pet_name}, a {pet_type} from Alexandria Animal Shelter.

Original description: "{description}"

Please provide a detailed analysis in JSON format with the following fields:

1. "physical_description": Detailed description of the pet's physical appearance, coloring, markings, size, breed characteristics
2. "facial_features": Specific details about eyes, nose, ears, expression
3. "pose_and_setting": How the pet is positioned, background, lighting
4. "personality_indicators": What the photo suggests about the pet's personality
5. "enhanced_prompt_professional": A detailed prompt for generating a professional portrait
6. "enhanced_prompt_storybook": A detailed prompt for generating a storybook illustration
7. "enhanced_prompt_ghibli": A detailed prompt for generating a Studio Ghibli-style image

Be very specific about colors, patterns, markings, and distinctive features that make this pet unique."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1500
        )
        
        analysis = json.loads(response.choices[0].message.content)
        print(f"✅ GPT-4o analysis complete for {pet_name}")
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing {pet_name}'s photo: {e}")
        return {
            "physical_description": f"Unable to analyze photo - {str(e)}",
            "facial_features": "Analysis failed",
            "pose_and_setting": "Analysis failed", 
            "personality_indicators": "Analysis failed",
            "enhanced_prompt_professional": f"Professional portrait of {pet_name}, a {pet_type}",
            "enhanced_prompt_storybook": f"Storybook illustration of {pet_name}, a {pet_type}",
            "enhanced_prompt_ghibli": f"Studio Ghibli style illustration of {pet_name}, a {pet_type}"
        }

async def create_enhanced_descriptions_file(pets: List[Dict], temp_dir: Path, client: OpenAI):
    """Create a comprehensive file with enhanced descriptions for all pets"""
    enhanced_data = {
        "generation_timestamp": datetime.now().isoformat(),
        "pets": []
    }
    
    for pet in pets:
        pet_name = pet.get('name', 'Pet')
        print(f"\n🎨 Processing {pet_name}...")
        
        # Download original photo
        original_photo_path = None
        photos = pet.get('photos', [])
        if photos:
            photo_url = extract_photo_url(photos[0])
            if photo_url:
                filename = f"{pet_name.lower().replace(' ', '_').replace('*', '')}_original.jpg"
                original_photo_path = download_image(photo_url, filename, temp_dir)
        
        # Analyze with GPT-4o if photo available
        analysis = {}
        if original_photo_path and original_photo_path.exists():
            analysis = await analyze_pet_photo_with_gpt4o(client, pet, original_photo_path)
        
        # Combine original data with analysis
        enhanced_pet = {
            "original_data": pet,
            "gpt4o_analysis": analysis,
            "image_generation_prompts": {
                "professional": analysis.get("enhanced_prompt_professional", f"Professional portrait of {pet_name}"),
                "storybook": analysis.get("enhanced_prompt_storybook", f"Storybook illustration of {pet_name}"),
                "ghibli": analysis.get("enhanced_prompt_ghibli", f"Studio Ghibli style illustration of {pet_name}")
            }
        }
        
        enhanced_data["pets"].append(enhanced_pet)
    
    # Save enhanced descriptions
    output_file = temp_dir / "enhanced_pet_descriptions.json"
    with open(output_file, 'w') as f:
        json.dump(enhanced_data, f, indent=2)
    
    print(f"\n✅ Enhanced descriptions saved to: {output_file}")
    return output_file

async def generate_fallback_images_with_descriptions(enhanced_descriptions_file: Path, temp_dir: Path):
    """Create text-based 'images' using the enhanced descriptions as fallback"""
    print(f"\n📝 Creating text-based image descriptions as fallback...")
    
    with open(enhanced_descriptions_file, 'r') as f:
        data = json.load(f)
    
    fallback_dir = temp_dir / "fallback_descriptions"
    fallback_dir.mkdir(exist_ok=True)
    
    for pet_data in data["pets"]:
        pet = pet_data["original_data"]
        analysis = pet_data["gpt4o_analysis"]
        pet_name = pet.get('name', 'Pet')
        
        # Create detailed text descriptions for each image type
        descriptions = {
            "professional": f"""
PROFESSIONAL PORTRAIT OF {pet_name.upper()}

Physical Description: {analysis.get('physical_description', 'Not available')}

Facial Features: {analysis.get('facial_features', 'Not available')}

Recommended Image Generation Prompt:
{analysis.get('enhanced_prompt_professional', 'Standard professional portrait')}

Style Notes: High-quality digital art, professional pet photography style, warm lighting, engaging and heartwarming.
""",
            "storybook": f"""
STORYBOOK ILLUSTRATION OF {pet_name.upper()}

Character Traits: {analysis.get('personality_indicators', 'Not available')}

Physical Description: {analysis.get('physical_description', 'Not available')}

Recommended Image Generation Prompt:
{analysis.get('enhanced_prompt_storybook', 'Standard storybook illustration')}

Style Notes: Children's book illustration, colorful, engaging, magical elements, perfect for storytelling.
""",
            "ghibli": f"""
STUDIO GHIBLI STYLE ILLUSTRATION OF {pet_name.upper()}

Magical Elements: Based on personality - {analysis.get('personality_indicators', 'Not available')}

Physical Description: {analysis.get('physical_description', 'Not available')}

Recommended Image Generation Prompt:
{analysis.get('enhanced_prompt_ghibli', 'Standard Ghibli illustration')}

Style Notes: Studio Ghibli animation aesthetic, soft watercolor textures, dreamy lighting, magical atmosphere.
"""
        }
        
        # Save each description type
        for desc_type, content in descriptions.items():
            filename = f"{pet_name.lower().replace(' ', '_').replace('*', '')}_{desc_type}_description.txt"
            desc_file = fallback_dir / filename
            with open(desc_file, 'w') as f:
                f.write(content)
            print(f"✅ Created {desc_type} description: {filename}")
    
    print(f"✅ Fallback descriptions saved to: {fallback_dir}")
    return fallback_dir

async def main():
    """Main function to create enhanced descriptions using GPT-4o"""
    print("🔍 Creating Enhanced Pet Descriptions with GPT-4o Vision")
    print("=" * 60)
    
    # Load pet data
    pets = load_pets_data()
    if not pets:
        print("❌ No pet data available")
        return
    
    print(f"🐾 Processing {len(pets)} pets from Alexandria Animal Shelter")
    
    # Create temp directory
    temp_dir = Path("output/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Get OpenAI client
    client = get_openai_client()
    if not client:
        print("❌ OpenAI client not available")
        return
    
    # Create enhanced descriptions using GPT-4o vision
    enhanced_file = await create_enhanced_descriptions_file(pets, temp_dir, client)
    
    # Create fallback text descriptions
    fallback_dir = await generate_fallback_images_with_descriptions(enhanced_file, temp_dir)
    
    print(f"\n✅ Enhanced Description Generation Complete!")
    print(f"📁 Enhanced data: {enhanced_file}")
    print(f"📁 Fallback descriptions: {fallback_dir}")
    print(f"\n💡 These enhanced descriptions can be used with any image generation service")
    print(f"   when DALL-E API limits are resolved!")

if __name__ == "__main__":
    asyncio.run(main()) 