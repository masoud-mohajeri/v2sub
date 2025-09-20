#!/usr/bin/env python3
"""
V2Ray Subscription Processor

This script processes v2ray subscription links from subs.txt (CSV format) and combines
all configurations into a single sum.txt file. It handles both base64 encoded and raw
configuration links.
"""

import csv
import base64
import requests
import sys
import os
from urllib.parse import urlparse
import time
from typing import List, Set

def is_base64_encoded(text: str) -> bool:
    """Check if a string is base64 encoded."""
    try:
        # Try to decode and re-encode to check if it's valid base64
        decoded = base64.b64decode(text)
        encoded = base64.b64encode(decoded).decode('utf-8')
        return encoded == text
    except Exception:
        return False

def fetch_subscription_content(url: str, timeout: int = 30) -> str:
    """Fetch content from a subscription URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def decode_base64_configs(content: str) -> List[str]:
    """Decode base64 encoded v2ray configurations."""
    configs = []
    try:
        # Try to decode the entire content as base64
        decoded = base64.b64decode(content).decode('utf-8')
        # Split by newlines to get individual configs
        configs = [line.strip() for line in decoded.split('\n') if line.strip()]
    except Exception as e:
        print(f"Error decoding base64 content: {e}")
    return configs

def extract_configs_from_content(content: str) -> List[str]:
    """Extract v2ray configurations from content (handles both base64 and raw)."""
    configs = []
    
    # First, try to decode as base64
    if is_base64_encoded(content.strip()):
        configs = decode_base64_configs(content)
    else:
        # Treat as raw content, split by lines
        configs = [line.strip() for line in content.split('\n') if line.strip()]
    
    return configs

def process_subscription_file(sub_file: str) -> Set[str]:
    """Process the subscription file containing subscription links."""
    all_configs = set()  # Use set to avoid duplicates
    
    if not os.path.exists(sub_file):
        print(f"Error: {sub_file} not found!")
        return all_configs
    
    try:
        with open(sub_file, 'r', encoding='utf-8') as file:
            # Read all content
            content = file.read().strip()
            
            # Split by comma to get URLs (handles both single line with commas and multiple lines)
            urls = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    # Split by comma and add each URL
                    line_urls = [url.strip() for url in line.split(',') if url.strip()]
                    urls.extend(line_urls)
            
            print(f"Found {len(urls)} subscription URLs to process...")
            
            for i, url in enumerate(urls, 1):
                print(f"Processing {i}/{len(urls)}: {url}")
                
                # Fetch content from URL
                content = fetch_subscription_content(url)
                
                if content:
                    # Extract configurations
                    configs = extract_configs_from_content(content)
                    print(f"  Found {len(configs)} configurations")
                    
                    # Add to our set (automatically removes duplicates)
                    for config in configs:
                        if config and config.startswith(('vmess://', 'vless://', 'ss://', 'trojan://', 'hysteria2://')):
                            all_configs.add(config)
                else:
                    print(f"  Failed to fetch content from {url}")
                
                # Add a small delay to be respectful to servers
                time.sleep(1)
                
    except Exception as e:
        print(f"Error processing {sub_file}: {e}")
    
    return all_configs

def write_sum_file(configs: Set[str], output_file: str):
    """Write all configurations to the output file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            for config in sorted(configs):  # Sort for consistent output
                file.write(config + '\n')
        print(f"Successfully wrote {len(configs)} configurations to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

def main():
    """Main function to process subscriptions."""
    sub_file = "subs.txt"
    output_file = "sum.txt"
    
    print("V2Ray Subscription Processor")
    print("=" * 40)
    
    # Process subscription file
    all_configs = process_subscription_file(sub_file)
    
    if all_configs:
        # Write to output file
        write_sum_file(all_configs, output_file)
        print(f"\nProcessing complete! Found {len(all_configs)} unique configurations.")
    else:
        print("No configurations found!")
        sys.exit(1)

if __name__ == "__main__":
    main()
