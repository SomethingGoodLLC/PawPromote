import asyncio
from typing import Annotated, Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pptx import Presentation
from PIL import Image as PILImage
import requests
from io import BytesIO
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

import os
import tempfile
import qrcode
from pptx.util import Inches

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

AGENT_JWT = "PLACEHOLDER_JWT"  # Replace with actual JWT after registration
session = GenAISession(jwt_token=AGENT_JWT)


def create_pdf_book(content):
    stories = content["stories"]
    images = {img['pet']: img['image_url'] for img in content["images"]}
    original_photos = {img['pet']: img['image_url'] for img in content.get("original_photos", [])}
    enhanced_images = {img['pet']: img['image_url'] for img in content.get("enhanced_images", [])}
    story_images = {img['pet']: img['image_url'] for img in content.get("story_images", [])}
    ghibli_images = {img['pet']: img['image_url'] for img in content.get("ghibli_images", [])}
    badges = {b['pet']: b['badge_url'] for b in content["badges"]}
    videos = {v['pet']: v['video_url'] for v in content["videos"]}
    petfinder_urls = {p['pet']: p['url'] for p in content.get("petfinder_urls", [])}
    is_multi = len(stories) > 1

    # Track temporary files for cleanup
    temp_files = []

    def download_and_add_image(img_url, pet_name, image_type, width=3*inch, height=2.25*inch):
        """Helper function to download and add images to the PDF"""
        if not img_url:
            return None
            
        try:
            # Skip placeholder URLs
            if img_url.startswith("https://example.com"):
                flowables.append(Paragraph(f"{image_type}: (Placeholder - requires valid OpenAI API key)", styles['Body']))
                return None
            
            # Check if it's a local file path
            if os.path.exists(img_url):
                print(f"Using local image file {image_type} for {pet_name}: {img_url}")
                img = PILImage.open(img_url)
                # For local files, we can use them directly
                pet_img = Image(img_url, width=width, height=height)
                flowables.append(pet_img)
                print(f"✅ Successfully added {image_type} for {pet_name}")
            else:
                # Download from URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(img_url, headers=headers, timeout=30)
                print(f"Downloading {image_type} for {pet_name}: {img_url} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    img = PILImage.open(BytesIO(response.content))
                    img_path = tempfile.mktemp(suffix='.jpg')
                    temp_files.append(img_path)
                    img.save(img_path)
                    pet_img = Image(img_path, width=width, height=height)
                    flowables.append(pet_img)
                    print(f"✅ Successfully added {image_type} for {pet_name}")
                else:
                    flowables.append(Paragraph(f"{image_type}: (Failed to download - HTTP {response.status_code})", styles['Body']))
                    return None
        except Exception as e:
            print(f"❌ Error downloading {image_type} for {pet_name}: {str(e)}")
            flowables.append(Paragraph(f"{image_type}: (Error: {str(e)})", styles['Body']))
            return None

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=36)
        flowables = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Header', fontSize=24, leading=28, alignment=1, spaceAfter=20, fontName='Helvetica-Bold', textColor=colors.darkblue))
        styles.add(ParagraphStyle(name='Subheader', fontSize=14, leading=16, alignment=0, spaceAfter=10, textColor=colors.grey))
        styles.add(ParagraphStyle(name='Body', fontSize=12, leading=14, spaceAfter=10))
        styles.add(ParagraphStyle(name='CTA', fontSize=12, leading=14, spaceAfter=20, fontName='Helvetica-Oblique', textColor=colors.green))
        styles.add(ParagraphStyle(name='ImageLabel', fontSize=10, leading=12, spaceAfter=5, fontName='Helvetica-Bold', textColor=colors.darkblue))

        # Cover page
        flowables.append(Paragraph("Forever Friends: Adoption Stories from Alexandria's Cutest Companions", styles['Header']))
        flowables.append(Spacer(1, 0.2*inch))
        flowables.append(Paragraph("Their Stories Await Your Love.", styles['Subheader']))
        flowables.append(Spacer(1, 0.5*inch))
        if stories:
            pet = stories[0]['pet']
            # Use enhanced image for cover if available, otherwise original
            cover_img_url = enhanced_images.get(pet) or original_photos.get(pet) or images.get(pet)
            if cover_img_url:
                download_and_add_image(cover_img_url, pet, "Cover Photo", width=4*inch, height=3*inch)
        flowables.append(PageBreak())

        # Table of Contents
        flowables.append(Paragraph("Table of Contents", styles['Header']))
        flowables.append(Spacer(1, 0.2*inch))
        for s in stories:
            header = s['story']['header']
            flowables.append(Paragraph(header, styles['Body']))
        flowables.append(PageBreak())

        # Pet stories
        for story in stories:
            pet = story['pet']
            story_dict = story['story']
            flowables.append(Paragraph(story_dict['header'], styles['Header']))
            flowables.append(Paragraph(story_dict['subheader'], styles['Subheader']))
            flowables.append(Spacer(1, 0.2*inch))

            # 1. Original Petfinder Photo
            flowables.append(Paragraph("📸 Original Petfinder Photo", styles['ImageLabel']))
            original_url = original_photos.get(pet)
            download_and_add_image(original_url, pet, "Original Photo")
            flowables.append(Spacer(1, 0.1*inch))

            # 2. GPT-Image-1 Enhanced Creative Photo
            flowables.append(Paragraph("🎨 GPT-Image-1 Enhanced Creative Photo", styles['ImageLabel']))
            enhanced_url = enhanced_images.get(pet)
            download_and_add_image(enhanced_url, pet, "Enhanced Creative Photo")
            flowables.append(Spacer(1, 0.1*inch))

            # 3. GPT-Image-1 Story-Specific Image
            flowables.append(Paragraph("📖 GPT-Image-1 Story-Specific Image", styles['ImageLabel']))
            story_url = story_images.get(pet)
            download_and_add_image(story_url, pet, "Story-Specific Image")
            flowables.append(Spacer(1, 0.1*inch))

            # 4. GPT-Image-1 Ghibli-Style Image
            flowables.append(Paragraph("🌸 GPT-Image-1 Ghibli-Style Image", styles['ImageLabel']))
            ghibli_url = ghibli_images.get(pet)
            download_and_add_image(ghibli_url, pet, "Ghibli-Style Image")
            flowables.append(Spacer(1, 0.2*inch))

            # Badge
            badge_url = badges.get(pet)
            if badge_url and not badge_url.startswith("https://example.com"):
                try:
                    response = requests.get(badge_url)
                    if response.status_code == 200:
                        img = PILImage.open(BytesIO(response.content))
                        img_path = tempfile.mktemp(suffix='.jpg')
                        temp_files.append(img_path)
                        img.save(img_path)
                        badge_img = Image(img_path, width=2*inch, height=1*inch)
                        flowables.append(badge_img)
                except:
                    pass
            else:
                flowables.append(Paragraph("Badge: (Unable to load)", styles['Body']))

            # Story content
            for paragraph in story_dict['paragraphs']:
                flowables.append(Paragraph(paragraph, styles['Body']))
            flowables.append(Spacer(1, 0.2*inch))

            # CTA
            flowables.append(Paragraph(story_dict['cta'], styles['CTA']))
            flowables.append(Spacer(1, 0.2*inch))

            # QR Code for Petfinder
            petfinder_url = petfinder_urls.get(pet)
            if petfinder_url:
                flowables.append(Paragraph(f"Scan to Learn More About {pet} on Petfinder!", styles['Body']))
                try:
                    qr = qrcode.QRCode(version=1, box_size=5, border=5)
                    qr.add_data(petfinder_url)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_path = tempfile.mktemp(suffix='.png')
                    temp_files.append(qr_path)
                    qr_img.save(qr_path)
                    qr_image = Image(qr_path, width=1.5*inch, height=1.5*inch)
                    flowables.append(qr_image)
                except:
                    flowables.append(Paragraph(f"QR Code: (Unable to generate)", styles['Body']))

            if story != stories[-1]:  # Not the last story
                flowables.append(PageBreak())

        # Build PDF
        doc.build(flowables)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return tmp_pdf.name

def create_ppt(content):
    stories = content["stories"]
    images = {img['pet']: img['image_url'] for img in content["images"]}
    story_images = {img['pet']: img['image_url'] for img in content.get("story_images", [])}
    badges = {b['pet']: b['badge_url'] for b in content["badges"]}
    videos = {v['pet']: v['video_url'] for v in content["videos"]}
    petfinder_urls = {p['pet']: p['url'] for p in content.get("petfinder_urls", [])}
    prs = Presentation()
    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    title.text = "Pet Adoption Stories"
    subtitle = slide.placeholders[1]
    subtitle.text = "Real Pets from Alexandria, VA Looking for Forever Homes"
    for story in stories:
        pet = story['pet']
        story_dict = story['story']
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = slide.shapes.title
        title.text = story_dict['header']
        content_placeholder = slide.placeholders[1]
        
        # Format story content for PowerPoint
        story_text = story_dict['subheader'] + "\n\n"
        for para in story_dict['paragraphs']:
            story_text += para + "\n\n"
        story_text += story_dict['cta']
        
        content_placeholder.text = story_text
        
        # Real pet photo
        img_url = images.get(pet)
        if img_url:
            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    img_path = tempfile.mktemp(suffix='.jpg')
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(2.5))
                    os.remove(img_path)
            except Exception as e:
                # Add text placeholder if image fails
                textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(2.5), Inches(1))
                text_frame = textbox.text_frame
                p = text_frame.add_paragraph()
                p.text = "Real Photo\n(Unable to load)"
        # Story-specific image
        story_img_url = story_images.get(pet)
        if story_img_url and not story_img_url.startswith("https://generated-story-image.example.com"):
            try:
                response = requests.get(story_img_url)
                if response.status_code == 200:
                    story_img_path = tempfile.mktemp(suffix='.jpg')
                    with open(story_img_path, 'wb') as f:
                        f.write(response.content)
                    slide.shapes.add_picture(story_img_path, Inches(4), Inches(2), width=Inches(2.5))
                    os.remove(story_img_path)
            except Exception as e:
                # Add text placeholder if image fails
                textbox = slide.shapes.add_textbox(Inches(4), Inches(2), Inches(2.5), Inches(1))
                text_frame = textbox.text_frame
                p = text_frame.add_paragraph()
                p.text = "Story Illustration\n(GPT-Image-1)"
        elif story_img_url:
            # Add text placeholder for mock URL
            textbox = slide.shapes.add_textbox(Inches(4), Inches(2), Inches(2.5), Inches(1))
            text_frame = textbox.text_frame
            p = text_frame.add_paragraph()
            p.text = "Story Illustration\n(GPT-Image-1)"
        # Badge
        badge_url = badges.get(pet)
        if badge_url and not badge_url.startswith("https://generated-badge.example.com"):
            try:
                response = requests.get(badge_url)
                if response.status_code == 200:
                    badge_path = tempfile.mktemp(suffix='.jpg')
                    with open(badge_path, 'wb') as f:
                        f.write(response.content)
                    slide.shapes.add_picture(badge_path, Inches(7), Inches(2), width=Inches(1.5))
                    os.remove(badge_path)
            except Exception as e:
                # Add text placeholder if image fails
                textbox = slide.shapes.add_textbox(Inches(7), Inches(2), Inches(1.5), Inches(1))
                text_frame = textbox.text_frame
                p = text_frame.add_paragraph()
                p.text = "Badge\n(Generated)"
        elif badge_url:
            # Add text placeholder for mock URL
            textbox = slide.shapes.add_textbox(Inches(7), Inches(2), Inches(1.5), Inches(1))
            text_frame = textbox.text_frame
            p = text_frame.add_paragraph()
            p.text = "Badge\n(Generated)"
        # Petfinder link - add as text box with hyperlink
        petfinder_url = petfinder_urls.get(pet)
        if petfinder_url:
            # Add text box for Petfinder link
            textbox = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(1))
            text_frame = textbox.text_frame
            p = text_frame.add_paragraph()
            r = p.add_run()
            r.text = f"Learn more about {pet} on Petfinder: {petfinder_url}"
            hlink = r.hyperlink
            hlink.address = petfinder_url
    with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as tmp_ppt:
        prs.save(tmp_ppt.name)
    return tmp_ppt.name


@session.bind(
    name="asset_assembler",
    description="Assembles stories and assets into books, PDFs, PPTs."
)
async def asset_assembler(
    agent_context: GenAIContext,
    content: Annotated[Dict[str, Any], "Generated content with stories and video/image URLs"],
    specification: Annotated[str, "Specification for assembly"] = ""
) -> Dict[str, str]:
    agent_context.logger.info(f"Assembling assets with specification: {specification}")
    pdf_path = create_pdf_book(content)
    ppt_path = create_ppt(content)
    return {"book_file": pdf_path, "ppt_file": ppt_path}


async def main():
    print("Asset Assembler agent started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main()) 