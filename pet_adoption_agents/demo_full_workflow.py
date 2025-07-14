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

async def simulate_content_generator(pets: List[Dict], humorous: bool = True) -> Dict:
    """Simulate content_generator agent with real pet data"""
    print("🤖 Content Generator: Starting content creation...")
    mock_context = MockAgentContext()
    
    content = {
        "stories": [],
        "images": [],
        "story_images": [],
        "badges": [],
        "videos": [],
        "petfinder_urls": []
    }
    
    # Humorous adventure stories for each pet - structured
    story_templates = {
        "Pepper": {
            "header": "Pepper: Alexandria's Curious Detective 🕵️‍♀️",
            "subheader": "Cracking cases, charming hearts.",
            "paragraphs": [
                "Meet Pepper, the mysterious black cat detective who has appointed herself as the neighborhood's Chief Security Officer. Her daily routine includes conducting thorough investigations of suspicious paper bags, interrogating dust bunnies, and filing detailed reports (by knocking things off tables).",
                "Pepper's greatest case was 'The Mystery of the Disappearing Treats,' which she solved by catching the dog red-pawed. She's seeking a family who appreciates her investigative skills and doesn't mind her habit of leaving 'evidence' (toy mice) in shoes as case files."
            ],
            "badge": "Top Cat Detective 🔍",
            "cta": "Ready to meet your new partner-in-crime-solving? Pepper awaits your companionship!"
        },
        "Winnie": {
            "header": "Winnie: Alexandria's Elegant Philosopher 👑",
            "subheader": "Wisdom, grace, and perfect naps.",
            "paragraphs": [
                "Winnie, the distinguished Russian Blue, has established herself as Alexandria's most refined feline socialite. At her age, she's mastered the art of dignified living and hosts daily 'Whisker & Wisdom' sessions where she shares life advice with younger cats.",
                "Her philosophy: 'Naps are not optional, they're essential.' Winnie is looking for a retirement home where she can continue her legacy as the neighborhood's most elegant philosopher, preferably with a sunny windowsill and premium catnip service."
            ],
            "badge": "Certified Wisdom Keeper 🌟",
            "cta": "Ready to learn from the master of sophisticated living? Winnie is accepting applications for her retirement home!"
        },
        "Zebra": {
            "header": "Zebra: The Identity-Confused Greeter 🐾",
            "subheader": "Part cat, part dog, all personality.",
            "paragraphs": [
                "Zebra, the tuxedo cat with a name that confuses everyone, has decided to embrace his identity crisis by becoming the shelter's official Welcome Committee of One. He greets every visitor with enthusiastic head bumps and purr-negotiations, convinced he's actually a dog trapped in a cat's body.",
                "His daily schedule includes: morning tail-wagging practice, afternoon visitor greeting, and evening 'How to Be More Dog' workshops for confused cats. He's seeking a family who won't mind his existential crisis and will love his over-the-top personality."
            ],
            "badge": "Professional Greeter 🎉",
            "cta": "Ready for a cat who thinks he's a dog? Zebra promises to greet you with enthusiasm every single day!"
        },
        "Rebekah": {
            "header": "Rebekah: Chief Happiness Officer 🌈",
            "subheader": "Professional tail-wagger and joy inspector.",
            "paragraphs": [
                "Rebekah, the German Shepherd mix, has appointed herself as Alexandria's Chief Happiness Officer and Professional Tail-Wagger. She takes her job seriously, conducting daily joy inspections throughout the neighborhood and organizing impromptu play sessions for anyone who looks remotely sad.",
                "Her resume includes: Expert Treat Tester, Certified Good Girl, and Advanced Belly Rub Recipient. She's looking for a family who needs a professional happiness consultant and doesn't mind her over-enthusiasm for making everyone's day better."
            ],
            "badge": "Happiness Expert 😊",
            "cta": "Need a professional happiness consultant? Rebekah is ready to make your every day brighter!"
        },
        "Crouton": {
            "header": "Crouton: The Golden Food Critic 🍽️",
            "subheader": "Dining experience coordinator and taste-tester extraordinaire.",
            "paragraphs": [
                "Crouton, the golden food critic, earned his name after a legendary incident involving a salad bar and his insatiable curiosity about human food. He's since become the shelter's official taste-tester and dining experience coordinator.",
                "His latest review: 'The morning kibble shows remarkable consistency with hints of chicken and a robust crunch - 4.5 paws out of 5.' He's established a waiting list for his exclusive 'Dinner and a Movie' nights. Crouton is seeking a family who appreciates fine dining and needs a professional food quality inspector."
            ],
            "badge": "Master Food Critic 🏆",
            "cta": "Ready for gourmet dining experiences? Crouton will elevate your meals to restaurant quality!"
        }
    }
    
    for pet in pets:
        name = pet["name"]
        
        # Add structured story
        story_dict = story_templates.get(name, {
            "header": f"{name}: Amazing Pet 🐾",
            "subheader": "Looking for a loving home.",
            "paragraphs": [f"{name} is an amazing {pet['type'].lower()} looking for a loving home!"],
            "badge": "Great Pet 🌟",
            "cta": f"Ready to meet {name}? Contact us today!"
        })
        content["stories"].append({"pet": name, "story": story_dict})
        
        # Simulate downloading and enhancing photo with GPT-Image-1
        if pet["photos"]:
            raw_url = pet["photos"][0]
            enhanced_url = raw_url.replace('.jpg', '_enhanced.jpg')  # Simulate enhancement
            content["images"].append({
                "pet": name,
                "image_url": enhanced_url,
                "type": "gpt_enhanced_photo"
            })
            print(f"   🎨 Enhanced photo for {name} with GPT-Image-1")
        else:
            content["images"].append({
                "pet": name,
                "image_url": f"https://placeholder.pet.photo/{name.lower()}.jpg",
                "type": "placeholder"
            })
            print(f"   ⚠️ No photo for {name} - using placeholder")
        
        # Add story-specific image
        content["story_images"].append({
            "pet": name,
            "image_url": f"https://generated-story-image.example.com/{name.lower()}_adventure.jpg",
            "type": "story_specific"
        })
        
        # Add badges and videos
        content["badges"].append({
            "pet": name,
            "badge_url": f"https://generated-badge.example.com/{name.lower()}_badge.jpg"
        })
        content["videos"].append({
            "pet": name,
            "video_url": f"https://generated-video.example.com/{name.lower()}_video.mp4"
        })
        
        # Add Petfinder URL
        content["petfinder_urls"].append({
            "pet": name,
            "url": pet.get("url", "")
        })
    
    print(f"✅ Content Generator: Created enhanced content for {len(pets)} pets")
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