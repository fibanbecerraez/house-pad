import os
import requests
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("RENDER_API_KEY")

# Base URL for Render API
BASE_URL = "https://api.render.com/v1"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

def list_services():
    """Fetch a list of services from Render."""
    url = f"{BASE_URL}/services"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        services = response.json()
        print("Services:")
        for service in services:
            print(f"- {service['name']} ({service['type']})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def get_service_details(service_id):
    """Fetch details for a specific service."""
    url = f"{BASE_URL}/services/{service_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        details = response.json()
        print(f"Service Details for {service_id}:")
        print(details)
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Fetching services...")
    list_services()
