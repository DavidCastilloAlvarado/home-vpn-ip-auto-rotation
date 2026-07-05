import json
import urllib3
import boto3
import os
import base64

def change_dns(public_ip):
    # Replace these variables with your actual values
    # SUBDOMAIN: mysub.domain.com
    ZONEID = os.getenv("ZONEID")
    RECORDID = os.getenv("RECORDID")
    api_url = f"https://api.hosting.ionos.com/dns/v1/zones/{ZONEID}/records/{RECORDID}"
    api_key = os.getenv("API_KEY")  # Retrieve API key from environment variable
    public_ip = public_ip  # Replace with the public IP you want to set
    
    headers = {
        'accept': 'application/json',
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    data = {
        "content": public_ip
    }

    http = urllib3.PoolManager()
    response = http.request(
        'PUT',
        api_url,
        body=json.dumps(data),
        headers=headers
    )

def lambda_handler(event, context):
    # SUBDOMAIN: mysub.domain.com
    encoded_body = event.get("body")
    decoded_bytes = base64.b64decode(encoded_body)
    decoded = decoded_bytes.decode("utf-8")
    body = {}
    for keyval in decoded.split("&", 1):
        key, val = keyval.split("=", 1)
        body[key] = val

    public_ip = body.get("public_ip")
    lambda_api_key = body.get("api_key")
    if lambda_api_key != os.getenv("lambda_api_key"):
        return {
            'statusCode': 403,
            'body': json.dumps({"status": "invalid api_key"})
        }
    change_dns(public_ip)
    return {
        'statusCode': 200,
        'body': json.dumps('VPN ready!')
    }
