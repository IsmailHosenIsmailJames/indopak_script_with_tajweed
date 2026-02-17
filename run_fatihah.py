import sys
import os
import difflib
import re
import json

# Bring in the full script content to be sure I am running the exact logic.
# Wait, I can import from transfer_tags if it works.
# But just to be safe I will copy paste minimal logic or import.
# Since transfer_tags.py is in current dir, I can import.

sys.path.append("/Users/ismailhosen/dev/indopak_script_with_tajweed")
from transfer_tags import process_file_v2

base_path = "/Users/ismailhosen/dev/indopak_script_with_tajweed"
indopak_dir = os.path.join(base_path, "quran_parts/indopak_script")
qpc_dir = os.path.join(base_path, "quran_parts/qpc_hafs_tajweed")
filename = "1_Al-Fatihah_ayah_1_to_ayah_7.json"

indo_abs = os.path.join(indopak_dir, filename)
qpc_abs = os.path.join(qpc_dir, filename)

print(f"Processing {filename}...")
if os.path.exists(indo_abs) and os.path.exists(qpc_abs):
    process_file_v2(indo_abs, qpc_abs)
    print("Done.")
else:
    print(f"File not found: {indo_abs} or {qpc_abs}")
