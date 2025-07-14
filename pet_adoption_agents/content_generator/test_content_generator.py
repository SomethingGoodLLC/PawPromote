import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from main import generate_story, generate_image, generate_badge, generate_video_from_photo, content_generator, get_openai_client


class MockContext:
    def __init__(self):
        self.logger = MagicMock()


@pytest.mark.asyncio
async def test_generate_story_without_humor():
    """Test generate_story function without humor flag"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    
    with patch('main.get_openai_client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Heartwarming story about Buddy'
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        result = await generate_story(pet, humorous=False)
        
        assert result == 'Heartwarming story about Buddy'
        mock_client.return_value.chat.completions.create.assert_called_once_with(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': "Create a heartwarming adventure story for Buddy using real description: Friendly dog. Include adoption CTA."}]
        )


@pytest.mark.asyncio
async def test_generate_story_with_humor():
    """Test generate_story function with humor flag"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    
    with patch('main.get_openai_client') as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Funny story about Buddy'
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        result = await generate_story(pet, humorous=True)
        
        assert result == 'Funny story about Buddy'
        mock_client.return_value.chat.completions.create.assert_called_once_with(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': "Create a funny, heartwarming adventure story for Buddy using real description: Friendly dog. Include puns, silly situations, and adoption CTA."}]
        )


@pytest.mark.asyncio
async def test_generate_image():
    """Test generate_image function"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    
    with patch('main.get_openai_client') as mock_client:
        mock_response = MagicMock()
        mock_response.data[0].url = 'http://example.com/image.png'
        mock_client.return_value.images.generate.return_value = mock_response
        
        result = await generate_image(pet, 'test image')
        
        assert result == 'http://example.com/image.png'
        mock_client.return_value.images.generate.assert_called_once_with(
            model='gpt-image-1', 
            prompt='Generate a test image for pet Buddy based on: Friendly dog', 
            n=1, 
            size='1024x1024'
        )


@pytest.mark.asyncio
async def test_generate_badge():
    """Test generate_badge function"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    
    with patch('main.generate_image') as mock_generate:
        mock_generate.return_value = 'http://example.com/badge.png'
        
        result = await generate_badge(pet)
        
        assert result == 'http://example.com/badge.png'
        mock_generate.assert_called_once_with(pet, 'status badge in a humorous style')


@pytest.mark.asyncio
async def test_generate_video_from_photo_no_photo():
    """Test generate_video_from_photo with no photo URL"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    
    result = await generate_video_from_photo(pet, None, humorous=False)
    
    assert result == 'no_video_generated'


@pytest.mark.asyncio
async def test_generate_video_from_photo_download_fail():
    """Test generate_video_from_photo with photo download failure"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog'}
    photo_url = 'http://example.com/photo.jpg'
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        
        result = await generate_video_from_photo(pet, photo_url, humorous=False)
        
        assert result == 'failed_to_download_photo'


@pytest.mark.asyncio
async def test_generate_video_from_photo_sora_success():
    """Test generate_video_from_photo with successful Sora API call"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog', 'type': 'dog'}
    photo_url = 'http://example.com/photo.jpg'
    
    with patch('requests.get') as mock_get, \
         patch('main.get_openai_client') as mock_client:
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'image_data'
        
        mock_response = MagicMock()
        mock_response.data[0].url = 'http://example.com/video.mp4'
        mock_client.return_value.videos.generate.return_value = mock_response
        
        result = await generate_video_from_photo(pet, photo_url, humorous=True)
        
        assert result == 'http://example.com/video.mp4'


@pytest.mark.asyncio
async def test_generate_video_from_photo_fallback_to_vertex():
    """Test generate_video_from_photo with fallback to Vertex AI"""
    pet = {'name': 'Buddy', 'description': 'Friendly dog', 'type': 'dog'}
    photo_url = 'http://example.com/photo.jpg'
    
    with patch('requests.get') as mock_get, \
         patch('main.get_openai_client') as mock_client, \
         patch('main.vertexai') as mock_vertexai, \
         patch('main.GenerativeModel') as mock_model, \
         patch('main.Part') as mock_part:
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'image_data'
        
        # Make Sora fail
        mock_client.return_value.videos.generate.side_effect = Exception('Sora failed')
        
        # Mock Vertex AI response
        mock_response = MagicMock()
        mock_response.candidates[0].content.parts[0].file_data.file_uri = 'gcs://video.uri'
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Mock Part.from_data
        mock_part.from_data.return_value = MagicMock()
        
        result = await generate_video_from_photo(pet, photo_url, humorous=False)
        
        assert result == 'gcs://video.uri'


@pytest.mark.asyncio
async def test_content_generator():
    """Test the main content_generator function"""
    mock_context = MockContext()
    pets = [{'name': 'Buddy', 'description': 'Friendly dog', 'photos': ['http://example.com/photo.jpg'], 'type': 'dog'}]
    
    with patch('main.generate_story') as mock_story, \
         patch('main.generate_image') as mock_image, \
         patch('main.generate_badge') as mock_badge, \
         patch('main.generate_video_from_photo') as mock_video:
        
        mock_story.return_value = 'Generated story text'
        mock_image.return_value = 'http://example.com/image.png'
        mock_badge.return_value = 'http://example.com/badge.png'
        mock_video.return_value = 'http://example.com/video.mp4'
        
        result = await content_generator(mock_context, pets, humorous=True)
        
        # Verify structure
        assert 'stories' in result
        assert 'images' in result
        assert 'badges' in result
        assert 'videos' in result
        
        # Verify content
        assert result['stories'][0]['pet'] == 'Buddy'
        assert result['stories'][0]['story'] == 'Generated story text'
        assert result['images'][0]['pet'] == 'Buddy'
        assert result['images'][0]['image_url'] == 'http://example.com/image.png'
        assert result['badges'][0]['pet'] == 'Buddy'
        assert result['badges'][0]['badge_url'] == 'http://example.com/badge.png'
        assert result['videos'][0]['pet'] == 'Buddy'
        assert result['videos'][0]['video_url'] == 'http://example.com/video.mp4'
        
        # Verify function calls
        mock_story.assert_called_once_with(pets[0], True)
        mock_image.assert_called_once_with(pets[0])
        mock_badge.assert_called_once_with(pets[0])
        mock_video.assert_called_once_with(pets[0], 'http://example.com/photo.jpg', True)


def test_get_openai_client_standard():
    """Test get_openai_client without Azure"""
    with patch('main.AZURE_OPENAI_ENDPOINT', None), \
         patch('main.OpenAI') as mock_openai:
        
        get_openai_client()
        
        mock_openai.assert_called_once_with(api_key='placeholder')


def test_get_openai_client_azure():
    """Test get_openai_client with Azure configuration"""
    with patch('main.AZURE_OPENAI_ENDPOINT', 'https://test.openai.azure.com/'), \
         patch('main.OpenAI') as mock_openai:
        
        get_openai_client()
        
        mock_openai.assert_called_once_with(
            api_key='placeholder',
            base_url='https://test.openai.azure.com/',
            api_version='2023-05-01'
        )


if __name__ == '__main__':
    pytest.main([__file__]) 