import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_master_orchestrator_mock():
    """Test master orchestrator function with mocked dependencies"""
    
    # Mock the session and context
    mock_session = MagicMock()
    mock_context = MagicMock()
    
    # Mock external dependencies
    with patch('requests.get') as mock_get, \
         patch('pet_adoption_agents.master_orchestrator.main.session') as mock_session_obj:
        
        # Setup mock responses
        mock_get.return_value.json.return_value = {
            'active_connections': [
                {'name': 'data_fetcher', 'id': 'fetcher_id'},
                {'name': 'content_generator', 'id': 'content_id'},
                {'name': 'asset_assembler', 'id': 'asset_id'},
                {'name': 'book_shipper', 'id': 'shipper_id'}
            ]
        }
        
        # Mock session.send calls
        mock_session_obj.send = AsyncMock()
        mock_session_obj.send.side_effect = [
            # Data fetcher response
            [
                {
                    "id": 1,
                    "name": "Buddy",
                    "description": "Friendly dog",
                    "photos": ["http://example.com/buddy.jpg"],
                    "status": "adoptable"
                },
                {
                    "id": 2,
                    "name": "Whiskers", 
                    "description": "Playful cat",
                    "photos": ["http://example.com/whiskers.jpg"],
                    "status": "adoptable"
                }
            ],
            # Content generator response
            {
                "stories": [
                    {"pet_id": 1, "story": "Buddy's adventure story"},
                    {"pet_id": 2, "story": "Whiskers' adventure story"}
                ]
            },
            # Asset assembler response
            {
                "videos": [
                    {"pet_id": 1, "video_url": "http://example.com/buddy_video.mp4"},
                    {"pet_id": 2, "video_url": "http://example.com/whiskers_video.mp4"}
                ]
            },
            # Book shipper response
            {
                "book_url": "http://example.com/pet_book.pdf",
                "shipping_status": "shipped"
            }
        ]
        
        # Import the function to test
        from pet_adoption_agents.master_orchestrator.main import master_orchestrator
        
        # Test the function
        result = await master_orchestrator(
            mock_context,
            task="Promote 2 adoptable pets from ASPCA shelter NY114 with humorous adventure stories: Create a book, generate videos from real photos, and ship to donor at 123 Main St"
        )
        
        # Verify the result
        assert result is not None
        assert "workflow_completed" in result
        assert result["workflow_completed"] is True
        assert "pets_processed" in result
        assert result["pets_processed"] == 2
        
        # Verify all agent calls were made
        assert mock_session_obj.send.call_count == 4
        
        # Verify the calls were made with correct parameters
        calls = mock_session_obj.send.call_args_list
        
        # First call should be to data_fetcher
        assert calls[0][1]['client_id'] == 'fetcher_id'
        assert calls[0][1]['message']['shelter_name'] == 'ASPCA'
        assert calls[0][1]['message']['shelter_id'] == 'NY114'
        assert calls[0][1]['message']['num_pets'] == 2
        assert calls[0][1]['message']['include_photos'] is True
        
        # Second call should be to content_generator
        assert calls[1][1]['client_id'] == 'content_id'
        
        # Third call should be to asset_assembler
        assert calls[2][1]['client_id'] == 'asset_id'
        
        # Fourth call should be to book_shipper
        assert calls[3][1]['client_id'] == 'shipper_id'

@pytest.mark.asyncio
async def test_pet_updates_mock():
    """Test pet_updates function with mocked dependencies"""
    
    # Mock the session and context
    mock_session = MagicMock()
    mock_context = MagicMock()
    
    # Mock external dependencies
    with patch('requests.get') as mock_get, \
         patch('pet_adoption_agents.master_orchestrator.main.session') as mock_session_obj:
        
        # Setup mock responses
        mock_get.return_value.json.return_value = {
            'active_connections': [
                {'name': 'content_generator', 'id': 'content_id'},
                {'name': 'asset_assembler', 'id': 'asset_id'}
            ]
        }
        
        # Mock session.send calls
        mock_session_obj.send = AsyncMock()
        mock_session_obj.send.side_effect = [
            # Content generator response
            {
                "updated_stories": [
                    {"pet_id": 1, "story": "Updated Buddy's adventure story"}
                ]
            },
            # Asset assembler response
            {
                "updated_videos": [
                    {"pet_id": 1, "video_url": "http://example.com/updated_buddy_video.mp4"}
                ]
            }
        ]
        
        # Import the function to test
        from pet_adoption_agents.master_orchestrator.main import pet_updates
        
        # Test the function
        result = await pet_updates(
            mock_context,
            updates=[
                {
                    "pet_id": 1,
                    "name": "Buddy",
                    "status": "adopted",
                    "photos": ["http://example.com/new_buddy.jpg"]
                }
            ]
        )
        
        # Verify the result
        assert result is not None
        assert "updates_processed" in result
        assert result["updates_processed"] is True
        assert "pets_updated" in result
        assert result["pets_updated"] == 1
        
        # Verify agent calls were made
        assert mock_session_obj.send.call_count == 2

@pytest.mark.asyncio
async def test_task_parsing():
    """Test task parsing functionality"""
    
    # Mock the session and context
    mock_context = MagicMock()
    
    # Import the function to test
    from pet_adoption_agents.master_orchestrator.main import parse_task
    
    # Test task parsing
    task = "Promote 3 adoptable pets from ASPCA shelter NY114 with humorous adventure stories: Create a book, generate videos from real photos, and ship to donor at 123 Main St"
    
    result = parse_task(task)
    
    # Verify parsing results
    assert result["num_pets"] == 3
    assert result["shelter_name"] == "ASPCA"
    assert result["shelter_id"] == "NY114"
    assert result["content_style"] == "humorous adventure stories"
    assert result["create_book"] is True
    assert result["generate_videos"] is True
    assert result["ship_to_donor"] is True
    assert "123 Main St" in result["shipping_address"] 