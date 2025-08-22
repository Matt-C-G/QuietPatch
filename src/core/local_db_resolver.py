# local_db_resolver.py - Local database lookup for offline CVE resolution
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import csv
import io

class LocalDBResolver:
    """Resolve CVEs from local database files instead of NVD API"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or os.environ.get("QP_DATA_DIR", "data"))
        self.db_dir = self.data_dir / "db"
        self._load_databases()
    
    def _load_databases(self):
        """Load all database files into memory"""
        try:
            # Load CPE to CVE mappings
            cpe_file = self.db_dir / "cpe_to_cves.json"
            if cpe_file.exists():
                with open(cpe_file, 'r') as f:
                    self.cpe_to_cves = json.load(f)
            else:
                self.cpe_to_cves = {}
            
            # Load CVE metadata
            meta_file = self.db_dir / "cve_meta.json"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    self.cve_meta = json.load(f)
            else:
                self.cve_meta = {}
            
            # Load KEV data
            kev_file = self.db_dir / "kev.json"
            if kev_file.exists():
                with open(kev_file, 'r') as f:
                    self.kev_data = json.load(f)
            else:
                self.kev_data = {}
            
            # Load EPSS data
            epss_file = self.db_dir / "epss.csv"
            if epss_file.exists():
                self.epss_data = {}
                with open(epss_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.epss_data[row['cve_id']] = float(row['epss_score'])
            else:
                self.epss_data = {}
            
            # Load aliases
            aliases_file = self.db_dir / "aliases.json"
            if aliases_file.exists():
                with open(aliases_file, 'r') as f:
                    self.aliases = json.load(f)
            else:
                self.aliases = {}
            
            # Load affects data for version-aware matching
            affects_file = self.db_dir / "affects.json"
            if affects_file.exists():
                with open(affects_file, 'r') as f:
                    self.affects = json.load(f)
            else:
                self.affects = {}
                
        except Exception as e:
            print(f"Warning: Failed to load local database: {e}")
            self.cpe_to_cves = {}
            self.cve_meta = {}
            self.kev_data = {}
            self.epss_data = {}
            self.aliases = {}
            self.affects = {}
    
    def _normalize_app_name(self, name: str) -> str:
        """Normalize app name using aliases"""
        name_lower = name.lower()
        for alias, canonical in self.aliases.items():
            if alias.lower() == name_lower:
                return canonical
        return name
    
    def _version_in_range(self, app_version: str, min_ver: str, max_ver: str) -> bool:
        """Check if app version is in the affected range"""
        try:
            # Simple version comparison - can be enhanced
            app_parts = [int(x) for x in app_version.split('.')]
            min_parts = [int(x) for x in min_ver.split('.')]
            max_parts = [int(x) for x in max_ver.split('.')]
            
            # Pad with zeros for comparison
            max_len = max(len(app_parts), len(min_parts), len(max_parts))
            app_parts.extend([0] * (max_len - len(app_parts)))
            min_parts.extend([0] * (max_len - len(min_parts)))
            max_parts.extend([0] * (max_len - len(max_parts)))
            
            return app_parts >= min_parts and app_parts <= max_parts
        except:
            return True  # If version parsing fails, assume affected
    
    def resolve_cves_for_app(self, app_name: str, app_version: str = "") -> List[Dict]:
        """Resolve CVEs for an app using local database"""
        normalized_name = self._normalize_app_name(app_name)
        vulns = []
        
        # Check if we have CPE mappings for this app
        if normalized_name in self.cpe_to_cves:
            for cve_info in self.cpe_to_cves[normalized_name]:
                cve_id = cve_info.get("cve_id")
                if not cve_id:
                    continue
                
                # Check version-aware matching
                if normalized_name in self.affects and cve_id in self.affects[normalized_name]:
                    version_rule = self.affects[normalized_name][cve_id]
                    min_ver = version_rule.get("min_version")
                    max_ver = version_rule.get("max_version")
                    
                    if min_ver or max_ver:
                        if not self._version_in_range(app_version, min_ver or "0", max_ver or "999"):
                            continue  # Version not affected
                
                # Get CVE metadata
                cve_data = self.cve_meta.get(cve_id, {})
                severity = cve_data.get("severity", "unknown")
                cvss = cve_data.get("cvss")
                description = cve_data.get("description", "")
                
                # Check if it's a known exploited vulnerability
                is_kev = cve_id in self.kev_data
                kev_action = self.kev_data.get(cve_id, {}).get("cisaRequiredAction", "") if is_kev else ""
                
                # Get EPSS score
                epss_score = self.epss_data.get(cve_id, 0.0)
                
                vuln = {
                    "cve_id": cve_id,
                    "severity": severity,
                    "cvss": cvss,
                    "summary": description,
                    "is_kev": is_kev,
                    "kev_action": kev_action,
                    "epss_score": epss_score,
                    "source": "local_db"
                }
                
                vulns.append(vuln)
        
        # Sort by severity (KEV first, then by CVSS)
        def sort_key(v):
            # KEV vulnerabilities get highest priority
            if v.get("is_kev"):
                return (5, v.get("cvss") or 0)
            # Then by severity
            sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
            return (sev_rank.get(v.get("severity", "unknown"), 0), v.get("cvss") or 0)
        
        vulns.sort(key=sort_key, reverse=True)
        return vulns
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics about the local database"""
        total_cves = len(self.cve_meta)
        kev_count = len(self.kev_data)
        high_crit_count = sum(1 for cve in self.cve_meta.values() 
                            if cve.get("severity") in ["high", "critical"])
        
        return {
            "total_cves": total_cves,
            "kev_count": kev_count,
            "high_critical_count": high_crit_count,
            "epss_coverage": len(self.epss_data),
            "version_aware_rules": len(self.affects)
        }
