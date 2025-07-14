#!/usr/bin/env python3
"""
Test script that calls the actual live agents
"""
import asyncio
import sys
import os

# Add the master_orchestrator directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'master_orchestrator'))

# Import the agent functions directly
try:
    from master_orchestrator.main import orchestrate_workflow
    from data_fetcher.main import fetch_pets
    from content_generator.main import content_generator
    from asset_assembler.main import asset_assembler
    from book_shipper.main import book_shipper
    print("✅ Successfully imported agent functions")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Note: This script requires the agent modules to be importable")
    sys.exit(1)

async def test_live_agents():
    """Test the actual live agents"""
    print("🎯 TESTING LIVE AGENTS")
    print("=" * 40)
    
    # Mock context for testing
    class MockContext:
        def __init__(self):
            self.logger = MockLogger()
    
    class MockLogger:
        def info(self, msg):
            print(f"📝 {msg}")
        def error(self, msg):
            print(f"❌ {msg}")
    
    context = MockContext()
    
    try:
        # Test 1: Fetch pets (using mock data since we don't have real API keys)
        print("\n1. Testing Data Fetcher...")
        print("-" * 25)
        
        # This will use placeholder data since we don't have real API keys
        pets_result = await fetch_pets(
            context,
            shelter_name="Alexandria Animal Shelter",
            shelter_id="VA935",
            num_pets=3,
            include_photos=True
        )
        
        print(f"✅ Data fetcher returned: {type(pets_result)}")
        if isinstance(pets_result, list) and len(pets_result) > 0:
            print(f"   First pet: {pets_result[0].get('name', 'Unknown')}")
        
        # Test 2: Content generator
        print("\n2. Testing Content Generator...")
        print("-" * 30)
        
        # Mock pet data for content generation
        mock_pets = [
            {
                "id": "pet_001",
                "name": "Buddy",
                "description": "A friendly golden retriever",
                "photos": ["https://example.com/buddy.jpg"]
            },
            {
                "id": "pet_002", 
                "name": "Whiskers",
                "description": "A curious tabby cat",
                "photos": ["https://example.com/whiskers.jpg"]
            }
        ]
        
        content_result = await content_generator(
            context,
            pets=mock_pets,
            humorous=True
        )
        
        print(f"✅ Content generator returned: {type(content_result)}")
        if isinstance(content_result, dict):
            stories = content_result.get("stories", [])
            print(f"   Generated {len(stories)} stories")
        
        # Test 3: Asset assembler
        print("\n3. Testing Asset Assembler...")
        print("-" * 28)
        
        # Mock content data
        mock_content = {
            "stories": [
                "Buddy's space adventure story...",
                "Whiskers's detective mystery..."
            ],
            "images": ["image1.jpg", "image2.jpg"]
        }
        
        assembly_result = await asset_assembler(
            context,
            content=mock_content,
            specification="Create PDF book with pet stories"
        )
        
        print(f"✅ Asset assembler returned: {type(assembly_result)}")
        if isinstance(assembly_result, dict):
            files = assembly_result.get("files", [])
            print(f"   Created {len(files)} files")
        
        # Test 4: Book shipper (mock)
        print("\n4. Testing Book Shipper...")
        print("-" * 24)
        
        # This would normally ship a real book
        shipping_result = await book_shipper(
            context,
            pdf_path="mock_book.pdf",
            book_title="Alexandria Pet Adventures",
            recipient_name="Pet Lover",
            street_address="123 Pet Lane",
            city="Alexandria",
            state="VA",
            postal_code="22314",
            country="US"
        )
        
        print(f"✅ Book shipper returned: {type(shipping_result)}")
        
        print("\n🎉 ALL AGENT TESTS COMPLETED!")
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_live_agents()) 