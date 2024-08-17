import os
import zipfile
import logging
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('C:/Users/sanil/Desktop/Automate-backup-/path.env')

# Retrieve environment variables
DESTINATION_DIR = os.getenv('DESTINATION_DIR')

# Load encryption key
def load_key():
    if not os.path.exists('backup_key.key'):
        raise FileNotFoundError("Key file 'backup_key.key' not found.")
    return open('backup_key.key', 'rb').read()

# Decrypt the backup
def decrypt_backup(zip_filename):
    try:
        key = load_key()
        f = Fernet(key)
        with open(zip_filename, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        with open(zip_filename, 'wb') as file:
            file.write(decrypted_data)
        print(f"Backup decrypted successfully: {zip_filename}")
        logging.info(f"Backup decrypted successfully: {zip_filename}")
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        print(f"Decryption failed: {e}")

# Extract the backup zip file
def extract_backup(zip_filename):
    try:
        extract_folder = zip_filename.replace('.zip', '')
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
        print(f"Backup extracted to: {extract_folder}")
        logging.info(f"Backup extracted to: {extract_folder}")
    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        print(f"Extraction failed: {e}")

# Usage example
if __name__ == "__main__":
    logging.basicConfig(filename='decrypt_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    zip_filename = input("Enter the name of the zip file to decrypt (with .zip extension): ")
    
    if not os.path.exists(zip_filename):
        print(f"File {zip_filename} does not exist.")
    else:
        decrypt_backup(zip_filename)
        extract_backup(zip_filename)
