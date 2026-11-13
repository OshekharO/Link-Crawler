import unittest
from unittest.mock import MagicMock, patch
import requests
from check_apis import check_url

class TestCheckApis(unittest.TestCase):
    
    def test_check_url_placeholder(self):
        entry = {"name": "Test API", "url": "https://example.com/movie/{imdbId}", "status": "offline"}
        result = check_url(entry)
        self.assertEqual(result["status"], "online")

    @patch('check_apis.requests.Session')
    def test_check_url_online_200(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        
        entry = {"name": "Test API", "url": "https://example.com/api", "status": "offline"}
        result = check_url(entry, session=mock_session)
        self.assertEqual(result["status"], "online")
        mock_session.get.assert_called_once()

    @patch('check_apis.requests.Session')
    def test_check_url_responsive_403(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_session.get.return_value = mock_response
        
        entry = {"name": "Test API", "url": "https://example.com/api", "status": "offline"}
        result = check_url(entry, session=mock_session)
        self.assertEqual(result["status"], "online")

    @patch('check_apis.requests.Session')
    def test_check_url_offline_404(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response
        
        entry = {"name": "Test API", "url": "https://example.com/api", "status": "online"}
        result = check_url(entry, session=mock_session)
        self.assertEqual(result["status"], "offline")

    @patch('check_apis.requests.Session')
    def test_check_url_exception(self, mock_session_class):
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        entry = {"name": "Test API", "url": "https://example.com/api", "status": "online"}
        result = check_url(entry, session=mock_session)
        self.assertEqual(result["status"], "offline")

if __name__ == '__main__':
    unittest.main()
