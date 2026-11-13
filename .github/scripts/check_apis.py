import json
import requests
import sys
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_url(api_entry, session=None):
    """Check if a URL is accessible and update status using connection pooling and robust status validation."""
    entry = dict(api_entry)
    name = entry.get('name', 'Unknown')
    url = entry.get('url', '')
    
    # URLs with placeholders like {imdbId} default to online (skip live request)
    if '{' in url and '}' in url:
        print(f"⚠️  Skipping live check for {name} (contains placeholders): {url}")
        entry['status'] = 'online'
        return entry
    
    req_session = session if session is not None else requests
    
    try:
        clean_url = url
        if any(domain in url for domain in ['docs.', 'documentation']):
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use split timeout (5s connect, 15s read) for faster failure detection
        response = req_session.get(
            clean_url, 
            headers=headers, 
            timeout=(5, 15),
            allow_redirects=True
        )
        
        # Consider server online if status code is successful (< 400) or responsive (< 500, e.g. 401/403/405 auth/method restrictions)
        if response.status_code < 500 and response.status_code != 404:
            print(f"✅ {name} is online: {url} (status {response.status_code})")
            entry['status'] = 'online'
        else:
            print(f"❌ {name} returned status {response.status_code}: {url}")
            entry['status'] = 'offline'
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} failed with error: {e}")
        entry['status'] = 'offline'

    return entry

def main():
    # Read the current APIs file
    try:
        with open('apis.json', 'r', encoding='utf-8') as f:
            apis = json.load(f)
    except Exception as e:
        print(f"❌ Error reading apis.json: {e}")
        sys.exit(1)
    
    print(f"Checking {len(apis)} API URLs with connection pooling...")
    
    updated_apis = [None] * len(apis)
    
    # Use requests.Session for connection reuse and performance optimization across threads
    with requests.Session() as session, ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {executor.submit(check_url, api, session): i for i, api in enumerate(apis)}
        
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                updated_apis[i] = future.result()
            except Exception as e:
                print(f"❌ Thread execution error for API index {i}: {e}")
                updated_apis[i] = dict(apis[i])
                updated_apis[i]['status'] = 'offline'
    
    online_count = sum(1 for api in updated_apis if api and api.get('status') == 'online')
    offline_count = sum(1 for api in updated_apis if api and api.get('status') == 'offline')

    print(f"\nResults:")
    print(f"Total APIs: {len(updated_apis)}")
    print(f"Online APIs: {online_count}")
    print(f"Offline APIs: {offline_count}")
    
    # Write the updated list back to the file
    try:
        with open('apis.json', 'w', encoding='utf-8') as f:
            json.dump(updated_apis, f, indent=4, ensure_ascii=False)
        print("apis.json successfully updated.")
    except Exception as e:
        print(f"❌ Error writing apis.json: {e}")
        sys.exit(1)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
