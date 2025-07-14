#!/usr/bin/env python3
"""
Create Enhanced Ghibli-style Pets Book with AI-generated images
Uses the existing content_generator and asset_assembler workflow
"""

import json
import os
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add paths to import from different agent directories
sys.path.insert(0, str(Path(__file__).parent / "content_generator"))
sys.path.insert(0, str(Path(__file__).parent / "asset_assembler"))

from content_generator.main import content_generator
from asset_assembler.main import create_pdf_book
from genai_session.utils.context import GenAIContext

class MockAgentContext:
    """Mock context for testing agent functions"""
    def __init__(self):
        self.logger = self
    
    def info(self, message):
        print(f"🤖 Agent Log: {message}")

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

def generate_ghibli_story(pet):
    """Generate a Ghibli-style magical story for a pet"""
    name = pet.get('name', 'Unknown')
    breed = pet.get('breeds', {}).get('primary', 'Mixed')
    age = pet.get('age', 'Adult')
    gender = pet.get('gender', 'Unknown')
    size = pet.get('size', 'Medium')
    description = pet.get('description', 'A wonderful pet looking for a home.')
    tags = pet.get('tags', [])
    
    # Create magical Ghibli-style story based on pet characteristics
    story_elements = []
    
    # Title with magical elements
    if 'Cat' in pet.get('type', ''):
        header = f"The Tale of {name}, the Mystical Feline Guardian"
    else:
        header = f"The Adventure of {name}, the Brave Forest Companion"
    
    # Magical opening
    subheader = "A magical story from the enchanted neighborhoods of Alexandria"
    
    # Main story based on pet characteristics
    paragraphs = []
    paragraphs.append("*In the enchanted neighborhoods of Alexandria, where the Potomac River whispers ancient secrets and cherry blossoms dance in the spring breeze, there lived a very special creature...*")
    
    if 'Shy' in tags:
        paragraphs.append(f"Deep in the quiet corners of the animal sanctuary, {name} discovered the magic of hidden places. Like Chihiro learning to see the spirit world, this gentle {breed.lower()} possessed the rare gift of seeing beauty in stillness. {name}'s whiskers would twitch with ancient wisdom, sensing the emotions of those who needed comfort most.")
    elif 'Friendly' in tags:
        paragraphs.append(f"With a heart as warm as the hearth in Howl's moving castle, {name} the {breed.lower()} became known throughout the shelter as the Great Welcomer. Like Totoro greeting new friends, {name} would bound forward with tail wagging, spreading joy like magical forest dust to everyone who crossed the threshold.")
    elif 'Playful' in tags:
        paragraphs.append(f"In the style of Kiki's playful spirit, {name} the {breed.lower()} turned every day into a grand adventure. Toys became magical artifacts, and the shelter yard transformed into an endless meadow where {name} could chase butterflies that sparkled like the soot sprites in Spirited Away.")
    else:
        paragraphs.append(f"Like the wise forest spirits in Princess Mononoke, {name} the {breed.lower()} carried an ancient soul within. There was something magical about the way {name} moved through the world, as if understanding secrets that only the most perceptive creatures could sense.")
    
    # Age-specific magical elements
    if age == 'Senior':
        paragraphs.append(f"As an elder of the animal kingdom, {name} possessed the wisdom of Calcifer's eternal flame. This {gender.lower()} sage had seen many seasons change, and now sought a special human companion who could appreciate the magic that comes with experience and unconditional love.")
    elif age == 'Young':
        paragraphs.append(f"Young {name} bubbled with the same curious energy as Mei discovering the forest spirits. This {gender.lower()} adventurer was ready to grow alongside a human family, learning life's magical lessons together like characters in a Ghibli tale.")
    else:
        paragraphs.append(f"In the prime of life, {name} radiated the confident magic of San running through the forest. This {gender.lower()} companion had found the perfect balance between playful spirit and gentle wisdom.")
    
    # Incorporate real shelter description with magical twist
    if description and len(description) > 50:
        paragraphs.append(f'*The shelter keepers whispered this tale about our magical friend:* "{description[:300]}{"..." if len(description) > 300 else ""}"')
    
    # Magical quest/call to action
    paragraphs.append(f"Now, {name} waits for the most important adventure of all - finding a forever family. Like every great Ghibli story, this tale needs a loving human companion to help write the next chapter. Will you be the one to discover the magic that {name} has been waiting to share?")
    
    cta = f"Contact the Alexandria Animal Shelter at 703-746-4774 to meet {name} and discover if you're meant to be part of this enchanted story."
    
    return {
        'header': header,
        'subheader': subheader,
        'paragraphs': paragraphs,
        'badge': f"Magical Companion ✨",
        'cta': cta
    }

async def create_enhanced_ghibli_pets_book():
    """Create an enhanced Ghibli-style book with AI-generated images"""
    
    print("🌟 Creating Enhanced Ghibli-Style Pets Book with AI Images")
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
        
        # Step 2: Generate AI-enhanced content using content_generator
        print(f"\n2. 🎨 Generating AI-enhanced content and images...")
        
        ctx = MockAgentContext()
        
        # Use the content_generator to create stories and AI images
        content = await content_generator(ctx, pets, humorous=True)
        
        print(f"✅ Generated content with {len(content['stories'])} stories!")
        print(f"   📸 Original photos: {len(content.get('original_photos', []))}")
        print(f"   🎨 Enhanced images: {len(content.get('enhanced_images', []))}")
        print(f"   📖 Story images: {len(content.get('story_images', []))}")
        print(f"   🌸 Ghibli images: {len(content.get('ghibli_images', []))}")
        
        # Step 3: Replace stories with Ghibli-style stories
        print(f"\n3. ✨ Enhancing stories with Ghibli magic...")
        
        ghibli_stories = []
        for pet in pets:
            ghibli_story = generate_ghibli_story(pet)
            ghibli_stories.append({"pet": pet["name"], "story": ghibli_story})
        
        # Replace the stories in content with our Ghibli stories
        content["stories"] = ghibli_stories
        
        print(f"✅ Enhanced {len(ghibli_stories)} stories with Ghibli magic!")
        
        # Step 4: Save AI-generated images to temp folder
        print(f"\n4. 💾 Saving AI-generated images to temp folder...")
        
        saved_count = 0
        for image_type in ['original_photos', 'enhanced_images', 'story_images', 'ghibli_images']:
            for img in content.get(image_type, []):
                pet_name = img['pet']
                img_url = img['image_url']
                
                # Skip placeholder URLs
                if img_url.startswith('https://example.com') or img_url.startswith('no_'):
                    continue
                
                # Check if it's already a local path
                if os.path.exists(img_url):
                    print(f"   📁 {pet_name} {image_type}: Already local file")
                    saved_count += 1
                    continue
                
                # Download and save to temp
                try:
                    import requests
                    response = requests.get(img_url, timeout=30)
                    if response.status_code == 200:
                        safe_name = pet_name.replace(' ', '_').replace('*', '').lower()
                        filename = f"{safe_name}_{image_type[:-1] if image_type.endswith('s') else image_type}.jpg"
                        save_path = temp_dir / filename
                        with open(save_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Update the content to point to local file
                        img['image_url'] = str(save_path)
                        print(f"   💾 Saved {filename}")
                        saved_count += 1
                    else:
                        print(f"   ❌ Failed to download {pet_name} {image_type}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error downloading {pet_name} {image_type}: {e}")
        
        print(f"✅ Saved {saved_count} AI-generated images to {temp_dir}")
        
        # Step 5: Create the enhanced book using asset_assembler
        print(f"\n5. 📚 Creating enhanced book with AI images...")
        
        pdf_result = create_pdf_book(content)
        
        if pdf_result:
            # Move the PDF to our output directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_pdf_path = output_dir / f"enhanced_ghibli_pets_book_{timestamp}.pdf"
            
            # Find the temporary PDF created by asset_assembler
            import tempfile
            import shutil
            temp_pdf_path = pdf_result  # This should be the path returned by create_pdf_book
            
            if os.path.exists(temp_pdf_path):
                shutil.move(temp_pdf_path, final_pdf_path)
                print(f"✅ Enhanced PDF book created: {final_pdf_path}")
                print(f"   📏 File size: {final_pdf_path.stat().st_size:,} bytes")
            else:
                print(f"❌ Could not find generated PDF at {temp_pdf_path}")
                return False
        else:
            print("❌ Failed to create PDF book")
            return False
        
        # Summary
        print(f"\n🎉 ENHANCED GHIBLI PETS BOOK WITH AI IMAGES COMPLETE!")
        print("=" * 60)
        print(f"📊 Real pets featured: {len(pets)}")
        print(f"📝 Ghibli stories created: {len(ghibli_stories)}")
        print(f"📸 AI images included: {saved_count}")
        print(f"📁 Temp images folder: {temp_dir}")
        print(f"📚 Final book: {final_pdf_path}")
        
        print(f"\n🐾 Featured Magical Companions:")
        for pet in pets:
            name = pet.get('name', 'Unknown')
            breed = pet.get('breeds', {}).get('primary', 'Mixed')
            age = pet.get('age', 'Unknown')
            print(f"   ✨ {name} - {breed} ({age})")
        
        print(f"\n🌟 This book includes real shelter photos AND AI-generated images!")
        print(f"   Contact Alexandria Animal Shelter at 703-746-4774 to meet them!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating enhanced book: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_enhanced_ghibli_pets_book())
    if success:
        print(f"\n✅ Enhanced book creation completed successfully!")
    else:
        print(f"\n❌ Enhanced book creation failed.") 