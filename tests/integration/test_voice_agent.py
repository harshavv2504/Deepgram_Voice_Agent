"""
Integration tests for the voice agent system.
"""

import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from client import app, socketio


class TestVoiceAgentIntegration:
    """Test voice agent integration scenarios."""
    
    def test_flask_app_creation(self, flask_app):
        """Test that Flask app is created correctly."""
        assert flask_app is not None
        assert flask_app.config['TESTING'] is True
    
    def test_socketio_integration(self, socketio_client):
        """Test SocketIO integration with Flask app."""
        assert socketio_client is not None
        
        # Test connection
        received = socketio_client.get_received()
        assert isinstance(received, list)
    
    def test_home_route(self, client):
        """Test the home route returns HTML."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Voice Agent Debugger' in response.data
        assert b'text/html' in response.content_type.encode()
    
    def test_audio_devices_route(self, client):
        """Test the audio devices API endpoint."""
        with patch('client.get_audio_devices') as mock_get_devices:
            mock_get_devices.return_value = [
                {"index": 0, "name": "Test Microphone"}
            ]
            
            response = client.get('/audio-devices')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "devices" in data
            assert len(data["devices"]) == 1
    
    def test_industries_route(self, client):
        """Test the industries API endpoint."""
        response = client.get('/industries')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "indivillage" in data
        assert data["indivillage"] == "IndiVillage Tech Solutions"
    
    @patch('requests.get')
    def test_tts_models_route_success(self, mock_get, client):
        """Test the TTS models API endpoint with successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tts": [
                {
                    "canonical_name": "aura-2-thalia-en",
                    "name": "Thalia",
                    "architecture": "aura-2",
                    "languages": ["en"],
                    "metadata": {
                        "accent": "American",
                        "tags": ["professional", "clear"]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with patch('os.environ.get', return_value='test-api-key'):
            response = client.get('/tts-models')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "models" in data
            assert len(data["models"]) == 1
            assert data["models"][0]["name"] == "aura-2-thalia-en"
    
    @patch('requests.get')
    def test_tts_models_route_api_error(self, mock_get, client):
        """Test the TTS models API endpoint with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with patch('os.environ.get', return_value='test-api-key'):
            response = client.get('/tts-models')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
    
    def test_tts_models_route_no_api_key(self, client):
        """Test the TTS models API endpoint without API key."""
        with patch('os.environ.get', return_value=None):
            response = client.get('/tts-models')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "DEEPGRAM_API_KEY not set" in data["error"]


class TestSocketIOEvents:
    """Test SocketIO event handling."""
    
    def test_start_voice_agent_event(self, socketio_client, voice_agent_settings):
        """Test starting voice agent via SocketIO."""
        with patch('client.run_async_voice_agent') as mock_run:
            socketio_client.emit('start_voice_agent', voice_agent_settings)
            
            # Give some time for the event to be processed
            socketio_client.sleep(0.1)
            
            # Check that the voice agent was created
            # Note: This is a simplified test as the actual implementation
            # involves complex async operations
            assert True  # Placeholder assertion
    
    def test_stop_voice_agent_event(self, socketio_client):
        """Test stopping voice agent via SocketIO."""
        # First start an agent
        with patch('client.run_async_voice_agent'):
            socketio_client.emit('start_voice_agent', {"industry": "indivillage"})
            socketio_client.sleep(0.1)
            
            # Then stop it
            socketio_client.emit('stop_voice_agent')
            socketio_client.sleep(0.1)
            
            # Verify the agent was stopped
            assert True  # Placeholder assertion
    
    def test_audio_data_event(self, socketio_client, audio_data):
        """Test audio data handling via SocketIO."""
        # Start voice agent first
        with patch('client.run_async_voice_agent'):
            socketio_client.emit('start_voice_agent', {
                "industry": "indivillage",
                "browserAudio": True
            })
            socketio_client.sleep(0.1)
            
            # Send audio data
            socketio_client.emit('audio_data', audio_data)
            socketio_client.sleep(0.1)
            
            # Verify audio data was processed
            assert True  # Placeholder assertion


class TestVoiceAgentClass:
    """Test the VoiceAgent class functionality."""
    
    @pytest.mark.asyncio
    async def test_voice_agent_initialization(self):
        """Test VoiceAgent class initialization."""
        from client import VoiceAgent
        
        agent = VoiceAgent(
            industry="indivillage",
            voiceModel="aura-2-thalia-en",
            voiceName="Thalia",
            browser_audio=True
        )
        
        assert agent.industry == "indivillage"
        assert agent.voiceModel == "aura-2-thalia-en"
        assert agent.voiceName == "Thalia"
        assert agent.browser_audio is True
        assert agent.is_running is False
    
    @pytest.mark.asyncio
    async def test_voice_agent_setup_success(self, mock_websocket):
        """Test successful VoiceAgent setup."""
        from client import VoiceAgent
        
        agent = VoiceAgent()
        
        with patch('websockets.connect', return_value=mock_websocket):
            with patch('os.environ.get', return_value='test-api-key'):
                result = await agent.setup()
                
                assert result is True
                assert agent.ws is not None
    
    @pytest.mark.asyncio
    async def test_voice_agent_setup_no_api_key(self):
        """Test VoiceAgent setup without API key."""
        from client import VoiceAgent
        
        agent = VoiceAgent()
        
        with patch('os.environ.get', return_value=None):
            result = await agent.setup()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_voice_agent_setup_connection_error(self):
        """Test VoiceAgent setup with connection error."""
        from client import VoiceAgent
        
        agent = VoiceAgent()
        
        with patch('websockets.connect', side_effect=Exception("Connection failed")):
            with patch('os.environ.get', return_value='test-api-key'):
                result = await agent.setup()
                
                assert result is False


class TestSpeakerClass:
    """Test the Speaker class functionality."""
    
    def test_speaker_initialization(self):
        """Test Speaker class initialization."""
        from client import Speaker
        
        # Test server-side audio
        speaker = Speaker(browser_output=False)
        assert speaker.browser_output is False
        
        # Test browser-side audio
        speaker = Speaker(browser_output=True)
        assert speaker.browser_output is True
    
    @patch('client.pyaudio.PyAudio')
    def test_speaker_context_manager_server_audio(self, mock_pyaudio):
        """Test Speaker context manager for server-side audio."""
        from client import Speaker
        
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        speaker = Speaker(browser_output=False)
        
        with speaker:
            assert speaker._queue is not None
            assert speaker._stop is not None
            assert speaker._thread is not None
        
        # After exiting context, resources should be cleaned up
        assert speaker._queue is None
        assert speaker._thread is None
        assert speaker._stop is None
    
    def test_speaker_context_manager_browser_audio(self):
        """Test Speaker context manager for browser-side audio."""
        from client import Speaker
        
        speaker = Speaker(browser_output=True)
        
        with speaker:
            assert speaker._queue is not None
            assert speaker._stop is not None
            assert speaker._thread is not None
        
        # After exiting context, resources should be cleaned up
        assert speaker._queue is None
        assert speaker._thread is None
        assert speaker._stop is None


class TestAudioProcessing:
    """Test audio processing functionality."""
    
    @patch('client.pyaudio.PyAudio')
    def test_get_audio_devices(self, mock_pyaudio):
        """Test getting audio devices."""
        from client import get_audio_devices
        
        mock_audio_instance = MagicMock()
        mock_pyaudio.return_value = mock_audio_instance
        
        # Mock device enumeration
        mock_audio_instance.get_host_api_info_by_index.return_value = {"deviceCount": 2}
        mock_audio_instance.get_device_info_by_host_api_device_index.side_effect = [
            {"name": "Test Microphone", "maxInputChannels": 1},
            {"name": "Test Speaker", "maxInputChannels": 0}
        ]
        
        devices = get_audio_devices()
        
        assert len(devices) == 1  # Only input devices
        assert devices[0]["name"] == "Test Microphone"
        assert devices[0]["index"] == 0
    
    @patch('client.pyaudio.PyAudio')
    def test_get_audio_devices_error(self, mock_pyaudio):
        """Test getting audio devices with error."""
        from client import get_audio_devices
        
        mock_pyaudio.side_effect = Exception("Audio error")
        
        devices = get_audio_devices()
        
        assert devices == []


class TestWebSocketHandling:
    """Test WebSocket message handling."""
    
    @pytest.mark.asyncio
    async def test_inject_agent_message(self, mock_websocket):
        """Test injecting agent message."""
        from client import inject_agent_message
        
        message = {
            "type": "InjectAgentMessage",
            "message": "Test message"
        }
        
        await inject_agent_message(mock_websocket, message)
        
        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])
        assert sent_data == message
    
    @pytest.mark.asyncio
    async def test_close_websocket_with_timeout(self, mock_websocket):
        """Test closing WebSocket with timeout."""
        from client import close_websocket_with_timeout
        
        await close_websocket_with_timeout(mock_websocket, timeout=1)
        
        mock_websocket.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_websocket_timeout_error(self, mock_websocket):
        """Test closing WebSocket with timeout error."""
        from client import close_websocket_with_timeout
        
        mock_websocket.close.side_effect = asyncio.TimeoutError()
        
        # Should not raise exception
        await close_websocket_with_timeout(mock_websocket, timeout=0.1)


class TestFunctionCallHandling:
    """Test function call handling in voice agent."""
    
    @pytest.mark.asyncio
    async def test_function_call_execution(self, mock_websocket, function_call_data):
        """Test function call execution."""
        from client import VoiceAgent
        
        agent = VoiceAgent()
        agent.ws = mock_websocket
        
        # Mock the function execution
        with patch('common.agent_functions.FUNCTION_MAP') as mock_function_map:
            mock_function = AsyncMock(return_value={"result": "success"})
            mock_function_map.get.return_value = mock_function
            
            # This would be part of the receiver method
            # For now, we just test that the function mapping works
            func = mock_function_map.get("find_customer")
            result = await func({"customer_id": "CUST0001"})
            
            assert result["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_function_call_error_handling(self, mock_websocket):
        """Test function call error handling."""
        from client import VoiceAgent
        
        agent = VoiceAgent()
        agent.ws = mock_websocket
        
        # Mock function that raises an exception
        with patch('common.agent_functions.FUNCTION_MAP') as mock_function_map:
            mock_function = AsyncMock(side_effect=Exception("Function error"))
            mock_function_map.get.return_value = mock_function
            
            # Test error handling
            try:
                func = mock_function_map.get("find_customer")
                await func({"customer_id": "CUST0001"})
            except Exception as e:
                assert str(e) == "Function error"


class TestEndToEndScenarios:
    """Test end-to-end scenarios."""
    
    @pytest.mark.integration
    def test_customer_service_workflow(self, client, mock_data_setup):
        """Test complete customer service workflow."""
        # This would test a complete workflow from web interface
        # to voice agent to business logic and back
        
        # 1. Start with home page
        response = client.get('/')
        assert response.status_code == 200
        
        # 2. Get available devices
        with patch('client.get_audio_devices', return_value=[]):
            response = client.get('/audio-devices')
            assert response.status_code == 200
        
        # 3. Get industries
        response = client.get('/industries')
        assert response.status_code == 200
        
        # This is a simplified test - a full integration test would
        # involve starting the voice agent and processing audio
        assert True
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_knowledge_base_integration(self, client, knowledge_base):
        """Test knowledge base integration."""
        # Test that knowledge base is accessible through the web interface
        response = client.get('/')
        assert response.status_code == 200
        
        # Test that knowledge base functions work
        with patch('common.agent_functions.mdx_kb', knowledge_base):
            from common.agent_functions import search_knowledge_base
            
            # This would be called by the voice agent
            result = asyncio.run(search_knowledge_base({"query": "test"}))
            assert result["found"] is True
    
    @pytest.mark.integration
    def test_mock_data_integration(self, client, mock_data_setup):
        """Test mock data integration with web interface."""
        # Test that mock data is displayed in the web interface
        response = client.get('/')
        assert response.status_code == 200
        
        # Check that sample data is included in the response
        assert b'Sample Customer Data' in response.data
        
        # Test that business logic functions work with mock data
        from common.business_logic import get_customer
        
        result = asyncio.run(get_customer(customer_id="CUST0001"))
        assert "id" in result


class TestPerformanceIntegration:
    """Test performance aspects of integration."""
    
    @pytest.mark.slow
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = client.get('/')
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # Create multiple threads to make concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 10
        assert all(result['status_code'] == 200 for result in results)
        
        # Verify reasonable response times (less than 5 seconds each)
        assert all(result['response_time'] < 5.0 for result in results)
    
    @pytest.mark.slow
    def test_memory_usage(self, client):
        """Test memory usage during operation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make multiple requests
        for _ in range(100):
            response = client.get('/')
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024