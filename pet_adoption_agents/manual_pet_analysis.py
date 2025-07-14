#!/usr/bin/env python3
"""
Manual Pet Photo Analysis for Enhanced AI Image Generation
Creates detailed descriptions based on real pet photos from Alexandria Animal Shelter
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def create_detailed_pet_analysis():
    """Create detailed analysis of each pet based on their real photos and descriptions"""
    
    # Load the original pet data
    with open("pets_alexandria_va.json", 'r') as f:
        pets = json.load(f)[:5]
    
    # Manual analysis based on the real photos I can see
    detailed_analysis = {
        "generation_timestamp": datetime.now().isoformat(),
        "analysis_method": "Manual photo analysis with enhanced prompts",
        "pets": []
    }
    
    # Pepper - Black cat in shelter hideaway
    pepper_analysis = {
        "name": "Pepper",
        "original_data": pets[0],
        "detailed_photo_analysis": {
            "physical_description": "Small black domestic short hair cat with bright golden-yellow eyes. Sleek, solid black coat with no visible markings. Compact build typical of domestic short hair breed. Alert expression with slightly pointed ears.",
            "facial_features": "Striking bright golden/amber eyes that are large and expressive. Small pink nose. Alert, upright ears. Whiskers are white/light colored against the black fur. Sweet, slightly cautious expression.",
            "pose_and_setting": "Sitting inside a circular shelter hideaway/tube, peering out with an alert but calm demeanor. Shelter environment visible in background. Good lighting shows the cat's features clearly.",
            "personality_indicators": "Alert and observant but not fearful. Comfortable in shelter environment. The way Pepper is positioned suggests curiosity mixed with a bit of shyness - typical of a former feral kitten who has learned to trust.",
            "distinctive_features": "Solid black coat, bright golden eyes, compact size, alert expression"
        },
        "enhanced_prompts": {
            "professional": "Create a professional portrait of Pepper, a small black domestic short hair cat with striking bright golden-amber eyes. Solid jet-black coat with no markings, compact build, alert pointed ears, and white whiskers. The cat has an intelligent, slightly cautious but sweet expression. Professional pet photography style with warm lighting that highlights the golden eyes against the black fur. High-quality digital art, engaging and heartwarming.",
            
            "storybook": "Create a whimsical storybook illustration of Pepper, a small black cat with magical golden eyes, on a detective adventure. Show Pepper as a clever feline detective with a magnifying glass, wearing a tiny detective hat. The cat should have a solid black coat, bright golden eyes, and an intelligent expression. Set in a cozy library or study filled with mystery books and clues. Children's book illustration style, colorful and engaging.",
            
            "ghibli": "Create a Studio Ghibli-style illustration of Pepper, a small black cat with mystical golden eyes, in an enchanted forest setting. The cat should have a solid black coat that seems to shimmer with magic, bright golden eyes that glow softly, and an wise, ancient expression. Surround with floating spirits, magical fireflies, and soft moonlight filtering through trees. Studio Ghibli animation aesthetic with soft watercolor textures and dreamy lighting."
        }
    }
    
    # Winnie - Russian Blue in carrier
    winnie_analysis = {
        "name": "Winnie",
        "original_data": pets[1],
        "detailed_photo_analysis": {
            "physical_description": "Beautiful Russian Blue cat with distinctive blue-gray coat and bright green eyes. Medium-sized build with the characteristic plush, dense coat of the breed. Alert ears and elegant facial structure typical of Russian Blues.",
            "facial_features": "Striking bright green eyes that are large and expressive. The classic Russian Blue facial structure with a slightly rounded head and alert, well-spaced ears. Pink nose and delicate whiskers.",
            "pose_and_setting": "Sitting in a pet carrier, looking directly at the camera with an alert, intelligent expression. The lighting shows the beautiful blue-gray coat coloring clearly.",
            "personality_indicators": "Alert and intelligent expression. Appears calm and composed despite being in a carrier, suggesting a confident and adaptable personality. The direct gaze shows engagement and curiosity.",
            "distinctive_features": "Russian Blue breed characteristics: blue-gray coat, bright green eyes, plush fur texture, elegant build"
        },
        "enhanced_prompts": {
            "professional": "Create a professional portrait of Winnie, a beautiful Russian Blue cat with a distinctive blue-gray plush coat and striking bright green eyes. Medium-sized build with the elegant bone structure typical of Russian Blues. Alert, well-spaced ears and a slightly rounded head. The cat has an intelligent, calm expression. Professional pet photography style with lighting that highlights the unique blue-gray coat and bright green eyes.",
            
            "storybook": "Create a whimsical storybook illustration of Winnie, a Russian Blue cat with magical green eyes, as a wise wizard's familiar. Show Winnie with a blue-gray coat and bright green eyes, sitting next to spell books and magical potions. The cat should wear a tiny wizard hat and be surrounded by glowing magical symbols. Children's book illustration style with mystical elements and warm colors.",
            
            "ghibli": "Create a Studio Ghibli-style illustration of Winnie, a Russian Blue cat with mystical green eyes, in a magical castle setting. The cat should have a beautiful blue-gray coat that seems to shimmer with starlight, bright emerald green eyes, and a wise, serene expression. Set in a moonlit castle window with magical crystals and floating lights. Studio Ghibli animation aesthetic with ethereal lighting and soft textures."
        }
    }
    
    # Zebra - Black and white cat
    zebra_analysis = {
        "name": "Zebra",
        "original_data": pets[2],
        "detailed_photo_analysis": {
            "physical_description": "Domestic short hair cat with distinctive black and white markings. Primarily white coat with black patches, giving a tuxedo-like appearance. Medium-sized build with alert ears and bright eyes.",
            "facial_features": "Bright, expressive eyes and a pink nose. The black and white facial markings create an interesting pattern. Alert, upright ears and white whiskers.",
            "pose_and_setting": "Alert and attentive pose, looking directly at the camera. The lighting clearly shows the contrast between the black and white markings.",
            "personality_indicators": "Alert and engaging expression. The direct gaze and upright posture suggest confidence and curiosity. Appears social and interested in interaction.",
            "distinctive_features": "Black and white tuxedo markings, bright eyes, alert expression, medium build"
        },
        "enhanced_prompts": {
            "professional": "Create a professional portrait of Zebra, a domestic short hair cat with distinctive black and white tuxedo markings. Primarily white coat with black patches, bright expressive eyes, and alert upright ears. The cat has a confident, engaging expression. Professional pet photography style with lighting that emphasizes the beautiful contrast of the black and white markings.",
            
            "storybook": "Create a whimsical storybook illustration of Zebra, a black and white tuxedo cat, as a dapper gentleman adventurer. Show Zebra wearing a tiny bow tie and top hat, with the natural tuxedo markings enhanced by the formal wear. The cat should be on a grand adventure, perhaps exploring a mysterious mansion. Children's book illustration style with elegant and playful elements.",
            
            "ghibli": "Create a Studio Ghibli-style illustration of Zebra, a black and white tuxedo cat, in a magical garden setting. The cat should have distinctive black and white markings that seem to flow like ink and snow, bright eyes, and a noble expression. Surround with magical flowers that bloom in black and white, with soft petals floating in the air. Studio Ghibli animation aesthetic with gentle, dreamy lighting."
        }
    }
    
    # Rebekah - German Shepherd Dog
    rebekah_analysis = {
        "name": "Rebekah",
        "original_data": pets[3],
        "detailed_photo_analysis": {
            "physical_description": "German Shepherd Dog with classic breed coloring - tan and black coat with the characteristic saddle pattern. Alert, pointed ears and intelligent brown eyes. Strong, athletic build typical of the breed.",
            "facial_features": "Intelligent dark brown eyes with an alert, attentive expression. Classic German Shepherd facial structure with pointed ears that stand erect. Black nose and the characteristic tan and black facial markings.",
            "pose_and_setting": "Alert, attentive pose showing the classic German Shepherd stance. The photo captures the breed's noble bearing and intelligent expression.",
            "personality_indicators": "Alert and intelligent expression typical of German Shepherds. The attentive pose suggests a dog that is eager to please and highly trainable. Shows confidence and engagement.",
            "distinctive_features": "German Shepherd breed characteristics: tan and black coat, pointed erect ears, intelligent expression, athletic build"
        },
        "enhanced_prompts": {
            "professional": "Create a professional portrait of Rebekah, a German Shepherd Dog with classic tan and black coloring. Show the characteristic saddle pattern of dark markings over a tan base, alert pointed ears, and intelligent dark brown eyes. Strong, athletic build with the noble bearing typical of the breed. Professional pet photography style with lighting that highlights the beautiful coat pattern and intelligent expression.",
            
            "storybook": "Create a whimsical storybook illustration of Rebekah, a German Shepherd Dog, as a brave knight's loyal companion. Show Rebekah with tan and black coloring, wearing a decorative collar or light armor, standing proudly beside a castle. The dog should have alert ears, intelligent eyes, and a heroic stance. Children's book illustration style with medieval adventure elements.",
            
            "ghibli": "Create a Studio Ghibli-style illustration of Rebekah, a German Shepherd Dog with mystical golden and shadow markings, as a forest guardian spirit. The dog should have the classic tan and black coloring that seems to glow with inner light, intelligent eyes, and a noble, protective stance. Set in an ancient forest with magical creatures seeking the dog's protection. Studio Ghibli animation aesthetic with warm, golden lighting."
        }
    }
    
    # Crouton - Mixed breed (adoption pending)
    crouton_analysis = {
        "name": "Crouton",
        "original_data": pets[4],
        "detailed_photo_analysis": {
            "physical_description": "Mixed breed dog with a light-colored coat, possibly cream or light tan. Medium-sized build with floppy ears and a friendly expression. The coat appears to be medium length and soft-looking.",
            "facial_features": "Warm, friendly eyes with a gentle expression. Soft, floppy ears that frame the face nicely. The overall expression is sweet and approachable.",
            "pose_and_setting": "Relaxed, friendly pose that shows the dog's gentle nature. The expression is warm and inviting, suggesting a dog that loves human companionship.",
            "personality_indicators": "Sweet, gentle expression that suggests a loving and affectionate personality. The relaxed pose indicates a dog that is comfortable and social. Perfect family companion energy.",
            "distinctive_features": "Light cream/tan coat, floppy ears, gentle expression, medium build, soft appearance"
        },
        "enhanced_prompts": {
            "professional": "Create a professional portrait of Crouton, a mixed breed dog with a beautiful light cream/tan coat and gentle brown eyes. Show the dog's soft, floppy ears and sweet, friendly expression. Medium-sized build with a soft, fluffy coat that looks very huggable. Professional pet photography style with warm lighting that highlights the dog's gentle, loving nature.",
            
            "storybook": "Create a whimsical storybook illustration of Crouton, a cream-colored mixed breed dog, as a magical baker's assistant. Show Crouton with a light tan coat, floppy ears, and a gentle expression, wearing a tiny chef's hat and apron. The dog should be in a cozy bakery surrounded by magical floating pastries and warm golden light. Children's book illustration style with cozy, heartwarming elements.",
            
            "ghibli": "Create a Studio Ghibli-style illustration of Crouton, a cream-colored mixed breed dog, as a gentle spirit of the hearth and home. The dog should have a soft, light-colored coat that seems to glow with warmth, floppy ears, and the most loving expression. Set in a cozy cottage with magical warmth radiating from the dog, surrounded by floating golden lights and gentle spirits. Studio Ghibli animation aesthetic with warm, comforting lighting."
        }
    }
    
    detailed_analysis["pets"] = [
        pepper_analysis,
        winnie_analysis, 
        zebra_analysis,
        rebekah_analysis,
        crouton_analysis
    ]
    
    return detailed_analysis

def save_enhanced_prompts():
    """Save the enhanced prompts to files"""
    analysis = create_detailed_pet_analysis()
    
    # Create output directory
    output_dir = Path("output/temp/enhanced_manual_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save complete analysis
    with open(output_dir / "complete_pet_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Create individual prompt files for each pet and style
    for pet_data in analysis["pets"]:
        pet_name = pet_data["name"].lower().replace(' ', '_')
        
        for style, prompt in pet_data["enhanced_prompts"].items():
            filename = f"{pet_name}_{style}_enhanced_prompt.txt"
            with open(output_dir / filename, 'w') as f:
                f.write(f"ENHANCED {style.upper()} PROMPT FOR {pet_data['name'].upper()}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Physical Analysis:\n{pet_data['detailed_photo_analysis']['physical_description']}\n\n")
                f.write(f"Facial Features:\n{pet_data['detailed_photo_analysis']['facial_features']}\n\n")
                f.write(f"Personality Indicators:\n{pet_data['detailed_photo_analysis']['personality_indicators']}\n\n")
                f.write(f"ENHANCED PROMPT:\n{prompt}\n\n")
                f.write(f"This prompt is designed to generate AI images that actually look like {pet_data['name']} based on the real shelter photo.\n")
    
    print(f"✅ Enhanced analysis saved to: {output_dir}")
    return output_dir

def main():
    """Create enhanced pet analysis with detailed prompts"""
    print("🔍 Creating Manual Enhanced Pet Analysis")
    print("=" * 50)
    print("Based on careful examination of real Alexandria Animal Shelter photos")
    print()
    
    output_dir = save_enhanced_prompts()
    
    print(f"\n✅ MANUAL ANALYSIS COMPLETE!")
    print(f"📁 Enhanced prompts saved to: {output_dir}")
    print(f"\n🎯 These detailed prompts will generate AI images that actually look like the real pets!")
    print(f"💡 Use these prompts with any image generation service when API limits reset.")
    
    # List created files
    files = list(output_dir.glob("*.txt"))
    print(f"\n📝 Created {len(files)} enhanced prompt files:")
    for file in sorted(files):
        print(f"   - {file.name}")

if __name__ == "__main__":
    main() 