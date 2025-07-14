import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from main import master_orchestrator, get_active_agents, get_agent_id


class MockContext:
    def __init__(self):
        self.logger = MagicMock()


@pytest.mark.asyncio
async def test_master_orchestrator_with_humor():
    """Test master_orchestrator with humorous task parsing"""
    mock_context = MockContext()
    task = "Promote 2 adoptable pets from ASPCA shelter NY114 with humorous adventure stories: Create a book, generate videos from real photos, and ship to donor at 123 Main St"
    
    with patch('main.get_active_agents') as mock_get_agents, \
         patch('main.session.send') as mock_send:
        
        # Mock active agents
        mock_get_agents.return_value = [
            {'name': 'data_fetcher', 'id': 'fetcher_id'},
            {'name': 'content_generator', 'id': 'generator_id'},
            {'name': 'asset_assembler', 'id': 'assembler_id'},
            {'name': 'book_shipper', 'id': 'shipper_id'}
        ]
        
        # Mock agent responses
        mock_send.side_effect = [
            AsyncMock(response=[{'name': 'Pet1', 'photos': ['http://photo1.jpg']}]),  # fetcher
            AsyncMock(response={'stories': [{'pet': 'Pet1', 'story': 'Funny story'}]}),  # generator
            AsyncMock(response={'book_file': 'book.pdf'}),  # assembler
            AsyncMock(response={'status': 'shipped'})  # shipper
        ]
        
        result = await master_orchestrator(mock_context, task)
        
        # Verify workflow completion
        assert 'status' in result
        assert result['status'] == 'completed'
        
        # Verify all 4 agents were called
        assert mock_send.call_count == 4
        
        # Verify content_generator was called with humorous=True
        generator_call = mock_send.call_args_list[1]
        assert generator_call[1]['client_id'] == 'generator_id'
        assert generator_call[1]['message']['humorous'] is True
        assert 'pets' in generator_call[1]['message']


@pytest.mark.asyncio
async def test_master_orchestrator_without_humor():
    """Test master_orchestrator without humor flag"""
    mock_context = MockContext()
    task = "Promote 2 adoptable pets from ASPCA shelter NY114 with adventure stories: Create a book, generate videos from real photos, and ship to donor at 123 Main St"
    
    with patch('main.get_active_agents') as mock_get_agents, \
         patch('main.session.send') as mock_send:
        
        # Mock active agents
        mock_get_agents.return_value = [
            {'name': 'data_fetcher', 'id': 'fetcher_id'},
            {'name': 'content_generator', 'id': 'generator_id'},
            {'name': 'asset_assembler', 'id': 'assembler_id'},
            {'name': 'book_shipper', 'id': 'shipper_id'}
        ]
        
        # Mock agent responses
        mock_send.side_effect = [
            AsyncMock(response=[{'name': 'Pet1', 'photos': ['http://photo1.jpg']}]),  # fetcher
            AsyncMock(response={'stories': [{'pet': 'Pet1', 'story': 'Regular story'}]}),  # generator
            AsyncMock(response={'book_file': 'book.pdf'}),  # assembler
            AsyncMock(response={'status': 'shipped'})  # shipper
        ]
        
        result = await master_orchestrator(mock_context, task)
        
        # Verify workflow completion
        assert 'status' in result
        assert result['status'] == 'completed'
        
        # Verify content_generator was called with humorous=False
        generator_call = mock_send.call_args_list[1]
        assert generator_call[1]['client_id'] == 'generator_id'
        assert generator_call[1]['message']['humorous'] is False


@pytest.mark.asyncio
async def test_master_orchestrator_invalid_task():
    """Test master_orchestrator with invalid task format"""
    mock_context = MockContext()
    task = "Invalid task format"
    
    result = await master_orchestrator(mock_context, task)
    
    assert 'error' in result
    assert result['error'] == 'Invalid task format'


@pytest.mark.asyncio
async def test_get_active_agents():
    """Test get_active_agents function"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'active_connections': [
                {'name': 'agent1', 'id': 'id1'},
                {'name': 'agent2', 'id': 'id2'}
            ]
        }
        mock_get.return_value = mock_response
        
        result = await get_active_agents()
        
        assert len(result) == 2
        assert result[0]['name'] == 'agent1'
        assert result[1]['name'] == 'agent2'


@pytest.mark.asyncio
async def test_get_active_agents_failure():
    """Test get_active_agents with API failure"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Server error'
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            await get_active_agents()
        
        assert 'Failed to get active agents' in str(exc_info.value)


def test_get_agent_id():
    """Test get_agent_id function"""
    agents = [
        {'name': 'agent1', 'id': 'id1'},
        {'name': 'agent2', 'id': 'id2'}
    ]
    
    result = get_agent_id(agents, 'agent1')
    assert result == 'id1'
    
    result = get_agent_id(agents, 'agent2')
    assert result == 'id2'


def test_get_agent_id_not_found():
    """Test get_agent_id with non-existent agent"""
    agents = [
        {'name': 'agent1', 'id': 'id1'},
        {'name': 'agent2', 'id': 'id2'}
    ]
    
    with pytest.raises(Exception) as exc_info:
        get_agent_id(agents, 'nonexistent')
    
    assert 'Agent nonexistent not found' in str(exc_info.value)


def test_humor_detection():
    """Test humor detection in task parsing"""
    # Test cases for humor detection
    test_cases = [
        ("Promote 2 pets with humorous stories", True),
        ("Promote 2 pets with HUMOROUS stories", True),
        ("Promote 2 pets with funny stories", False),  # Only "humorous" triggers the flag
        ("Promote 2 pets with adventure stories", False),
        ("Promote 2 pets with humorous adventure stories", True),
    ]
    
    for task, expected_humor in test_cases:
        humor_detected = "humorous" in task.lower()
        assert humor_detected == expected_humor, f"Failed for task: {task}"


if __name__ == '__main__':
    pytest.main([__file__]) 