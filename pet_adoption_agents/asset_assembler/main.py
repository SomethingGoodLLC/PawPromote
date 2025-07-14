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
    story_images = {img['pet']: img['image_url'] for img in content.get("story_images", [])}
    badges = {b['pet']: b['badge_url'] for b in content["badges"]}
    videos = {v['pet']: v['video_url'] for v in content["videos"]}
    petfinder_urls = {p['pet']: p['url'] for p in content.get("petfinder_urls", [])}
    is_multi = len(stories) > 1

    # Track temporary files for cleanup
    temp_files = []

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=36)
        flowables = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Header', fontSize=24, leading=28, alignment=1, spaceAfter=20, fontName='Helvetica-Bold', textColor=colors.darkblue))
        styles.add(ParagraphStyle(name='Subheader', fontSize=14, leading=16, alignment=0, spaceAfter=10, textColor=colors.grey))
        styles.add(ParagraphStyle(name='Body', fontSize=12, leading=14, spaceAfter=10))
        styles.add(ParagraphStyle(name='CTA', fontSize=12, leading=14, spaceAfter=20, fontName='Helvetica-Oblique', textColor=colors.green))

        # Cover page
        flowables.append(Paragraph("Forever Friends: Adoption Stories from Alexandria's Cutest Companions", styles['Header']))
        flowables.append(Spacer(1, 0.2*inch))
        flowables.append(Paragraph("Their Stories Await Your Love.", styles['Subheader']))
        flowables.append(Spacer(1, 0.5*inch))
        if stories:
            pet = stories[0]['pet']
            img_url = images.get(pet)
            if img_url:
                try:
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        img_path = tempfile.mktemp(suffix='.jpg')
                        temp_files.append(img_path)
                        img.save(img_path)
                        cover_img = Image(img_path, width=4*inch, height=3*inch)
                        flowables.append(cover_img)
                except:
                    pass
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

            # Real photo
            img_url = images.get(pet)
            if img_url:
                try:
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        img_path = tempfile.mktemp(suffix='.jpg')
                        temp_files.append(img_path)
                        img.save(img_path)
                        pet_img = Image(img_path, width=3*inch, height=2.25*inch)
                        flowables.append(pet_img)
                except:
                    flowables.append(Paragraph("Real Photo: (Unable to load)", styles['Body']))
            flowables.append(Spacer(1, 0.2*inch))

            # Badge
            badge_url = badges.get(pet)
            if badge_url:
                try:
                    response = requests.get(badge_url)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        img_path = tempfile.mktemp(suffix='.jpg')
                        temp_files.append(img_path)
                        img.save(img_path)
                        badge_img = Image(img_path, width=1*inch, height=1*inch)
                        flowables.append(badge_img)
                except:
                    flowables.append(Paragraph("Badge: (Unable to load)", styles['Body']))

            # Story paragraphs
            for para in story_dict['paragraphs']:
                flowables.append(Paragraph(para, styles['Body']))

            # Illustration
            story_img_url = story_images.get(pet)
            if story_img_url:
                try:
                    response = requests.get(story_img_url)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        img_path = tempfile.mktemp(suffix='.jpg')
                        temp_files.append(img_path)
                        img.save(img_path)
                        story_img = Image(img_path, width=3*inch, height=2.25*inch)
                        flowables.append(story_img)
                except:
                    flowables.append(Paragraph("Story Illustration: (Unable to load)", styles['Body']))
            flowables.append(Spacer(1, 0.2*inch))

            # CTA
            flowables.append(Paragraph(story_dict['cta'], styles['CTA']))

            # QR code linking to Petfinder page
            petfinder_url = petfinder_urls.get(pet)
            if petfinder_url:
                qr = qrcode.QRCode()
                qr.add_data(petfinder_url)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_path = tempfile.mktemp(suffix='.png')
                temp_files.append(qr_path)
                qr_img.save(qr_path)
                flowables.append(Paragraph("Scan to Learn More About " + pet + " on Petfinder!", styles['Body']))
                flowables.append(Image(qr_path, width=1*inch, height=1*inch))

            flowables.append(PageBreak())

        # Back page
        flowables.append(Paragraph("Adoption Instructions", styles['Header']))
        flowables.append(Paragraph("To adopt one of these wonderful pets, contact the Alexandria shelter at adoption@alexandriashelter.org or visit our website for the adoption process.", styles['Body']))

        doc.build(flowables)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
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