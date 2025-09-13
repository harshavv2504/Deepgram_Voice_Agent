import json
from datetime import datetime, timedelta
import asyncio
from common.business_logic import (
    get_customer,
    get_customer_appointments,
    get_customer_orders,
    schedule_appointment,
    get_available_appointment_slots,
    reschedule_appointment,
    cancel_appointment,
    update_appointment_status,
    prepare_agent_filler_message,
    prepare_farewell_message,
)

# Import MDX knowledge base handler
try:
    from knowledgebase.mdx_handler import MDXKnowledgeBase
    mdx_kb = MDXKnowledgeBase()
except ImportError:
    mdx_kb = None


async def find_customer(params):
    """Look up a customer by phone, email, or ID."""
    phone = params.get("phone")
    email = params.get("email")
    customer_id = params.get("customer_id")

    result = await get_customer(phone=phone, email=email, customer_id=customer_id)
    return result


async def get_appointments(params):
    """Get appointments for a customer."""
    customer_id = params.get("customer_id")
    if not customer_id:
        return {"error": "customer_id is required"}

    result = await get_customer_appointments(customer_id)
    return result


async def get_orders(params):
    """Get orders for a customer."""
    customer_id = params.get("customer_id")
    if not customer_id:
        return {"error": "customer_id is required"}

    result = await get_customer_orders(customer_id)
    return result


async def create_appointment(params):
    """Schedule a new appointment."""
    customer_id = params.get("customer_id")
    date = params.get("date")
    service = params.get("service")

    if not all([customer_id, date, service]):
        return {"error": "customer_id, date, and service are required"}

    result = await schedule_appointment(customer_id, date, service)
    return result


async def check_availability(params):
    """Check available appointment slots."""
    start_date = params.get("start_date")
    end_date = params.get(
        "end_date", (datetime.fromisoformat(start_date) + timedelta(days=7)).isoformat()
    )

    if not start_date:
        return {"error": "start_date is required"}

    result = await get_available_appointment_slots(start_date, end_date)
    return result


async def reschedule_appointment_func(params):
    """Reschedule an existing appointment."""
    appointment_id = params.get("appointment_id")
    new_date = params.get("new_date")
    new_service = params.get("new_service")

    if not all([appointment_id, new_date, new_service]):
        return {"error": "appointment_id, new_date, and new_service are required"}

    result = await reschedule_appointment(appointment_id, new_date, new_service)
    return result


async def cancel_appointment_func(params):
    """Cancel an existing appointment."""
    appointment_id = params.get("appointment_id")

    if not appointment_id:
        return {"error": "appointment_id is required"}

    result = await cancel_appointment(appointment_id)
    return result


async def update_appointment_status_func(params):
    """Update the status of an existing appointment."""
    appointment_id = params.get("appointment_id")
    new_status = params.get("new_status")

    if not all([appointment_id, new_status]):
        return {"error": "appointment_id and new_status are required"}

    result = await update_appointment_status(appointment_id, new_status)
    return result


async def agent_filler(websocket, params):
    """
    Handle agent filler messages while maintaining proper function call protocol.
    """
    result = await prepare_agent_filler_message(websocket, **params)
    return result


async def end_call(websocket, params):
    """
    End the conversation and close the connection.
    """
    farewell_type = params.get("farewell_type", "general")
    result = await prepare_farewell_message(websocket, farewell_type)
    return result


async def search_knowledge_base(params):
    """Search the IndiVillage knowledge base for specific information."""
    if not mdx_kb:
        return {"error": "Knowledge base not available"}
    
    query = params.get("query", "")
    if not query:
        return {"error": "Search query is required"}
    
    try:
        results = mdx_kb.search_knowledge_base(query)
        if results:
            # Return the most relevant result
            best_match = results[0]
            return {
                "found": True,
                "title": best_match.get("title", ""),
                "topic": best_match.get("topic", ""),
                "content": best_match.get("content_raw", ""),
                "tags": best_match.get("tags", []),
                "total_results": len(results)
            }
        else:
            return {"found": False, "message": "No information found for that query"}
    except Exception as e:
        return {"error": f"Error searching knowledge base: {str(e)}"}


async def get_knowledge_base_topics(params):
    """Get all available topics in the IndiVillage knowledge base."""
    if not mdx_kb:
        return {"error": "Knowledge base not available"}
    
    try:
        topics = mdx_kb.get_topics()
        return {
            "topics": topics,
            "total_topics": len(topics)
        }
    except Exception as e:
        return {"error": f"Error getting topics: {str(e)}"}


async def get_knowledge_base_entry(params):
    """Get a specific entry from the IndiVillage knowledge base by topic or title."""
    if not mdx_kb:
        return {"error": "Knowledge base not available"}
    
    topic = params.get("topic", "")
    title = params.get("title", "")
    
    if not topic and not title:
        return {"error": "Either topic or title is required"}
    
    try:
        if topic:
            # Search by topic using fuzzy search
            results = mdx_kb.search_knowledge_base(topic)
            if results:
                # Return the first result for this topic
                entry = results[0]
                return {
                    "found": True,
                    "title": entry.get("title", ""),
                    "topic": entry.get("topic", ""),
                    "content": entry.get("content_raw", ""),
                    "tags": entry.get("tags", [])
                }
            else:
                return {"found": False, "message": f"No entries found for topic: {topic}"}
        else:
            # Search by title - try exact match first, then fuzzy search
            entries = mdx_kb.read_knowledge_base()
            if not entries:
                return {"found": False, "message": "Knowledge base is empty"}
            
            # First try exact title match
            title_lower = title.lower().strip()
            for entry in entries:
                entry_title = entry.get("title", "").lower().strip()
                if entry_title == title_lower:
                    return {
                        "found": True,
                        "title": entry.get("title", ""),
                        "topic": entry.get("topic", ""),
                        "content": entry.get("content_raw", ""),
                        "tags": entry.get("tags", [])
                    }
            
            # If no exact match, try fuzzy search as fallback
            results = mdx_kb.search_knowledge_base(title)
            if results:
                entry = results[0]
                return {
                    "found": True,
                    "title": entry.get("title", ""),
                    "topic": entry.get("topic", ""),
                    "content": entry.get("content_raw", ""),
                    "tags": entry.get("tags", [])
                }
            else:
                return {"found": False, "message": f"No entries found for title: {title}"}
    except Exception as e:
        return {"error": f"Error getting entry: {str(e)}"}


async def create_customer_account(params):
    """Create a new customer account with proper validation."""
    # Import here to avoid circular import issues
    try:
        from common.business_logic import create_new_customer
    except ImportError:
        return {"error": "Customer creation service temporarily unavailable"}
    
    name = params.get("name", "").strip()
    phone = params.get("phone", "").strip()
    email = params.get("email", "").strip()
    
    # Validate required fields
    if not name:
        return {"error": "Customer name is required"}
    if not phone:
        return {"error": "Phone number is required"}
    if not email:
        return {"error": "Email address is required"}
    
    # Basic format validation
    if len(name) < 2:
        return {"error": "Name must be at least 2 characters long"}
    
    # Phone validation (basic)
    if not phone.startswith("+") or len(phone) < 10:
        return {"error": "Phone number must be in international format (e.g., +15551234567)"}
    
    # Email validation (basic)
    if "@" not in email or "." not in email:
        return {"error": "Please provide a valid email address"}
    
    try:
        result = await create_new_customer(name, phone, email)
        return result
    except Exception as e:
        return {"error": f"Error creating customer: {str(e)}"}


# Function definitions that will be sent to the Voice Agent API
FUNCTION_DEFINITIONS = [
    {
        "name": "agent_filler",
        "description": """Use this function to provide natural conversational filler before looking up information.
        ALWAYS call this function first with message_type='lookup' when you're about to look up customer information.
        After calling this function, you MUST immediately follow up with the appropriate lookup function (e.g., find_customer).""",
        "parameters": {
            "type": "object",
            "properties": {
                "message_type": {
                    "type": "string",
                    "description": "Type of filler message to use. Use 'lookup' when about to search for information.",
                    "enum": ["lookup", "general"],
                }
            },
            "required": ["message_type"],
        },
    },
    {
        "name": "find_customer",
        "description": """Look up a customer's account information. Use context clues to determine what type of identifier the user is providing:

        Customer ID formats:
        - Numbers only (e.g., '169', '42') → Format as 'CUST0169', 'CUST0042'
        - With prefix (e.g., 'CUST169', 'customer 42') → Format as 'CUST0169', 'CUST0042'
        
        Phone number recognition:
        - Standard format: '555-123-4567' → Format as '+15551234567'
        - With area code: '(555) 123-4567' → Format as '+15551234567'
        - Spoken naturally: 'five five five, one two three, four five six seven' → Format as '+15551234567'
        - International: '+1 555-123-4567' → Use as is
        - Always add +1 country code if not provided
        
        Email address recognition:
        - Spoken naturally: 'my email is john dot smith at example dot com' → Format as 'john.smith@example.com'
        - With domain: 'john@example.com' → Use as is
        - Spelled out: 'j o h n at example dot com' → Format as 'john@example.com'""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID. Format as CUSTXXXX where XXXX is the number padded to 4 digits with leading zeros. Example: if user says '42', pass 'CUST0042'",
                },
                "phone": {
                    "type": "string",
                    "description": """Phone number with country code. Format as +1XXXXXXXXXX:
                    - Add +1 if not provided
                    - Remove any spaces, dashes, or parentheses
                    - Convert spoken numbers to digits
                    Example: 'five five five one two three four five six seven' → '+15551234567'""",
                },
                "email": {
                    "type": "string",
                    "description": """Email address in standard format:
                    - Convert 'dot' to '.'
                    - Convert 'at' to '@'
                    - Remove spaces between spelled out letters
                    Example: 'j dot smith at example dot com' → 'j.smith@example.com'""",
                },
            },
        },
    },
    {
        "name": "get_appointments",
        "description": """Retrieve all appointments for a customer. Use this function when:
        - A customer asks about their upcoming appointments
        - A customer wants to know their appointment schedule
        - A customer asks 'When is my next appointment?'
        
        Always verify you have the customer's account first using find_customer before checking appointments.""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from find_customer first.",
                }
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "get_orders",
        "description": """Retrieve order history for a customer. Use this function when:
        - A customer asks about their orders
        - A customer wants to check order status
        - A customer asks questions like 'Where is my order?' or 'What did I order?'
        
        Always verify you have the customer's account first using find_customer before checking orders.""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from find_customer first.",
                }
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "create_appointment",
        "description": """Schedule a new appointment for a customer. Use this function when:
        - A customer wants to book a new appointment
        - A customer asks to schedule a service
        
        Before scheduling:
        1. Verify customer account exists using find_customer
        2. Check availability using check_availability
        3. Confirm date/time and service type with customer before booking""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from find_customer first.",
                },
                "date": {
                    "type": "string",
                    "description": "Appointment date and time in ISO format (YYYY-MM-DDTHH:MM:SS). Must be a time slot confirmed as available.",
                },
                "service": {
                    "type": "string",
                    "description": "Type of service requested. Must be one of the following: Consultation, Follow-up, Review, or Planning",
                    "enum": ["Consultation", "Follow-up", "Review", "Planning"],
                },
            },
            "required": ["customer_id", "date", "service"],
        },
    },
    {
        "name": "check_availability",
        "description": """Check available appointment slots within a date range. Use this function when:
        - A customer wants to know available appointment times
        - Before scheduling a new appointment
        - A customer asks 'When can I come in?' or 'What times are available?'
        
        After checking availability, present options to the customer in a natural way, like:
        'I have openings on [date] at [time] or [date] at [time]. Which works better for you?'""",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in ISO format (YYYY-MM-DDTHH:MM:SS). Usually today's date for immediate availability checks.",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in ISO format. Optional - defaults to 7 days after start_date. Use for specific date range requests.",
                },
            },
            "required": ["start_date"],
        },
    },
    {
        "name": "end_call",
        "description": """End the conversation and close the connection. Call this function when:
        - User says goodbye, thank you, etc.
        - User indicates they're done ("that's all I need", "I'm all set", etc.)
        - User wants to end the conversation
        
        Examples of triggers:
        - "Thank you, bye!"
        - "That's all I needed, thanks"
        - "Have a good day"
        - "Goodbye"
        - "I'm done"
        
        Do not call this function if the user is just saying thanks but continuing the conversation.""",
        "parameters": {
            "type": "object",
            "properties": {
                "farewell_type": {
                    "type": "string",
                    "description": "Type of farewell to use in response",
                    "enum": ["thanks", "general", "help"],
                }
            },
            "required": ["farewell_type"],
        },
    },
    {
        "name": "search_knowledge_base",
        "description": """Search the IndiVillage knowledge base for specific information. Use this function when:
        - Users ask questions about IndiVillage's services, company, leadership, or impact
        - Users want to know about specific topics like data services, rural empowerment, or social enterprise
        - Users ask "What does IndiVillage do?" or "Tell me about IndiVillage"
        - Users want information about specific areas like workforce, locations, or client collaborations
        
        DO NOT use this function for:
        - Questions about other companies (Google, Microsoft, Apple, etc.)
        - Topics unrelated to IndiVillage Tech Solutions
        - General business questions not specific to IndiVillage
        
        This function searches across all available topics in the IndiVillage knowledge base only.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query or question from the user. Should be specific and relevant to IndiVillage Tech Solutions.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_knowledge_base_topics",
        "description": """Get all available topics in the IndiVillage knowledge base. Use this function when:
        - Users ask "What topics can you tell me about?" or "What information do you have?"
        - Users want to know what areas of IndiVillage you can discuss
        - Users ask for an overview of available information
        - You need to show users what topics are available for discussion""",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_knowledge_base_entry",
        "description": """Get a specific entry from the IndiVillage knowledge base by topic or title. Use this function when:
        - Users ask for specific information about a particular IndiVillage topic
        - Users want detailed information about a specific area like "leadership team" or "key services"
        - Users ask "Tell me more about [specific IndiVillage topic]"
        - You need to provide comprehensive information about a particular IndiVillage subject
        
        DO NOT use this function for:
        - Questions about other companies (Google, Microsoft, Apple, etc.)
        - Topics unrelated to IndiVillage Tech Solutions""",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The specific topic to search for (e.g., 'Company Information', 'Leadership Team', 'Key Services')",
                },
                "title": {
                    "type": "string",
                    "description": "The specific title to search for (e.g., 'IndiVillage Tech Solutions - Company Overview')",
                }
            },
        },
    },
    {
        "name": "create_customer_account",
        "description": """Create a new customer account when they don't have one. Use this function when:
        - A customer says they need to create an account
        - A customer asks to sign up or register
        - A customer doesn't exist in the system and needs to be added
        - A customer wants to become a new client
        
        INITIAL RESPONSE: When a customer asks to create an account, respond with: "I can certainly help you with that! I just need a few details to do it."
        
        IMPORTANT: Always ask customers to spell out their details due to transcription accuracy issues.
        - Ask them to spell their name letter by letter
        - Ask them to spell their phone number digit by digit
        - Ask them to spell their email address letter by letter
        - Confirm all details before creating the account""",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer's full name. Ask them to spell it out letter by letter for accuracy.",
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number in international format (e.g., +15551234567). Ask them to spell it digit by digit.",
                },
                "email": {
                    "type": "string",
                    "description": "Email address. Ask them to spell it out letter by letter for accuracy.",
                }
            },
            "required": ["name", "phone", "email"],
        },
    },
    {
        "name": "reschedule_appointment",
        "description": """Reschedule an existing appointment to a new date and time. Use this function when:
        - A customer wants to change their appointment time
        - A customer asks to move their appointment to a different date
        - A customer needs to reschedule due to conflicts
        
        Before rescheduling:
        1. Get the appointment ID from get_appointments
        2. Check new availability using check_availability
        3. Confirm the new date/time and service with customer""",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "The appointment ID (e.g., APT0001) to reschedule. Must be obtained from get_appointments first.",
                },
                "new_date": {
                    "type": "string",
                    "description": "New appointment date and time in ISO format (YYYY-MM-DDTHH:MM:SS). Must be a confirmed available time slot.",
                },
                "new_service": {
                    "type": "string",
                    "description": "Type of service for the rescheduled appointment. Must be one of: Consultation, Follow-up, Review, or Planning",
                    "enum": ["Consultation", "Follow-up", "Review", "Planning"],
                },
            },
            "required": ["appointment_id", "new_date", "new_service"],
        },
    },
    {
        "name": "cancel_appointment",
        "description": """Cancel an existing appointment. Use this function when:
        - A customer wants to cancel their appointment
        - A customer can no longer make their scheduled time
        - A customer requests to cancel their booking
        
        Before cancelling:
        1. Get the appointment ID from get_appointments
        2. Confirm cancellation with the customer""",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "The appointment ID (e.g., APT0001) to cancel. Must be obtained from get_appointments first.",
                },
            },
            "required": ["appointment_id"],
        },
    },
    {
        "name": "update_appointment_status",
        "description": """Update the status of an existing appointment. Use this function when:
        - Marking an appointment as completed after the meeting
        - Changing appointment status for administrative purposes
        - Updating appointment status based on customer feedback
        
        Valid statuses: Scheduled, Completed, Cancelled""",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "The appointment ID (e.g., APT0001) to update. Must be obtained from get_appointments first.",
                },
                "new_status": {
                    "type": "string",
                    "description": "New status for the appointment",
                    "enum": ["Scheduled", "Completed", "Cancelled"],
                },
            },
            "required": ["appointment_id", "new_status"],
        },
    },
]

# Map function names to their implementations
FUNCTION_MAP = {
    "find_customer": find_customer,
    "get_appointments": get_appointments,
    "get_orders": get_orders,
    "create_appointment": create_appointment,
    "check_availability": check_availability,
    "reschedule_appointment": reschedule_appointment_func,
    "cancel_appointment": cancel_appointment_func,
    "update_appointment_status": update_appointment_status_func,
    "agent_filler": agent_filler,
    "end_call": end_call,
    "search_knowledge_base": search_knowledge_base,
    "get_knowledge_base_topics": get_knowledge_base_topics,
    "get_knowledge_base_entry": get_knowledge_base_entry,
    "create_customer_account": create_customer_account,
}
