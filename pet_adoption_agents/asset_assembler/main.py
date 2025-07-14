import asyncio
from typing import Annotated, Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pptx import Presentation
from PIL import Image
import requests
from io import BytesIO
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="asset_assembler",
    description="Assembles stories and assets into books, PDFs, PPTs."
)
async def asset_assembler(
    agent_context: GenAIContext,
    content: Annotated[Dict[str, Any], "Generated content with stories and video/image URLs"]
) -> Dict[str, str]:
    agent_context.logger.info("Assembling assets")

    # Create PDF book
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    y = 700
    for story in content["stories"]:
        c.drawString(100, y, f"Pet: {story['pet']}")
        c.drawString(100, y - 20, story["story"])
        y -= 50
    c.save()
    pdf_buffer.seek(0)
    with open("pet_book.pdf", "wb") as f:
        f.write(pdf_buffer.read())
    book_file = "pet_book.pdf"

    # Create PPT (simple example)
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    title.text = "Pet Adoption Stories"
    for video in content.get("videos", []):
        # Add images/videos (PPT supports images; videos as links)
        img_response = requests.get(video["badge_url"])
        img = Image.open(BytesIO(img_response.content))
        img_path = f"{video['pet']}_badge.jpg"
        img.save(img_path)
        slide.shapes.add_picture(img_path, 1000000, 1000000)
    prs.save("pet_book.pptx")

    return {"book_file": book_file, "ppt_file": "pet_book.pptx"}


async def main():
    print("Asset Assembler agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 