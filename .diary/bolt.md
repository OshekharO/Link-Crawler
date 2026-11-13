## 2026-11-13 - API Checker & Frontend Dashboard Optimization

**Learning:** 
- `requests.get` without a session creates a new TCP connection and SSL handshake per thread, increasing latency and resource usage in concurrent checks.
- API endpoints often return 401 Unauthorized, 403 Forbidden, or 405 Method Not Allowed on root GET requests even when the server/service is online; strict `< 400` checks can lead to false negatives for protected or doc-only API roots.
- Frontend rendering via direct string concatenation in jQuery lacks error handling for network/JSON failures and exposes the UI to XSS risks if API metadata is untrusted.

**Action:**
- Implemented `requests.Session` with connection pooling in `check_apis.py`, split connect/read timeouts `(5, 15)`, and expanded status code validation to treat server-responsive codes (`< 500` except 404) as online.
- Added comprehensive unit tests (`test_check_apis.py`) using `unittest.mock`.
- Enhanced `index.html` with error handling (`.fail()`), alphabetical sorting of API entries, and safe DOM manipulation (`textContent`) to prevent XSS and improve UX.
