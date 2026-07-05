"""
This program send a POST request to a lambda function in which
a program will use this publicIP to update the A record in my Domain
using the IONOS DNS api service.
"""
import requests as r
import logging
from datetime import datetime
import os
import json


# Create a unique filename based on the current datetime
curr_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"{curr_dir}/logs/app_{timestamp}.log"

# Configure logging
logging.basicConfig(
    filename=log_filename,                # Unique log file name
    filemode='w',                         # Open in write mode (create a new file each time)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    level=logging.DEBUG                    # Minimum level of messages to log
)

# Current Ip value
ip_file = f"{curr_dir}/current_ip.json"
# SUBDOMAIN: mysubdomain

CUSTOMDDNS_SVC = os.getenv("CUSTOMDDNS_SVC")
API_KEY = os.getenv("API_KEY")

def get_last_ip():
    # Check if the file exists; if not, create it with an empty dictionary
    if not os.path.exists(ip_file):
        with open(ip_file, 'w') as file:
            json.dump({}, file)  # Initialize with an empty dictionary or any default data structure you prefer

    # Open the file and load the data
    with open(ip_file, 'r') as file:
        data = json.load(file)
    return data

def save_curr_ip(ip):
    with open(ip_file, 'w') as file:
        json.dump({"ip": ip}, file, indent=4) 

def main():
    response = r.get("https://icanhazip.com")
    if response.status_code != 200:
        logging.error("icanhazip service not available")
        return
    myip = response.text.strip()
    last_ip = get_last_ip().get("ip")
    if myip == last_ip:
        logging.info(f"The ip did not change ip: {last_ip}")
        return
    
    payload = {
        "api_key": API_KEY,
        "public_ip": myip,
    }
    
    response = r.post(CUSTOMDDNS_SVC, data=payload)
    
    if response.status_code != 200:
        logging.error(f"Custom DDNS service failed: {response.text}")
        return
    
    logging.info(response.text)
    
    save_curr_ip(myip)
    
    

if __name__ == "__main__":
    main()
