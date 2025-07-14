#!/usr/bin/env python3
"""
Create a Ghibli-style Real Pets Book with Alexandria, VA pets
Generates magical, whimsical stories with pet photos in Studio Ghibli style
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import tempfile
import asyncio
import shutil
from content_generator.main import content_generator
from genai_session.utils.context import GenAIContext

def load_real_alexandria_pets():
    """Load real pet data from Alexandria, VA"""
    json_path = Path(__file__).parent / "pets_alexandria_va.json"
    
    if not json_path.exists():
        print(f"❌ Pet data file not found: {json_path}")
        return []
    
    with open(json_path, 'r') as f:
        pets_data = json.load(f)
    
    # Take first 5 pets and format for display
    return pets_data[:5]

def download_pet_photo(photo_url, pet_name, temp_dir):
    """Download a pet photo and return the local path"""
    try:
        response = requests.get(photo_url, timeout=10)
        response.raise_for_status()
        
        # Get file extension from URL
        parsed_url = urlparse(photo_url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1] if os.path.splitext(path)[1] else '.jpg'
        
        # Create safe filename
        safe_name = "".join(c for c in pet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}_photo{ext}"
        filepath = temp_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        print(f"   ⚠️  Could not download photo for {pet_name}: {e}")
        return None

def generate_ghibli_story(pet, temp_dir):
    """Generate a Ghibli-style magical story for a pet"""
    name = pet.get('name', 'Unknown')
    breed = pet.get('breeds', {}).get('primary', 'Mixed')
    age = pet.get('age', 'Adult')
    gender = pet.get('gender', 'Unknown')
    size = pet.get('size', 'Medium')
    description = pet.get('description', 'A wonderful pet looking for a home.')
    tags = pet.get('tags', [])
    photos = pet.get('photos', [])
    
    # Download the first photo if available
    photo_path = None
    if photos:
        photo_url = photos[0].get('large') or photos[0].get('medium') or photos[0].get('small')
        if photo_url:
            photo_path = download_pet_photo(photo_url, name, temp_dir)
    
    # Create magical Ghibli-style story based on pet characteristics
    story_elements = []
    
    # Title with magical elements
    if 'Cat' in pet.get('type', ''):
        story_elements.append(f"🌟 **The Tale of {name}, the Mystical Feline Guardian** 🌟")
    else:
        story_elements.append(f"🌟 **The Adventure of {name}, the Brave Forest Companion** 🌟")
    
    # Magical opening
    story_elements.append("")
    story_elements.append("*In the enchanted neighborhoods of Alexandria, where the Potomac River whispers ancient secrets and cherry blossoms dance in the spring breeze, there lived a very special creature...*")
    story_elements.append("")
    
    # Main story based on pet characteristics
    if 'Shy' in tags:
        story_elements.append(f"Deep in the quiet corners of the animal sanctuary, {name} discovered the magic of hidden places. Like Chihiro learning to see the spirit world, this gentle {breed.lower()} possessed the rare gift of seeing beauty in stillness. {name}'s whiskers would twitch with ancient wisdom, sensing the emotions of those who needed comfort most.")
    elif 'Friendly' in tags:
        story_elements.append(f"With a heart as warm as the hearth in Howl's moving castle, {name} the {breed.lower()} became known throughout the shelter as the Great Welcomer. Like Totoro greeting new friends, {name} would bound forward with tail wagging, spreading joy like magical forest dust to everyone who crossed the threshold.")
    elif 'Playful' in tags:
        story_elements.append(f"In the style of Kiki's playful spirit, {name} the {breed.lower()} turned every day into a grand adventure. Toys became magical artifacts, and the shelter yard transformed into an endless meadow where {name} could chase butterflies that sparkled like the soot sprites in Spirited Away.")
    else:
        story_elements.append(f"Like the wise forest spirits in Princess Mononoke, {name} the {breed.lower()} carried an ancient soul within. There was something magical about the way {name} moved through the world, as if understanding secrets that only the most perceptive creatures could sense.")
    
    story_elements.append("")
    
    # Age-specific magical elements
    if age == 'Senior':
        story_elements.append(f"As an elder of the animal kingdom, {name} possessed the wisdom of Calcifer's eternal flame. This {gender.lower()} sage had seen many seasons change, and now sought a special human companion who could appreciate the magic that comes with experience and unconditional love.")
    elif age == 'Young':
        story_elements.append(f"Young {name} bubbled with the same curious energy as Mei discovering the forest spirits. This {gender.lower()} adventurer was ready to grow alongside a human family, learning life's magical lessons together like characters in a Ghibli tale.")
    else:
        story_elements.append(f"In the prime of life, {name} radiated the confident magic of San running through the forest. This {gender.lower()} companion had found the perfect balance between playful spirit and gentle wisdom.")
    
    story_elements.append("")
    
    # Incorporate real shelter description with magical twist
    if description and len(description) > 50:
        story_elements.append("*The shelter keepers whispered this tale about our magical friend:*")
        story_elements.append(f'"{description[:300]}{"..." if len(description) > 300 else ""}"')
        story_elements.append("")
    
    # Magical quest/call to action
    story_elements.append(f"Now, {name} waits for the most important adventure of all - finding a forever family. Like every great Ghibli story, this tale needs a loving human companion to help write the next chapter. Will you be the one to discover the magic that {name} has been waiting to share?")
    
    story_elements.append("")
    story_elements.append("*The forest spirits believe that every creature has a perfect match waiting somewhere in the world. Perhaps that match is you.*")
    
    story_elements.append("")
    story_elements.append("🏠 **Begin Your Magical Journey:**")
    story_elements.append(f"Contact the Alexandria Animal Shelter at 703-746-4774 to meet {name} and discover if you're meant to be part of this enchanted story.")
    
    return {
        'story': '\n'.join(story_elements),
        'photo_path': photo_path
    }

def create_ghibli_pdf(pets, stories_data, output_path):
    """Create a magical Ghibli-style PDF with photos"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
        
        # Create PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        
        # Ghibli-inspired color palette
        forest_green = HexColor('#2E7D32')
        sky_blue = HexColor('#1976D2')
        warm_orange = HexColor('#F57C00')
        
        # Custom styles
        title_style = ParagraphStyle(
            'GhibliTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=forest_green,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'GhibliSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            textColor=sky_blue,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        story_title_style = ParagraphStyle(
            'StoryTitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            textColor=warm_orange,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        story_text_style = ParagraphStyle(
            'StoryText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14
        )
        
        magical_style = ParagraphStyle(
            'MagicalText',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=forest_green,
            alignment=TA_JUSTIFY,
            fontName='Helvetica-Oblique',
            leading=13
        )
        
        story = []
        
        # Magical title page
        story.append(Paragraph("🌟 Alexandria Pets: Magical Tales of Hope 🌟", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("*Where Every Pet Has a Story Worth Telling*", subtitle_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Featuring {len(pets)} enchanting companions seeking their forever homes", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("✨ Inspired by the magic of Studio Ghibli ✨", magical_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Created on: " + datetime.now().strftime("%B %d, %Y"), styles['Normal']))
        story.append(PageBreak())
        
        # Add each pet story
        for i, (pet, story_data) in enumerate(zip(pets, stories_data)):
            name = pet.get('name', 'Unknown')
            breed = pet.get('breeds', {}).get('primary', 'Mixed')
            age = pet.get('age', 'Unknown')
            gender = pet.get('gender', 'Unknown')
            size = pet.get('size', 'Unknown')
            
            # Pet photo if available
            if story_data['photo_path'] and story_data['photo_path'].exists():
                try:
                    # Add photo with magical border effect
                    img = Image(str(story_data['photo_path']), width=4*inch, height=3*inch)
                    img.hAlign = 'CENTER'
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    print(f"   ⚠️  Could not add photo for {name}: {e}")
            
            # Pet details in magical format
            details = f"🐾 <b>Breed:</b> {breed} | <b>Age:</b> {age} | <b>Gender:</b> {gender} | <b>Size:</b> {size} 🐾"
            story.append(Paragraph(details, story_text_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Story content with magical formatting
            story_paragraphs = story_data['story'].split('\n')
            for paragraph in story_paragraphs:
                if paragraph.strip():
                    if paragraph.startswith('🌟 **') or paragraph.startswith('🏠 **'):
                        # Story titles
                        clean_title = paragraph.replace('🌟 **', '').replace('**', '').replace('🏠 **', '')
                        story.append(Paragraph(clean_title, story_title_style))
                    elif paragraph.startswith('*') and paragraph.endswith('*'):
                        # Magical italic text
                        clean_text = paragraph[1:-1]  # Remove asterisks
                        story.append(Paragraph(clean_text, magical_style))
                    elif paragraph.startswith('"') and paragraph.endswith('"'):
                        # Shelter quotes
                        story.append(Paragraph(paragraph, magical_style))
                    else:
                        # Regular story text
                        story.append(Paragraph(paragraph, story_text_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # Add page break except for last story
            if i < len(pets) - 1:
                story.append(PageBreak())
        
        # Magical contact information page
        story.append(PageBreak())
        story.append(Paragraph("🏰 Begin Your Magical Journey 🏰", story_title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("*Every great adventure begins with a single step...*", magical_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Alexandria Animal Shelter</b>", story_text_style))
        story.append(Paragraph("4101 Eisenhower Ave", story_text_style))
        story.append(Paragraph("Alexandria, VA 22304", story_text_style))
        story.append(Paragraph("Phone: 703-746-4774", story_text_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Visit us to meet these magical companions in person and discover if you're meant to be part of their enchanted story!", magical_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("✨ *The forest spirits believe that every creature has a perfect match waiting somewhere in the world.* ✨", magical_style))
        
        # Build PDF
        doc.build(story)
        return True
        
    except ImportError:
        print("❌ ReportLab not available. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

async def create_ghibli_pets_book():
    """Create a Ghibli-style book with real pets from Alexandria, VA"""
    
    print("🌟 Creating Enhanced Ghibli-Style Real Pets Book - Alexandria, VA")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Create temp directory for generated images
    temp_dir = output_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Load real pet data
        print("\n1. 📊 Loading real pet data from Alexandria, VA...")
        pets = load_real_alexandria_pets()
        
        if not pets:
            print("❌ No pets data available")
            return False
        
        print(f"✅ Loaded {len(pets)} real pets from Alexandria Animal Shelter!")
        
        # Display pets
        for i, pet in enumerate(pets, 1):
            name = pet.get('name', 'Unknown')
            breed = pet.get('breeds', {}).get('primary', 'Mixed')
            print(f"   {i}. {name} - {breed}")
        
        # Step 2: Generate content with AI images using content_generator
        print(f"\n2. 🎨 Generating AI-enhanced content and images...")
        
        agent_context = GenAIContext()  # Create mock context
        content = await content_generator(agent_context, pets, humorous=True)  # Generate with humorous style
        
        # Save generated images to temp folder
        print("   💾 Saving generated images to {temp_dir}...")
        for image_type in ['original_photos', 'enhanced_images', 'story_images', 'ghibli_images']:
            for img in content.get(image_type, []):
                pet_name = img['pet']
                img_url = img['image_url']
                if not img_url.startswith('https://example.com') and not img_url.startswith('no_'):
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        safe_name = pet_name.replace(' ', '_').lower()
                        filename = f"{safe_name}_{image_type[:-7]}.jpg"  # e.g. pepper_ghibli.jpg
                        save_path = temp_dir / filename
                        with open(save_path, 'wb') as f:
                            f.write(response.content)
                        print(f"     Saved {filename}")
        
        print(f"✅ Generated content with {len(content['stories'])} stories and AI images!")
        
        # Prepare stories_data with AI images paths
        stories_data = []
        for pet in pets:
            name = pet.get('name', 'Unknown')
            safe_name = name.replace(' ', '_').lower()
            story_data = {
                'story': generate_ghibli_story(pet)['story'],  # Keep original story generation
                'photo_path': temp_dir / f"{safe_name}_original.jpg" if (temp_dir / f"{safe_name}_original.jpg").exists() else None,
                'enhanced_path': temp_dir / f"{safe_name}_enhanced.jpg" if (temp_dir / f"{safe_name}_enhanced.jpg").exists() else None,
                'story_img_path': temp_dir / f"{safe_name}_story.jpg" if (temp_dir / f"{safe_name}_story.jpg").exists() else None,
                'ghibli_path': temp_dir / f"{safe_name}_ghibli.jpg" if (temp_dir / f"{safe_name}_ghibli.jpg").exists() else None
            }
            stories_data.append(story_data)
        
        # Step 3: Create the magical book
        print(f"\n3. 📚 Creating enhanced magical book with AI-generated images...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = output_dir / f"enhanced_ghibli_pets_book_{timestamp}.pdf"
        
        pdf_success = create_enhanced_ghibli_pdf(pets, stories_data, pdf_path)
        
        if pdf_success:
            print(f"✅ Enhanced PDF book created: {pdf_path}")
            if pdf_path.exists():
                print(f"   📏 File size: {pdf_path.stat().st_size:,} bytes")
        
        # Summary
        print(f"\n🎉 ENHANCED MAGICAL GHIBLI PETS BOOK CREATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Real pets featured: {len(pets)}")
        print(f"📝 Magical stories created: {len(stories_data)}")
        print(f"📸 AI Images included: {sum(1 for s in stories_data if s['ghibli_path'])}")
        print(f"📚 Book format: Enhanced Ghibli-style PDF with multiple AI images per pet")
        print(f"📁 Temp images: {temp_dir}")
        print(f"📁 Output directory: {output_dir}")
        
        print(f"\n🐾 Featured Magical Companions:")
        for pet in pets:
            name = pet.get('name', 'Unknown')
            breed = pet.get('breeds', {}).get('primary', 'Mixed')
            age = pet.get('age', 'Unknown')
            print(f"   ✨ {name} - {breed} ({age})")
        
        print(f"\n🌟 These magical stories bring real pets to life in the style of Studio Ghibli!")
        print(f"   Contact Alexandria Animal Shelter at 703-746-4774 to meet them!")
        
        return True
        
    finally:
        # Don't clean up temp dir as per user request
        pass

def create_enhanced_ghibli_pdf(pets, stories_data, output_path):
    """Create an enhanced magical Ghibli-style PDF with multiple AI images and prettier design"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, FrameBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
        from reportlab.graphics.shapes import Drawing, Rect
        from reportlab.platypus.frames import Frame
        from reportlab.pdfgen.canvas import Canvas
        
        # Create PDF document with custom canvas for backgrounds
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, 
                                leftMargin=0.5*inch, rightMargin=0.5*inch,
                                topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        # Enhanced color palette for prettier Ghibli feel
        forest_green = HexColor('#228B22')
        sky_blue = HexColor('#87CEEB')
        warm_orange = HexColor('#FFA500')
        soft_pink = HexColor('#FFB6C1')
        magical_purple = HexColor('#9370DB')
        
        # Prettier custom styles with better typography
        title_style = ParagraphStyle(
            'GhibliTitle',
            fontName='Helvetica-Bold',
            fontSize=32,
            leading=36,
            textColor=forest_green,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        subtitle_style = ParagraphStyle(
            'GhibliSubtitle',
            fontName='Helvetica-Oblique',
            fontSize=16,
            leading=18,
            textColor=sky_blue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        story_title_style = ParagraphStyle(
            'StoryTitle',
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=warm_orange,
            alignment=TA_LEFT,
            spaceAfter=15
        )
        
        story_text_style = ParagraphStyle(
            'StoryText',
            fontName='Helvetica',
            fontSize=12,
            leading=16,
            alignment=TA_JUSTIFY,
            textColor=black,
            spaceAfter=10
        )
        
        magical_style = ParagraphStyle(
            'MagicalText',
            fontName='Helvetica-Oblique',
            fontSize=11,
            leading=14,
            textColor=magical_purple,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )
        
        # Function to add decorative frame around images
        def add_image_with_frame(img_path, width, height):
            if not img_path or not img_path.exists():
                return Spacer(1, height)
            
            drawing = Drawing(width + 20, height + 20)
            drawing.add(Rect(0, 0, width + 20, height + 20, strokeColor=soft_pink, fillColor=white, strokeWidth=2))
            drawing.add(Rect(5, 5, width + 10, height + 10, strokeColor=warm_orange, fillColor=None, strokeWidth=1))
            img = Image(str(img_path), width=width, height=height)
            img.drawOn(drawing._canvas, 10, 10)
            return drawing
        
        story_flow = []
        
        # Enhanced title page with magical background (simulated with text)
        story_flow.append(Paragraph("🌸✨ Alexandria Pets: Magical Tales of Hope ✨🌸", title_style))
        story_flow.append(Spacer(1, 0.3*inch))
        story_flow.append(Paragraph("*Where Every Whisker Hides a Wonder*", subtitle_style))
        story_flow.append(Spacer(1, 0.4*inch))
        story_flow.append(Paragraph(f"Featuring {len(pets)} enchanting companions seeking their forever homes", story_text_style))
        story_flow.append(Spacer(1, 0.3*inch))
        story_flow.append(Paragraph("🌟 Inspired by the whimsical world of Studio Ghibli 🌟", magical_style))
        story_flow.append(Spacer(1, 0.3*inch))
        story_flow.append(Paragraph("Created on: " + datetime.now().strftime("%B %d, %Y"), story_text_style))
        story_flow.append(PageBreak())
        
        # Add each pet story with multiple images
        for i, (pet, story_data) in enumerate(zip(pets, stories_data)):
            name = pet.get('name', 'Unknown')
            breed = pet.get('breeds', {}).get('primary', 'Mixed')
            age = pet.get('age', 'Unknown')
            gender = pet.get('gender', 'Unknown')
            size = pet.get('size', 'Unknown')
            
            # Pet details with pretty icons
            details = f"🐾 <font color=orange>Breed:</font> {breed} | <font color=orange>Age:</font> {age} | <font color=orange>Gender:</font> {gender} | <font color=orange>Size:</font> {size} 🐾"
            story_flow.append(Paragraph(details, magical_style))
            story_flow.append(Spacer(1, 0.2*inch))
            
            # Add original photo
            if story_data['photo_path']:
                story_flow.append(Paragraph("📸 Real Shelter Photo", story_text_style))
                story_flow.append(add_image_with_frame(story_data['photo_path'], 2.5*inch, 1.875*inch))
                story_flow.append(Spacer(1, 0.2*inch))
            
            # Add enhanced AI image
            if story_data.get('enhanced_path'):
                story_flow.append(Paragraph("🎨 AI-Enhanced Creative Image", story_text_style))
                story_flow.append(add_image_with_frame(story_data['enhanced_path'], 2.5*inch, 1.875*inch))
                story_flow.append(Spacer(1, 0.2*inch))
            
            # Add story AI image
            if story_data.get('story_img_path'):
                story_flow.append(Paragraph("📖 Story-Specific AI Image", story_text_style))
                story_flow.append(add_image_with_frame(story_data['story_img_path'], 2.5*inch, 1.875*inch))
                story_flow.append(Spacer(1, 0.2*inch))
            
            # Add Ghibli AI image
            if story_data.get('ghibli_path'):
                story_flow.append(Paragraph("🌟 Ghibli-Style AI Image", story_text_style))
                story_flow.append(add_image_with_frame(story_data['ghibli_path'], 2.5*inch, 1.875*inch))
                story_flow.append(Spacer(1, 0.2*inch))
            
            # Story content with enhanced formatting
            story_paragraphs = story_data['story'].split('\n')
            for paragraph in story_paragraphs:
                if paragraph.strip():
                    if paragraph.startswith('🌟 **') or paragraph.startswith('🏠 **'):
                        clean_title = paragraph.replace('🌟 **', '').replace('**', '').replace('🏠 **', '')
                        story_flow.append(Paragraph(clean_title, story_title_style))
                    elif paragraph.startswith('*') and paragraph.endswith('*'):
                        clean_text = paragraph[1:-1]
                        story_flow.append(Paragraph(clean_text, magical_style))
                    elif paragraph.startswith('"') and paragraph.endswith('"'):
                        story_flow.append(Paragraph(paragraph, magical_style))
                    else:
                        story_flow.append(Paragraph(paragraph, story_text_style))
                    story_flow.append(Spacer(1, 0.1*inch))
            
            # Add decorative separator
            story_flow.append(Paragraph("✨🌸✨", magical_style))
            story_flow.append(PageBreak())
        
        # Enhanced contact page
        story_flow.append(Paragraph("🏰 Begin Your Magical Journey 🏰", title_style))
        story_flow.append(Spacer(1, 0.3*inch))
        story_flow.append(Paragraph("*Every great adventure begins with a single step...*", subtitle_style))
        story_flow.append(Spacer(1, 0.2*inch))
        story_flow.append(Paragraph("<b>Alexandria Animal Shelter</b>", story_text_style))
        story_flow.append(Paragraph("4101 Eisenhower Ave", story_text_style))
        story_flow.append(Paragraph("Alexandria, VA 22304", story_text_style))
        story_flow.append(Paragraph("Phone: 703-746-4774", story_text_style))
        story_flow.append(Spacer(1, 0.3*inch))
        story_flow.append(Paragraph("Visit us to meet these magical companions in person and discover if you're meant to be part of their enchanted story!", magical_style))
        story_flow.append(Spacer(1, 0.2*inch))
        story_flow.append(Paragraph("✨ *The forest spirits believe that every creature has a perfect match waiting somewhere in the world.* ✨", magical_style))
        
        # Build PDF
        doc.build(story_flow)
        return True
        
    except ImportError:
        print("❌ ReportLab not available. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_ghibli_pets_book())
    if success:
        print(f"\n✅ Magical book creation completed successfully!")
    else:
        print(f"\n❌ Magical book creation failed.")