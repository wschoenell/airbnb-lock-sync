import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from airbnb_ical.airbnb_ical import get_future_events
from telegram_bot.telegram_bot import send_telegram_message

def check_code(reservation, access_code, check_times=os.getenv("MAIN_UPDATE_TIMES", 'False').lower() in ('true', '1', 't')):
    """
    Compare reservation details with access code details.
    """
    if reservation['last_digits'] != int(access_code['code']):
        print(f"Discrepancy found for reservation {reservation['confirmation_code']}: "
              f"Expected last digits {reservation['last_digits']}, "
              f"but access code is {access_code['code']}.")
        return False
    if check_times:
        # Normalize datetime strings for comparison (handle different ISO 8601 formats)
        def normalize_datetime(dt_str):
            if not dt_str:
                return None
            try:
                # Parse and convert to datetime object
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                # Return as ISO string without microseconds
                return dt.replace(microsecond=0).isoformat()
            except:
                return dt_str
        
        reservation_start = normalize_datetime(reservation['start'])
        access_start = normalize_datetime(access_code.get('starts_at'))
        
        if reservation_start != access_start:
            print(f"Discrepancy in start time for reservation {reservation['confirmation_code']}: "
                f"Expected start {reservation_start}, "
                f"but access code starts at {access_start}.")
            return False
        
        reservation_end = normalize_datetime(reservation['end'])
        access_end = normalize_datetime(access_code.get('ends_at'))
        
        if reservation_end != access_end:
            print(f"Discrepancy in end time for reservation {reservation['confirmation_code']}: "
                f"Expected end {reservation_end}, "
                f"but access code ends at {access_end}.")
            return False
    return True


def format_datetime(iso_datetime):
    """Format ISO datetime to readable format in Airbnb timezone."""
    if not iso_datetime:
        return "N/A"
    try:
        # Parse the datetime
        dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        
        # Convert to Airbnb timezone if specified
        airbnb_tz = os.getenv("AIRBNB_TZ")
        if airbnb_tz:
            local_tz = ZoneInfo(airbnb_tz)
            dt = dt.astimezone(local_tz)
            # Format with timezone abbreviation
            return dt.strftime("%b %d, %Y at %I:%M %p %Z")
        else:
            # Default to UTC display
            return dt.strftime("%b %d, %Y at %I:%M %p UTC")
    except:
        return iso_datetime


def update_code(reservation, access_code, lock):
    """
    Update access code to match reservation details.
    """
    dry_run = os.getenv("MAIN_DRY_RUN", 'False').lower() in ('true', '1', 't')
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Updating access code {access_code['name']} to match reservation {reservation['confirmation_code']}.")
    
    if not dry_run:
        lock.update_access_code(
            name=reservation['confirmation_code'],
            code=str(reservation['last_digits']),
            starts_at=reservation['start'],
            ends_at=reservation['end']
        )
    
    # Send Telegram notification
    message = (
        f"{'🧪 [DRY RUN] ' if dry_run else ''}🔄 *Lock Code {'Would Be ' if dry_run else ''}Updated*\n\n"
        f"📋 Reservation: `{reservation['confirmation_code']}`\n"
        f"🔑 Access Code: `{reservation['last_digits']}`\n"
        f"📅 Check-in: {format_datetime(reservation['start'])}\n"
        f"📅 Check-out: {format_datetime(reservation['end'])}\n"
    )
    if reservation.get('url'):
        message += f"🔗 [View Reservation]({reservation['url']})\n"
    
    send_telegram_message(message=message, parse_mode="Markdown")

def delete_code(access_code, lock):
    """
    Delete an access code that has no matching reservation.
    """
    dry_run = os.getenv("MAIN_DRY_RUN", 'False').lower() in ('true', '1', 't')
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Deleting access code {access_code['name']} with code {access_code['code']}.")
    
    if not dry_run:
        lock.delete_access_code(name=access_code['name'])
    
    # Send Telegram notification
    message = (
        f"{'🧪 [DRY RUN] ' if dry_run else ''}🗑️ *Lock Code {'Would Be ' if dry_run else ''}Deleted*\n\n"
        f"📋 Reservation: `{access_code['name']}`\n"
        f"🔑 Access Code: `{access_code['code']}`\n"
        f"ℹ️ Reason: No matching reservation found"
    )
    send_telegram_message(message=message, parse_mode="Markdown")


def create_code(reservation, lock):
    """
    Create a new access code based on reservation details.
    """
    dry_run = os.getenv("MAIN_DRY_RUN", 'False').lower() in ('true', '1', 't')
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Creating access code for reservation {reservation['confirmation_code']} with code {reservation['last_digits']}.")
    
    if not dry_run:
        lock.create_access_code(
            name=reservation['confirmation_code'],
            code=str(reservation['last_digits']),
            starts_at=reservation['start'],
            ends_at=reservation['end']
        )
    
    # Send Telegram notification
    message = (
        f"{'🧪 [DRY RUN] ' if dry_run else ''}✅ *New Lock Code {'Would Be ' if dry_run else ''}Created*\n\n"
        f"📋 Reservation: `{reservation['confirmation_code']}`\n"
        f"🔑 Access Code: `{reservation['last_digits']}`\n"
        f"📅 Check-in: {format_datetime(reservation['start'])}\n"
        f"📅 Check-out: {format_datetime(reservation['end'])}\n"
    )
    if reservation.get('url'):
        message += f"🔗 [View Reservation]({reservation['url']})\n"
    
    send_telegram_message(message=message, parse_mode="Markdown")

if __name__ == "__main__":
    current_reservations = get_future_events()
    print("Current Reservations from Airbnb iCal:")
    for reservation in current_reservations:
        print(reservation)
    
    # get the access codes from the yale lock
    from yale.yale import YaleLock
    yale_lock = YaleLock(device_id=os.getenv("SEAM_LOCK"))
    access_codes = yale_lock.grab_access_codes()
    print("Access Codes from Yale Lock:")
    for code in access_codes:
        print(f"Access Code Name: {code['name']}, Code: {code['code']}")

    # Compare reservations with access codes and print discrepancies
    # Codes are the last 4 phone digits stored in reservation['last_digits']
    # Name is reservation['confirmation_code']
    print("\nDiscrepancies between Reservations and Access Codes:")
    reservation_codes = {str(res['confirmation_code']): res for res in current_reservations if res['confirmation_code']}
    lock_codes = {code['name']: code for code in access_codes}
    for code, reservation in reservation_codes.items():
        if code not in lock_codes:
            print(f"Missing Access Code for Reservation: {reservation}")
            # Create the access code
            create_code(reservation, yale_lock)
            sys.exit(0)
        else:
            if not check_code(reservation, lock_codes[code]):
                update_code(reservation, lock_codes[code], yale_lock)
    
    # Check for any access codes that do not have a matching reservation
    for code, access_code in lock_codes.items():
        if code not in reservation_codes:
            print(f"Extra Access Code without Reservation: {access_code['name']}, Code: {access_code['code']}")
            delete_code(access_code, yale_lock)