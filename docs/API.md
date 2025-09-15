# TechFlow Voice Agent System - API Documentation

## Overview

The TechFlow Voice Agent System provides both REST API endpoints and WebSocket-based real-time communication for voice interaction capabilities.

## Base URL

```
http://localhost:5000
```

## Authentication

The system uses environment variables for API key management:
- `DEEPGRAM_API_KEY`: Required for voice processing capabilities

## REST API Endpoints

### 1. Home Page

**GET /**

Returns the main web interface for the voice agent system.

**Response:**
- **Content-Type:** `text/html`
- **Status:** 200 OK

**Example:**
```bash
curl http://localhost:5000/
```

### 2. Audio Devices

**GET /audio-devices**

Retrieves available audio input devices on the system.

**Response:**
```json
{
  "devices": [
    {
      "index": 0,
      "name": "Default Microphone"
    },
    {
      "index": 1,
      "name": "USB Microphone"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 500: Error accessing audio devices

**Example:**
```bash
curl http://localhost:5000/audio-devices
```

### 3. Industries

**GET /industries**

Returns available industry configurations for the voice agent.

**Response:**
```json
{
  "techflow": "TechFlow Solutions"
}
```

**Status Codes:**
- 200: Success

**Example:**
```bash
curl http://localhost:5000/industries
```

### 4. TTS Models

**GET /tts-models**

Fetches available Text-to-Speech models from Deepgram API.

**Response:**
```json
{
  "models": [
    {
      "name": "aura-2-thalia-en",
      "display_name": "Thalia",
      "language": "en",
      "accent": "American",
      "tags": "professional, clear",
      "description": "American accent. professional, clear"
    }
  ]
}
```

**Error Response:**
```json
{
  "error": "DEEPGRAM_API_KEY not set"
}
```

**Status Codes:**
- 200: Success
- 500: API key missing or Deepgram API error

**Example:**
```bash
curl http://localhost:5000/tts-models
```

## WebSocket Events

The system uses Socket.IO for real-time communication.

### Client to Server Events

#### 1. start_voice_agent

Starts a new voice agent session.

**Event:** `start_voice_agent`

**Payload:**
```json
{
  "industry": "techflow",
  "voiceModel": "aura-2-thalia-en",
  "voiceName": "Thalia",
  "browserAudio": true,
  "inputDeviceId": "default"
}
```

**Parameters:**
- `industry` (string): Industry configuration to use
- `voiceModel` (string): TTS model identifier
- `voiceName` (string): Display name for the voice
- `browserAudio` (boolean): Whether to use browser-based audio capture
- `inputDeviceId` (string): Audio input device identifier

#### 2. stop_voice_agent

Stops the current voice agent session.

**Event:** `stop_voice_agent`

**Payload:** None

#### 3. audio_data

Sends audio data from browser to the voice agent.

**Event:** `audio_data`

**Payload:**
```json
{
  "audio": "<binary_audio_data>",
  "sampleRate": 48000
}
```

**Parameters:**
- `audio` (binary): PCM audio data as Int16Array
- `sampleRate` (number): Sample rate of the audio data

### Server to Client Events

#### 1. conversation_update

Sends conversation updates to the client.

**Event:** `conversation_update`

**Payload:**
```json
{
  "role": "user|assistant",
  "content": "Message content",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. log_message

Sends system log messages to the client.

**Event:** `log_message`

**Payload:**
```json
{
  "message": "Log message with ANSI colors",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 3. audio_output

Sends audio output to the browser for playback.

**Event:** `audio_output`

**Payload:**
```json
{
  "audio": "<binary_audio_data>",
  "sampleRate": 16000
}
```

## Voice Agent Functions

The voice agent supports the following function calls through natural language:

### Customer Management

#### find_customer

Looks up customer information by phone, email, or ID.

**Parameters:**
- `customer_id` (string): Customer ID in CUSTXXXX format
- `phone` (string): Phone number with country code (+1XXXXXXXXXX)
- `email` (string): Email address

**Example Usage:**
- "Find customer with ID 123"
- "Look up customer with phone 555-123-4567"
- "Find customer john.doe@example.com"

#### create_customer_account

Creates a new customer account.

**Parameters:**
- `name` (string): Customer's full name
- `phone` (string): Phone number in international format
- `email` (string): Email address

**Example Usage:**
- "I need to create a new account"
- "Can you set up an account for me?"

### Appointment Management

#### get_appointments

Retrieves customer appointments.

**Parameters:**
- `customer_id` (string): Customer ID

**Example Usage:**
- "When is my next appointment?"
- "Show me my appointments"

#### create_appointment

Schedules a new appointment.

**Parameters:**
- `customer_id` (string): Customer ID
- `date` (string): Appointment date/time in ISO format
- `service` (string): Service type (Consultation, Follow-up, Review, Planning)

**Example Usage:**
- "I want to schedule a consultation"
- "Book me an appointment for next Tuesday"

#### reschedule_appointment

Reschedules an existing appointment.

**Parameters:**
- `appointment_id` (string): Appointment ID
- `new_date` (string): New date/time in ISO format
- `new_service` (string): Service type

**Example Usage:**
- "I need to reschedule my appointment"
- "Can we move my meeting to Thursday?"

#### cancel_appointment

Cancels an existing appointment.

**Parameters:**
- `appointment_id` (string): Appointment ID

**Example Usage:**
- "I need to cancel my appointment"
- "Please cancel my meeting"

#### check_availability

Checks available appointment slots.

**Parameters:**
- `start_date` (string): Start date for availability check
- `end_date` (string, optional): End date (defaults to 7 days after start)

**Example Usage:**
- "What times are available this week?"
- "When can I come in?"

### Order Management

#### get_orders

Retrieves customer order history.

**Parameters:**
- `customer_id` (string): Customer ID

**Example Usage:**
- "Check my order status"
- "What orders do I have?"

### Knowledge Base

#### search_knowledge_base

Searches TechFlow knowledge base.

**Parameters:**
- `query` (string): Search query

**Example Usage:**
- "What does TechFlow do?"
- "Tell me about your services"

#### get_knowledge_base_topics

Gets all available knowledge base topics.

**Example Usage:**
- "What topics can you tell me about?"
- "What information do you have?"

#### get_knowledge_base_entry

Gets specific knowledge base entry.

**Parameters:**
- `topic` (string): Topic name
- `title` (string): Entry title

**Example Usage:**
- "Tell me about the leadership team"
- "What are your key services?"

### Utility Functions

#### agent_filler

Provides conversational filler while processing.

**Parameters:**
- `message_type` (string): Type of filler message

#### end_call

Ends the conversation.

**Parameters:**
- `farewell_type` (string): Type of farewell (thanks, general, help)

**Example Usage:**
- "Thank you, goodbye"
- "That's all I need"

## Error Handling

### HTTP Error Responses

All API endpoints return appropriate HTTP status codes:

- **200 OK**: Successful request
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Missing or invalid API key
- **404 Not Found**: Endpoint not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### WebSocket Error Handling

WebSocket errors are handled gracefully with automatic reconnection attempts and error logging.

## Rate Limiting

Currently, no rate limiting is implemented, but it's recommended for production deployments.

## Data Formats

### Date/Time Format

All date/time values use ISO 8601 format:
```
2024-01-15T14:30:00
```

### Phone Number Format

Phone numbers should be in international format:
```
+15551234567
```

### Customer ID Format

Customer IDs follow the pattern:
```
CUSTXXXX (e.g., CUST0001)
```

### Appointment ID Format

Appointment IDs follow the pattern:
```
APTXXXX (e.g., APT0001)
```

### Order ID Format

Order IDs follow the pattern:
```
ORDXXXX (e.g., ORD0001)
```

## Audio Specifications

### Input Audio

- **Format**: Linear PCM
- **Sample Rate**: 48kHz (browser) → 16kHz (processing)
- **Channels**: Mono (1 channel)
- **Bit Depth**: 16-bit
- **Encoding**: Int16 array

### Output Audio

- **Format**: Linear PCM
- **Sample Rate**: 16kHz
- **Channels**: Mono (1 channel)
- **Bit Depth**: 16-bit
- **Container**: Raw audio data

## Business Rules

### Appointment Scheduling

- **Business Hours**: 9 AM - 5 PM
- **Days**: Monday - Friday (weekdays only)
- **Time Slots**: 1-hour intervals
- **Advance Booking**: Must be scheduled in the future
- **Conflict Prevention**: No double-booking allowed

### Customer Data

- **ID Generation**: Automatic sequential numbering
- **Phone Validation**: International format required
- **Email Validation**: Basic format checking
- **Duplicate Prevention**: Phone and email uniqueness enforced

## Integration Examples

### JavaScript Client

```javascript
// Connect to Socket.IO
const socket = io();

// Start voice agent
socket.emit('start_voice_agent', {
  industry: 'techflow',
  voiceModel: 'aura-2-thalia-en',
  browserAudio: true
});

// Listen for conversation updates
socket.on('conversation_update', (data) => {
  console.log(`${data.role}: ${data.content}`);
});

// Send audio data
socket.emit('audio_data', {
  audio: audioBuffer,
  sampleRate: 48000
});
```

### Python Client

```python
import socketio
import requests

# REST API call
response = requests.get('http://localhost:5000/industries')
industries = response.json()

# Socket.IO client
sio = socketio.Client()

@sio.on('conversation_update')
def on_conversation_update(data):
    print(f"{data['role']}: {data['content']}")

sio.connect('http://localhost:5000')
sio.emit('start_voice_agent', {
    'industry': 'techflow',
    'voiceModel': 'aura-2-thalia-en'
})
```

## Security Considerations

- **API Keys**: Store securely in environment variables
- **Input Validation**: All user inputs are validated
- **Audio Data**: Processed securely and not permanently stored
- **WebSocket Security**: Use WSS in production
- **CORS**: Configure appropriately for production

## Monitoring and Logging

The system provides comprehensive logging:

- **Request Logging**: All HTTP requests logged
- **WebSocket Events**: Connection and message logging
- **Function Calls**: Voice agent function execution logging
- **Error Tracking**: Detailed error logging with stack traces
- **Performance Metrics**: Latency tracking for operations

## Development and Testing

### Mock Data

The system includes comprehensive mock data for testing:
- 1000 sample customers
- 500 sample appointments
- 2000 sample orders

### Test Endpoints

Use the following for testing:
- Customer ID: `CUST0001`
- Phone: `+15551234567`
- Email: `customer0@example.com`

For more information, see the [Contributing Guide](../CONTRIBUTING.md) and [README](../README.md).