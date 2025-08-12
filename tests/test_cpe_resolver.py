# test_cpe_resolver.py - Tests for CPE resolver functionality
import unittest
import tempfile
import json
import os
import requests
from pathlib import Path
from unittest.mock import patch, Mock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from match.cpe_resolver import CPEResolver

class TestCPEResolver(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.cache_dir.mkdir()
        self.resolver = CPEResolver(str(self.cache_dir))
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_build_candidate_cpes(self):
        """Test building candidate CPE strings"""
        app_name = "test_app"
        version = "1.2.3"
        
        candidates = self.resolver.build_candidate_cpes(app_name, version)
        
        # Should generate multiple CPE patterns
        self.assertGreater(len(candidates), 0)
        
        # All should be valid CPE format
        for cpe in candidates:
            self.assertTrue(self.resolver._validate_cpe(cpe))
        
        # Should include version-specific patterns
        version_patterns = [cpe for cpe in candidates if "1.2.3" in cpe]
        self.assertGreater(len(version_patterns), 0)
        
        # Should include partial version patterns
        partial_patterns = [cpe for cpe in candidates if "1.2" in cpe]
        self.assertGreater(len(partial_patterns), 0)
    
    def test_build_candidate_cpes_no_version(self):
        """Test building CPEs when no version is provided"""
        app_name = "test_app"
        version = ""
        
        candidates = self.resolver.build_candidate_cpes(app_name, version)
        
        # Should still generate patterns
        self.assertGreater(len(candidates), 0)
        
        # Should not have version-specific patterns
        version_patterns = [cpe for cpe in candidates if ":1.2.3:" in cpe]
        self.assertEqual(len(version_patterns), 0)
    
    def test_validate_cpe(self):
        """Test CPE validation"""
        # Valid CPEs
        valid_cpes = [
            "cpe:2.3:a:vendor:product:1.0:*:*:*:*:*:*:*:*",
            "cpe:2.3:a:*:product:1.0:*:*:*:*:*:*:*:*",
            "cpe:2.3:a:vendor:product:*:*:*:*:*:*:*:*:*"
        ]
        
        for cpe in valid_cpes:
            self.assertTrue(self.resolver._validate_cpe(cpe))
        
        # Invalid CPEs
        invalid_cpes = [
            "cpe:2.3:vendor:product:1.0",  # Missing parts
            "cpe:2.4:a:vendor:product:1.0:*:*:*:*:*:*:*:*",  # Wrong version
            "invalid:cpe:format",
            ""
        ]
        
        for cpe in invalid_cpes:
            self.assertFalse(self.resolver._validate_cpe(cpe))
    
    def test_score_cpe_specificity(self):
        """Test CPE specificity scoring"""
        # More specific CPEs should score higher
        specific_cpe = "cpe:2.3:a:vendor:product:1.2.3:*:*:*:*:*:*:*:*"
        wildcard_cpe = "cpe:2.3:a:*:*:*:*:*:*:*:*:*:*:*"
        
        specific_score = self.resolver._score_cpe_specificity(specific_cpe)
        wildcard_score = self.resolver._score_cpe_specificity(wildcard_cpe)
        
        self.assertGreater(specific_score, wildcard_score)
    
    def test_cache_operations(self):
        """Test cache loading and saving"""
        # Test initial cache loading
        self.assertEqual(len(self.resolver.cache), 0)
        
        # Test cache saving
        test_data = {"test_key": "test_value"}
        self.resolver.cache.update(test_data)
        self.resolver._save_cache()
        
        # Test cache reloading
        new_resolver = CPEResolver(str(self.cache_dir))
        self.assertIn("test_key", new_resolver.cache)
        self.assertEqual(new_resolver.cache["test_key"], "test_value")
    
    def test_resolve_best_cpe_with_cache(self):
        """Test CPE resolution with caching"""
        app_name = "cached_app"
        version = "2.0"
        
        # First resolution should cache the result
        cpe1 = self.resolver.resolve_best_cpe(app_name, version)
        self.assertIsNotNone(cpe1)
        
        # Second resolution should use cache
        cpe2 = self.resolver.resolve_best_cpe(app_name, version)
        self.assertEqual(cpe1, cpe2)
        
        # Check cache was saved
        cache_file = self.cache_dir / "cpe_index.json"
        self.assertTrue(cache_file.exists())
        
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            cache_key = f"{app_name}:{version}"
            self.assertIn(cache_key, cache_data)
    
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful HTTP request"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.resolver._make_request("https://test.com")
        
        self.assertEqual(result, {"test": "data"})
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_make_request_timeout(self, mock_get):
        """Test HTTP request timeout handling"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = self.resolver._make_request("https://test.com")
        
        self.assertIsNone(result)
        # Should retry multiple times
        self.assertGreater(mock_get.call_count, 1)
    
    @patch('requests.Session.get')
    def test_make_request_rate_limit(self, mock_get):
        """Test HTTP 429 rate limit handling"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        result = self.resolver._make_request("https://test.com")
        
        self.assertIsNone(result)
        # Should retry with longer delays for rate limiting
        self.assertGreater(mock_get.call_count, 1)
    
    @patch('requests.Session.get')
    def test_search_nvd_cpe(self, mock_get):
        """Test NVD CPE search functionality"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "cpes": [
                {"cpeName": "cpe:2.3:a:vendor:product:1.0:*:*:*:*:*:*:*:*"},
                {"cpeName": "cpe:2.3:a:vendor:product:2.0:*:*:*:*:*:*:*:*"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.resolver.search_nvd_cpe("test_app", "1.0")
        
        self.assertIsNotNone(result)
        self.assertTrue(self.resolver._validate_cpe(result))
    
    def test_normalize_app_name(self):
        """Test app name normalization for CPE generation"""
        test_cases = [
            ("Test App", "test_app"),
            ("Test-App", "test_app"),
            ("Test.App", "testapp"),
            ("Test123App", "test123app"),
            ("Test App 123", "test_app_123")
        ]
        
        for input_name, expected in test_cases:
            candidates = self.resolver.build_candidate_cpes(input_name, "1.0")
            # All generated CPEs should contain the normalized name
            for cpe in candidates:
                self.assertIn(expected, cpe)

if __name__ == "__main__":
    unittest.main()
