# TechFlow Voice Agent System

A sophisticated AI-powered voice agent system built for TechFlow Solutions, combining real-time voice interaction with comprehensive business logic for customer service, appointment scheduling, and knowledge base queries.

## 🎯 Project Overview

This is a **Flask-based voice agent application** that provides:
- **Real-time voice conversations** using Deepgram's Voice Agent API
- **Intelligent customer service** with appointment and order management
- **Knowledge base integration** for TechFlow company information
- **Web-based interface** for testing and debugging voice interactions
- **Automatic meeting scheduling** with email and calendar integration

## 🏗️ Architecture

### Core Components

1. **Voice Agent Engine** (`client.py`)
   - Flask web server with SocketIO for real-time communication
   - WebSocket connection to Deepgram Voice Agent API
   - Audio processing pipeline for browser-based microphone input
   - Real-time audio streaming and playback

2. **Business Logic Layer** (`common/business_logic.py`)
   - Customer management (CRUD operations)
   - Appointment scheduling and management
   - Order tracking and status updates
   - Mock data generation and persistence
   - Automatic meeting invite system

3. **Agent Functions** (`common/agent_functions.py`)
   - Function definitions for voice agent capabilities
   - Customer lookup and account management
   - Appointment operations (create, reschedule, cancel)
   - Knowledge base search and retrieval
   - Account creation with transcription accuracy handling

4. **Knowledge Base System** (`knowledgebase/`)
   - MDX-based knowledge management
   - Fuzzy search capabilities
   - Company information, services, and FAQ storage
   - Dynamic content retrieval for voice responses

5. **Web Interface** (`templates/index.html`)
   - Real-time conversation display
   - Audio device selection and configuration
   - Voice model selection (Deepgram TTS models)
   - Debug logging and system monitoring

## 🚀 Key Features

### Voice Interaction
- **Natural Language Processing**: Understands customer intents and requests
- **Real-time Audio**: Browser-based microphone input with WebSocket streaming
- **Multiple Voice Models**: Support for various Deepgram TTS voices
- **Conversation Management**: Maintains context throughout interactions

### Customer Service Capabilities
- **Customer Lookup**: Find customers by phone, email, or ID
- **Appointment Management**: Schedule, reschedule, and cancel appointments
- **Order Tracking**: Check order status and history
- **Account Creation**: Create new customer accounts with validation
- **Availability Checking**: Real-time appointment slot availability

### Knowledge Base Integration
- **Company Information**: Comprehensive TechFlow company data
- **Service Details**: Information about AI and customer service solutions
- **Leadership Team**: Executive and board member information
- **Client Collaborations**: Partnership and client success stories
- **Technology Innovation**: AI advancement and community initiatives

### Business Intelligence
- **Mock Data System**: Generates realistic customer, appointment, and order data
- **Data Persistence**: Maintains data consistency across sessions
- **Automatic Scheduling**: Integrates with Google Calendar and Gmail
- **Performance Tracking**: Latency monitoring and system metrics

## 📋 Prerequisites

- **Python 3.12+**
- **Deepgram API Key** (for voice processing)
- **Google API Credentials** (for calendar/email integration)
- **Modern web browser** with microphone support

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice-agent-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   ```

4. **Configure Google API credentials** (optional)
   - Place `credentials.json` in the `common/` directory
   - Required for automatic meeting scheduling

## 🚀 Usage

### Starting the Application

```bash
python client.py
```

The application will start on `http://localhost:5000`

### Web Interface

1. **Open your browser** and navigate to `http://localhost:5000`
2. **Select audio devices** and voice model preferences
3. **Click "Start Voice Agent"** to begin voice interaction
4. **Grant microphone permissions** when prompted
5. **Start speaking** to interact with the voice agent

### Voice Commands Examples

#### Customer Service
- *"I need to check my order"*
- *"When is my next appointment?"*
- *"I want to schedule a consultation"*
- *"Can you reschedule my meeting?"*
- *"I need to create a new account"*

#### TechFlow Information
- *"What does TechFlow do?"*
- *"Tell me about your services"*
- *"Who is the leadership team?"*
- *"What is your technology focus?"*
- *"How can TechFlow help my business?"*

## 🏢 Business Logic

### Customer Management
- **Unique ID Generation**: Automatic customer ID assignment (CUST0001, CUST0002, etc.)
- **Data Validation**: Phone number and email format validation
- **Duplicate Prevention**: Checks for existing customers before creation

### Appointment System
- **Business Hours**: 9 AM - 5 PM, weekdays only
- **Conflict Detection**: Prevents double-booking of time slots
- **Automatic Notifications**: Email and calendar invites sent automatically
- **Status Tracking**: Scheduled, Completed, Cancelled status management

### Order Management
- **Order Tracking**: Real-time status updates
- **Customer Association**: Links orders to customer accounts
- **Historical Data**: Maintains order history and analytics

## 🧠 AI Agent Capabilities

### Function Selection Intelligence
The agent intelligently chooses between two function types:

1. **Knowledge Base Functions** - For TechFlow company questions
2. **Customer Service Functions** - For operational tasks

### Conversation Management
- **Context Awareness**: Maintains conversation context
- **Intent Recognition**: Understands customer needs and goals
- **Service Matching**: Connects customer problems to TechFlow solutions
- **Consultation Guidance**: Knows when to offer business consultations

### Transcription Accuracy
- **Spelling Assistance**: Asks customers to spell details for accuracy
- **Format Conversion**: Automatically formats phone numbers and IDs
- **Validation**: Confirms information before processing

## 📊 Data Management

### Mock Data System
- **Realistic Data**: Generates 1000 customers, 500 appointments, 2000 orders
- **Relationship Integrity**: Maintains proper data relationships
- **Persistence**: Saves data to `mock_data_outputs/mock_data.json`
- **Sample Display**: Shows representative data in web interface

### Data Validation
- **Integrity Checks**: Validates data consistency
- **Duplicate Detection**: Identifies and prevents duplicate records
- **Orphan Prevention**: Ensures referential integrity

## 🔧 Configuration

### Audio Settings
- **Input Sample Rate**: 48kHz (browser) → 16kHz (processing)
- **Audio Format**: Linear16 PCM
- **Buffer Size**: 4096 samples
- **Device Selection**: Multiple input device support

### Voice Models
- **Deepgram Integration**: Automatic TTS model loading
- **Voice Selection**: Multiple voice personalities available
- **Language Support**: Primarily English with accent variations

### Business Rules
- **Appointment Hours**: 9 AM - 5 PM, Monday-Friday
- **ID Formats**: CUST#### for customers, APT#### for appointments, ORD#### for orders
- **Phone Format**: International format with +1 country code

## 🐳 Docker Support

```bash
# Build the Docker image
docker build -t voice-agent-system .

# Run the container
docker run -p 5000:5000 -e DEEPGRAM_API_KEY=your_key voice-agent-system
```

## 📁 Project Structure

```
├── client.py                 # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── common/                  # Core business logic
│   ├── agent_functions.py   # Voice agent function definitions
│   ├── agent_templates.py   # Agent personality and prompts
│   ├── business_logic.py    # Customer/appointment/order management
│   ├── config.py           # Application configuration
│   ├── log_formatter.py    # Custom logging formatter
│   ├── meeting_modular.py  # Calendar/email integration
│   └── prompt_templates.py # AI prompt templates
├── knowledgebase/          # Knowledge management system
│   ├── mdx_handler.py      # MDX file processing
│   ├── knowledge_base.json # Structured knowledge data
│   └── mdx/               # Company information files
├── templates/             # Web interface
│   └── index.html        # Main web application
├── static/               # Web assets
│   ├── style.css        # Application styling
│   └── syncscroll.js    # Synchronized scrolling
└── mock_data_outputs/   # Generated data storage
```

## 🔍 Debugging and Monitoring

### Web Interface Features
- **Real-time Conversation**: Live conversation transcript
- **System Logs**: Detailed logging with color coding
- **Audio Monitoring**: Device status and audio level indicators
- **Performance Metrics**: Latency tracking for various operations

### Log Categories
- **Blue**: User speech and input
- **Green**: Agent responses and audio output
- **Purple**: Function calls and AI processing
- **Yellow**: Performance and latency metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software developed for TechFlow Solutions.

## 🆘 Support

For technical support or questions:
- Check the web interface logs for debugging information
- Verify Deepgram API key configuration
- Ensure microphone permissions are granted
- Review browser console for JavaScript errors

## 🔮 Future Enhancements

- **Multi-language Support**: Expand beyond English
- **Advanced Analytics**: Customer interaction insights
- **CRM Integration**: Connect with external customer systems
- **Mobile App**: Native mobile application
- **Advanced AI**: Enhanced natural language understanding
- **Workflow Automation**: Extended business process automation

---

**TechFlow Solutions** - Where cutting-edge AI meets exceptional customer experiences.