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