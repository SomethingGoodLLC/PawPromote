#!/usr/bin/env python3
"""
Demo script showing the pet adoption agent workflow
"""
import asyncio
import sys
import os

# Add the parent directory to the path to import the agent modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def demo_workflow():
    """Demonstrate the pet adoption workflow"""
    print("🎯 PET ADOPTION AGENT WORKFLOW DEMO")
    print("=" * 50)
    
    # Mock data for demonstration
    pets_data = [
        {
            "id": "pet_001",
            "name": "Buddy",
            "description": "A friendly golden retriever who loves to play fetch and meet new people. Very energetic and great with kids.",
            "photos": ["https://example.com/buddy.jpg"],
            "age": "3 years",
            "breed": "Golden Retriever"
        },
        {
            "id": "pet_002",
            "name": "Whiskers",
            "description": "A curious tabby cat who enjoys sunny windowsills and chasing toy mice. Independent but affectionate.",
            "photos": ["https://example.com/whiskers.jpg"],
            "age": "2 years", 
            "breed": "Tabby Cat"
        },
        {
            "id": "pet_003",
            "name": "Max",
            "description": "An energetic border collie who loves running, herding, and solving puzzle toys. Very intelligent.",
            "photos": ["https://example.com/max.jpg"],
            "age": "4 years",
            "breed": "Border Collie"
        }
    ]
    
    print("\n📋 Step 1: Pet Data (from Alexandria shelters)")
    print("=" * 30)
    for i, pet in enumerate(pets_data, 1):
        print(f"{i}. {pet['name']} - {pet['breed']} ({pet['age']})")
        print(f"   Description: {pet['description'][:60]}...")
    
    print(f"\n✅ Retrieved {len(pets_data)} adoptable pets")
    
    print("\n🎨 Step 2: Content Generation")
    print("=" * 30)
    
    # Generate sample adventure stories
    stories = [
        f"🐕 {pets_data[0]['name']}'s Space Adventure: When Buddy discovered a mysterious glowing tennis ball in the park, he never imagined it would transport him to Planet Biscuit, where he became the hero who saved the Treat Kingdom from the evil Vacuum Monster!",
        
        f"🐱 {pets_data[1]['name']}'s Detective Mystery: Detective Whiskers put on her tiny detective hat and solved the case of the missing catnip cookies, following a trail of crumbs that led her through a thrilling chase across rooftops and into the secret lair of the Cookie Bandit!",
        
        f"🐕 {pets_data[2]['name']}'s Superhero Tale: When the city's frisbees started disappearing, Super Max used his incredible speed and herding abilities to track down the Frisbee Phantom and return joy to all the dogs in Alexandria!"
    ]
    
    for i, story in enumerate(stories, 1):
        print(f"\n📖 Story {i}: {story}")
    
    print(f"\n✅ Generated {len(stories)} humorous adventure stories")
    
    print("\n📚 Step 3: Asset Assembly")
    print("=" * 30)
    
    # Simulate creating book and presentation
    assets = [
        "📄 alexandria_pet_adventures.pdf (24 pages)",
        "🎭 pet_adoption_presentation.pptx (12 slides)",
        "🖼️ pet_photo_collage.jpg (high resolution)",
        "📋 adoption_info_sheet.pdf (contact details)"
    ]
    
    for asset in assets:
        print(f"✅ Created: {asset}")
    
    print("\n📦 Step 4: Book Shipping Preparation")
    print("=" * 30)
    
    shipping_info = {
        "book_title": "Alexandria Pet Adventure Stories",
        "recipient": "Pet Adoption Supporter",
        "address": "123 Pet Lover Lane, Alexandria, VA 22314",
        "format": "Perfect Bound, 8.5x11 inches",
        "paper": "Premium white paper",
        "quantity": 1,
        "shipping": "Standard (5-7 business days)"
    }
    
    print("📚 Book Details:")
    for key, value in shipping_info.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n🎉 WORKFLOW COMPLETED!")
    print("=" * 50)
    
    print("\n📊 Summary:")
    print("✅ 3 pets from Alexandria shelters processed")
    print("✅ 3 humorous adventure stories generated")
    print("✅ 4 marketing assets created (PDF, PPT, images)")
    print("✅ Physical book prepared for shipping")
    
    print("\n🎯 This demonstrates:")
    print("• Multi-agent workflow coordination")
    print("• Natural language task processing")
    print("• Real-world API integration capability")
    print("• End-to-end automation from data to delivery")
    print("• GenAI protocol agent communication")
    
    print("\n💡 For your hackathon demo:")
    print("• Show this running live with real API calls")
    print("• Demonstrate agent-to-agent communication")
    print("• Highlight the GenAI protocol usage")
    print("• Show the complete workflow from plain text input")
    
    print("\n🏆 Key features implemented:")
    print("• Task parsing from natural language")
    print("• Petfinder API integration")
    print("• OpenAI content generation")
    print("• PDF/PPT creation")
    print("• Lulu print-on-demand integration")
    print("• Real-time status tracking")

if __name__ == "__main__":
    asyncio.run(demo_workflow()) 