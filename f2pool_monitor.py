#!/usr/bin/env python3
import requests
import sys
import json
import time
import argparse
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/var/log/zabbix/f2pool_monitor.log'
)

# Configuration
API_BASE_URL = "https://api.f2pool.com/v2"
CONFIG = {
    "api_secret": "YOUR_API_SECRET",     # Replace with your F2P-API-SECRET
    "currency": "bitcoin",               # Cryptocurrency to monitor (bitcoin, bitcoin-cash, or litecoin)
}

# Supported currencies for hashrate monitoring
SUPPORTED_CURRENCIES = ["bitcoin", "bitcoin-cash", "litecoin"]

def parse_args():
    parser = argparse.ArgumentParser(description='F2Pool Hashrate Monitor for Zabbix')
    parser.add_argument('username', help='F2Pool username to monitor')
    return parser.parse_args()

def validate_config():
    """
    Validate configuration settings
    """
    if CONFIG["currency"] not in SUPPORTED_CURRENCIES:
        logging.error(f"Unsupported currency: {CONFIG['currency']}. Must be one of: {', '.join(SUPPORTED_CURRENCIES)}")
        return False
    return True

def hash_to_th(hash_rate):
    """
    Convert hashrate from H/s to TH/s
    """
    return hash_rate / 1e12 if hash_rate else 0

def get_hashrate_info(username):
    """
    Fetch hashrate data from F2Pool API
    """
    try:
        endpoint = f"{API_BASE_URL}/hash_rate/info"
        headers = {
            "Content-Type": "application/json",
            "F2P-API-SECRET": CONFIG["api_secret"]
        }
        
        payload = {
            "currency": CONFIG["currency"],
            "mining_user_name": username
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code != 200:
            error_data = response.json()
            logging.error(f"API error: {error_data.get('msg', 'Unknown error')}")
            return None
            
        data = response.json()
        
        if 'code' in data and 'msg' in data:
            logging.error(f"API error: {data['msg']}")
            return None
            
        return data
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return None

def main():
    args = parse_args()
    username = args.username
    
    if not validate_config():
        sys.exit(1)
    
    hashrate_data = get_hashrate_info(username)
    if not hashrate_data:
        sys.exit(1)
    
    info_data = hashrate_data.get('info', {})
    
    # Get raw values and convert to TH/s
    metrics = {
        'hash_rate': round(hash_to_th(info_data.get('hash_rate', 0)), 2),
        'h1_hash_rate': round(hash_to_th(info_data.get('h1_hash_rate', 0)), 2),
        'h24_hash_rate': round(hash_to_th(info_data.get('h24_hash_rate', 0)), 2),
        'h1_stale_rate': round(hash_to_th(info_data.get('h1_stale_hash_rate', 0)), 2),
        'h24_stale_rate': round(hash_to_th(info_data.get('h24_stale_hash_rate', 0)), 2),
        'h24_delay_rate': round(hash_to_th(info_data.get('h24_delay_hash_rate', 0)), 2),
        'local_hash_rate': round(hash_to_th(info_data.get('local_hash_rate', 0)), 2),
        'h24_local_rate': round(hash_to_th(info_data.get('h24_local_hash_rate', 0)), 2),
        'name': info_data.get('name', '')
    }
    
    # Calculate rejection rate percentage
    if metrics['h24_hash_rate'] > 0:
        rejection_rate = (metrics['h24_stale_rate'] / metrics['h24_hash_rate']) * 100
        metrics['rejection_rate'] = round(rejection_rate, 2)
    else:
        metrics['rejection_rate'] = 0
    
    # Print JSON output for Zabbix
    print(json.dumps(metrics))

if __name__ == "__main__":
    main()
