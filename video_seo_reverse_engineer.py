#!/usr/bin/env python3
"""
Root wrapper for scripts/video_seo_reverse_engineer.py
"""
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scripts.video_seo_reverse_engineer import *

if __name__ == "__main__":
    from scripts.video_seo_reverse_engineer import main
    main()
