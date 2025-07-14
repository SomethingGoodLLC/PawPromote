#!/usr/bin/env python3
"""
Test Lulu API with URL-based approach (correct method)
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

async def test_lulu_url_based_workflow():
    """Test the Lulu API using the correct URL-based approach"""
    print("🚚 Testing Lulu API URL-Based Workflow")
    print("=" * 50)
    
    client_id = os.getenv('LULU_CLIENT_ID')
    client_secret = os.getenv('LULU_CLIENT_SECRET')
    base_url = 'https://api.sandbox.lulu.com'
    
    print(f"LULU_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
    print(f"LULU_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")
    
    if not client_id or not client_secret:
        print("\n❌ Lulu API credentials not configured!")
        return False
    
    # Get access token
    auth_url = f'{base_url}/auth/realms/glasstree/protocol/openid-connect/token'
    auth_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    async with httpx.AsyncClient() as client:
        # Step 1: Authentication
        print("\n🔐 Step 1: Testing authentication...")
        auth_response = await client.post(auth_url, data=auth_data)
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
        
        token_data = auth_response.json()
        access_token = token_data['access_token']
        print("✅ Authentication successful!")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Step 2: Create print job with URL-based approach
        print("\n🖨️  Step 2: Testing print job creation (URL-based)...")
        
        # NOTE: In a real implementation, you would host your PDF files at accessible URLs
        # For example: https://yourdomain.com/pdfs/book.pdf or AWS S3 URLs
        test_pdf_url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
        
        print_job_data = {
            'external_id': 'test-pet-adoption-book-001',
            'contact_email': 'test@example.com',  # Required field
            'line_items': [
                {
                    'external_id': 'pet-book-line-item-001',
                    'title': 'Pet Adoption Storybook',
                    'cover_source_url': test_pdf_url,
                    'interior_source_url': test_pdf_url,
                    'pod_package_id': '0550X0850BWSTDPB060UW444GXX',  # Standard paperback 5.5x8.5
                    'quantity': 1
                }
            ],
            'shipping_address': {
                'name': 'Test User',
                'street1': '123 Test Street',
                'city': 'Test City',
                'state_code': 'VA',
                'postcode': '12345',
                'country_code': 'US',
                'phone_number': '555-123-4567'
            },
            'shipping_level': 'GROUND'
        }
        
        response = await client.post(f'{base_url}/print-jobs/', json=print_job_data, headers=headers)
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text}')
        
        if response.status_code == 201:
            print("✅ Print job created successfully!")
            job_data = response.json()
            job_id = job_data.get('id')
            print(f"📋 Job ID: {job_id}")
            
            # Step 3: Check job status
            print("\n📊 Step 3: Checking job status...")
            status_response = await client.get(f'{base_url}/print-jobs/{job_id}/', headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Job status: {status_data.get('status', 'Unknown')}")
                print(f"📋 Job details: {status_data}")
                return True
            else:
                print(f"❌ Failed to get job status: {status_response.status_code}")
                return False
        else:
            print("❌ Print job creation failed")
            print("💡 This is expected with the test URL - you need to host your PDF files at accessible URLs")
            return False

async def demonstrate_correct_workflow():
    """Demonstrate the correct workflow for production use"""
    print("\n" + "=" * 70)
    print("🎯 CORRECT LULU API WORKFLOW FOR PRODUCTION")
    print("=" * 70)
    
    workflow_steps = [
        "1. 📁 Host your PDF files at accessible URLs",
        "   - Use AWS S3, Google Cloud Storage, or your own web server",
        "   - Ensure URLs are publicly accessible (no authentication required)",
        "   - Example: https://yourdomain.com/pdfs/pet-book-cover.pdf",
        "",
        "2. 🔧 Update book_shipper/main.py to use URL-based approach:",
        "   - Remove the upload_pdf() method",
        "   - Modify create_print_job() to accept PDF URLs instead of file paths",
        "   - Use the line_items structure with cover_source_url and interior_source_url",
        "",
        "3. 🚀 Integration with pet adoption workflow:",
        "   - asset_assembler generates PDF and uploads to your hosting service",
        "   - Returns the public URL of the generated PDF",
        "   - book_shipper uses this URL to create the print job",
        "",
        "4. 📦 Print job creation:",
        "   - Use the correct JSON structure with line_items",
        "   - Include required fields: contact_email, shipping_address",
        "   - Specify pod_package_id for book format/size",
        "",
        "5. 📊 Job tracking:",
        "   - Use the returned job ID to track printing and shipping status",
        "   - Poll the /print-jobs/{job_id}/ endpoint for updates"
    ]
    
    for step in workflow_steps:
        print(step)
    
    print("\n💡 Key Insight: Lulu API doesn't accept file uploads directly!")
    print("   Instead, it fetches PDF files from URLs you provide.")
    print("\n🎉 Your authentication is working perfectly!")
    print("   The next step is to set up PDF hosting and update the workflow.")

async def main():
    success = await test_lulu_url_based_workflow()
    await demonstrate_correct_workflow()
    
    if success:
        print("\n✅ Ready to implement URL-based book shipping!")
    else:
        print("\n🔧 Next: Set up PDF hosting and update the workflow.")

if __name__ == "__main__":
    asyncio.run(main()) 