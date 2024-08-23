import os
import shutil
import zipfile
import datetime
import logging
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
SOURCE_DIR = os.getenv('SOURCE_DIR')
DESTINATION_DIR = os.getenv('DESTINATION_DIR')

# Generate or load encryption key
def generate_key():
    key = Fernet.generate_key()
    with open('backup_key.key', 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    if not os.path.exists('backup_key.key'):
        print("Key file not found. Generating a new key.")
        generate_key()
    return open('backup_key.key', 'rb').read()

# Validate environment variables
if not all([SOURCE_DIR, DESTINATION_DIR]):
    raise EnvironmentError("One or more environment variables are not set")

# Setup logging
logging.basicConfig(filename='backup_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a backup
def create_backup():
    backup_folder = os.path.join(DESTINATION_DIR, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(backup_folder)
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        relative_path = os.path.relpath(root, SOURCE_DIR)
        dest_dir = os.path.join(backup_folder, relative_path)
        os.makedirs(dest_dir, exist_ok=True)
        
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            shutil.copy2(source_file, dest_file)
    
    logging.info(f"Backup created successfully at {backup_folder}")
    return backup_folder

# Compress the backup
def compress_backup(backup_folder):
    zip_filename = f"{backup_folder}.zip"
    with zipfile.ZipFile(zip_filename, 'w') as backup_zip:
        for folder_name, subfolders, filenames in os.walk(backup_folder):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                backup_zip.write(file_path, os.path.relpath(file_path, backup_folder))
    logging.info(f"Backup compressed to {zip_filename}")
    return zip_filename

# Encrypt the backup
def encrypt_backup(zip_filename):
    try:
        key = load_key()
        f = Fernet(key)
        with open(zip_filename, 'rb') as file:
            file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        with open(zip_filename, 'wb') as file:
            file.write(encrypted_data)
        logging.info(f"Backup encrypted with key saved in 'backup_key.key'")
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        print(f"Encryption failed: {e}")


# Verify backup integrity
def generate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_backup(zip_filename):
    checksum = generate_checksum(zip_filename)
    logging.info(f"{zip_filename} - Checksum: {checksum}")

if __name__ == "__main__":
    try:
        backup_folder = create_backup()
        zip_filename = compress_backup(backup_folder)
        encrypt_backup(zip_filename)
        verify_backup(zip_filename)
        logging.info("Backup process completed.")
        print("Backup successful.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"Backup failed: {e}")
