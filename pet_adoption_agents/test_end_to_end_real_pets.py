#!/usr/bin/env python3
"""
End-to-end test with real pets from Alexandria, VA
This test demonstrates the complete workflow using actual pet data from pets_alexandria_va.json
"""

import asyncio
import json
import os
import sys
from datetime import datetime
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
from asset_assembler.main import create_pdf_book
from book_shipper.main import book_shipper

class MockAgentContext:
    """Mock context for testing agent functions"""
    def __init__(self):
        self.logger = self
    
    def info(self, message):
        print(f"🤖 Agent Log: {message}")

def load_real_alexandria_pets_data():
    """Load real pet data from Alexandria, VA"""
    json_path = Path(__file__).parent / "pets_alexandria_va.json"
    
    if not json_path.exists():
        print(f"❌ Pet data file not found: {json_path}")
        return []
    
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
            "age": pet_data.get("age", "Adult"),
            "size": pet_data.get("size", "Medium"),
            "gender": pet_data.get("gender", "Unknown"),
            "contact": pet_data.get("contact", {
                "email": "shelter@alexandriava.gov",
                "phone": "703-746-4774"
            })
        }
        formatted_pets.append(formatted_pet)
    
    return formatted_pets

async def test_real_pets_workflow():
    """Test the complete workflow with real pets from Alexandria, VA"""
    
    print("🐕 Starting End-to-End Test with Real Pets from Alexandria, VA")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Load real pet data from Alexandria, VA
        print("\n1. 📊 Loading real pet data from Alexandria, VA...")
        
        pets_data = load_real_alexandria_pets_data()
        
        if not pets_data:
            print("❌ No pets data available")
            return False
            
        print(f"✅ Found {len(pets_data)} real pets!")
        
        # Display pet summary
        for i, pet in enumerate(pets_data, 1):
            breed_str = ", ".join(pet.get('breeds', {}).get('primary', 'Mixed')) if pet.get('breeds') else 'Mixed'
            print(f"   {i}. {pet.get('name', 'Unknown')} - {breed_str} ({pet.get('age', 'Unknown age')})")
        
        # Step 2: Generate content for the real pets using the content generator agent
        print(f"\n2. 📝 Generating stories for {len(pets_data)} real pets...")
        
        ctx = MockAgentContext()
        
        # Call the content generator agent
        stories_result = await content_generator(
            ctx,
            pets_data,
            humorous=True
        )
        
        if not stories_result.get("success"):
            print(f"❌ Failed to generate content: {stories_result.get('error', 'Unknown error')}")
            return False
            
        stories = stories_result.get("stories", [])
        print(f"✅ Generated {len(stories)} heartwarming stories!")
        
        # Step 3: Assemble the book with real pet stories
        print(f"\n3. 📚 Assembling book with real pet stories...")
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"alexandria_pets_book_{timestamp}.pdf"
        pdf_path = output_dir / pdf_filename
        
        # Create the book using asset assembler
        book_result = await create_pdf_book(
            ctx,
            stories,
            "Alexandria Pets: Real Stories of Hope",
            f"Featuring {len(pets_data)} amazing pets looking for homes",
            str(pdf_path)
        )
        
        if not book_result.get("success"):
            print(f"❌ Failed to assemble book: {book_result.get('error', 'Unknown error')}")
            return False
            
        print(f"✅ Book assembled successfully!")
        print(f"   📄 PDF created: {pdf_path}")
        
        if pdf_path.exists():
            print(f"   📏 File size: {pdf_path.stat().st_size:,} bytes")
        
        # Step 4: Test book shipping preparation
        print(f"\n4. 📦 Testing book shipping preparation...")
        
        shipping_address = {
            "name": "Alexandria Animal Shelter",
            "street1": "4101 Eisenhower Ave",
            "city": "Alexandria",
            "state": "VA",
            "postal_code": "22304",
            "country": "US",
            "phone": "703-746-4774",
            "email": "shelter@alexandriava.gov"
        }
        
        # Test shipping preparation
        shipping_result = await book_shipper(
            ctx,
            str(pdf_path),
            "Alexandria Pets: Real Stories of Hope",
            1,  # quantity
            shipping_address
        )
        
        if not shipping_result.get("success"):
            print(f"❌ Shipping preparation failed: {shipping_result.get('error', 'Unknown error')}")
            return False
            
        print(f"✅ Book shipping prepared successfully!")
        print(f"   📋 Print job validated with Lulu API")
        
        # Final summary
        print(f"\n🎉 END-TO-END TEST WITH REAL PETS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Real pets processed: {len(pets_data)}")
        print(f"📝 Stories generated: {len(stories)}")
        print(f"📚 Book created: {pdf_filename}")
        print(f"📦 Shipping prepared: Alexandria Animal Shelter")
        
        # Show some sample pet details
        print(f"\n🐾 Real Pets Featured:")
        for i, pet in enumerate(pets_data, 1):
            breed_info = pet.get('breeds', {})
            breed_str = breed_info.get('primary', 'Mixed') if breed_info else 'Mixed'
            print(f"   {i}. {pet.get('name', 'Unknown')} - {breed_str}")
            print(f"      Age: {pet.get('age', 'Unknown')}, Size: {pet.get('size', 'Unknown')}")
            print(f"      Gender: {pet.get('gender', 'Unknown')}")
            if pet.get('description'):
                desc = pet['description'][:100] + "..." if len(pet['description']) > 100 else pet['description']
                print(f"      Description: {desc}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_real_pets_workflow())
    
    if success:
        print(f"\n✅ All tests passed! Real pets workflow is working perfectly.")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed. Please check the output above.")
        sys.exit(1) 