import json

tajweedRulesList = list()

with open("rules_list.json", "r") as f:
    tajweedRulesList = list(json.load(f))


def compress_script(script: str):
    for i in range(len(tajweedRulesList) - 1):
        rule = tajweedRulesList[i]
        script = script.replace(rule, f"r{i}")
    return script


with open("indopak_with_tajweed/indopak_with_tajweed.json", "r") as f:
    data = f.read()
    compressed_data = compress_script(data)
    with open(
            "indopak_with_tajweed/indopak_with_tajweed_compressed.json",
            "w",
    ) as f:
        f.write(compressed_data)
