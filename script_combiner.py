import json
import os


def combine_scripts(folder_path: str) -> dict:
    combined_scripts = dict()
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith(".json"):
            with open(os.path.join(folder_path, file), "r") as f:
                data = dict(json.load(f))
                for (surah_number, surah) in data.items():
                    for (ayah_number, ayah) in surah.items():
                        if (surah_number not in combined_scripts):
                            combined_scripts[surah_number] = dict()
                        if (ayah_number not in combined_scripts[surah_number]):
                            combined_scripts[surah_number][ayah_number] = list(
                            )
                        combined_scripts[surah_number][ayah_number].extend(
                            ayah)

                combined_scripts[surah_number] = dict(
                    sorted(combined_scripts[surah_number].items(),
                           key=lambda x: int(x[0])))

    return combined_scripts


combined_scripts = combine_scripts("quran_parts/indopak_script")
combined_scripts = dict(sorted(combined_scripts.items(), key=lambda x: x[0]))
with open("indopak_with_tajweed/indopak_with_tajweed.json", "w") as f:
    json.dump(combined_scripts, f, indent=4, ensure_ascii=False)
