import json
import os

qpc_hafs_tajweed_script = dict()
indopak_script = dict()
with open("resources_from_qul/qpc-hafs-tajweed.json", "r") as f:
    qpc_hafs_tajweed_script = dict(json.load(f))

with open("resources_from_qul/indopak.json") as f:
    indopak_script = dict(json.load(f))


def simplify(script:dict) -> dict:
    simplified = dict()
    for (key, value) in script.items():
        surahNumber, ayahNumber, wordNumber = str(key).split(":")
        text = value["text"]
        
        if surahNumber not in simplified:
            simplified[surahNumber] = dict()
        
        if ayahNumber not in simplified[surahNumber]:
            simplified[surahNumber][ayahNumber] = list()
        
        simplified[surahNumber][ayahNumber].append(text)
    
    return simplified


with open("simplified_script/simplified_qpc_hafs_tajweed.json", "w") as f:
    json.dump(simplify(qpc_hafs_tajweed_script), f, indent=4, ensure_ascii=False)

with open("simplified_script/simplified_indopak_script.json", "w") as f:
    json.dump(simplify(indopak_script), f, indent=4, ensure_ascii=False)

print("Done")