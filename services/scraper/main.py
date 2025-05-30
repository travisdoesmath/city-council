import os
import requests
import boto3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

SESSION_DATE = "20250520"
BASE_URL = f"https://www.austintexas.gov/department/city-council/2025/{SESSION_DATE}-wrk.htm"
BUCKET_NAME = os.getenv("S3_BUCKET")

s3 = boto3.client("s3")

def fetch_meeting_links():
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "document.cfm" in href.lower() and a.text.strip() != '':
            full_url = urljoin(BASE_URL, href)
            filename = a.text.strip().replace(",", "").replace(" ", "_").replace("_-_", "-").replace(":_","-") + ".pdf"
            if not filename.startswith(SESSION_DATE):
                filename = f"{SESSION_DATE}_{filename}"
            
            links.append((filename, full_url))

    return links

def file_exists_in_s3(key):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except s3.exceptions.ClientError:
        return False

def upload_to_s3(filename, content):
    s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=content)
    print(f"Uploaded to S3: {filename}")

def download_and_upload(links):
    for filename, url in links:
        if file_exists_in_s3(filename):
            print(f"Skipping (already in S3): {filename}")
            continue

        print(f"Downloading: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            upload_to_s3(filename, response.content)
        else:
            print(f"Failed to download {url} (status {response.status_code})")

if __name__ == "__main__":
    links = fetch_meeting_links()
    print(f"Found {len(links)} potential files")
    download_and_upload(links)