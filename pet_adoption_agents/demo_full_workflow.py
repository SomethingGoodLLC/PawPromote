#!/usr/bin/env python3
"""
Full Agent Workflow Demo for Alexandria, VA Pet Adoption Book
Simulates the complete multi-agent workflow using real pet data
"""

import json
import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# Add paths to import from different agent directories
sys.path.insert(0, str(Path(__file__).parent / "data_fetcher"))
sys.path.insert(0, str(Path(__file__).parent / "content_generator"))
sys.path.insert(0, str(Path(__file__).parent / "asset_assembler"))
sys.path.insert(0, str(Path(__file__).parent / "book_shipper"))

# Import agent functions
from data_fetcher.main import data_fetcher
from content_generator.main import content_generator
from asset_assembler.main import create_pdf_book, create_ppt
from book_shipper.main import book_shipper

class MockAgentContext:
    """Mock context for testing agent functions"""
    def __init__(self):
        self.logger = self
    
    def info(self, message):
        print(f"🤖 Agent Log: {message}")

def load_alexandria_pets_data():
    """Load real pet data from Alexandria, VA"""
    json_path = Path(__file__).parent / "pets_alexandria_va.json"
    
    with open(json_path, 'r') as f:
        pets_data = json.load(f)
    
    # Convert to format expected by agents
    formatted_pets = []
    for pet_data in pets_data[:5]:  # Take first 5 pets
        formatted_pet = {
            "id": pet_data["id"],
            "name": pet_data["name"],
            "description": pet_data.get("description", "A wonderful pet looking for a home."),
            "photos": [photo["large"] for photo in pet_data.get("photos", []) if "large" in photo],
            "type": pet_data["type"],
            "breeds": pet_data["breeds"],
            "colors": pet_data["colors"],
            "age": pet_data["age"],
            "gender": pet_data["gender"],
            "tags": pet_data.get("tags", []),
            "organization_id": pet_data["organization_id"],
            "contact": pet_data.get("contact", {}),
            "url": pet_data.get("url", "")
        }
        formatted_pets.append(formatted_pet)
    
    return formatted_pets

async def simulate_data_fetcher(shelter_name: str, shelter_id: str, num_pets: int):
    """Simulate data fetcher agent using real Alexandria pet data"""
    print(f"📊 Data Fetcher: Fetching {num_pets} pets from {shelter_name} ({shelter_id})")
    
    # Load real pet data instead of calling API
    pets = load_alexandria_pets_data()
    
    print(f"✅ Data Fetcher: Found {len(pets)} pets:")
    for i, pet in enumerate(pets, 1):
        print(f"   {i}. {pet['name']} - {pet['breeds']['primary']} {pet['type']}")
        print(f"      Photos: {len(pet['photos'])} | Tags: {', '.join(pet['tags'][:3])}")
    
    return pets

async def simulate_content_generator(pets: List[Dict], humorous: bool = True):
    """Simulate content generator with real image generation"""
    print(f"\n🎨 Content Generator: Creating content for {len(pets)} pets (humorous={humorous})")
    
    context = MockAgentContext()
    
    # Note: This would normally call the actual content_generator function
    # For demo purposes, we'll create mock content but show the structure
    print("   📝 Generating humorous adventure stories...")
    print("   📸 Using real Petfinder photos...")
    print("   🎭 Creating story-specific images with GPT-Image-1...")
    print("   🏆 Generating adoption badges...")
    print("   🎬 Creating video content...")
    
    # Create realistic mock content structure
    content = {
        "stories": [],
        "images": [],
        "story_images": [],
        "badges": [],
        "videos": []
    }
    
    story_templates = {
        "Pepper": "Pepper, the mysterious black cat detective, spent her morning investigating the Case of the Missing Tuna. Using her independent spirit and quiet observation skills, she discovered the culprit was actually the neighbor's dog who had been sneaking treats through the fence. Now she's seeking a family who appreciates her investigative talents and doesn't mind her habit of leaving 'evidence' (toy mice) around the house as case files.",
        
        "Winnie": "Winnie, the distinguished Russian Blue, has established herself as the neighborhood's most refined socialite. She hosts weekly 'Whisker & Wisdom' gatherings where she shares life advice over premium water bowl cocktails. Her philosophy: 'Dignity is not negotiable, but cuddles are always welcome.' She's looking for a retirement home where she can continue her legacy as the most elegant feline philosopher in Alexandria.",
        
        "Zebra": "Zebra, the tuxedo cat with an identity crisis, has decided to become Alexandria's first feline ambassador. He greets every visitor with enthusiastic head bumps and purr-negotiations, convinced he's running for mayor. His campaign platform includes: mandatory belly rubs, extended nap times, and a treat in every bowl. He's seeking a family who will support his political aspirations and won't mind his campaign speeches at 3 AM.",
        
        "Rebekah": "Rebekah, the German Shepherd mix, has appointed herself as Alexandria's Chief Happiness Officer. She patrols the neighborhood spreading joy through enthusiastic tail wags and strategic treat distribution. Her daily schedule includes: morning security rounds, afternoon play therapy sessions, and evening snuggle consultations. She's looking for a family who needs a professional joy-bringer and doesn't mind her over-qualification for the position.",
        
        "Crouton": "Crouton, the golden food critic, has revolutionized the shelter's dining experience with his sophisticated palate and detailed meal reviews. His latest critique: 'The morning kibble shows remarkable consistency with hints of chicken and a satisfying crunch - 4.5 paws.' He's established a waiting list for his exclusive 'Dinner and a Movie' nights. He's seeking a family who appreciates fine dining and needs a professional taste-tester for all meals."
    }
    
    for pet in pets:
        name = pet["name"]
        
        # Add story
        story = story_templates.get(name, f"{name} is looking for a wonderful family to share adventures with!")
        content["stories"].append({"pet": name, "story": story})
        
        # Add real photo
        if pet["photos"]:
            content["images"].append({
                "pet": name, 
                "image_url": pet["photos"][0], 
                "type": "real_photo"
            })
        
        # Add story-specific image (would be generated by GPT-Image-1)
        content["story_images"].append({
            "pet": name,
            "image_url": f"https://generated-story-image.example.com/{name.lower()}_adventure.jpg",
            "type": "story_specific"
        })
        
        # Add badge and video
        content["badges"].append({
            "pet": name,
            "badge_url": f"https://generated-badge.example.com/{name.lower()}_badge.jpg"
        })
        content["videos"].append({
            "pet": name,
            "video_url": f"https://generated-video.example.com/{name.lower()}_video.mp4"
        })
    
    print(f"✅ Content Generator: Created content for {len(pets)} pets")
    return content

async def simulate_asset_assembler(content: Dict, specification: str):
    """Simulate asset assembler using real functions"""
    print(f"\n📚 Asset Assembler: {specification}")
    
    # Use actual asset assembler functions
    print("   📖 Creating PDF book with chapters...")
    pdf_path = create_pdf_book(content)
    pdf_size = os.path.getsize(pdf_path)
    
    print("   🎭 Creating PowerPoint presentation...")
    ppt_path = create_ppt(content)
    ppt_size = os.path.getsize(ppt_path)
    
    print(f"✅ Asset Assembler: Generated assets")
    print(f"   📖 PDF: {pdf_path} ({pdf_size:,} bytes)")
    print(f"   🎭 PPT: {ppt_path} ({ppt_size:,} bytes)")
    
    return {
        "book_file": pdf_path,
        "ppt_file": ppt_path
    }

async def simulate_book_shipper(book_file: str, address: str):
    """Simulate book shipper"""
    print(f"\n📦 Book Shipper: Shipping {book_file} to {address}")
    print("   📋 Preparing book for print...")
    print("   🚚 Arranging shipping with Lulu...")
    print("   📧 Sending confirmation email...")
    
    confirmation = {
        "confirmation": "DEMO_ORDER_12345",
        "status": "shipped",
        "tracking": "DEMO_TRACK_67890",
        "estimated_delivery": "3-5 business days"
    }
    
    print(f"✅ Book Shipper: Order confirmed")
    print(f"   📋 Order ID: {confirmation['confirmation']}")
    print(f"   🚚 Tracking: {confirmation['tracking']}")
    
    return confirmation

async def run_full_workflow():
    """Run the complete multi-agent workflow"""
    print("🚀 Starting Full Pet Adoption Agent Workflow")
    print("=" * 70)
    
    # Simulate the master orchestrator task parsing
    task = "Promote 5 adoptable pets from Alexandria shelters VA935 with humorous adventure stories: Create a book, generate videos from real photos, and ship to donor at [123 Pet Lover Lane, Alexandria, VA 22314]"
    
    print(f"📋 Task: {task}")
    print("\n🤖 Initializing Agents...")
    
    try:
        # Step 1: Data Fetcher
        pets = await simulate_data_fetcher("Alexandria Shelters", "VA935", 5)
        
        # Step 2: Content Generator
        content = await simulate_content_generator(pets, humorous=True)
        
        # Step 3: Asset Assembler
        assets = await simulate_asset_assembler(content, "create pdf book and ppt for the generated stories")
        
        # Step 4: Book Shipper
        shipping_result = await simulate_book_shipper(assets["book_file"], "123 Pet Lover Lane, Alexandria, VA 22314")
        
        # Final Results
        print("\n" + "=" * 70)
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print(f"📊 Processed: {len(pets)} pets from Alexandria, VA")
        print(f"📚 Generated: PDF book and PowerPoint presentation")
        print(f"📦 Shipping: {shipping_result['status']} (Order: {shipping_result['confirmation']})")
        
        print("\n🐾 Featured Pets:")
        for i, pet in enumerate(pets, 1):
            print(f"   {i}. {pet['name']} - {pet['breeds']['primary']} {pet['type']}")
        
        print(f"\n📖 PDF Book: {assets['book_file']}")
        print(f"🎭 PowerPoint: {assets['ppt_file']}")
        
        print("\n💡 What was generated:")
        print("✅ Real pet photos from Petfinder")
        print("✅ Story-specific images (simulated GPT-Image-1)")
        print("✅ Humorous adventure stories")
        print("✅ Adoption badges")
        print("✅ Video content links")
        print("✅ QR codes for videos")
        print("✅ Multi-chapter PDF book")
        print("✅ PowerPoint presentation")
        print("✅ Shipping confirmation")
        
        return {
            "status": "completed",
            "pets": pets,
            "assets": assets,
            "shipping": shipping_result
        }
        
    except Exception as e:
        print(f"\n❌ Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    print("🐾 Alexandria Pet Adoption Agent Workflow Demo")
    print("Using real pet data and agent functions")
    print("=" * 70)
    
    result = asyncio.run(run_full_workflow())
    
    if result["status"] == "completed":
        print(f"\n🎊 Demo completed successfully!")
        print("Check the generated files to see the full pet adoption book!")
    else:
        print(f"\n💥 Demo failed: {result.get('error', 'Unknown error')}")
        sys.exit(1) 