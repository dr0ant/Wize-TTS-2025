import logging
import os
from pyicloud import PyiCloudService
from shutil import copyfileobj

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ICloudConnection:
    def __init__(self, username, password, drive_file):
        """Initialize connection to iCloud and handle 2FA if required."""
        self.drive_file = drive_file  # Store the specific drive file structure
        logger.info(f"Initializing iCloud connection for user: {username}")
        try:
            self.icloud = PyiCloudService(username, password)
            if self.icloud.requires_2fa:
                logger.info("Two-factor authentication is required.")
                self._handle_2fa()
            elif self.icloud.requires_2sa:
                logger.info("Two-step authentication is required.")
                self._handle_2sa()
            self.drive = self.icloud.drive
            logger.info("iCloud connection established successfully.")
        except Exception as e:
            logger.error(f"Error establishing iCloud connection: {e}")
            raise

    def _handle_2fa(self):
        """Handle the two-factor authentication process."""
        try:
            code = input("Enter the 2FA code sent to your trusted device: ")
            if not self.icloud.validate_2fa_code(code):
                raise Exception("Invalid 2FA code.")
            logger.info("Two-factor authentication successful.")
        except Exception as e:
            logger.error(f"Error during 2FA: {e}")
            raise

    def _handle_2sa(self):
        """Handle the two-step authentication process."""
        try:
            devices = self.icloud.trusted_devices
            logger.info("Two-step authentication devices:")
            for i, device in enumerate(devices):
                logger.info(f"{i}: {device.get('deviceName', 'Unknown Device')}")

            device_index = int(input("Select a device to send the authentication code to: "))
            self.icloud.send_verification_code(devices[device_index])
            code = input("Enter the code sent to your device: ")
            if not self.icloud.validate_verification_code(devices[device_index], code):
                raise Exception("Invalid verification code.")
            logger.info("Two-step authentication successful.")
        except Exception as e:
            logger.error(f"Error during 2SA: {e}")
            raise

    def load_md_files(self):
        """Load multiple files based on the provided drive_file structure."""
        try:
            logger.info(f"Attempting to fetch file: {self.drive_file}")
            # Navigate through the directories to the file
            drive_file = self._navigate_to_file(self.drive_file)
            
            if drive_file:
                logger.info(f"File found: {drive_file.name}")
                logger.info(f"Date modified: {drive_file.date_modified}")
                logger.info(f"File size: {drive_file.size} bytes")
                logger.info(f"File type: {drive_file.type}")

                # Download the file to the tmp_md directory
                content = self._download_file(drive_file)
                logger.info(f"File Content (Preview): {content[:200]}...\n")
            else:
                logger.error(f"File not found at the specified path: {self.drive_file}")

        except Exception as e:
            logger.error(f"Error during loading file: {e}")

    def _navigate_to_file(self, path_parts):
        """Navigate through the iCloud drive structure based on the provided path."""
        try:
            drive_file = self.drive
            for part in path_parts:
                drive_file = drive_file[part]  # Navigate to the next directory/file
            return drive_file
        except KeyError:
            logger.error(f"Invalid path or directory: {'/'.join(path_parts)}")
            return None

    def _download_file(self, drive_file):
        """Download a file from iCloud and save it to the tmp_md directory."""
        logger.info(f"Downloading content of file: {drive_file.name}")
        try:
            # Ensure tmp_md directory exists
            os.makedirs("tmp_md", exist_ok=True)

            # Save the file in the tmp_md directory
            file_path = os.path.join("tmp_md", drive_file.name)
            
            # Open the file stream and save it locally
            with drive_file.open(stream=True) as response:
                with open(file_path, 'wb') as file_out:
                    copyfileobj(response.raw, file_out)
            
            logger.info(f"File {drive_file.name} downloaded successfully to {file_path}.")
            return file_path  # Return the local file path
            
        except Exception as e:
            logger.error(f"Error downloading file {drive_file.name}: {e}")
            raise


