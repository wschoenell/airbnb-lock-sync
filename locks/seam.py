from seam import Seam
import os


class SeamLock:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.seam = Seam()

    def create_access_code(self, name: str, code: str, starts_at=None, ends_at=None):
        access_code = self.seam.access_codes.create(
            device_id=self.device_id,
            name=name,
            code=code,
            starts_at=starts_at,
            ends_at=ends_at
        )
        return access_code

    def grab_access_codes(self):
        access_codes = self.seam.access_codes.list(device_id=self.device_id)
        return [code.__dict__ for code in access_codes]
    
    def update_access_code(self, name: str, code: str, starts_at=None, ends_at=None):
        access_codes = self.grab_access_codes()
        for ac in access_codes:
            if ac['name'] == name:
                updated_code = self.seam.access_codes.update(
                    access_code_id=ac['access_code_id'],
                    name=name,
                    code=code,
                    starts_at=starts_at,
                    ends_at=ends_at
                )
                return updated_code
            
    def delete_access_code(self, name: str):
        access_codes = self.grab_access_codes()
        for ac in access_codes:
            if ac['name'] == name:
                self.seam.access_codes.delete(access_code_id=ac['access_code_id'])
                return
    
if __name__ == "__main__":
    device_id = os.getenv("SEAM_LOCK") 
    lock = SeamLock(device_id=device_id)
    
    # # Create a new access code
    # new_code = lock.create_access_code(name="Guest Code", code="4567")
    # print(f"Created Access Code: {new_code.code}")
    
    # Retrieve and print all access codes
    codes = lock.grab_access_codes()
    print(codes)

# try:
#     # Optional: Check if the device supports online access codes
#     
#     if device.can_program_online_access_codes:
#         # Create the ongoing access code
#         access_code = seam.access_codes.create(
#             device_id=device_id,
#             name="My Ongoing Code",
#             code="1234" # Specify your desired PIN code
#         )
#         print(f"Successfully created ongoing access code: {access_code.code}")
#     else:
#         print("Device does not support programming online access codes.")
# except Exception as e:
#     print(f"An error occurred: {e}")
