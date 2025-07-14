#!/usr/bin/env python3
"""
Preview a Ghibli-style story for one of the real pets
"""

import json
from pathlib import Path

def load_real_alexandria_pets():
    """Load real pet data from Alexandria, VA"""
    json_path = Path(__file__).parent / "pets_alexandria_va.json"
    
    if not json_path.exists():
        print(f"❌ Pet data file not found: {json_path}")
        return []
    
    with open(json_path, 'r') as f:
        pets_data = json.load(f)
    
    return pets_data[:5]

def generate_ghibli_story_preview(pet):
    """Generate a Ghibli-style magical story for a pet"""
    name = pet.get('name', 'Unknown')
    breed = pet.get('breeds', {}).get('primary', 'Mixed')
    age = pet.get('age', 'Adult')
    gender = pet.get('gender', 'Unknown')
    size = pet.get('size', 'Medium')
    description = pet.get('description', 'A wonderful pet looking for a home.')
    tags = pet.get('tags', [])
    
    # Create magical Ghibli-style story
    story_elements = []
    
    # Title with magical elements
    if 'Cat' in pet.get('type', ''):
        story_elements.append(f"🌟 **The Tale of {name}, the Mystical Feline Guardian** 🌟")
    else:
        story_elements.append(f"🌟 **The Adventure of {name}, the Brave Forest Companion** 🌟")
    
    # Magical opening
    story_elements.append("")
    story_elements.append("*In the enchanted neighborhoods of Alexandria, where the Potomac River whispers ancient secrets and cherry blossoms dance in the spring breeze, there lived a very special creature...*")
    story_elements.append("")
    
    # Main story based on pet characteristics
    if 'Shy' in tags:
        story_elements.append(f"Deep in the quiet corners of the animal sanctuary, {name} discovered the magic of hidden places. Like Chihiro learning to see the spirit world, this gentle {breed.lower()} possessed the rare gift of seeing beauty in stillness. {name}'s whiskers would twitch with ancient wisdom, sensing the emotions of those who needed comfort most.")
    elif 'Friendly' in tags:
        story_elements.append(f"With a heart as warm as the hearth in Howl's moving castle, {name} the {breed.lower()} became known throughout the shelter as the Great Welcomer. Like Totoro greeting new friends, {name} would bound forward with tail wagging, spreading joy like magical forest dust to everyone who crossed the threshold.")
    elif 'Playful' in tags:
        story_elements.append(f"In the style of Kiki's playful spirit, {name} the {breed.lower()} turned every day into a grand adventure. Toys became magical artifacts, and the shelter yard transformed into an endless meadow where {name} could chase butterflies that sparkled like the soot sprites in Spirited Away.")
    else:
        story_elements.append(f"Like the wise forest spirits in Princess Mononoke, {name} the {breed.lower()} carried an ancient soul within. There was something magical about the way {name} moved through the world, as if understanding secrets that only the most perceptive creatures could sense.")
    
    story_elements.append("")
    
    # Age-specific magical elements
    if age == 'Senior':
        story_elements.append(f"As an elder of the animal kingdom, {name} possessed the wisdom of Calcifer's eternal flame. This {gender.lower()} sage had seen many seasons change, and now sought a special human companion who could appreciate the magic that comes with experience and unconditional love.")
    elif age == 'Young':
        story_elements.append(f"Young {name} bubbled with the same curious energy as Mei discovering the forest spirits. This {gender.lower()} adventurer was ready to grow alongside a human family, learning life's magical lessons together like characters in a Ghibli tale.")
    else:
        story_elements.append(f"In the prime of life, {name} radiated the confident magic of San running through the forest. This {gender.lower()} companion had found the perfect balance between playful spirit and gentle wisdom.")
    
    story_elements.append("")
    
    # Incorporate real shelter description with magical twist
    if description and len(description) > 50:
        story_elements.append("*The shelter keepers whispered this tale about our magical friend:*")
        story_elements.append(f'"{description[:300]}{"..." if len(description) > 300 else ""}"')
        story_elements.append("")
    
    # Magical quest/call to action
    story_elements.append(f"Now, {name} waits for the most important adventure of all - finding a forever family. Like every great Ghibli story, this tale needs a loving human companion to help write the next chapter. Will you be the one to discover the magic that {name} has been waiting to share?")
    
    story_elements.append("")
    story_elements.append("*The forest spirits believe that every creature has a perfect match waiting somewhere in the world. Perhaps that match is you.*")
    
    story_elements.append("")
    story_elements.append("🏠 **Begin Your Magical Journey:**")
    story_elements.append(f"Contact the Alexandria Animal Shelter at 703-746-4774 to meet {name} and discover if you're meant to be part of this enchanted story.")
    
    return '\n'.join(story_elements)

def preview_ghibli_stories():
    """Preview the magical Ghibli stories"""
    
    print("🌟 Ghibli-Style Pet Stories Preview")
    print("=" * 50)
    
    pets = load_real_alexandria_pets()
    
    if not pets:
        print("❌ No pets data available")
        return
    
    # Show preview of first pet (Pepper)
    pepper = pets[0]
    
    print(f"\n📸 Pet Photo URL: {pepper.get('photos', [{}])[0].get('large', 'No photo') if pepper.get('photos') else 'No photo'}")
    print(f"🐾 Pet Details: {pepper.get('name')} - {pepper.get('breeds', {}).get('primary', 'Mixed')} ({pepper.get('age', 'Unknown')})")
    print(f"🏷️  Tags: {', '.join(pepper.get('tags', []))}")
    
    print("\n" + "="*50)
    print("MAGICAL GHIBLI STORY:")
    print("="*50)
    
    story = generate_ghibli_story_preview(pepper)
    print(story)
    
    print("\n" + "="*50)
    print("📚 This is just one of 5 magical stories in the full PDF!")
    print("📸 The PDF version includes actual pet photos downloaded from the web!")
    print("🎨 Each story is uniquely crafted based on the pet's real personality and characteristics!")

if __name__ == "__main__":
    preview_ghibli_stories() 