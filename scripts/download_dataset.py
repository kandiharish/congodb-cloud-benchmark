import os
import sys
import requests
from tqdm import tqdm
import gzip
import logging
import time

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

URL = "https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
FILE_PATH = os.path.join(RAW_DIR, "soc-pokec-relationships.txt.gz")


def get_remote_file_size(url, headers):
    try:
        response = requests.head(url, headers=headers, timeout=30)
        response.raise_for_status()
        return int(response.headers.get('content-length', 0))
    except Exception as e:
        logging.warning(f"Could not get remote file size: {e}")
        return 0

def download_file(url, filepath):
    """Downloads a file from a URL to a local path with a progress bar and robust resuming."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    total_size = get_remote_file_size(url, headers)
    
    if os.path.exists(filepath):
        local_size = os.path.getsize(filepath)
        if total_size and local_size == total_size:
            logging.info(f"File already exists and is complete at {filepath}. Skipping download.")
            return
    else:
        local_size = 0

    logging.info(f"Downloading dataset from {url}")
    
    max_retries = 10
    
    for attempt in range(1, max_retries + 1):
        if local_size > 0:
            headers['Range'] = f"bytes={local_size}-"
            mode = 'ab'
        else:
            if 'Range' in headers:
                del headers['Range']
            mode = 'wb'

        try:
            response = requests.get(url, stream=True, headers=headers, timeout=60)
            response.raise_for_status()
            
            # If server doesn't support partial content when requested, start over
            if local_size > 0 and response.status_code != 206:
                logging.warning("Server does not support resuming. Restarting download.")
                local_size = 0
                mode = 'wb'
                if 'Range' in headers:
                    del headers['Range']
                response = requests.get(url, stream=True, headers=headers, timeout=60)
                response.raise_for_status()
            
            # Ensure total_size is accurate based on response
            if not total_size:
                content_length = int(response.headers.get('content-length', 0))
                if response.status_code == 206:
                    total_size = local_size + content_length
                else:
                    total_size = content_length

            with open(filepath, mode) as file, tqdm(
                desc=os.path.basename(filepath),
                initial=local_size,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=8192):
                    if data:
                        size = file.write(data)
                        bar.update(size)
                        local_size += size
            
            # If we exit the context manager cleanly, verify completion
            if total_size and local_size >= total_size:
                logging.info("Download completed successfully.")
                return
            else:
                logging.warning("Connection dropped before completion. Will resume.")
                
        except Exception as e:
            logging.error(f"Attempt {attempt}/{max_retries} failed: {e}")
            if attempt == max_retries:
                logging.error("Max retries reached. Exiting.")
                sys.exit(1)
            time.sleep(5)


def validate_file(filepath):
    """Validates if the downloaded file is a valid gzip file and can be read."""
    logging.info("Validating downloaded gzip file...")
    try:
        file_size = os.path.getsize(filepath)
        logging.info(f"Downloaded file size: {file_size / (1024 * 1024):.2f} MB")
        
        # Test reading the first few lines to validate gzip integrity
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
        
        logging.info("Dataset validation passed.")
    except gzip.BadGzipFile:
        logging.error("Validation failed: The downloaded file is not a valid gzip file or is corrupted.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Validation failed with error: {e}")
        sys.exit(1)


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    download_file(URL, FILE_PATH)
    validate_file(FILE_PATH)
    
    logging.info("Next steps: Implement dataset subset generator for deterministic benchmark data.")

if __name__ == "__main__":
    main()
