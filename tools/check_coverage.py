#!/usr/bin/env python3
"""Check coverage gate for release-gates workflow."""

import json
import sys


def main():
    try:
        with open("data/vuln_log.json") as f:
            j = json.load(f)

        has = sum(1 for a in j if any("cve_id" in str(v) for v in a.get("vulnerabilities", [])))
        print("apps_with_cves:", has)

        if has >= 1:
            print("✓ Coverage gate passed: at least 1 app with CVEs found")
            sys.exit(0)
        else:
            print("✗ Coverage gate failed: no apps with CVEs found")
            sys.exit(2)

    except FileNotFoundError:
        print("✗ Coverage gate failed: data/vuln_log.json not found")
        sys.exit(2)
    except Exception as e:
        print(f"✗ Coverage gate failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
