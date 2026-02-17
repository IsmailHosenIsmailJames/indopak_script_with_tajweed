import json
import unicodedata

def dump_unicode(text):
    print(f"String: {text}")
    print("  IDX | CHAR | CODE | NAME")
    for i, c in enumerate(text):
        name = unicodedata.name(c, "UNKNOWN")
        print(f"  {i:3} | {c!r:4} | {ord(c):04X} | {name}")

indo_path = "quran_parts/indopak_script/1_Al-Fatihah_ayah_1_to_ayah_7.json"
qpc_path = "quran_parts/qpc_hafs_tajweed/1_Al-Fatihah_ayah_1_to_ayah_7.json"

with open(indo_path, 'r') as f:
    data = json.load(f)
    print("Keys:", list(data.keys()))
    words = data["1"]["7"]
    if len(words) > 1 and words[-1].strip().isdigit():
        word = words[-2]
    else:
        word = words[-1]
    
    dump_unicode(word)

print("\n--- QPC Word (Ayah 7, last word) ---")
with open(qpc_path, 'r') as f:
    data = json.load(f)
    words = data["1"]["7"]
    if len(words) > 1 and words[-1].strip().isdigit():
        word = words[-2]
    else:
        word = words[-1]
    
    dump_unicode(word)
