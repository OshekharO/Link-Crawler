import json
import requests
import sys
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_url(api_entry):
    """Check if a URL is accessible"""
    name = api_entry['name']
    url = api_entry['url']
    
    # Skip URLs with placeholders like {imdbId}
    if '{' in url and '}' in url:
        print(f"⚠️  Skipping {name} (contains placeholders): {url}")
        return api_entry, True
    
    try:
        # Clean the URL for checking
        clean_url = url
        
        # For documentation URLs, try to get the main page
        if any(domain in url for domain in ['docs.', 'documentation']):
            # Try to get the root documentation page
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(
            clean_url, 
            headers=headers, 
            timeout=20,
            allow_redirects=True
        )
        
        # Consider 2xx and 3xx status codes as working
        if response.status_code < 400:
            print(f"✅ {name} is working: {url}")
            return api_entry, True
        else:
            print(f"❌ {name} returned status {response.status_code}: {url}")
            return api_entry, False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} failed with error: {e}")
        return api_entry, False

def main():
    # Read the current APIs file
    with open('apis.json', 'r', encoding='utf-8') as f:
        apis = json.load(f)
    
    print(f"Checking {len(apis)} API URLs...")
    
    # Check all URLs concurrently for better performance
    working_apis = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_api = {executor.submit(check_url, api): api for api in apis}
        
        for future in as_completed(future_to_api):
            api_entry, is_working = future.result()
            if is_working:
                working_apis.append(api_entry)
    
    print(f"\nResults:")
    print(f"Total APIs: {len(apis)}")
    print(f"Working APIs: {len(working_apis)}")
    print(f"Broken APIs removed: {len(apis) - len(working_apis)}")
    
    # Write the updated list back to the file
    with open('apis.json', 'w', encoding='utf-8') as f:
        json.dump(working_apis, f, indent=4, ensure_ascii=False)
    
    # Set output for the workflow
    if len(working_apis) < len(apis):
        print("Changes detected - file will be updated")
        sys.exit(0)  # Success with changes
    else:
        print("No changes needed")
        sys.exit(0)  # Success without changes

if __name__ == "__main__":
    main()
