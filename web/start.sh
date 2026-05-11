#!/bin/bash
cd "$(dirname "$0")"
echo "Open http://localhost:8765 in je browser"
python3 -m http.server 8765
