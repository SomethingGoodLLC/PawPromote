import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_fetch_pets_mock():
    """Test data fetcher fetch_pets function with mocked dependencies"""
    
    # Mock the session and context
    mock_session = MagicMock()
    mock_context = MagicMock()
    
    # Mock external dependencies
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('impyla.dbapi.connect') as mock_connect, \
         patch('asyncio.create_task') as mock_create_task:
        
        # Setup mock responses
        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_get.return_value.json.return_value = {
            "animals": [
                {
                    "id": 1,
                    "name": "Buddy",
                    "description": "Friendly dog",
                    "photos": [{"full": "http://example.com/buddy.jpg"}],
                    "status": "adoptable"
                },
                {
                    "id": 2,
                    "name": "Whiskers",
                    "description": "Playful cat",
                    "photos": [{"full": "http://example.com/whiskers.jpg"}],
                    "status": "adoptable"
                }
            ]
        }
        
        # Mock Impala connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Buddy", "Friendly dog", "http://example.com/buddy.jpg", "adoptable"),
            (2, "Whiskers", "Playful cat", "http://example.com/whiskers.jpg", "adoptable")
        ]
        mock_connect.return_value.cursor.return_value = mock_cursor
        
        # Mock the async task
        mock_create_task.return_value = AsyncMock()
        
        # Import the function to test
        from pet_adoption_agents.data_fetcher.main import fetch_pets
        
        # Test the function
        result = await fetch_pets(
            mock_context,
            shelter_name="Test Shelter",
            shelter_id="TEST123",
            num_pets=2,
            include_photos=True
        )
        
        # Verify the result
        assert result is not None
        assert "pets" in result
        assert len(result["pets"]) == 2
        assert result["pets"][0]["name"] == "Buddy"
        assert result["pets"][1]["name"] == "Whiskers"
        
        # Verify API calls were made
        mock_post.assert_called_once()  # Petfinder auth
        mock_get.assert_called_once()   # Petfinder API call

@pytest.mark.asyncio 
async def test_fetch_pets_with_fallback():
    """Test data fetcher with photo fallback scraping"""
    
    # Mock the session and context
    mock_session = MagicMock()
    mock_context = MagicMock()
    
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('bs4.BeautifulSoup') as mock_soup, \
         patch('impyla.dbapi.connect') as mock_connect:
        
        # Setup mock responses - no photos in API response
        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_get.return_value.json.return_value = {
            "animals": [
                {
                    "id": 1,
                    "name": "Buddy",
                    "description": "Friendly dog",
                    "photos": [],  # No photos
                    "status": "adoptable",
                    "url": "http://example.com/buddy"
                }
            ]
        }
        
        # Mock web scraping fallback
        mock_soup_instance = MagicMock()
        mock_soup_instance.find_all.return_value = [
            MagicMock(get=lambda x: "http://example.com/scraped_buddy.jpg")
        ]
        mock_soup.return_value = mock_soup_instance
        
        # Mock Impala connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor
        
        # Import the function to test
        from pet_adoption_agents.data_fetcher.main import fetch_pets
        
        # Test the function
        result = await fetch_pets(
            mock_context,
            shelter_name="Test Shelter", 
            shelter_id="TEST123",
            num_pets=1,
            include_photos=True
        )
        
        # Verify fallback scraping was used
        assert result is not None
        assert "pets" in result
        assert len(result["pets"]) == 1
        assert result["pets"][0]["name"] == "Buddy"
        # Should have scraped photo
        assert "http://example.com/scraped_buddy.jpg" in result["pets"][0]["photos"]

@pytest.mark.asyncio
async def test_impala_query():
    """Test Impala database query functionality"""
    
    with patch('impyla.dbapi.connect') as mock_connect:
        
        # Mock Impala connection and cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Buddy", "Friendly dog", "http://example.com/buddy.jpg", "adoptable"),
            (2, "Whiskers", "Playful cat", "http://example.com/whiskers.jpg", "adopted")
        ]
        mock_connect.return_value.cursor.return_value = mock_cursor
        
        # Import the function to test
        from pet_adoption_agents.data_fetcher.main import query_impala_pets
        
        # Test the function
        result = query_impala_pets()
        
        # Verify the result
        assert len(result) == 2
        assert result[0]["name"] == "Buddy"
        assert result[0]["status"] == "adoptable"
        assert result[1]["name"] == "Whiskers"
        assert result[1]["status"] == "adopted"
        
        # Verify database query was executed
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once() 