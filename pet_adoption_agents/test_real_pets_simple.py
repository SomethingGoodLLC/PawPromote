#!/usr/bin/env python3
"""
Simple end-to-end demonstration with real pets from Alexandria, VA
Shows what the workflow would do with actual pet data
"""

import json
import os
from datetime import datetime
from pathlib import Path

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

def generate_sample_story(pet):
    """Generate a sample story for a pet"""
    name = pet.get('name', 'Unknown')
    breed = pet.get('breeds', {}).get('primary', 'Mixed')
    age = pet.get('age', 'Adult')
    gender = pet.get('gender', 'Unknown')
    
    # Create a personalized story based on pet details
    story = f"""
**{name}: Alexandria's Charming {breed}**

Meet {name}, a delightful {age.lower()} {breed.lower()} who has been waiting for the perfect family to call home. This {gender.lower()} companion has a heart full of love and a personality that shines brighter than the Alexandria waterfront.

{name} loves to explore new adventures and would make a wonderful addition to any loving home. With {name.lower()}'s gentle nature and playful spirit, this sweet pet is ready to bring joy and companionship to a special family.

If you're looking for a loyal friend who will fill your days with happiness and your heart with love, {name} might be the perfect match for you!

*Contact the Alexandria Animal Shelter to learn more about adopting {name}.*
"""
    return story.strip()

def demonstrate_real_pets_workflow():
    """Demonstrate the complete workflow with real pets"""
    
    print("🐕 Real Pets Workflow Demonstration - Alexandria, VA")
    print("=" * 60)
    
    # Step 1: Load real pet data
    print("\n1. 📊 Loading real pet data from Alexandria, VA...")
    pets = load_real_alexandria_pets()
    
    if not pets:
        print("❌ No pets data available")
        return
    
    print(f"✅ Loaded {len(pets)} real pets from Alexandria Animal Shelter!")
    
    # Step 2: Display pet details
    print("\n2. 🐾 Real Pets Available for Adoption:")
    print("-" * 40)
    
    for i, pet in enumerate(pets, 1):
        name = pet.get('name', 'Unknown')
        breed = pet.get('breeds', {}).get('primary', 'Mixed')
        age = pet.get('age', 'Unknown')
        gender = pet.get('gender', 'Unknown')
        size = pet.get('size', 'Unknown')
        
        print(f"\n{i}. {name}")
        print(f"   Breed: {breed}")
        print(f"   Age: {age}")
        print(f"   Gender: {gender}")
        print(f"   Size: {size}")
        
        # Show description if available
        if pet.get('description'):
            desc = pet['description'][:150] + "..." if len(pet['description']) > 150 else pet['description']
            print(f"   Description: {desc}")
        
        # Show photos count
        photos = pet.get('photos', [])
        if photos:
            print(f"   Photos: {len(photos)} available")
        
        # Show tags
        tags = pet.get('tags', [])
        if tags:
            print(f"   Tags: {', '.join(tags[:5])}")
    
    # Step 3: Generate sample stories
    print(f"\n3. 📝 Sample Stories Generated:")
    print("-" * 40)
    
    stories = []
    for pet in pets:
        story = generate_sample_story(pet)
        stories.append(story)
        print(f"\n{story}")
        print("\n" + "="*50)
    
    # Step 4: Simulate book creation
    print(f"\n4. 📚 Book Creation Simulation:")
    print("-" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    book_title = f"Alexandria Pets: Real Stories of Hope"
    pdf_filename = f"alexandria_pets_book_{timestamp}.pdf"
    
    print(f"📖 Title: {book_title}")
    print(f"📄 Filename: {pdf_filename}")
    print(f"📊 Content: {len(stories)} heartwarming stories")
    print(f"🐾 Featuring: {', '.join([pet.get('name', 'Unknown') for pet in pets])}")
    
    # Step 5: Simulate shipping preparation
    print(f"\n5. 📦 Shipping Preparation:")
    print("-" * 40)
    
    shipping_info = {
        "destination": "Alexandria Animal Shelter",
        "address": "4101 Eisenhower Ave, Alexandria, VA 22304",
        "phone": "703-746-4774",
        "purpose": "Promote pet adoption"
    }
    
    print(f"🏢 Destination: {shipping_info['destination']}")
    print(f"📍 Address: {shipping_info['address']}")
    print(f"📞 Phone: {shipping_info['phone']}")
    print(f"🎯 Purpose: {shipping_info['purpose']}")
    
    # Final summary
    print(f"\n🎉 REAL PETS WORKFLOW DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Real pets processed: {len(pets)}")
    print(f"📝 Stories created: {len(stories)}")
    print(f"📚 Book ready: {book_title}")
    print(f"📦 Shipping planned: Alexandria Animal Shelter")
    
    print(f"\n💡 This demonstration shows how the system would work with real pet data:")
    print(f"   • Load actual pets from Alexandria Animal Shelter")
    print(f"   • Generate personalized stories for each pet")
    print(f"   • Create a professional book to promote adoptions")
    print(f"   • Prepare for shipping to help pets find homes")
    
    print(f"\n🐾 These are real pets waiting for homes in Alexandria, VA!")
    print(f"   Visit the Alexandria Animal Shelter to meet them in person.")

if __name__ == "__main__":
    demonstrate_real_pets_workflow() 