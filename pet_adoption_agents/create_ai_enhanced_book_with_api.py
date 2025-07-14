#!/usr/bin/env python3
"""
Enhanced AI Book Creation Script with Real AI Image Generation
Creates a beautiful pet adoption book with real photos and AI-generated images
Loads OpenAI API key from .env file
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not available. Install with: uv add python-dotenv")

# Add OpenAI for AI image generation
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available. Install with: uv add openai")

# Ghibli-inspired color palette
GHIBLI_COLORS = {
    'forest_green': Color(0.13, 0.55, 0.13),    # #228B22
    'sky_blue': Color(0.53, 0.81, 0.92),        # #87CEEB
    'warm_orange': Color(1.0, 0.65, 0.0),       # #FFA500
    'magical_purple': Color(0.58, 0.44, 0.86),  # #9370DB
    'soft_pink': Color(1.0, 0.71, 0.76),        # #FFB6C1
    'earth_brown': Color(0.65, 0.16, 0.16),     # #A0522D
    'cream': Color(0.96, 0.96, 0.86),           # #F5F5DC
    'deep_teal': Color(0.0, 0.5, 0.5),          # #008080
}

def load_pets_data() -> List[Dict]:
    """Load pet data from the Alexandria pets JSON file"""
    json_path = Path("pets_alexandria_va.json")
    if not json_path.exists():
        print(f"❌ Pet data file not found: {json_path}")
        return []
    
    try:
        with open(json_path, 'r') as f:
            pets = json.load(f)
        
        # Take first 5 pets for the demo
        pets = pets[:5]
        print(f"✅ Loaded {len(pets)} pets from Alexandria Animal Shelter")
        return pets
    except Exception as e:
        print(f"❌ Error loading pet data: {e}")
        return []

def create_output_directory() -> Path:
    """Create output directory with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create temp directory for images
    temp_dir = output_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    return output_dir, temp_dir

def extract_photo_url(photo_data) -> Optional[str]:
    """Extract photo URL from pet photo data structure"""
    if not photo_data:
        return None
    
    # Handle different photo data structures
    if isinstance(photo_data, str):
        return photo_data
    elif isinstance(photo_data, dict):
        # Try different size options
        for size in ['large', 'medium', 'small']:
            if size in photo_data and photo_data[size]:
                return photo_data[size]
        # Fallback to any URL-like value
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
        print("❌ OpenAI library not available. Install with: uv add openai")
        return None
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "placeholder" or len(api_key) < 20:
        print("❌ OpenAI API key not found or invalid in .env file")
        print("   Please set OPENAI_API_KEY in your .env file")
        print("   Get one at: https://platform.openai.com/api-keys")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI API key loaded successfully from .env file")
        return client
    except Exception as e:
        print(f"❌ Error with OpenAI API key: {e}")
        return None

async def generate_ai_image(client: OpenAI, pet: Dict, image_type: str, temp_dir: Path, original_photo_path: Optional[Path] = None) -> Optional[Path]:
    """Generate AI image using OpenAI's DALL-E, optionally using the real pet photo as input"""
    if not client:
        return None
    
    pet_name = pet.get('name', 'Pet')
    pet_type = pet.get('type', 'animal')
    description = pet.get('description', 'A wonderful pet')
    
    # Get pet appearance details from description
    appearance_keywords = []
    if description:
        desc_lower = description.lower()
        # Extract color information
        colors = ['black', 'white', 'brown', 'gray', 'grey', 'orange', 'tabby', 'calico', 'tortoiseshell', 'tuxedo', 'siamese', 'russian blue']
        for color in colors:
            if color in desc_lower:
                appearance_keywords.append(color)
    
    # Get breed information
    breed = pet.get('breeds', {}).get('primary', '')
    if breed:
        appearance_keywords.append(breed.lower())
    
    appearance_desc = f"This specific {pet_type.lower()} has {', '.join(appearance_keywords)} coloring" if appearance_keywords else f"This {pet_type.lower()}"
    
    # Create different prompts based on image type
    if image_type == "enhanced":
        prompt = f"""Create a beautiful, enhanced portrait of this specific {pet_type.lower()} named {pet_name}. 
        {appearance_desc}. Based on description: {description}
        Style: High-quality digital art, vibrant colors, professional pet photography style, 
        warm lighting, engaging and heartwarming. Perfect for a pet adoption book.
        Keep the pet's exact coloring, markings, and distinctive features."""
        
    elif image_type == "story":
        prompt = f"""Create a whimsical, story-book illustration of this specific {pet_type.lower()} named {pet_name} 
        in an adventure scene. {appearance_desc}. Based on: {description}
        Style: Children's book illustration, colorful, engaging, magical elements, 
        perfect for storytelling. Show this pet as a heroic character.
        Keep the pet's exact coloring, markings, and distinctive features."""
        
    elif image_type == "ghibli":
        prompt = f"""Create a Studio Ghibli-style illustration of this specific {pet_type.lower()} named {pet_name}. 
        {appearance_desc}. Based on: {description}
        Style: Studio Ghibli animation aesthetic, soft watercolor textures, dreamy lighting, 
        magical atmosphere, gentle colors, ethereal quality, whimsical and heartwarming. 
        Set in a magical forest or countryside.
        Keep the pet's exact coloring, markings, and distinctive features."""
    
    else:
        prompt = f"A beautiful portrait of this specific {pet_type.lower()} named {pet_name}. {appearance_desc}. {description}"
    
    try:
        print(f"🎨 Generating {image_type} image for {pet_name}...")
        
        # If we have the original photo, try to use it as reference (image variation)
        if original_photo_path and original_photo_path.exists():
            try:
                # Read the original image file
                with open(original_photo_path, 'rb') as image_file:
                    # Use image variation to create similar-looking pet
                    response = client.images.create_variation(
                        image=image_file,
                        n=1,
                        size="1024x1024"
                    )
                    print(f"✅ Created variation based on original photo for {pet_name}")
            except Exception as variation_error:
                print(f"⚠️  Image variation failed for {pet_name}, using text generation: {variation_error}")
                # Fall back to text-based generation
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                    quality="hd"
                )
        else:
            # Use text-based generation with detailed appearance description
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="hd"
            )
        
        # Download the generated image
        image_url = response.data[0].url
        filename = f"{pet_name.lower().replace(' ', '_').replace('*', '')}_{image_type}.png"
        
        return download_image(image_url, filename, temp_dir)
        
    except Exception as e:
        print(f"❌ Error generating {image_type} image for {pet_name}: {e}")
        return None

def create_ghibli_story(pet: Dict) -> str:
    """Create a Ghibli-style story for the pet"""
    name = pet.get('name', 'Pet')
    pet_type = pet.get('type', 'animal')
    description = pet.get('description', 'A wonderful companion')
    
    # Ghibli-style story templates
    ghibli_stories = {
        'Cat': f"""In a hidden corner of Alexandria, where moonbeams paint silver paths through secret gardens, there dwells a mystical feline named {name}.

Like Jiji, the wise black cat companion, {name} possesses an ancient knowledge that sparkles in their emerald eyes. {description}

Every twilight, {name} would sit by the window, watching the world with the same contemplative grace as the Cat King from the Cat Kingdom. Their purr resonates with the same magical frequency as the wind through Totoro's forest.

The shelter becomes {name}'s temporary castle in the sky, where they reign with gentle dignity, much like Princess Mononoke's connection to the forest spirits. {name}'s whiskers twitch with the wisdom of ages, sensing the approach of their destined human companion.

Soon, {name} will find their Sophie – someone who will see past the ordinary to discover the extraordinary magic that lives within this remarkable soul.""",

        'Dog': f"""In the enchanted neighborhoods of Alexandria, where the Potomac River whispers ancient secrets and cherry blossoms dance in the wind, there lived a remarkable {pet_type} named {name}.

Like Haku from the spirit world, {name} possessed an otherworldly grace and wisdom that touched everyone who met them. {description}

Each morning, {name} would patrol the mystical gardens of Alexandria, much like Totoro watching over the forest spirits. Their gentle soul carried the same warmth as Calcifer's flame, bringing comfort to all who needed it.

The other animals in the shelter would gather around {name}, drawn by the same magnetic kindness that made Kiki such a beloved witch. {name}'s eyes held the depth of ancient forests and the promise of countless adventures yet to come.

Now, {name} waits for their own Chihiro – a brave soul ready to embark on the greatest adventure of all: the journey of unconditional love and companionship.""",

        'default': f"""In the magical realm of Alexandria, where ordinary streets hide extraordinary wonders, there lived a special {pet_type} named {name}.

Like the gentle spirits that inhabit Miyazaki's worlds, {name} possessed a pure heart that could touch the souls of all who encountered them. {description}

{name} carried the same noble spirit as San from the forest, the same loyal heart as Haku, and the same gentle wisdom as Totoro. Their presence brought peace to the shelter, like Howl's moving castle bringing wonder to the countryside.

Every day, {name} would gaze toward the horizon, dreaming of the adventure that awaited – not one of distant lands, but of a warm home where love flows as freely as the wind through Kiki's hair.

The magic of {name}'s story is still being written, waiting for the perfect person to turn the page and begin their shared journey through life's beautiful mysteries."""
    }
    
    return ghibli_stories.get(pet_type, ghibli_stories['default'])

async def create_enhanced_pdf(pets: List[Dict], output_dir: Path, temp_dir: Path, openai_client: Optional[OpenAI]):
    """Create enhanced PDF with real and AI-generated images"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = output_dir / f"ai_enhanced_ghibli_book_{timestamp}.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles with Ghibli colors
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=GHIBLI_COLORS['forest_green'],
        spaceAfter=20,
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=GHIBLI_COLORS['sky_blue'],
        spaceAfter=15,
        alignment=1,
        fontName='Helvetica-Oblique'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=GHIBLI_COLORS['magical_purple'],
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    story_style = ParagraphStyle(
        'StoryText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=GHIBLI_COLORS['earth_brown'],
        spaceAfter=12,
        alignment=4,  # Justified
        leftIndent=20,
        rightIndent=20
    )
    
    # Process each pet
    for i, pet in enumerate(pets):
        name = pet.get('name', f'Pet {i+1}')
        pet_type = pet.get('type', 'animal')
        
        # Title page for each pet
        story.append(Paragraph(f"The Tale of {name}, the Mystical {pet_type} Guardian", title_style))
        story.append(Paragraph("A magical story from the enchanted neighborhoods of Alexandria", subtitle_style))
        story.append(Spacer(1, 30))
        
        # Download original photo
        photos = pet.get('photos', [])
        original_photo_path = None
        if photos:
            photo_url = extract_photo_url(photos[0])
            if photo_url:
                filename = f"{name.lower().replace(' ', '_')}_original.jpg"
                original_photo_path = download_image(photo_url, filename, temp_dir)
        
        # Real Shelter Photo Section
        story.append(Paragraph("■ Real Shelter Photo", section_style))
        if original_photo_path and original_photo_path.exists():
            try:
                img = Image(str(original_photo_path), width=3*inch, height=3*inch)
                story.append(img)
            except Exception as e:
                print(f"❌ Error adding original photo for {name}: {e}")
                story.append(Paragraph(f"Original photo could not be displayed", story_style))
        else:
            story.append(Paragraph(f"Original Photo: (Could not download from shelter)", story_style))
        
        story.append(Spacer(1, 20))
        
        # AI-Enhanced Creative Image Section
        story.append(Paragraph("■ AI-Enhanced Creative Image", section_style))
        if openai_client:
            enhanced_image_path = await generate_ai_image(openai_client, pet, "enhanced", temp_dir, original_photo_path)
            if enhanced_image_path and enhanced_image_path.exists():
                try:
                    img = Image(str(enhanced_image_path), width=3*inch, height=3*inch)
                    story.append(img)
                except Exception as e:
                    print(f"❌ Error adding enhanced image for {name}: {e}")
                    story.append(Paragraph(f"Enhanced Creative Image: (AI-Generated Image - Error displaying)", story_style))
            else:
                story.append(Paragraph(f"Enhanced Creative Image: (AI-Generated Image - Generation failed)", story_style))
        else:
            story.append(Paragraph(f"Enhanced Creative Image: (AI-Generated Image - Requires OpenAI API)", 
                                 ParagraphStyle('PlaceholderText', parent=story_style, textColor=GHIBLI_COLORS['magical_purple'])))
        
        story.append(Spacer(1, 20))
        
        # Story-Specific AI Image Section
        story.append(Paragraph("■ Story-Specific AI Image", section_style))
        if openai_client:
            story_image_path = await generate_ai_image(openai_client, pet, "story", temp_dir, original_photo_path)
            if story_image_path and story_image_path.exists():
                try:
                    img = Image(str(story_image_path), width=3*inch, height=3*inch)
                    story.append(img)
                except Exception as e:
                    print(f"❌ Error adding story image for {name}: {e}")
                    story.append(Paragraph(f"Story-Specific Image: (AI-Generated Image - Error displaying)", story_style))
            else:
                story.append(Paragraph(f"Story-Specific Image: (AI-Generated Image - Generation failed)", story_style))
        else:
            story.append(Paragraph(f"Story-Specific Image: (AI-Generated Image - Requires OpenAI API)", 
                                 ParagraphStyle('PlaceholderText', parent=story_style, textColor=GHIBLI_COLORS['magical_purple'])))
        
        story.append(Spacer(1, 20))
        
        # Ghibli-Style AI Image Section
        story.append(Paragraph("■ Ghibli-Style AI Image", section_style))
        if openai_client:
            ghibli_image_path = await generate_ai_image(openai_client, pet, "ghibli", temp_dir, original_photo_path)
            if ghibli_image_path and ghibli_image_path.exists():
                try:
                    img = Image(str(ghibli_image_path), width=3*inch, height=3*inch)
                    story.append(img)
                except Exception as e:
                    print(f"❌ Error adding ghibli image for {name}: {e}")
                    story.append(Paragraph(f"Ghibli-Style Image: (AI-Generated Image - Error displaying)", story_style))
            else:
                story.append(Paragraph(f"Ghibli-Style Image: (AI-Generated Image - Generation failed)", story_style))
        else:
            story.append(Paragraph(f"Ghibli-Style Image: (AI-Generated Image - Requires OpenAI API)", 
                                 ParagraphStyle('PlaceholderText', parent=story_style, textColor=GHIBLI_COLORS['magical_purple'])))
        
        story.append(Spacer(1, 30))
        
        # Ghibli Story
        ghibli_story = create_ghibli_story(pet)
        for paragraph in ghibli_story.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), story_style))
                story.append(Spacer(1, 12))
        
        # Page break between pets (except for the last one)
        if i < len(pets) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    
    file_size = pdf_path.stat().st_size
    print(f"✅ Enhanced PDF created: {pdf_path} ({file_size:,} bytes)")
    
    return pdf_path

async def main():
    """Main function to create the enhanced AI book"""
    print("🎨 Creating Enhanced AI Pet Adoption Book with Real Image Generation")
    print("=" * 60)
    
    # Load pet data
    pets = load_pets_data()
    if not pets:
        print("❌ No pet data available")
        return
    
    # Create output directory
    output_dir, temp_dir = create_output_directory()
    
    # Get OpenAI client using .env file
    openai_client = get_openai_client()
    
    if openai_client:
        print("🎨 OpenAI API ready - AI images will be generated!")
    else:
        print("⚠️  OpenAI API not available - only real photos will be included.")
    
    # Create enhanced PDF
    pdf_path = await create_enhanced_pdf(pets, output_dir, temp_dir, openai_client)
    
    print(f"\n✅ Book creation complete!")
    print(f"📖 PDF: {pdf_path}")
    print(f"📁 Images saved to: {temp_dir}")
    
    # List downloaded images
    image_files = list(temp_dir.glob("*.jpg")) + list(temp_dir.glob("*.png"))
    if image_files:
        print(f"\n📸 Downloaded {len(image_files)} images:")
        for img_file in sorted(image_files):
            size = img_file.stat().st_size
            print(f"   - {img_file.name} ({size:,} bytes)")

if __name__ == "__main__":
    asyncio.run(main()) 