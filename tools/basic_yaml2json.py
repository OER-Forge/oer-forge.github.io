#!/usr/bin/env python3
# basic_yaml2json.py (copied to scripts/ for robust YAML parsing)
# Original script for converting YAML to JSON for menu parsing in build-web.manifest.py
# This version will be improved for robust parsing of PyYAML-generated YAML files.

import sys
import json
import yaml

def main():
    if len(sys.argv) != 2:
        print("Usage: python basic_yaml2json.py <input.yml>", file=sys.stderr)
        sys.exit(1)
    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # Output as compact JSON
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[ERROR] Failed to parse {input_path}: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
