import os
import json

partsList = os.listdir("quran_parts/indopak_script")

for part in partsList:
    data = dict()
    with open(f"quran_parts/indopak_script/{part}", "r") as f:
        data = json.load(f)

    for (surahNumber, surahData) in data.items():
        for (ayaNumber, ayaData) in surahData.items():
            data[surahNumber][ayaNumber] = list(ayaData)[0]

    with open(f"quran_parts/indopak_script/{part}", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
