#!/usr/bin/env python3
"""
Create AI-Enhanced Pet Adoption Book with Enhanced Descriptions
Uses detailed manual analysis when AI generation is not available
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime
from io import BytesIO

# PDF creation imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from PIL import Image as PILImage
import qrcode

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
        
        # Check if data is directly an array or wrapped in an object
        if isinstance(data, list):
            pets = data
        else:
            pets = data.get('animals', [])
        
        if not pets:
            print("❌ No animals found in pets data")
            return []
        
        print(f"✅ Loaded {len(pets)} pets from Alexandria Animal Shelter")
        return pets
    
    except Exception as e:
        print(f"❌ Error loading pets data: {e}")
        return []

def load_enhanced_descriptions(pet_name: str) -> Dict[str, str]:
    """Load enhanced descriptions for a pet from the manual analysis"""
    descriptions = {}
    
    # Safe pet name for file lookup
    safe_name = pet_name.lower().replace(' ', '_').replace('*', '').replace('adoption_pending', 'adoption_pending')
    
    # Load different types of enhanced prompts
    enhanced_dir = Path(__file__).parent / "output" / "temp" / "enhanced_manual_analysis"
    
    for image_type in ['professional', 'storybook', 'ghibli']:
        prompt_file = enhanced_dir / f"{safe_name}_{image_type}_enhanced_prompt.txt"
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r') as f:
                    content = f.read()
                descriptions[image_type] = content
            except Exception as e:
                print(f"⚠️  Could not load {image_type} description for {pet_name}: {e}")
                descriptions[image_type] = f"Enhanced {image_type} description not available"
    
    return descriptions

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
        'paragraphs': [
            f"Once upon a time in Alexandria, there lived a special {pet_type} named {name}.",
            f"This {breed} had the most amazing personality and was waiting for someone special to take them home.",
            f"{name} loves to play, cuddle, and bring joy to everyone around.",
            f"Could you be the perfect match for {name}?"
        ],
        'cta': f"Ready to meet {name}? Contact Alexandria Animal Shelter today!"
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
        "petfinder_urls": [],
        "enhanced_descriptions": {}  # Store enhanced descriptions
    }

    for pet in pets:
        pet_name = pet.get('name', 'Pet')
        print(f"  Processing {pet_name}...")
        
        # Load enhanced descriptions
        descriptions = load_enhanced_descriptions(pet_name)
        content["enhanced_descriptions"][pet_name] = descriptions
        
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

def create_pdf_book(content):
    """Create PDF book from content with enhanced descriptions"""
    stories = content["stories"]
    images = {img['pet']: img['image_url'] for img in content["images"]}
    original_photos = {img['pet']: img['image_url'] for img in content.get("original_photos", [])}
    enhanced_images = {img['pet']: img['image_url'] for img in content.get("enhanced_images", [])}
    story_images = {img['pet']: img['image_url'] for img in content.get("story_images", [])}
    ghibli_images = {img['pet']: img['image_url'] for img in content.get("ghibli_images", [])}
    badges = {b['pet']: b['badge_url'] for b in content["badges"]}
    videos = {v['pet']: v['video_url'] for v in content["videos"]}
    petfinder_urls = {p['pet']: p['url'] for p in content.get("petfinder_urls", [])}
    enhanced_descriptions = content.get("enhanced_descriptions", {})
    is_multi = len(stories) > 1

    # Track temporary files for cleanup
    temp_files = []

    def download_and_add_image(img_url, pet_name, image_type, width=3*inch, height=2.25*inch):
        """Helper function to download and add images to the PDF"""
        if not img_url:
            return None
            
        try:
            # Skip placeholder URLs but show enhanced description instead
            if img_url.startswith("https://example.com"):
                # Get enhanced description for this image type
                descriptions = enhanced_descriptions.get(pet_name, {})
                
                if image_type == "Enhanced Creative Photo":
                    desc_key = "professional"
                elif image_type == "Story-Specific Image":
                    desc_key = "storybook"
                elif image_type == "Ghibli-Style Image":
                    desc_key = "ghibli"
                else:
                    desc_key = None
                
                if desc_key and desc_key in descriptions:
                    # Extract key parts from the enhanced description
                    desc_text = descriptions[desc_key]
                    
                    # Find the enhanced prompt section
                    if "ENHANCED PROMPT:" in desc_text:
                        prompt_section = desc_text.split("ENHANCED PROMPT:")[1].strip()
                        # Take first few lines of the prompt
                        prompt_lines = prompt_section.split('\n')[:3]
                        enhanced_desc = ' '.join(prompt_lines)
                    else:
                        enhanced_desc = f"Enhanced {image_type.lower()} based on detailed analysis of {pet_name}'s photo"
                    
                    # Create a styled description instead of generic placeholder
                    desc_style = ParagraphStyle(
                        'EnhancedDesc',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=colors.darkblue,
                        leftIndent=20,
                        rightIndent=20,
                        spaceAfter=10,
                        fontName='Helvetica-Oblique'
                    )
                    
                    flowables.append(Paragraph(f"🎨 {image_type} Vision:", styles['ImageLabel']))
                    flowables.append(Paragraph(enhanced_desc, desc_style))
                    print(f"✅ Added enhanced description for {image_type} for {pet_name}")
                else:
                    flowables.append(Paragraph(f"{image_type}: (AI generation not available - requires OpenAI API key)", styles['Body']))
                return None
            
            # Check if it's a local file path
            if os.path.exists(img_url):
                print(f"Using local image file {image_type} for {pet_name}: {img_url}")
                img = PILImage.open(img_url)
                # For local files, we can use them directly
                pet_img = Image(img_url, width=width, height=height)
                flowables.append(pet_img)
                print(f"✅ Successfully added {image_type} for {pet_name}")
            else:
                # Download from URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(img_url, headers=headers, timeout=30)
                print(f"Downloading {image_type} for {pet_name}: {img_url} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    img = PILImage.open(BytesIO(response.content))
                    img_path = tempfile.mktemp(suffix='.jpg')
                    temp_files.append(img_path)
                    img.save(img_path)
                    pet_img = Image(img_path, width=width, height=height)
                    flowables.append(pet_img)
                    print(f"✅ Successfully added {image_type} for {pet_name}")
                else:
                    flowables.append(Paragraph(f"{image_type}: (Failed to download - HTTP {response.status_code})", styles['Body']))
                    return None
        except Exception as e:
            print(f"❌ Error downloading {image_type} for {pet_name}: {str(e)}")
            flowables.append(Paragraph(f"{image_type}: (Error: {str(e)})", styles['Body']))
            return None

    # Create output file
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = output_dir / f"enhanced_pets_book_{timestamp}.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=36)
    flowables = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Header', fontSize=24, leading=28, alignment=1, spaceAfter=20, fontName='Helvetica-Bold', textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='Subheader', fontSize=14, leading=16, alignment=0, spaceAfter=10, textColor=colors.grey))
    styles.add(ParagraphStyle(name='Body', fontSize=12, leading=14, spaceAfter=10))
    styles.add(ParagraphStyle(name='CTA', fontSize=12, leading=14, spaceAfter=20, fontName='Helvetica-Oblique', textColor=colors.green))
    styles.add(ParagraphStyle(name='ImageLabel', fontSize=10, leading=12, spaceAfter=5, fontName='Helvetica-Bold', textColor=colors.darkblue))

    # Cover page
    flowables.append(Paragraph("Forever Friends: Enhanced AI Pet Adoption Stories", styles['Header']))
    flowables.append(Spacer(1, 0.2*inch))
    flowables.append(Paragraph("From Alexandria's Cutest Companions - With Detailed AI Analysis", styles['Subheader']))
    flowables.append(Spacer(1, 0.5*inch))
    if stories:
        pet = stories[0]['pet']
        # Use enhanced image for cover if available, otherwise original
        cover_img_url = enhanced_images.get(pet) or original_photos.get(pet) or images.get(pet)
        if cover_img_url:
            download_and_add_image(cover_img_url, pet, "Cover Photo", width=4*inch, height=3*inch)
    flowables.append(PageBreak())

    # Table of Contents
    flowables.append(Paragraph("Table of Contents", styles['Header']))
    flowables.append(Spacer(1, 0.2*inch))
    for s in stories:
        header = s['story']['header']
        flowables.append(Paragraph(header, styles['Body']))
    flowables.append(PageBreak())

    # Pet stories
    for story in stories:
        pet = story['pet']
        story_dict = story['story']
        flowables.append(Paragraph(story_dict['header'], styles['Header']))
        flowables.append(Paragraph(story_dict['subheader'], styles['Subheader']))
        flowables.append(Spacer(1, 0.2*inch))

        # 1. Original Petfinder Photo
        flowables.append(Paragraph("📸 Original Petfinder Photo", styles['ImageLabel']))
        original_url = original_photos.get(pet)
        download_and_add_image(original_url, pet, "Original Photo")
        flowables.append(Spacer(1, 0.1*inch))

        # 2. GPT-Image-1 Enhanced Creative Photo
        flowables.append(Paragraph("🎨 GPT-Image-1 Enhanced Creative Photo", styles['ImageLabel']))
        enhanced_url = enhanced_images.get(pet)
        download_and_add_image(enhanced_url, pet, "Enhanced Creative Photo")
        flowables.append(Spacer(1, 0.1*inch))

        # 3. GPT-Image-1 Story-Specific Image
        flowables.append(Paragraph("📖 GPT-Image-1 Story-Specific Image", styles['ImageLabel']))
        story_url = story_images.get(pet)
        download_and_add_image(story_url, pet, "Story-Specific Image")
        flowables.append(Spacer(1, 0.1*inch))

        # 4. GPT-Image-1 Ghibli-Style Image
        flowables.append(Paragraph("🌸 GPT-Image-1 Ghibli-Style Image", styles['ImageLabel']))
        ghibli_url = ghibli_images.get(pet)
        download_and_add_image(ghibli_url, pet, "Ghibli-Style Image")
        flowables.append(Spacer(1, 0.2*inch))

        # Story content
        for paragraph in story_dict['paragraphs']:
            flowables.append(Paragraph(paragraph, styles['Body']))
        flowables.append(Spacer(1, 0.2*inch))

        # CTA
        flowables.append(Paragraph(story_dict['cta'], styles['CTA']))
        flowables.append(Spacer(1, 0.2*inch))

        if story != stories[-1]:  # Not the last story
            flowables.append(PageBreak())

    # Build PDF
    doc.build(flowables)
    
    # Clean up temporary files
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except:
            pass
    
    return str(pdf_path)

async def main():
    """Main function to create AI-enhanced book with descriptions"""
    print("🎨 Creating AI-Enhanced Pet Adoption Book with Enhanced Descriptions")
    print("=" * 70)
    
    # Load pet data
    pets = load_pets_data()
    if not pets:
        print("❌ No pet data available")
        return
    
    # Generate content with AI images and enhanced descriptions
    content = await generate_content_for_pets(pets, humorous=True)
    
    print(f"\n✅ Content generation complete!")
    print(f"   📖 Stories: {len(content.get('stories', []))}")
    print(f"   📸 Original photos: {len(content.get('original_photos', []))}")
    print(f"   🎨 Enhanced images: {len(content.get('enhanced_images', []))}")
    print(f"   📚 Story images: {len(content.get('story_images', []))}")
    print(f"   🌸 Ghibli images: {len(content.get('ghibli_images', []))}")
    print(f"   📝 Enhanced descriptions: {len(content.get('enhanced_descriptions', []))}")
    
    # Create PDF
    print(f"\n📚 Creating PDF book with enhanced descriptions...")
    try:
        pdf_path = create_pdf_book(content)
        print(f"✅ PDF created: {pdf_path}")
        
        # Check file size
        file_size = Path(pdf_path).stat().st_size
        print(f"📄 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n✅ Enhanced AI Book Creation Complete!")
    print(f"📖 Your book with detailed descriptions is ready: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(main()) 