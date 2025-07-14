import asyncio
import os
from typing import Annotated

import requests
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)

LULU_API_KEY = os.getenv("LULU_API_KEY", "placeholder")
LULU_API_URL = "https://api.lulu.com/v1"  # Example endpoint; check docs


@session.bind(
    name="book_shipper",
    description="Ships physical books using Lulu API."
)
async def book_shipper(
    agent_context: GenAIContext,
    book_file: Annotated[str, "Path to the book PDF file"],
    address: Annotated[str, "Shipping address"]
):
    agent_context.logger.info(f"Shipping book {book_file} to {address}")

    # Upload PDF to Lulu and create print job (simplified; adjust per API docs)
    with open(book_file, "rb") as f:
        files = {"file": f}
        upload_response = requests.post(
            f"{LULU_API_URL}/uploads",
            headers={"Authorization": f"Bearer {LULU_API_KEY}"},
            files=files
        )
    upload_id = upload_response.json().get("id")

    # Create shipping order
    order_data = {
        "upload_id": upload_id,
        "shipping_address": address,
        "quantity": 1
    }
    order_response = requests.post(
        f"{LULU_API_URL}/print-jobs",
        headers={"Authorization": f"Bearer {LULU_API_KEY}"},
        json=order_data
    )
    confirmation = order_response.json().get("order_id")

    return {"confirmation": confirmation, "status": "shipped"}


async def main():
    print("Book Shipper agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 