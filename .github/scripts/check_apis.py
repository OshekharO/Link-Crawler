import json
import requests
import sys
import os
import threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

thread_local = threading.local()

def get_session():
    """Get thread-local requests session for connection reuse (HTTP keep-alive)."""
    if not hasattr(thread_local, "session"):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        thread_local.session = session
    return thread_local.session

def check_url(api_entry):
    """Check if a URL is accessible and update status"""
    entry = dict(api_entry)
    name = entry['name']
    url = entry['url']
    
    # URLs with placeholders like {imdbId} default to online (or skip live request)
    if '{' in url and '}' in url:
        print(f"⚠️  Skipping live check for {name} (contains placeholders): {url}")
        entry['status'] = 'online'
        return entry
    
    try:
        clean_url = url
        if any(domain in url for domain in ['docs.', 'documentation']):
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}"
        
        session = get_session()
        response = session.get(
            clean_url, 
            timeout=20,
            allow_redirects=True
        )
        
        if response.status_code < 400:
            print(f"✅ {name} is online: {url}")
            entry['status'] = 'online'
        else:
            print(f"❌ {name} returned status {response.status_code}: {url}")
            entry['status'] = 'offline'
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} failed with error: {e}")
        entry['status'] = 'offline'

    return entry

def main():
    # Read the current APIs file with robust error handling
    try:
        with open('apis.json', 'r', encoding='utf-8') as f:
            apis = json.load(f)
    except FileNotFoundError:
        print("❌ Error: apis.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse apis.json as valid JSON: {e}")
        sys.exit(1)
    
    print(f"Checking {len(apis)} API URLs...")
    
    updated_apis = [None] * len(apis)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(check_url, api): i for i, api in enumerate(apis)}
        
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            updated_apis[i] = future.result()
    
    online_count = sum(1 for api in updated_apis if api.get('status') == 'online')
    offline_count = sum(1 for api in updated_apis if api.get('status') == 'offline')

    print(f"\nResults:")
    print(f"Total APIs: {len(updated_apis)}")
    print(f"Online APIs: {online_count}")
    print(f"Offline APIs: {offline_count}")
    
    # Write the updated list back to the file
    with open('apis.json', 'w', encoding='utf-8') as f:
        json.dump(updated_apis, f, indent=4, ensure_ascii=False)
    
    print("apis.json successfully updated.")
    sys.exit(0)

if __name__ == "__main__":
    main()
