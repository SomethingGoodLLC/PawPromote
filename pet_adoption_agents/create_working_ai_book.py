#!/usr/bin/env python3
"""
Create AI-Enhanced Pet Adoption Book using existing working components
Uses content_generator and asset_assembler properly
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the content_generator and asset_assembler to path
sys.path.append(str(Path(__file__).parent / "content_generator"))
sys.path.append(str(Path(__file__).parent / "asset_assembler"))

from content_generator.main import content_generator
from asset_assembler.main import asset_assembler

# Mock context for testing
class MockAgentContext:
    def __init__(self):
        self.logger = MockLogger()
    
class MockLogger:
    def info(self, msg):
        print(f"ℹ️  {msg}")
    
    def error(self, msg):
        print(f"❌ {msg}")
    
    def warning(self, msg):
        print(f"⚠️  {msg}")

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

def create_output_directory() -> tuple[Path, Path]:
    """Create output and temp directories"""
    output_dir = Path(__file__).parent / "output"
    temp_dir = output_dir / "temp"
    
    output_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)
    
    return output_dir, temp_dir

async def main():
    """Main function to create AI-enhanced book using existing components"""
    print("🎨 Creating AI-Enhanced Pet Adoption Book using Working Components")
    print("=" * 65)
    
    # Load pet data
    pets = load_pets_data()
    if not pets:
        print("❌ No pet data available")
        return
    
    # Create output directories
    output_dir, temp_dir = create_output_directory()
    
    # Create mock context
    ctx = MockAgentContext()
    
    print(f"\n🔄 Step 1: Generating content with AI images...")
    print(f"📊 Processing {len(pets)} pets from Alexandria Animal Shelter")
    
    # Use the existing content_generator to create stories and AI images
    try:
        content = await content_generator(ctx, pets, humorous=True)
        print(f"✅ Content generation complete!")
        print(f"   📖 Stories: {len(content.get('stories', []))}")
        print(f"   📸 Original photos: {len(content.get('original_photos', []))}")
        print(f"   🎨 Enhanced images: {len(content.get('enhanced_images', []))}")
        print(f"   📚 Story images: {len(content.get('story_images', []))}")
        print(f"   🌸 Ghibli images: {len(content.get('ghibli_images', []))}")
        print(f"   🏆 Badges: {len(content.get('badges', []))}")
        print(f"   🎬 Videos: {len(content.get('videos', []))}")
        
    except Exception as e:
        print(f"❌ Error in content generation: {e}")
        return
    
    print(f"\n🔄 Step 2: Assembling book with AI images...")
    
    # Use the existing asset_assembler to create the PDF
    try:
        result = await asset_assembler(ctx, content, "Enhanced AI Pet Adoption Book")
        print(f"✅ Book assembly complete!")
        print(f"📖 PDF: {result.get('book_file', 'Not created')}")
        print(f"📊 PPT: {result.get('ppt_file', 'Not created')}")
        
    except Exception as e:
        print(f"❌ Error in book assembly: {e}")
        return
    
    print(f"\n✅ AI-Enhanced Book Creation Complete!")
    print(f"📁 Check the output directory for your book and images")
    
    # List generated files
    if temp_dir.exists():
        image_files = list(temp_dir.glob("*.jpg")) + list(temp_dir.glob("*.png"))
        if image_files:
            print(f"\n📸 Generated images ({len(image_files)}):")
            for img_file in sorted(image_files):
                size = img_file.stat().st_size
                print(f"   - {img_file.name} ({size:,} bytes)")

if __name__ == "__main__":
    asyncio.run(main()) 