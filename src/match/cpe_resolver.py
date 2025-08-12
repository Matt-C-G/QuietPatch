# cpe_resolver.py - CPE matching and resolution for vulnerability scanning
import json
import time
import requests
from pathlib import Path
from typing import List, Optional, Dict
from urllib.parse import quote_plus

class CPEResolver:
    """CPE resolver with local caching and fallback strategies"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "cpe_index.json"
        self.cache = self._load_cache()
        self.session = requests.Session()
        self.session.timeout = 10  # 10 second timeout
        
    def _load_cache(self) -> Dict:
        """Load existing cache or create new one"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError:
            pass
    
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """Make HTTP request with timeout and backoff"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    return None
                time.sleep(base_delay * (2 ** attempt))
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [429, 500, 502, 503, 504]:
                    if attempt == max_retries - 1:
                        return None
                    delay = base_delay * (2 ** attempt)
                    if e.response.status_code == 429:
                        delay = max(delay, 5.0)  # Longer delay for rate limiting
                    time.sleep(delay)
                else:
                    return None
            except Exception:
                if attempt == max_retries - 1:
                    return None
                time.sleep(base_delay * (2 ** attempt))
        
        return None
    
    def build_candidate_cpes(self, app_name: str, version: str) -> List[str]:
        """Build candidate CPE strings for an application"""
        candidates = []
        
        # Normalize app name for CPE format
        normalized_name = app_name.lower().replace(' ', '_').replace('-', '_')
        normalized_name = ''.join(c for c in normalized_name if c.isalnum() or c == '_')
        
        # Common CPE patterns
        patterns = [
            f"cpe:2.3:a:*:{normalized_name}:{version}:*:*:*:*:*:*:*:*",
            f"cpe:2.3:a:{normalized_name}:{normalized_name}:{version}:*:*:*:*:*:*:*",
            f"cpe:2.3:a:*:{normalized_name}:*:*:*:*:*:*:*:*:*",
            f"cpe:2.3:a:{normalized_name}:{normalized_name}:*:*:*:*:*:*:*:*:*"
        ]
        
        # Add version-specific patterns
        if version:
            # Handle version formats like "1.2.3", "1.2", "1"
            version_parts = version.split('.')
            for i in range(len(version_parts)):
                partial_version = '.'.join(version_parts[:i+1])
                patterns.append(f"cpe:2.3:a:*:{normalized_name}:{partial_version}:*:*:*:*:*:*:*:*")
                patterns.append(f"cpe:2.3:a:{normalized_name}:{normalized_name}:{partial_version}:*:*:*:*:*:*:*:*")
        
        return list(set(patterns))  # Remove duplicates
    
    def resolve_best_cpe(self, app_name: str, version: str) -> Optional[str]:
        """Resolve the best CPE match for an application"""
        cache_key = f"{app_name}:{version}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Build candidate CPEs
        candidates = self.build_candidate_cpes(app_name, version)
        
        # Try to find exact matches first
        for cpe in candidates:
            if self._validate_cpe(cpe):
                # Cache the result
                self.cache[cache_key] = cpe
                self._save_cache()
                return cpe
        
        # If no exact match, try to find the most specific one
        best_cpe = None
        best_score = -1
        
        for cpe in candidates:
            score = self._score_cpe_specificity(cpe)
            if score > best_score:
                best_score = score
                best_cpe = cpe
        
        if best_cpe:
            self.cache[cache_key] = best_cpe
            self._save_cache()
        
        return best_cpe
    
    def _validate_cpe(self, cpe: str) -> bool:
        """Basic CPE format validation"""
        if not cpe.startswith("cpe:2.3:"):
            return False
        
        parts = cpe.split(":")
        if len(parts) < 11:
            return False
        
        return True
    
    def _score_cpe_specificity(self, cpe: str) -> int:
        """Score CPE based on specificity (higher = more specific)"""
        score = 0
        
        # Prefer vendor-specific over wildcard
        if cpe.split(":")[3] != "*":
            score += 10
        
        # Prefer product-specific over wildcard
        if cpe.split(":")[4] != "*":
            score += 10
        
        # Prefer version-specific over wildcard
        if cpe.split(":")[5] != "*":
            score += 20
        
        # Prefer longer version strings
        version = cpe.split(":")[5]
        if version != "*":
            score += len(version)
        
        return score
    
    def search_nvd_cpe(self, app_name: str, version: str) -> Optional[str]:
        """Search NVD for CPE matches (fallback method)"""
        try:
            # Search NVD CPE API
            search_url = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
            params = {
                "keywordSearch": f"{app_name} {version}",
                "resultsPerPage": 5
            }
            
            result = self._make_request(search_url, params=params)
            if result and "cpes" in result:
                for cpe in result["cpes"]:
                    cpe_name = cpe.get("cpeName", "")
                    if cpe_name and self._validate_cpe(cpe_name):
                        return cpe_name
            
        except Exception:
            pass
        
        return None
