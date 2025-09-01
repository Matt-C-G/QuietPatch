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
                
                # Generate actionable remediation
                action = self._generate_action(normalized_name, cve_id, severity, is_kev)
                
                vuln = {
                    "cve_id": cve_id,
                    "severity": severity,
                    "cvss": cvss,
                    "summary": description,
                    "is_kev": is_kev,
                    "kev_action": kev_action,
                    "epss_score": epss_score,
                    "action": action,
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
    
    def _generate_action(self, app_name: str, cve_id: str, severity: str, is_kev: bool) -> str:
        """Generate actionable remediation steps for a vulnerability"""
        app_lower = app_name.lower()
        
        # Critical vulnerabilities get immediate action
        if severity == "critical" or is_kev:
            if "firefox" in app_lower:
                return "brew upgrade firefox || Download latest from mozilla.org"
            elif "wireshark" in app_lower:
                return "brew upgrade wireshark || Download from wireshark.org"
            elif "pdfgear" in app_lower:
                return "Update PDFgear immediately - critical RCE vulnerability"
            else:
                return "Update immediately - critical vulnerability actively exploited"
        
        # High severity vulnerabilities
        elif severity == "high":
            if "safari" in app_lower:
                return "Update macOS to latest version (Safari updates included)"
            elif "microsoft" in app_lower or "word" in app_lower or "excel" in app_lower:
                return "Update Microsoft Office via AutoUpdate or download latest"
            elif "zoom" in app_lower:
                return "Update Zoom client from zoom.us/download"
            elif "openvpn" in app_lower:
                return "Update OpenVPN Connect from openvpn.net"
            else:
                return "Update to latest version - high severity vulnerability"
        
        # Medium severity vulnerabilities
        elif severity == "medium":
            if "numbers" in app_lower or "pages" in app_lower or "keynote" in app_lower:
                return "Update macOS to latest version (iWork updates included)"
            elif "discord" in app_lower:
                return "Update Discord client - restart app to trigger update"
            elif "onedrive" in app_lower:
                return "Update OneDrive via Microsoft AutoUpdate"
            else:
                return "Update when convenient - medium severity vulnerability"
        
        # Low severity or unknown
        else:
            return "Monitor for updates - low risk vulnerability"
    
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
