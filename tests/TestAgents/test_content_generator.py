import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pet_adoption_agents.content_generator.main import generate_story, generate_image, generate_badge, generate_video_from_photo, content_generator, get_openai_client
from genai_session.utils.context import GenAIContext

@pytest.mark.asyncio
async def test_generate_story_without_humor():
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    with patch('pet_adoption_agents.content_generator.main.get_openai_client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Heartwarming story'
        mock_client.return_value.chat.completions.create.return_value = mock_response
        result = await generate_story(pet, humorous=False)
        assert result == 'Heartwarming story'
        mock_client.return_value.chat.completions.create.assert_called_once_with(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': "Create a heartwarming adventure story for Buddy using real description: Friendly dog. Include adoption CTA."}]
        )

@pytest.mark.asyncio
async def test_generate_story_with_humor():
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    with patch('pet_adoption_agents.content_generator.main.get_openai_client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Funny story'
        mock_client.return_value.chat.completions.create.return_value = mock_response
        result = await generate_story(pet, humorous=True)
        assert result == 'Funny story'
        mock_client.return_value.chat.completions.create.assert_called_once_with(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': "Create a funny, heartwarming adventure story for Buddy using real description: Friendly dog. Include puns, silly situations, and adoption CTA."}]
        )

@pytest.mark.asyncio
async def test_generate_image():
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    with patch('pet_adoption_agents.content_generator.main.get_openai_client') as mock_client:
        mock_response = MagicMock()
        mock_response.data[0].url = 'http://image.url'
        mock_client.return_value.images.generate.return_value = mock_response
        result = await generate_image(pet, 'test image')
        assert result == 'http://image.url'
        mock_client.return_value.images.generate.assert_called_once_with(
            model='dall-e-3', prompt='Generate a test image for pet Buddy based on: Friendly dog', n=1, size='1024x1024'
        )

@pytest.mark.asyncio
async def test_generate_badge():
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    with patch('pet_adoption_agents.content_generator.main.generate_image') as mock_generate:
        mock_generate.return_value = 'http://badge.url'
        result = await generate_badge(pet)
        assert result == 'http://badge.url'
        mock_generate.assert_called_once_with(pet, 'status badge in a humorous style')

@pytest.mark.asyncio
async def test_generate_video_from_photo_success():
    pet = {'name': 'Buddy', 'description': 'Friendly dog', 'type': 'dog'}
    photo_url = 'http://photo.url'
    with patch('requests.get') as mock_get, patch('pet_adoption_agents.content_generator.main.get_openai_client') as mock_client:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'image_data'
        mock_response = MagicMock()
        mock_response.data[0].url = 'http://video.url'
        mock_client.return_value.videos.generate.return_value = mock_response
        result = await generate_video_from_photo(pet, photo_url, humorous=True)
        assert result == 'http://video.url'

@pytest.mark.asyncio
async def test_generate_video_from_photo_fallback():
    pet = {'name': 'Buddy', 'description': 'Friendly dog', 'type': 'dog'}
    photo_url = 'http://photo.url'
    with patch('requests.get') as mock_get, patch('pet_adoption_agents.content_generator.main.get_openai_client') as mock_client, \
         patch('vertexai.init'), patch('vertexai.preview.generative_models.GenerativeModel') as mock_model:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'image_data'
        mock_client.return_value.videos.generate.side_effect = Exception('Sora failed')
        mock_response = MagicMock()
        mock_response.candidates[0].content.parts[0].file_data.file_uri = 'gcs://video.uri'
        mock_model.return_value.generate_content.return_value = mock_response
        result = await generate_video_from_photo(pet, photo_url, humorous=False)
        assert result == 'gcs://video.uri'

@pytest.mark.asyncio
async def test_content_generator():
    mock_context = MagicMock(spec=GenAIContext)
    pets = [{'name': 'Buddy', 'description': 'Friendly dog', 'photos': ['http://photo.url'], 'type': 'dog'}]
    with patch('pet_adoption_agents.content_generator.main.generate_story') as mock_story, \
         patch('pet_adoption_agents.content_generator.main.generate_image') as mock_image, \
         patch('pet_adoption_agents.content_generator.main.generate_badge') as mock_badge, \
         patch('pet_adoption_agents.content_generator.main.generate_video_from_photo') as mock_video:
        mock_story.return_value = 'story text'
        mock_image.return_value = 'image url'
        mock_badge.return_value = 'badge url'
        mock_video.return_value = 'video url'
        result = await content_generator(mock_context, pets, humorous=True)
        assert 'stories' in result
        assert result['stories'][0]['story'] == 'story text'
        assert result['images'][0]['image_url'] == 'image url'
        assert result['badges'][0]['badge_url'] == 'badge url'
        assert result['videos'][0]['video_url'] == 'video url'
        mock_story.assert_called_once_with(pets[0], True)
        mock_image.assert_called_once_with(pets[0])
        mock_badge.assert_called_once_with(pets[0])
        mock_video.assert_called_once_with(pets[0], 'http://photo.url', True) 