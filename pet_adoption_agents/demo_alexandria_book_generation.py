#!/usr/bin/env python3
"""
Alexandria Pet Adoption Book Generation Demo
Uses real pet data and asset assembler functions to create a book
"""

import json
import os
import sys
from pathlib import Path

# Add asset assembler path
sys.path.insert(0, str(Path(__file__).parent / "asset_assembler"))

# Import only the functions we need (not the full agent)
from asset_assembler.main import create_pdf_book, create_ppt

def load_alexandria_pets():
    """Load real pet data from Alexandria, VA"""
    json_path = Path(__file__).parent / "pets_alexandria_va.json"
    
    with open(json_path, 'r') as f:
        pets_data = json.load(f)
    
    # Format for display
    pets = []
    for pet_data in pets_data[:5]:
        pet = {
            "name": pet_data["name"],
            "type": pet_data["type"],
            "breed": pet_data["breeds"]["primary"],
            "age": pet_data["age"],
            "gender": pet_data["gender"],
            "description": pet_data.get("description", "A wonderful pet looking for a home."),
            "photos": [photo["large"] for photo in pet_data.get("photos", []) if "large" in photo],
            "tags": pet_data.get("tags", []),
            "organization": pet_data["organization_id"],
            "contact": pet_data.get("contact", {}).get("email", ""),
            "url": pet_data.get("url", "")
        }
        pets.append(pet)
    
    return pets

def create_content_for_pets(pets):
    """Create content structure with real pet data and humorous stories"""
    
    # Humorous adventure stories for each pet - structured format
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
    
    content = {
        "stories": [],
        "images": [],
        "story_images": [],
        "badges": [],
        "videos": [],
        "petfinder_urls": []
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
        
        # Add real pet photo processed through GPT-Image-1
        if pet["photos"]:
            content["images"].append({
                "pet": name,
                "image_url": pet["photos"][0],  # This would be the GPT-Image-1 enhanced version
                "type": "gpt_enhanced_photo"
            })
        else:
            # Placeholder if no photo
            content["images"].append({
                "pet": name,
                "image_url": f"https://placeholder.pet.photo/{name.lower()}.jpg",
                "type": "placeholder"
            })
        
        # Add story-specific image (simulated GPT-Image-1 generation)
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
        
        # Add Petfinder URL
        content["petfinder_urls"].append({
            "pet": name,
            "url": pet.get("url", "")
        })
    
    return content

def print_pet_info(pets):
    """Print detailed information about each pet"""
    print("🐾 Featured Pets from Alexandria, VA:")
    print("=" * 70)
    
    for i, pet in enumerate(pets, 1):
        print(f"\n{i}. {pet['name']} - {pet['breed']} {pet['type']}")
        print(f"   📊 Details: {pet['age']} {pet['gender']}")
        print(f"   🏷️  Tags: {', '.join(pet['tags'][:4])}")
        print(f"   📸 Photos: {len(pet['photos'])} available")
        print(f"   🏢 Organization: {pet['organization']}")
        print(f"   📧 Contact: {pet['contact']}")
        print(f"   🌐 Petfinder: {pet['url'][:50]}..." if pet['url'] else "   🌐 No URL available")
        print(f"   📝 Description: {pet['description'][:100]}...")

def main():
    """Main function to generate the pet adoption book"""
    print("📚 Alexandria Pet Adoption Book Generator")
    print("Using Real Pet Data + Asset Assembler Workflow")
    print("=" * 70)
    
    try:
        # Load real pet data
        print("📊 Loading real pet data from Alexandria, VA...")
        pets = load_alexandria_pets()
        print(f"✅ Loaded {len(pets)} pets from Alexandria shelters")
        
        # Display pet information
        print_pet_info(pets)
        
        # Create content structure
        print(f"\n🎨 Creating content for {len(pets)} pets...")
        print("   📝 Writing humorous adventure stories...")
        print("   📸 Using real Petfinder photos...")
        print("   🎭 Simulating GPT-Image-1 story illustrations...")
        print("   🏆 Creating adoption badges...")
        print("   🎬 Adding video content...")
        
        content = create_content_for_pets(pets)
        
        # Generate assets using real asset assembler functions
        print(f"\n📚 Generating book assets...")
        
        print("   📖 Creating PDF book with chapters...")
        pdf_path = create_pdf_book(content)
        pdf_size = os.path.getsize(pdf_path)
        
        print("   🎭 Creating PowerPoint presentation...")
        ppt_path = create_ppt(content)
        ppt_size = os.path.getsize(ppt_path)
        
        # Results summary
        print("\n" + "=" * 70)
        print("🎉 BOOK GENERATION COMPLETED!")
        print("=" * 70)
        
        print(f"📖 PDF Book: {pdf_path}")
        print(f"   📏 Size: {pdf_size:,} bytes")
        print(f"   📄 Pages: Cover + {len(pets)} chapters")
        
        print(f"\n🎭 PowerPoint: {ppt_path}")
        print(f"   📏 Size: {ppt_size:,} bytes")
        print(f"   🎬 Slides: Title + {len(pets)} pet stories")
        
        print(f"\n🐾 Featured Pets:")
        for i, pet in enumerate(pets, 1):
            print(f"   {i}. {pet['name']} ({pet['breed']} {pet['type']})")
        
        print(f"\n📍 Location: Alexandria, VA")
        print(f"🏠 Organizations: {', '.join(set(pet['organization'] for pet in pets))}")
        
        print("\n💡 What's in the book:")
        print("✅ Real pet photos from Petfinder API")
        print("✅ Story-specific illustrations (simulated)")
        print("✅ Humorous adventure stories for each pet")
        print("✅ Adoption badges and QR codes")
        print("✅ Multi-chapter PDF with cover page")
        print("✅ PowerPoint presentation")
        print("✅ Contact information for adoption")
        
        print("\n🎯 Next Steps:")
        print("1. Open the PDF to see the complete pet adoption book")
        print("2. View the PowerPoint for a presentation format")
        print("3. Contact the shelters to adopt these amazing pets!")
        print("4. Share the book to help these pets find homes!")
        
        return {
            "pdf_path": pdf_path,
            "ppt_path": ppt_path,
            "pets_count": len(pets),
            "pets": pets
        }
        
    except Exception as e:
        print(f"\n❌ Error generating book: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    
    if result:
        print(f"\n🎊 Success! Generated adoption book for {result['pets_count']} Alexandria pets!")
        print("The files contain real pet data and photos from Petfinder.")
        print("These are actual pets looking for homes in Alexandria, VA!")
    else:
        print("\n💥 Failed to generate book.")
        sys.exit(1) 