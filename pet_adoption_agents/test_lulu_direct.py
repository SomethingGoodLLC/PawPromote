#!/usr/bin/env python3
"""
Direct test of Lulu API functionality without GenAI session dependencies
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Import the LuluAPIClient directly
import sys
sys.path.append('book_shipper')
from book_shipper.main import LuluAPIClient, ShippingAddress, BookSpecification

async def test_lulu_workflow():
    """Test the complete Lulu API workflow"""
    print("🚚 Testing Lulu API Workflow")
    print("=" * 50)
    
    # Check environment variables
    client_id = os.getenv('LULU_CLIENT_ID')
    client_secret = os.getenv('LULU_CLIENT_SECRET')
    
    print(f"LULU_CLIENT_ID: {'✅ Set' if client_id and client_id != 'NOT SET' else '❌ Not set'}")
    print(f"LULU_CLIENT_SECRET: {'✅ Set' if client_secret and client_secret != 'NOT SET' else '❌ Not set'}")
    
    if not client_id or client_id == 'NOT SET' or not client_secret or client_secret == 'NOT SET':
        print("\n❌ Lulu API credentials not properly configured!")
        print("Please update your .env file with:")
        print("LULU_CLIENT_ID=35353952-5212-4b65-a793-23ca59319846")
        print("LULU_CLIENT_SECRET=RUtHNXne3cLPJ4ibWwfdkAJ0YEXLAYV0")
        return False
    
    # Initialize Lulu API client
    client = LuluAPIClient()
    
    # Test 1: Authentication
    print("\n🔐 Step 1: Testing authentication...")
    auth_success = await client.authenticate()
    if not auth_success:
        print("❌ Authentication failed")
        return False
    print("✅ Authentication successful!")
    
    # Test 2: Upload PDF
    print("\n📄 Step 2: Testing PDF upload...")
    pdf_path = "test_book_lulu.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF not found: {pdf_path}")
        return False
    
    file_id = await client.upload_pdf(pdf_path, "test_book_lulu.pdf")
    if not file_id:
        print("❌ PDF upload failed")
        return False
    print(f"✅ PDF uploaded successfully! File ID: {file_id}")
    
    # Test 3: Create print job
    print("\n🖨️  Step 3: Testing print job creation...")
    
    # Create test shipping address
    shipping_address = ShippingAddress(
        name="Test User",
        street1="123 Test Street",
        city="Test City",
        state="VA",
        postal_code="12345",
        email="test@example.com"
    )
    
    # Create book specification
    book_spec = BookSpecification(
        title="Test Pet Adoption Book",
        quantity=1
    )
    
    job_id = await client.create_print_job(file_id, book_spec, shipping_address)
    if not job_id:
        print("❌ Print job creation failed")
        return False
    print(f"✅ Print job created successfully! Job ID: {job_id}")
    
    # Test 4: Check job status
    print("\n📊 Step 4: Testing job status check...")
    status = await client.get_job_status(job_id)
    if not status:
        print("❌ Job status check failed")
        return False
    print(f"✅ Job status retrieved: {status.get('status', 'Unknown')}")
    
    print("\n🎉 All tests passed! Lulu API integration is working correctly.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_lulu_workflow())
    if success:
        print("\n✅ Ready for production book shipping!")
    else:
        print("\n❌ Please fix the issues above before proceeding.") 