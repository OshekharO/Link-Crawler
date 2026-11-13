## 2026-11-13 - HTTP Connection Reuse and Robust UI Error Handling

**Learning:** 
- In Python scripts executing concurrent network checks (`ThreadPoolExecutor`), recreating `requests.get` without a session results in redundant TCP handshakes and TLS negotiations per request. Using `requests.Session()` with thread-local storage (`threading.local`) enables HTTP connection reuse (keep-alive) and significantly improves performance.
- In client-side HTML pages fetching static JSON data via AJAX (`$.getJSON`), lacking loading states and `.fail()` error handlers leaves the UI unresponsive and blank if the resource fails to load or parse.

**Action:**
- Integrated thread-local `requests.Session()` in `.github/scripts/check_apis.py` and added robust JSON parsing error handling.
- Added loading placeholder and `.fail()` error handling in `index.html` to guarantee responsive UX feedback during async data fetching.
