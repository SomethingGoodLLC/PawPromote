#!/usr/bin/env python3
"""
Book Shipper Agent - Handles physical book printing and shipping via Lulu API
"""

import asyncio
import os
import json
import base64
import mimetypes
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

import requests
import httpx
from pydantic import BaseModel, Field
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
LULU_API_BASE_URL = "https://api.lulu.com"
LULU_CLIENT_ID = os.getenv("LULU_CLIENT_ID", "your_lulu_client_id")
LULU_CLIENT_SECRET = os.getenv("LULU_CLIENT_SECRET", "your_lulu_client_secret")
LULU_SANDBOX = os.getenv("LULU_SANDBOX", "true").lower() == "true"

if LULU_SANDBOX:
    LULU_API_BASE_URL = "https://api.sandbox.lulu.com"

AGENT_JWT = os.getenv("AGENT_JWT", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkMGZkMjQ4MC0yMTQxLTQxYTAtOGY0My05OTkwNTc3ZjY3MmEiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.IPtSYWAY7Qh8LM_1Q2egcA05AoeBBU60eSSkze3BiCk")
session = GenAISession(jwt_token=AGENT_JWT)

print(f"🚚 Book Shipper Agent initialized")
print(f"📚 Lulu API: {'Sandbox' if LULU_SANDBOX else 'Production'}")
print(f"🔑 Lulu Client ID: {'✅ Set' if LULU_CLIENT_ID != 'your_lulu_client_id' else '❌ Not set'}")


class BookFormat(str, Enum):
    """Available book formats for printing"""
    PERFECT_BOUND = "PERFECT_BOUND"
    SADDLE_STITCHED = "SADDLE_STITCHED"
    COIL_BOUND = "COIL_BOUND"
    HARDCOVER = "HARDCOVER"


class PaperType(str, Enum):
    """Available paper types"""
    WHITE = "WHITE"
    CREAM = "CREAM"
    PREMIUM = "PREMIUM"


class PrintQuality(str, Enum):
    """Print quality options"""
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


@dataclass
class ShippingAddress:
    """Shipping address information"""
    name: str
    street1: str
    city: str
    state: str
    postal_code: str
    street2: Optional[str] = None
    country: str = "US"
    phone: Optional[str] = None
    email: Optional[str] = None


@dataclass
class BookSpecification:
    """Book printing specifications"""
    title: str
    format: BookFormat = BookFormat.PERFECT_BOUND
    paper_type: PaperType = PaperType.WHITE
    print_quality: PrintQuality = PrintQuality.PREMIUM
    cover_finish: str = "MATTE"
    binding_color: str = "BLACK"
    quantity: int = 1
    page_count: Optional[int] = None
    width: float = 8.5  # inches
    height: float = 11.0  # inches


class LuluAPIClient:
    """Lulu API client for book printing and shipping"""
    
    def __init__(self):
        self.base_url = LULU_API_BASE_URL
        self.client_id = LULU_CLIENT_ID
        self.client_secret = LULU_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Lulu API and get access token"""
        try:
            auth_url = f"{self.base_url}/auth/realms/glasstree/protocol/openid-connect/token"
            
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(auth_url, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now().timestamp() + expires_in
                    print(f"✅ Lulu API authentication successful")
                    return True
                else:
                    print(f"❌ Lulu API authentication failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Lulu API authentication error: {e}")
            return False
    
    async def upload_pdf(self, pdf_path: str, filename: str) -> Optional[str]:
        """Upload PDF file to Lulu and return file ID"""
        if not self.access_token:
            if not await self.authenticate():
                return None
        
        try:
            # Read PDF file
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
            
            # Prepare file upload
            files = {
                'file': (filename, pdf_content, 'application/pdf')
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            upload_url = f"{self.base_url}/print-files/"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(upload_url, files=files, headers=headers)
                
                if response.status_code == 201:
                    file_data = response.json()
                    file_id = file_data["id"]
                    print(f"✅ PDF uploaded successfully: {file_id}")
                    return file_id
                else:
                    print(f"❌ PDF upload failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ PDF upload error: {e}")
            return None
    
    async def create_print_job(self, file_id: str, spec: BookSpecification, 
                             shipping_address: ShippingAddress) -> Optional[str]:
        """Create a print job and return job ID"""
        if not self.access_token:
            if not await self.authenticate():
                return None
        
        try:
            # Prepare print job data
            job_data = {
                "line_items": [
                    {
                        "external_id": f"pet-adoption-book-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "printable_normalization": {
                            "cover": {
                                "source_url": f"lulu://print-files/{file_id}"
                            },
                            "interior": {
                                "source_url": f"lulu://print-files/{file_id}"
                            }
                        },
                        "print_quality": spec.print_quality.value,
                        "quantity": spec.quantity,
                        "product_specification": {
                            "binding_type": spec.format.value,
                            "paper_type": spec.paper_type.value,
                            "cover_finish": spec.cover_finish,
                            "binding_color": spec.binding_color,
                            "page_count": spec.page_count or 50,  # Default if not specified
                            "width": spec.width,
                            "height": spec.height
                        }
                    }
                ],
                "shipping_address": {
                    "name": shipping_address.name,
                    "street1": shipping_address.street1,
                    "street2": shipping_address.street2,
                    "city": shipping_address.city,
                    "state_code": shipping_address.state,
                    "postcode": shipping_address.postal_code,
                    "country_code": shipping_address.country,
                    "phone_number": shipping_address.phone,
                    "email": shipping_address.email
                },
                "contact_email": shipping_address.email or "noreply@petadoption.com"
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            job_url = f"{self.base_url}/print-jobs/"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(job_url, json=job_data, headers=headers)
                
                if response.status_code == 201:
                    job_data = response.json()
                    job_id = job_data["id"]
                    print(f"✅ Print job created successfully: {job_id}")
                    return job_id
                else:
                    print(f"❌ Print job creation failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Print job creation error: {e}")
            return None
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get print job status and tracking information"""
        if not self.access_token:
            if not await self.authenticate():
                return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            status_url = f"{self.base_url}/print-jobs/{job_id}/"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(status_url, headers=headers)
                
                if response.status_code == 200:
                    job_data = response.json()
                    return job_data
                else:
                    print(f"❌ Job status check failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ Job status check error: {e}")
            return None


async def ship_book(pdf_path: str, book_title: str, shipping_address: ShippingAddress,
                   book_spec: Optional[BookSpecification] = None) -> Dict[str, Any]:
    """
    Main function to ship a book via Lulu API
    
    Args:
        pdf_path: Path to the PDF file to print
        book_title: Title of the book
        shipping_address: Shipping address information
        book_spec: Book specifications (optional, uses defaults if not provided)
    
    Returns:
        Dictionary with shipping results and tracking information
    """
    print(f"📚 Starting book shipping process for: {book_title}")
    print(f"📄 PDF: {pdf_path}")
    print(f"🏠 Shipping to: {shipping_address.name}, {shipping_address.city}, {shipping_address.state}")
    
    # Use default book specification if not provided
    if book_spec is None:
        book_spec = BookSpecification(
            title=book_title,
            format=BookFormat.PERFECT_BOUND,
            paper_type=PaperType.WHITE,
            print_quality=PrintQuality.PREMIUM,
            quantity=1
        )
    
    # Initialize Lulu API client
    lulu_client = LuluAPIClient()
    
    # Step 1: Authenticate with Lulu API
    if not await lulu_client.authenticate():
        return {
            "success": False,
            "error": "Failed to authenticate with Lulu API",
            "job_id": None,
            "tracking_info": None
        }
    
    # Step 2: Upload PDF file
    filename = f"{book_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_id = await lulu_client.upload_pdf(pdf_path, filename)
    
    if not file_id:
        return {
            "success": False,
            "error": "Failed to upload PDF to Lulu",
            "job_id": None,
            "tracking_info": None
        }
    
    # Step 3: Create print job
    job_id = await lulu_client.create_print_job(file_id, book_spec, shipping_address)
    
    if not job_id:
        return {
            "success": False,
            "error": "Failed to create print job",
            "job_id": None,
            "tracking_info": None
        }
    
    # Step 4: Get initial job status
    job_status = await lulu_client.get_job_status(job_id)
    
    print(f"✅ Book shipping initiated successfully!")
    print(f"📋 Job ID: {job_id}")
    print(f"📊 Status: {job_status.get('status', 'Unknown') if job_status else 'Unknown'}")
    
    return {
        "success": True,
        "job_id": job_id,
        "file_id": file_id,
        "status": job_status.get('status', 'CREATED') if job_status else 'CREATED',
        "tracking_info": job_status.get('tracking_info') if job_status else None,
        "estimated_delivery": job_status.get('estimated_delivery') if job_status else None,
        "total_cost": job_status.get('total_cost') if job_status else None,
        "shipping_address": {
            "name": shipping_address.name,
            "city": shipping_address.city,
            "state": shipping_address.state,
            "country": shipping_address.country
        }
    }


@session.bind(
    name="book_shipper",
    description="Ships physical books via Lulu API - handles PDF upload, print job creation, and tracking"
)
async def book_shipper(
    agent_context: GenAIContext,
    pdf_path: Annotated[str, "Path to the PDF file to print and ship"],
    book_title: Annotated[str, "Title of the book to be printed"],
    recipient_name: Annotated[str, "Name of the recipient"],
    street_address: Annotated[str, "Street address for shipping"],
    city: Annotated[str, "City for shipping"],
    state: Annotated[str, "State/province for shipping"],
    postal_code: Annotated[str, "Postal/ZIP code for shipping"],
    country: Annotated[str, "Country for shipping"] = "US",
    phone: Annotated[Optional[str], "Phone number (optional)"] = None,
    email: Annotated[Optional[str], "Email address (optional)"] = None,
    quantity: Annotated[int, "Number of books to print"] = 1,
    book_format: Annotated[str, "Book format (PERFECT_BOUND, HARDCOVER, etc.)"] = "PERFECT_BOUND",
    paper_type: Annotated[str, "Paper type (WHITE, CREAM, PREMIUM)"] = "WHITE"
) -> Dict[str, Any]:
    """
    Ship a physical book via Lulu API
    
    This function handles the complete book shipping process:
    1. Uploads PDF to Lulu
    2. Creates print job with specifications
    3. Initiates shipping to provided address
    4. Returns tracking information
    """
    agent_context.logger.info(f"Shipping book '{book_title}' to {recipient_name} in {city}, {state}")
    
    # Create shipping address
    shipping_address = ShippingAddress(
        name=recipient_name,
        street1=street_address,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        phone=phone,
        email=email
    )
    
    # Create book specification
    book_spec = BookSpecification(
        title=book_title,
        format=BookFormat(book_format),
        paper_type=PaperType(paper_type),
        print_quality=PrintQuality.PREMIUM,
        quantity=quantity
    )
    
    # Ship the book
    result = await ship_book(pdf_path, book_title, shipping_address, book_spec)
    
    if result["success"]:
        agent_context.logger.info(f"Book shipping successful - Job ID: {result['job_id']}")
    else:
        agent_context.logger.error(f"Book shipping failed: {result['error']}")
    
    return result


@session.bind(
    name="track_shipment",
    description="Track the status of a book shipment using job ID"
)
async def track_shipment(
    agent_context: GenAIContext,
    job_id: Annotated[str, "Lulu print job ID to track"]
) -> Dict[str, Any]:
    """
    Track the status of a book shipment
    
    Returns current status, tracking information, and estimated delivery
    """
    agent_context.logger.info(f"Tracking shipment for job ID: {job_id}")
    
    lulu_client = LuluAPIClient()
    
    if not await lulu_client.authenticate():
        return {
            "success": False,
            "error": "Failed to authenticate with Lulu API",
            "status": "UNKNOWN"
        }
    
    job_status = await lulu_client.get_job_status(job_id)
    
    if job_status:
        return {
            "success": True,
            "job_id": job_id,
            "status": job_status.get('status', 'UNKNOWN'),
            "tracking_info": job_status.get('tracking_info'),
            "estimated_delivery": job_status.get('estimated_delivery'),
            "total_cost": job_status.get('total_cost'),
            "line_items": job_status.get('line_items', [])
        }
    else:
        return {
            "success": False,
            "error": "Failed to retrieve job status",
            "status": "UNKNOWN"
        }


async def main():
    """Main function for testing the book shipper"""
    print("🚚 Book Shipper Agent started")
    print("📚 Ready to ship physical books via Lulu API")
    
    # Example usage for testing
    if os.path.exists("../alexandria_pets_complete_storybook_20250714_012300.pdf"):
        print("📖 Found test PDF - running shipping simulation...")
        
        # Test shipping address
        test_address = ShippingAddress(
            name="Test Recipient",
            street1="123 Test Street",
            city="Test City",
            state="CA",
            postal_code="90210",
            country="US",
            email="test@example.com"
        )
        
        # Test book shipping (this would create a real print job in production)
        result = await ship_book(
            pdf_path="../alexandria_pets_complete_storybook_20250714_012300.pdf",
            book_title="Alexandria Pet Adoption Storybook",
            shipping_address=test_address
        )
        
        print(f"📋 Shipping result: {result}")
    
    # Start the agent session
    await session.process_events()


if __name__ == "__main__":
    asyncio.run(main()) 