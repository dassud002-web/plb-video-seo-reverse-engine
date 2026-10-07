#!/usr/bin/env python3
"""
Launcher script for PLB Story Forge
===================================
Runs Story Forge on port 5050 and displays actionable console diagnostics.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from story_forge.app import app

def main():
    port = int(os.environ.get("PORT", 5050))
    url = f"http://127.0.0.1:{port}"
    print("=" * 70)
    print(" 🎬 PLB STORY FORGE — VIDEO → 50 STORY → RECURSIVE STORY ENGINE")
    print("=" * 70)
    print(f"Server is starting on: {url}")
    print("Features active:")
    print("  • Video Story Evidence Extraction (18 Domains)")
    print("  • Story DNA Synthesis & Thematic Tension")
    print("  • 50 Distinct Root Stories across 20 Evolutionary Dimensions")
    print("  • Recursive Expansion (EXPAND ×50 on any story node)")
    print("  • Story Lineage & Evolution Graph with Dimensional Shifts")
    print("  • Deterministic Diversity Engine (Anti-Duplication Threshold >= 0.70)")
    print("  • Multi-Format Exports: JSON, Markdown Story Bible, TXT, ZIP")
    print("=" * 70)

    try:
        if os.environ.get("OPEN_BROWSER", "0") == "1":
            webbrowser.open(url)
    except Exception:
        pass

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
