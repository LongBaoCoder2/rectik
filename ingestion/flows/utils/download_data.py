import os
import requests
import zipfile
import logging
import gdown

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Drive file ID and the destination folder for the data
FILE_ID = "1qe5hOSBxzIuxBb1G_Ih5X-O65QElollE"
DEST_FOLDER = os.getenv("DATA_DIR", "./data")  # Path inside the Docker container where data should be placed
ZIP_PATH = os.path.join(DEST_FOLDER, "KuaiRec.zip")

def download_and_unzip(file_id, zip_path, extract_to):
    """
    Downloads a zip file from Google Drive using gdown and extracts it.
    """
    # Construct the download URL
    url = f"https://drive.google.com/uc?id={file_id}"
    
    print("Downloading data from Google Drive using gdown...")
    gdown.download(url, zip_path, quiet=False)

    print("Unzipping the downloaded file...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    print(f"Data has been extracted to {extract_to}")
    os.remove(zip_path)  # Clean up the zip file


def download_file_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive given a file ID.
    """
    URL = "https://drive.google.com/"
    
    logging.debug(f"Starting download from Google Drive with file ID: {file_id}")
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    logging.debug(f"Initial response status code: {response.status_code}")
    
    token = get_confirm_token(response)
    
    if token:
        logging.debug(f"Found confirmation token: {token}")
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
        logging.debug(f"Response after confirming token: {response.status_code}")
    
    save_response_content(response, destination)

def get_confirm_token(response):
    """
    Retrieves a confirmation token for downloading large files from Google Drive.
    """
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            logging.debug(f"Download warning token detected: {value}")
            return value
    logging.debug("No download warning token found.")
    return None

def save_response_content(response, destination):
    """
    Saves the content of the response to the destination file.
    """
    CHUNK_SIZE = 32768
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    logging.debug(f"Saving content to: {destination}")
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # Filter out keep-alive new chunks
                f.write(chunk)
    
    logging.info(f"File saved to {destination}")

def unzip_file(zip_path, extract_to):
    """
    Unzips a file to the specified directory.
    """
    logging.debug(f"Unzipping file: {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logging.info(f"File unzipped to {extract_to}")

def remove_non_csv_files(directory):
    """
    Removes all files in the specified directory that are not in CSV format.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                logging.debug(f"Removing non-CSV file: {file_path}")
                os.remove(file_path)
    logging.info("Non-CSV files removed.")

def main():
    """
    Main function to download, unzip, and clean up the data.
    """
    logging.info("Starting the data download process...")
    logging.debug(f"Destination folder: {DEST_FOLDER}, Zip path: {ZIP_PATH}")
    
    try:
        logging.info("Downloading data from Google Drive...")
        download_file_from_google_drive(FILE_ID, ZIP_PATH)

        logging.info("Unzipping the downloaded file...")
        unzip_file(ZIP_PATH, DEST_FOLDER)

        logging.info(f"Data has been extracted to {DEST_FOLDER}")
        os.remove(ZIP_PATH)  # Clean up the zip file
        logging.debug(f"Zip file {ZIP_PATH} removed.")

        logging.info("Removing non-CSV files...")
        remove_non_csv_files(DEST_FOLDER)
    
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    # main()
    download_and_unzip(FILE_ID, ZIP_PATH, DEST_FOLDER)
