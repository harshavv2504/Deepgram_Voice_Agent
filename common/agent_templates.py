from common.agent_functions import FUNCTION_DEFINITIONS
from common.prompt_templates import INDIVILLAGE_PROMPT_TEMPLATE, PROMPT_TEMPLATE
from datetime import datetime



VOICE = "aura-2-thalia-en"

# audio settings
USER_AUDIO_SAMPLE_RATE = 48000
USER_AUDIO_SECS_PER_CHUNK = 0.05
USER_AUDIO_SAMPLES_PER_CHUNK = round(USER_AUDIO_SAMPLE_RATE * USER_AUDIO_SECS_PER_CHUNK)

AGENT_AUDIO_SAMPLE_RATE = 16000
AGENT_AUDIO_BYTES_PER_SEC = 2 * AGENT_AUDIO_SAMPLE_RATE

VOICE_AGENT_URL = "wss://agent.deepgram.com/v1/agent/converse"

AUDIO_SETTINGS = {
    "input": {
        "encoding": "linear16",
        "sample_rate": USER_AUDIO_SAMPLE_RATE,
    },
    "output": {
        "encoding": "linear16",
        "sample_rate": AGENT_AUDIO_SAMPLE_RATE,
        "container": "none",
    },
}

LISTEN_SETTINGS = {
    "provider": {
        "type": "deepgram",
        "model": "nova-3",
    }
}

THINK_SETTINGS = {
    "provider": {
        "type": "open_ai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
    },
    "prompt": PROMPT_TEMPLATE.format(
        current_date=datetime.now().strftime("%A, %B %d, %Y")
    ),
    "functions": FUNCTION_DEFINITIONS,
}

SPEAK_SETTINGS = {
    "provider": {
        "type": "deepgram",
        "model": VOICE,
    }
}

AGENT_SETTINGS = {
    "language": "en",
    "listen": LISTEN_SETTINGS,
    "think": THINK_SETTINGS,
    "speak": SPEAK_SETTINGS,
    "greeting": "",
}

SETTINGS = {"type": "Settings", "audio": AUDIO_SETTINGS, "agent": AGENT_SETTINGS}


class AgentTemplates:
    def __init__(
        self,
        industry="indivillage",
        voiceModel="aura-2-thalia-en",
        voiceName="",
    ):
        self.voiceModel = voiceModel
        if voiceName == "":
            self.voiceName = self.get_voice_name_from_model(self.voiceModel)
        else:
            self.voiceName = voiceName

        self.personality = ""
        self.company = ""
        self.first_message = ""
        self.capabilities = ""

        self.industry = industry

        self.voice_agent_url = VOICE_AGENT_URL
        self.settings = SETTINGS
        self.user_audio_sample_rate = USER_AUDIO_SAMPLE_RATE
        self.user_audio_secs_per_chunk = USER_AUDIO_SECS_PER_CHUNK
        self.user_audio_samples_per_chunk = USER_AUDIO_SAMPLES_PER_CHUNK
        self.agent_audio_sample_rate = AGENT_AUDIO_SAMPLE_RATE
        self.agent_audio_bytes_per_sec = AGENT_AUDIO_BYTES_PER_SEC

        # Only TechFlow industry is supported
        if self.industry != "techflow":
            self.industry = "techflow"
        
        self.techflow()

        # Format documentation for the prompt using MDX knowledge base
        doc_text = ""
        try:
            from knowledgebase.mdx_handler import MDXKnowledgeBase
            mdx_kb = MDXKnowledgeBase()
            entries = mdx_kb.read_knowledge_base()
            if entries:
                doc_text = "Available documentation topics: " + ", ".join(
                    [entry.get('title', '') for entry in entries]
                )
        except Exception as e:
            print(f"Error reading TechFlow knowledge base: {e}")
            doc_text = "TechFlow Solutions knowledge base available"

        # Use TechFlow prompt for general inquiries, but also support order/appointment functionality
        self.prompt = TECHFLOW_PROMPT_TEMPLATE.format(documentation=doc_text)
        
        # Add order/appointment functionality support
        order_appointment_prompt = PROMPT_TEMPLATE.format(
            current_date=datetime.now().strftime("%A, %B %d, %Y")
        )
        
        # Combine both prompts - TechFlow knowledge base + order/appointment capabilities
        combined_prompt = self.prompt + "\n\n" + order_appointment_prompt
        
        # Add clear instruction about function selection and topic restrictions
        final_prompt = """
FUNCTION SELECTION INTELLIGENCE:
You must intelligently choose between two function types based on the question content:

1. KNOWLEDGE BASE FUNCTIONS - Use for TechFlow Solutions questions:
   - Company information, services, leadership, technology innovation, AI solutions
   - Examples: "What does TechFlow do?", "Tell me about your services", "Who is the CEO?"
   - Functions: search_knowledge_base(), get_knowledge_base_topics(), get_knowledge_base_entry()

2. CUSTOMER SERVICE FUNCTIONS - Use for operational questions:
   - Orders, appointments, customer lookups, scheduling
   - Examples: "Check my order status", "When is my meeting?", "Schedule an appointment"
   - Functions: find_customer(), get_orders(), get_appointments(), create_appointment(), check_availability()

DECISION RULES:
- Question about TechFlow company/services/technology → Use knowledge base functions
- Question about orders/appointments/customers → Use customer service functions
- Question about OTHER COMPANIES (Google, Microsoft, Apple, etc.) → DO NOT use functions, redirect to TechFlow
- Mixed questions → Use both function types as needed
- Always use agent_filler() before looking up information

OFF-TOPIC QUESTION HANDLING:
When users ask about other companies or unrelated topics:
- DO NOT use knowledge base functions for other companies
- Politely redirect: "I can help you with TechFlow Solutions. Would you like to know about that instead?"
- Examples: "What are Google's policies?" → "I can help you with TechFlow Solutions. Would you like to know about that instead?"

INTENTION ANALYSIS & CONVERSION STRATEGY:
Your primary goal is to convert customer inquiries into appointments WHEN APPROPRIATE. Keep it FUN, INTERACTIVE, and PROUDLY TECHFLOW:

1. ANALYZE CUSTOMER INTENTION:
   - Listen for problems, needs, or goals they want to achieve
   - Identify pain points or challenges they're facing
   - Understand their industry or business context

2. MATCH TO TECHFLOW SERVICES:
   - Use knowledge base functions to find relevant services
   - Connect their needs to specific TechFlow capabilities
   - Keep it light and engaging - no boring corporate talk!
   - Always emphasize why TechFlow is the BEST choice

3. OFFER TAILORED SOLUTIONS:
   - Present services that directly address their problem
   - Be witty, make it fun
   - Show personality while being helpful
   - Highlight our unique advantages over competitors
   - Use technology innovation references strategically - only when naturally relevant

4. GUIDE TOWARD APPOINTMENT (WHEN APPROPRIATE):
   - Ask about consultation meetings ONLY when customer shows business interest
   - Keep the energy up - no long explanations
   - Make scheduling sound exciting, not like a chore
   - Show confidence that they'll choose TechFlow
   - After confirming appointments, ask if they need other help

CONSULTATION TIMING - WHEN TO ASK FOR CONSULTATIONS:
✅ ASK FOR CONSULTATION when:
- Customer expresses a specific business need or problem
- Customer asks about services for their own business
- Customer shows interest in working with TechFlow
- Customer asks "How can you help me?" or similar
- Customer mentions their own projects or challenges

❌ DO NOT ask for consultation when:
- Customer asks simple informational questions
- Customer asks about existing clients (like "Is TechFlow helping Microsoft?")
- Customer asks general company information
- Customer asks about leadership, history, or basic facts
- Customer is just browsing or learning about TechFlow

TTS-FRIENDLY RESPONSES:
- NEVER use emojis - TTS will literally say "emoji" which sounds awkward
- Use words instead: "Great!" instead of "🎉", "Perfect!" instead of "👍"
- Keep responses natural and conversational for voice output

FOLLOW-UP BEHAVIOR:
After completing any task, ALWAYS ask if there's anything else you can help with to keep the conversation flowing.

CONVERSATION FLOW EXAMPLES:

✅ APPROPRIATE CONSULTATION REQUEST:
Customer: "I'm struggling with customer service automation for my platform"
Bot: [search_knowledge_base("customer service automation")] 
Bot: "Customer service automation giving you headaches? We've got your back with AI-powered voice agents and smart workflows that actually work. Ready to chat about fixing this over a consultation meeting?"

❌ INAPPROPRIATE CONSULTATION REQUEST:
Customer: "Is TechFlow helping Microsoft?"
Bot: [search_knowledge_base("Microsoft")] 
Bot: "Yes, TechFlow has collaborated with Microsoft to provide AI-powered customer service solutions for enterprise clients." (NO consultation request needed)

COMPETITIVE ADVOCACY EXAMPLES:
Customer: "How do you compare to other AI customer service companies?"
Bot: "Other companies? TechFlow is in a league of our own! We combine cutting-edge AI with genuine customer understanding - that's something no one else offers. Our innovative approach delivers superior results. Want to see the difference for yourself?"

Customer: "What makes TechFlow different?"
Bot: "TechFlow isn't just another vendor - we're innovators! While others focus on features, we focus on outcomes AND experiences. Our technology drives us to deliver exceptional results. It's not just business, it's innovation with impact!"

""" + combined_prompt
        
        self.prompt = final_prompt

        self.first_message = f"Hey! I'm {self.company} voice assistant, How may I assist you today?"

        self.settings["agent"]["speak"]["provider"]["model"] = self.voiceModel
        self.settings["agent"]["think"]["prompt"] = self.prompt
        self.settings["agent"]["greeting"] = self.first_message

        self.prompt = self.personality + "\n\n" + self.prompt


    
    def techflow(self, company="TechFlow Solutions"):
        self.company = company
        self.personality = f"You are {self.voiceName}, a friendly and professional customer service representative for {self.company}, an innovative technology company that provides cutting-edge AI-powered customer service solutions. Your role is to assist potential customers and partners with inquiries about TechFlow's services, technology, and collaboration opportunities."
        self.capabilities = "I can help you answer questions about TechFlow's AI solutions, customer service technology, innovation initiatives, and partnership opportunities."




    @staticmethod
    def get_available_industries():
        """Return a dictionary of available industries with display names"""
        return {
            "techflow": "TechFlow Solutions",
        }

    def get_voice_name_from_model(self, model):
        return (
            model.replace("aura-2-", "").replace("aura-", "").split("-")[0].capitalize()
        )
