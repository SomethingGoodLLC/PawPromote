#!/usr/bin/env python3
"""
Demo: Complete Multi-Agent Pet Adoption Workflow Orchestration

This script demonstrates the full end-to-end workflow:
1. Task parsing from natural language
2. Pet data fetching from real shelters
3. AI content generation with stories and images
4. Professional book/PDF assembly
5. Physical book shipping via Lulu API

Usage:
    python demo_full_orchestration.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from master_orchestrator.main import WorkflowOrchestrator, TaskParser
from book_shipper.main import ship_book, ShippingAddress, BookSpecification


async def demo_task_parsing():
    """Demonstrate natural language task parsing"""
    print("🧠 TASK PARSING DEMONSTRATION")
    print("=" * 60)
    
    parser = TaskParser()
    
    # Example tasks that users might request
    example_tasks = [
        "Create a humorous book for 5 pets from Alexandria, VA and ship to 123 Main St, Arlington, VA 22201",
        "Generate a professional PDF storybook for 3 dogs in Baltimore, MD",
        "Make a funny presentation about cats in Washington, DC with both PDF and PowerPoint",
        "Ship the Alexandria pet book to John Doe, 456 Oak Ave, Richmond, VA 23220",
        "Create an adventure-themed book for 7 pets from Arlington, VA title: 'Pet Heroes of Arlington'",
        "Generate a heartwarming story collection for 4 cats and dogs in Alexandria, VA"
    ]
    
    for i, task in enumerate(example_tasks, 1):
        print(f"\n📝 Task {i}: {task}")
        parsed = parser.parse_task(task)
        
        print(f"   🎯 Type: {parsed.task_type.value}")
        print(f"   📍 Location: {parsed.location or 'Not specified'}")
        print(f"   🐾 Number of pets: {parsed.num_pets}")
        print(f"   🎨 Theme: {parsed.theme} ({'humorous' if parsed.humorous else 'serious'})")
        print(f"   📄 Output formats: {[f.value for f in parsed.output_formats]}")
        
        if parsed.book_title:
            print(f"   📚 Book title: {parsed.book_title}")
        
        if parsed.shipping_address:
            addr = parsed.shipping_address
            print(f"   🚚 Shipping to: {addr['city']}, {addr['state']} {addr['postal_code']}")
    
    print("\n✅ Task parsing demonstration complete!")


async def demo_workflow_coordination():
    """Demonstrate workflow coordination and agent communication"""
    print("\n🎯 WORKFLOW COORDINATION DEMONSTRATION")
    print("=" * 60)
    
    orchestrator = WorkflowOrchestrator()
    
    # Example workflow task
    task_description = "Create a humorous book for 3 pets from Alexandria, VA"
    
    print(f"📋 Processing task: {task_description}")
    
    # Parse the task
    task_request = orchestrator.parser.parse_task(task_description)
    
    print(f"🔍 Parsed task details:")
    print(f"   - Task type: {task_request.task_type.value}")
    print(f"   - Location: {task_request.location}")
    print(f"   - Number of pets: {task_request.num_pets}")
    print(f"   - Theme: {task_request.theme}")
    print(f"   - Output formats: {[f.value for f in task_request.output_formats]}")
    
    # Simulate workflow steps (in a real implementation, this would call actual agents)
    print(f"\n🚀 Workflow execution simulation:")
    print(f"   1. 🔍 Fetching {task_request.num_pets} pets from {task_request.location}...")
    print(f"   2. 🎨 Generating {task_request.theme} content with AI images...")
    print(f"   3. 📚 Assembling {task_request.output_formats[0]} book...")
    
    if task_request.shipping_address:
        print(f"   4. 🚚 Shipping to {task_request.shipping_address['city']}, {task_request.shipping_address['state']}...")
    
    print(f"   ✅ Workflow coordination complete!")


async def demo_book_shipping():
    """Demonstrate book shipping functionality"""
    print("\n🚚 BOOK SHIPPING DEMONSTRATION")
    print("=" * 60)
    
    # Check if we have a test PDF
    test_pdf_path = "alexandria_pets_complete_storybook_20250714_012300.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"⚠️  Test PDF not found: {test_pdf_path}")
        print(f"   This demo requires a generated PDF from the content generation workflow.")
        return
    
    # Create a test shipping address
    shipping_address = ShippingAddress(
        name="Pet Adoption Supporter",
        street1="123 Pet Lover Lane",
        city="Alexandria",
        state="VA",
        postal_code="22301",
        country="US",
        email="petlover@example.com"
    )
    
    # Create book specification
    book_spec = BookSpecification(
        title="Alexandria Pet Adoption Storybook",
        quantity=1
    )
    
    print(f"📚 Shipping book details:")
    print(f"   - Title: {book_spec.title}")
    print(f"   - Format: {book_spec.format.value}")
    print(f"   - Paper: {book_spec.paper_type.value}")
    print(f"   - Quality: {book_spec.print_quality.value}")
    print(f"   - Quantity: {book_spec.quantity}")
    
    print(f"📦 Shipping address:")
    print(f"   - Name: {shipping_address.name}")
    print(f"   - Address: {shipping_address.street1}")
    print(f"   - City: {shipping_address.city}, {shipping_address.state} {shipping_address.postal_code}")
    print(f"   - Country: {shipping_address.country}")
    
    print(f"\n🚀 Initiating book shipping...")
    
    # Attempt to ship the book (will fail without real Lulu API credentials)
    result = await ship_book(test_pdf_path, book_spec.title, shipping_address, book_spec)
    
    if result["success"]:
        print(f"✅ Book shipping successful!")
        print(f"   - Job ID: {result['job_id']}")
        print(f"   - Status: {result['status']}")
        if result.get('tracking_info'):
            print(f"   - Tracking: {result['tracking_info']}")
    else:
        print(f"❌ Book shipping simulation failed (expected without real API credentials)")
        print(f"   - Error: {result['error']}")
        print(f"   - This is normal without Lulu API credentials configured")


async def demo_complete_workflow():
    """Demonstrate the complete end-to-end workflow"""
    print("\n🎊 COMPLETE WORKFLOW DEMONSTRATION")
    print("=" * 60)
    
    # Example complete workflow task
    task_description = "Create a humorous book for 5 pets from Alexandria, VA and ship to 123 Main St, Arlington, VA 22201"
    
    print(f"📋 Complete workflow task: {task_description}")
    
    orchestrator = WorkflowOrchestrator()
    
    # Parse the task
    task_request = orchestrator.parser.parse_task(task_description)
    
    print(f"\n🔍 Task analysis:")
    print(f"   - Type: {task_request.task_type.value}")
    print(f"   - Location: {task_request.location}")
    print(f"   - Pets: {task_request.num_pets}")
    print(f"   - Theme: {task_request.theme}")
    print(f"   - Shipping required: {'Yes' if task_request.shipping_address else 'No'}")
    
    if task_request.shipping_address:
        addr = task_request.shipping_address
        print(f"   - Destination: {addr['city']}, {addr['state']} {addr['postal_code']}")
    
    print(f"\n🚀 Workflow execution plan:")
    print(f"   1. 🔍 Data Fetcher: Retrieve {task_request.num_pets} pets from {task_request.location}")
    print(f"   2. 🎨 Content Generator: Create {task_request.theme} stories with AI images")
    print(f"   3. 📚 Asset Assembler: Build professional PDF book")
    
    if task_request.shipping_address:
        print(f"   4. 🚚 Book Shipper: Print and ship via Lulu API")
    
    print(f"\n💡 Agent communication:")
    print(f"   - Master Orchestrator coordinates all agents")
    print(f"   - Uses GenAI Protocol for decentralized messaging")
    print(f"   - Each agent operates independently with bound functions")
    print(f"   - Workflow state tracking and error handling")
    
    print(f"\n✅ Complete workflow demonstration ready!")
    print(f"   To execute this workflow with real agents:")
    print(f"   1. Start all agent services (data_fetcher, content_generator, asset_assembler, book_shipper)")
    print(f"   2. Configure Lulu API credentials for shipping")
    print(f"   3. Call orchestrate_workflow() with the task description")


async def main():
    """Main demonstration function"""
    print("🎯 MULTI-AGENT PET ADOPTION WORKFLOW ORCHESTRATION")
    print("=" * 80)
    print("This demo shows the complete workflow from task parsing to book shipping")
    print("=" * 80)
    
    try:
        # Run all demonstrations
        await demo_task_parsing()
        await demo_workflow_coordination()
        await demo_book_shipping()
        await demo_complete_workflow()
        
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRATION COMPLETE!")
        print("=" * 80)
        
        print("\n📚 What you've seen:")
        print("✅ Natural language task parsing")
        print("✅ Multi-agent workflow coordination")
        print("✅ Book shipping integration with Lulu API")
        print("✅ Complete end-to-end workflow orchestration")
        
        print("\n🚀 Next steps:")
        print("1. Configure real API credentials (Lulu, Petfinder, OpenAI)")
        print("2. Start all agent services in separate processes")
        print("3. Use the master orchestrator to coordinate real workflows")
        print("4. Monitor workflow execution and handle errors")
        
        print("\n💡 Key features implemented:")
        print("- Task parsing from natural language")
        print("- Decentralized agent communication")
        print("- Workflow state management")
        print("- Error handling and recovery")
        print("- Physical book printing and shipping")
        print("- AI content generation integration")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 