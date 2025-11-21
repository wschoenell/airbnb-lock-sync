import os
import sys
from airbnb_ical.airbnb_ical import get_future_events

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
        if reservation['start'] != access_code.get('starts_at'):
            print(f"Discrepancy in start time for reservation {reservation['confirmation_code']}: "
                f"Expected start {reservation['start']}, "
                f"but access code starts at {access_code.get('starts_at')}.")
            return False
        if reservation['end'] != access_code.get('ends_at'):
            print(f"Discrepancy in end time for reservation {reservation['confirmation_code']}: "
                f"Expected end {reservation['end']}, "
                f"but access code ends at {access_code.get('ends_at')}.")
            return False
    return True


def update_code(reservation, access_code, lock):
    """
    Update access code to match reservation details.
    """
    print(f"Updating access code {access_code['name']} to match reservation {reservation['confirmation_code']}.")
    lock.update_access_code(
        name=reservation['confirmation_code'],
        code=str(reservation['last_digits']),
        starts_at=reservation['start'],
        ends_at=reservation['end']
    )

def delete_code(access_code, lock):
    """
    Delete an access code that has no matching reservation.
    """
    print(f"Deleting access code {access_code['name']} with code {access_code['code']}.")
    # Here you would add the logic to delete the access code via the YaleLock class
    # For example:
    # yale_lock.seam.access_codes.delete(access_code_id=access_code['id'])
    lock.delete_access_code(name=access_code['name'])


def create_code(reservation, lock):
    """
    Create a new access code based on reservation details.
    """
    print(f"Creating access code for reservation {reservation['confirmation_code']} with code {reservation['last_digits']}.")
    lock.create_access_code(
        name=reservation['confirmation_code'],
        code=str(reservation['last_digits']),
        starts_at=reservation['start'],
        ends_at=reservation['end']
    )

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