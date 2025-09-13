from datetime import datetime, timedelta

def generate_meeting_json(appointment, customer):
    """
    Generate meeting data in the required format for modular pipeline integration.
    This function does NOT save to disk, only returns the dict.
    """
    # Parse start time from appointment['date']
    meeting_start = appointment["date"]
    # Calculate end time (+30 minutes, ISO 8601 format)
    start_dt = datetime.fromisoformat(meeting_start)
    meeting_end = (start_dt + timedelta(minutes=30)).isoformat()

    meeting_json = {
        "organizer_name": "IndiVillage Tech Solutions",
        "attendees": [
            {
                "email": customer.get("email", ""),
                "name": customer.get("name", "")
            }
        ],
        "meeting_topic": "IndiVillage Consultation Meeting",
        "meeting_date": meeting_start[:10],
        "meeting_start": meeting_start,
        "meeting_end": meeting_end,
        "meeting_description": "Discuss your project requirements and how IndiVillage can help you achieve your goals",
        "meeting_location": "Zoom"
    }
    return meeting_json

def schedule_meeting_from_json(json_input):
    """
    Use the provided meeting JSON to send emails and create a calendar event via Google APIs.
    This function is adapted for modular pipeline use.
    """
    from email.mime.text import MIMEText
    import base64
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import os
    
    try:
        # Validate input
        required_fields = ["organizer_name", "attendees", "meeting_topic", "meeting_date", 
                          "meeting_start", "meeting_end", "meeting_description", "meeting_location"]
        for field in required_fields:
            if field not in json_input:
                raise ValueError(f"Missing required field: {field}")
        
        if not json_input["attendees"]:
            raise ValueError("No attendees specified")
            
    except Exception as e:
        print(f"❌ Input validation failed: {e}")
        return False

    GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def get_gmail_service():
        creds = None
        if os.path.exists("common/token_gmail.json"):
            creds = Credentials.from_authorized_user_file("common/token_gmail.json", GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ credentials.json file not found. Please ensure Google API credentials are properly configured.")
                return False
            with open("common/token_gmail.json", "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    def get_calendar_service():
        creds = None
        if os.path.exists("common/token_calendar.json"):
            creds = Credentials.from_authorized_user_file("common/token_calendar.json", CALENDAR_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("❌ Calendar credentials not found or expired. Please ensure Google Calendar API credentials are properly configured.")
                return None
            with open("common/token_calendar.json", "w") as token:
                token.write(creds.to_json())
        return build("calendar", "v3", credentials=creds)

    organizer_name = json_input["organizer_name"]
    attendees = json_input["attendees"]
    meeting_topic = json_input["meeting_topic"]
    meeting_date = json_input["meeting_date"]
    meeting_start = json_input["meeting_start"]
    meeting_end = json_input["meeting_end"]
    meeting_description = json_input["meeting_description"]
    meeting_location = json_input["meeting_location"]

    gmail_service = get_gmail_service()
    calendar_service = get_calendar_service()
    
    # Check if services are properly initialized
    if not gmail_service:
        print("❌ Failed to initialize Gmail service")
        return False
    if not calendar_service:
        print("❌ Failed to initialize Calendar service")
        return False

    # --- Send personalized emails ---
    for attendee in attendees:
        try:
            email = attendee["email"]
            name = attendee.get("name", "there")
            subject = f"Meeting Confirmation: {meeting_topic} on {meeting_date}"
            body_text = f"""Hi {name},

Thank you for choosing IndiVillage Tech Solutions! This is to confirm your consultation meeting scheduled as below:

Meeting Details:
• Topic: {meeting_topic}
• Date: {meeting_date}
• Time: {meeting_start[-8:]} - {meeting_end[-8:]}
• Location: {meeting_location}

We're excited to discuss your project requirements and explore how IndiVillage can help you achieve your goals. Please ensure you have a stable internet connection for the Zoom meeting.

A calendar invite has also been sent to your email.

Looking forward to our conversation!

Best regards,
{organizer_name}
Team
"""
            message = MIMEText(body_text)
            message["to"] = email
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            message_body = {"raw": raw}
            sent = gmail_service.users().messages().send(userId="me", body=message_body).execute()
            print(f"✅ Email sent to {email}! ID:", sent["id"])
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")
            continue

    # --- Create calendar event ---
    try:
        print(f"📅 Creating calendar event for {meeting_topic}...")
        
        # Use system timezone or default to Asia/Kolkata
        import time
        try:
            system_timezone = time.tzname[time.daylight]
            if not system_timezone or system_timezone == 'UTC':
                system_timezone = 'Asia/Kolkata'  # Default fallback
        except:
            system_timezone = 'Asia/Kolkata'  # Default fallback
            
        event = {
            'summary': meeting_topic,
            'description': meeting_description,
            'location': meeting_location,
            'start': {'dateTime': meeting_start, 'timeZone': system_timezone},
            'end': {'dateTime': meeting_end, 'timeZone': system_timezone},
            'attendees': [{'email': attendee["email"]} for attendee in attendees],
            'reminders': {'useDefault': True},
        }
        
        print(f"📅 Event details: {meeting_start} to {meeting_end} ({system_timezone})")
        print(f"📅 Attendees: {[attendee['email'] for attendee in attendees]}")
        
        created_event = calendar_service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        print(f"✅ Calendar event created successfully!")
        print(f"✅ Event ID: {created_event.get('id')}")
        print(f"✅ Event Link: {created_event.get('htmlLink')}")
        
    except Exception as e:
        print(f"❌ Failed to create calendar event: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full error: {traceback.format_exc()}")
        return False
    
    return True
