#!/usr/bin/env python3
"""
Script to fetch and display future events from an iCal calendar in JSON format.
"""

import json
import os
import re
import requests
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from icalendar import Calendar


def get_future_events(url=os.getenv("AIRBNB_ICAL"), check_in_time=os.getenv("AIRBNB_CHECK_IN"), check_out_time=os.getenv("AIRBNB_CHECK_OUT"), tz=os.getenv("AIRBNB_TZ"), max_start_days=os.getenv("AIRBNB_MAX_START")):
    """
    Fetch iCal calendar from URL and extract future reserved events.
    
    Args:
        url (str): The URL of the iCal calendar
        
    Returns:
        list: List of future reserved events as dictionaries
    """
    # Fetch calendar from URL
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        calendar = Calendar.from_ical(response.content)
    except requests.RequestException as e:
        print(f"Error fetching calendar: {e}")
        return []
    
    now = datetime.now(timezone.utc)
    future_events = []
    
    # Calculate maximum start date if specified
    max_start_date = None
    if max_start_days is not None:
        max_start_date = now + timedelta(days=int(max_start_days))
    
    for component in calendar.walk():
        if component.name == "VEVENT":
            # Get event summary
            summary = str(component.get('summary', ''))
            
            # Only process "Reserved" events
            if summary != "Reserved":
                continue
            
            # Get event start time
            dtstart = component.get('dtstart')
            if dtstart is None:
                continue
                
            event_start = dtstart.dt
            
            # Convert to datetime if it's a date object
            if not isinstance(event_start, datetime):
                event_start = datetime.combine(event_start, datetime.min.time())
            
            # Make timezone aware if naive
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
            
            # Get event end time
            dtend = component.get('dtend')
            event_end = None
            if dtend:
                event_end = dtend.dt
                if not isinstance(event_end, datetime):
                    event_end = datetime.combine(event_end, datetime.min.time())
                if event_end.tzinfo is None:
                    event_end = event_end.replace(tzinfo=timezone.utc)
            
            # Only include events that haven't ended yet (based on end date)
            if event_end and event_end > now:
                # Apply custom check-in and check-out times if provided
                if check_in_time is not None:
                    # Parse check_in_time (expected format: "HH:MM" or "HH:MM:SS")
                    time_parts = check_in_time.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    event_start = event_start.replace(hour=hour, minute=minute, second=second)
                
                if check_out_time is not None:
                    # Parse check_out_time (expected format: "HH:MM" or "HH:MM:SS")
                    time_parts = check_out_time.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    event_end = event_end.replace(hour=hour, minute=minute, second=second)
                
                # Convert to UTC if timezone is specified
                if tz is not None:
                    local_tz = ZoneInfo(tz)
                    # If times are naive or in UTC, treat them as local time first
                    if event_start.tzinfo is None or event_start.tzinfo == timezone.utc:
                        event_start = event_start.replace(tzinfo=local_tz)
                    event_start = event_start.astimezone(timezone.utc)
                    
                    if event_end.tzinfo is None or event_end.tzinfo == timezone.utc:
                        event_end = event_end.replace(tzinfo=local_tz)
                    event_end = event_end.astimezone(timezone.utc)
                
                # Skip events that start after the maximum start date
                if max_start_date is not None and event_start > max_start_date:
                    continue
                
                # Extract reservation details from description
                description = str(component.get('description', ''))
                
                # Extract reservation confirmation code from URL
                confirmation_code = None
                last_digits = None
                
                # Look for URL pattern: https://www.airbnb.com/hosting/reservations/details/CONFIRMATION_CODE
                url_match = re.search(r'https://www\.airbnb\.com/hosting/reservations/details/([A-Z0-9]+)', description)
                if url_match:
                    confirmation_code = url_match.group(1)
                
                # Extract last 4 digits from phone number
                digits_match = re.search(r'Phone Number \(Last 4 Digits\):\s*(\d{4})', description)
                if digits_match:
                    last_digits = int(digits_match.group(1))
                
                event_data = {
                    'start': event_start.isoformat(),
                    'end': event_end.isoformat() if event_end else None,
                    'last_digits': last_digits,
                    'url': url_match.group(0) if url_match else None,
                    'confirmation_code': confirmation_code
                }
                
                future_events.append(event_data)
    
    # Sort events by start time
    future_events.sort(key=lambda x: x['start'])
    
    return future_events


def main():
    """
    Main function to fetch and display future events.
    """
    # Check for ICAL environment variable first
    ical_url = os.getenv('ICAL')
    
    if not ical_url:
        # If not set, prompt the user
        ical_url = input("Enter the iCal calendar URL: ").strip()
    
    if not ical_url:
        print("Error: No URL provided")
        return
    
    print("Fetching calendar and extracting future events...")
    future_events = get_future_events(ical_url)
    
    # Display results in JSON format
    print("\nFuture Reserved Events (JSON):")
    print(json.dumps(future_events, indent=2))
    
    print(f"\nTotal future reserved events found: {len(future_events)}")


if __name__ == "__main__":
    main()
