#!/usr/bin/env python3
"""
Create a Real Pets Book with Alexandria, VA pets
Generates an actual PDF book using real pet data
"""

import json
import os
from datetime import datetime
from pathlib import Path

def load_real_alexandria_pets():
    """Load real pet data from Alexandria, VA"""
    json_path = Path(__file__).parent / "pets_alexandria_va.json"
    
    if not json_path.exists():
        print(f"❌ Pet data file not found: {json_path}")
        return []
    
    with open(json_path, 'r') as f:
        pets_data = json.load(f)
    
    # Take first 5 pets and format for display
    return pets_data[:5]

def generate_enhanced_story(pet):
    """Generate an enhanced story for a pet based on their real data"""
    name = pet.get('name', 'Unknown')
    breed = pet.get('breeds', {}).get('primary', 'Mixed')
    age = pet.get('age', 'Adult')
    gender = pet.get('gender', 'Unknown')
    size = pet.get('size', 'Medium')
    description = pet.get('description', 'A wonderful pet looking for a home.')
    tags = pet.get('tags', [])
    
    # Create personalized story based on actual pet characteristics
    story_intro = f"**{name}: Alexandria's Special {breed}**\n\n"
    
    # Use real description as base
    story_content = f"Meet {name}, a {age.lower()} {breed.lower()} with a heart full of love. "
    
    # Add personality based on tags
    if 'Friendly' in tags:
        story_content += f"{name} has a friendly personality that lights up any room. "
    elif 'Shy' in tags:
        story_content += f"{name} is a gentle soul who takes time to warm up but gives the deepest love. "
    elif 'Playful' in tags:
        story_content += f"{name} loves to play and would bring endless joy to an active family. "
    
    # Add size-specific details
    if size == 'Large':
        story_content += f"This {size.lower()} companion needs space to roam and a family who appreciates bigger dogs. "
    elif size == 'Small':
        story_content += f"This {size.lower()} bundle of joy is perfect for cozy homes and lap cuddles. "
    
    # Add age-specific details
    if age == 'Senior':
        story_content += f"As a senior pet, {name} offers the wisdom of years and the gratitude of a second chance. "
    elif age == 'Young':
        story_content += f"With youthful energy, {name} is ready to grow up alongside a loving family. "
    
    # Use actual description excerpt
    if description and len(description) > 50:
        story_content += f"\n\nFrom the shelter: \"{description[:200]}{'...' if len(description) > 200 else ''}\"\n\n"
    
    # Call to action
    story_content += f"If you're looking for a loyal companion who will fill your days with love, {name} might be the perfect match for you!\n\n"
    story_content += f"*Contact the Alexandria Animal Shelter at 703-746-4774 to learn more about adopting {name}.*"
    
    return story_intro + story_content

def create_pdf_with_reportlab(pets, stories, output_path):
    """Create PDF using ReportLab if available"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import blue, black
        
        # Create PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=blue,
            alignment=1  # Center alignment
        )
        
        story_title_style = ParagraphStyle(
            'StoryTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=black
        )
        
        story = []
        
        # Title page
        story.append(Paragraph("Alexandria Pets: Real Stories of Hope", title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Featuring {len(pets)} amazing pets looking for homes", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Generated on: " + datetime.now().strftime("%B %d, %Y"), styles['Normal']))
        story.append(PageBreak())
        
        # Add each pet story
        for i, (pet, pet_story) in enumerate(zip(pets, stories)):
            # Pet name as title
            name = pet.get('name', 'Unknown')
            story.append(Paragraph(f"Story {i+1}: {name}", story_title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Pet details
            breed = pet.get('breeds', {}).get('primary', 'Mixed')
            age = pet.get('age', 'Unknown')
            gender = pet.get('gender', 'Unknown')
            size = pet.get('size', 'Unknown')
            
            details = f"<b>Breed:</b> {breed} | <b>Age:</b> {age} | <b>Gender:</b> {gender} | <b>Size:</b> {size}"
            story.append(Paragraph(details, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Story content
            story_paragraphs = pet_story.split('\n\n')
            for paragraph in story_paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip(), styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            # Add page break except for last story
            if i < len(pets) - 1:
                story.append(PageBreak())
        
        # Contact information page
        story.append(PageBreak())
        story.append(Paragraph("Contact Information", story_title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Alexandria Animal Shelter</b>", styles['Normal']))
        story.append(Paragraph("4101 Eisenhower Ave", styles['Normal']))
        story.append(Paragraph("Alexandria, VA 22304", styles['Normal']))
        story.append(Paragraph("Phone: 703-746-4774", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Visit us to meet these wonderful pets in person!", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return True
        
    except ImportError:
        print("❌ ReportLab not available. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return False

def create_text_book(pets, stories, output_path):
    """Create a text version of the book"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("ALEXANDRIA PETS: REAL STORIES OF HOPE\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Featuring {len(pets)} amazing pets looking for homes\n")
            f.write(f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n\n")
            f.write("=" * 50 + "\n\n")
            
            for i, (pet, pet_story) in enumerate(zip(pets, stories)):
                f.write(f"STORY {i+1}: {pet.get('name', 'Unknown').upper()}\n")
                f.write("-" * 30 + "\n\n")
                
                # Pet details
                breed = pet.get('breeds', {}).get('primary', 'Mixed')
                age = pet.get('age', 'Unknown')
                gender = pet.get('gender', 'Unknown')
                size = pet.get('size', 'Unknown')
                
                f.write(f"Breed: {breed} | Age: {age} | Gender: {gender} | Size: {size}\n\n")
                
                # Story content
                f.write(pet_story)
                f.write("\n\n" + "=" * 50 + "\n\n")
            
            # Contact information
            f.write("CONTACT INFORMATION\n")
            f.write("-" * 20 + "\n\n")
            f.write("Alexandria Animal Shelter\n")
            f.write("4101 Eisenhower Ave\n")
            f.write("Alexandria, VA 22304\n")
            f.write("Phone: 703-746-4774\n\n")
            f.write("Visit us to meet these wonderful pets in person!\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating text book: {e}")
        return False

def create_real_pets_book():
    """Create a book with real pets from Alexandria, VA"""
    
    print("📚 Creating Real Pets Book - Alexandria, VA")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Load real pet data
    print("\n1. 📊 Loading real pet data from Alexandria, VA...")
    pets = load_real_alexandria_pets()
    
    if not pets:
        print("❌ No pets data available")
        return False
    
    print(f"✅ Loaded {len(pets)} real pets from Alexandria Animal Shelter!")
    
    # Display pets
    for i, pet in enumerate(pets, 1):
        name = pet.get('name', 'Unknown')
        breed = pet.get('breeds', {}).get('primary', 'Mixed')
        print(f"   {i}. {name} - {breed}")
    
    # Step 2: Generate enhanced stories
    print(f"\n2. 📝 Generating enhanced stories for real pets...")
    stories = []
    for pet in pets:
        story = generate_enhanced_story(pet)
        stories.append(story)
    
    print(f"✅ Generated {len(stories)} personalized stories!")
    
    # Step 3: Create the book
    print(f"\n3. 📚 Creating book files...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Try to create PDF first
    pdf_path = output_dir / f"alexandria_real_pets_book_{timestamp}.pdf"
    pdf_success = create_pdf_with_reportlab(pets, stories, pdf_path)
    
    if pdf_success:
        print(f"✅ PDF book created: {pdf_path}")
        if pdf_path.exists():
            print(f"   📏 File size: {pdf_path.stat().st_size:,} bytes")
    
    # Always create text version as backup
    text_path = output_dir / f"alexandria_real_pets_book_{timestamp}.txt"
    text_success = create_text_book(pets, stories, text_path)
    
    if text_success:
        print(f"✅ Text book created: {text_path}")
        if text_path.exists():
            print(f"   📏 File size: {text_path.stat().st_size:,} bytes")
    
    # Summary
    print(f"\n🎉 REAL PETS BOOK CREATION COMPLETE!")
    print("=" * 50)
    print(f"📊 Real pets featured: {len(pets)}")
    print(f"📝 Stories created: {len(stories)}")
    print(f"📚 Book formats: {'PDF + Text' if pdf_success else 'Text only'}")
    print(f"📁 Output directory: {output_dir}")
    
    print(f"\n🐾 Featured Pets:")
    for pet in pets:
        name = pet.get('name', 'Unknown')
        breed = pet.get('breeds', {}).get('primary', 'Mixed')
        age = pet.get('age', 'Unknown')
        print(f"   • {name} - {breed} ({age})")
    
    print(f"\n💡 These are real pets waiting for homes in Alexandria, VA!")
    print(f"   Contact Alexandria Animal Shelter at 703-746-4774")
    
    return True

if __name__ == "__main__":
    success = create_real_pets_book()
    if success:
        print(f"\n✅ Book creation completed successfully!")
    else:
        print(f"\n❌ Book creation failed.") 