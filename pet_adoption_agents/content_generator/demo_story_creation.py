#!/usr/bin/env python3
"""
Demo script showing how to create stories and enhanced images using the content generator.
"""

import asyncio
import os
from main import generate_story, generate_enhanced_image_from_photo, generate_badge

# Mock context for demo
class MockContext:
    def __init__(self):
        self.logger = MockLogger()

class MockLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    
    def error(self, msg):
        print(f"[ERROR] {msg}")

async def demo_story_creation():
    """Demo creating stories for pets"""
    print("=== Pet Story Creation Demo ===\n")
    
    # Sample pet data (like what would come from Petfinder)
    sample_pets = [
        {
            "name": "Buddy",
            "type": "dog",
            "description": "A friendly golden retriever who loves playing fetch and swimming. Very gentle with children.",
            "photos": ["https://example.com/buddy.jpg"]  # Real photo URL would go here
        },
        {
            "name": "Whiskers",
            "type": "cat", 
            "description": "A playful tabby cat who enjoys sunbathing and chasing toy mice. Purrs loudly when happy.",
            "photos": ["https://example.com/whiskers.jpg"]
        }
    ]
    
    for pet in sample_pets:
        print(f"Creating content for {pet['name']}...")
        
        # Generate regular story
        print("\n1. Regular Story:")
        try:
            story = await generate_story(pet, humorous=False)
            print(f"Story: {story[:200]}...")
        except Exception as e:
            print(f"Story generation failed: {e}")
        
        # Generate humorous story
        print("\n2. Humorous Story:")
        try:
            funny_story = await generate_story(pet, humorous=True)
            print(f"Funny Story: {funny_story[:200]}...")
        except Exception as e:
            print(f"Humorous story generation failed: {e}")
        
        # Generate enhanced image from photo
        print("\n3. Enhanced Image from Photo:")
        try:
            # Different scene options
            scenes = [
                "in a beautiful park with autumn leaves",
                "in a cozy living room by a fireplace",
                "at a dog beach with waves in the background",
                "in a sunny garden with flowers"
            ]
            
            for scene in scenes[:2]:  # Try first 2 scenes
                enhanced_image_url = await generate_enhanced_image_from_photo(
                    pet, 
                    pet['photos'][0], 
                    scene
                )
                print(f"Enhanced image ({scene}): {enhanced_image_url}")
        except Exception as e:
            print(f"Enhanced image generation failed: {e}")
        
        # Generate badge
        print("\n4. Status Badge:")
        try:
            badge_url = await generate_badge(pet)
            print(f"Badge: {badge_url}")
        except Exception as e:
            print(f"Badge generation failed: {e}")
        
        print("\n" + "="*50 + "\n")

async def demo_custom_scenes():
    """Demo creating images with custom scenes"""
    print("=== Custom Scene Demo ===\n")
    
    pet = {
        "name": "Luna",
        "type": "cat",
        "description": "A sleek black cat with bright green eyes, very curious and intelligent",
        "photos": ["https://example.com/luna.jpg"]
    }
    
    custom_scenes = [
        "sitting regally on a velvet cushion in an elegant room",
        "exploring a magical forest with glowing mushrooms",
        "lounging in a modern apartment with city views",
        "playing in a field of lavender flowers at sunset",
        "wearing a tiny crown in a fairy tale castle setting"
    ]
    
    print(f"Creating custom scenes for {pet['name']}:\n")
    
    for i, scene in enumerate(custom_scenes, 1):
        try:
            image_url = await generate_enhanced_image_from_photo(pet, pet['photos'][0], scene)
            print(f"{i}. Scene: {scene}")
            print(f"   Image URL: {image_url}\n")
        except Exception as e:
            print(f"{i}. Scene: {scene}")
            print(f"   Failed: {e}\n")

def main():
    """Run the demo"""
    print("Content Generator Demo")
    print("Note: This demo requires valid OpenAI API keys to work properly.")
    print("Without API keys, it will show mock behavior.\n")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "placeholder":
        print("⚠️  OPENAI_API_KEY not set. This will show mock behavior only.")
        print("Set your API key with: export OPENAI_API_KEY='your-key-here'\n")
    
    # Run demos
    asyncio.run(demo_story_creation())
    asyncio.run(demo_custom_scenes())

if __name__ == "__main__":
    main() 