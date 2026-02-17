import json
import os

tajweedRulesList = list()

with open("rules_list.json", "r") as f:
    tajweedRulesList = list(json.load(f))


def compress_script(script: str):
    for i in range(len(tajweedRulesList) - 1):
        rule = tajweedRulesList[i]
        script = script.replace(rule, f"r{i}")
    return script

folder_path = "indopak_with_tajweed"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)    
with open(os.path.join(folder_path, "indopak_with_tajweed.json"), "r") as f:
    data = f.read()
    compressed_data = compress_script(data)
    with open(
            os.path.join(folder_path, "indopak_with_tajweed_compressed.json"),
            "w",
    ) as f:
        f.write(compressed_data)
