import os
import json


def make_parts_of_scripts(
    simplified_script: dict,
    surah_name_list: list,
    ayah_length_per_parts: int,
    destination_to_save: str,
):
    ayah_count = 0
    ayah_dict = dict()
    first_ayah_count = ""

    for (surah_number, surah) in simplified_script.items():
        for (ayah_number, words_list) in dict(surah).items():
            if surah_number not in ayah_dict:
                ayah_dict[surah_number] = dict()
            if ayah_number not in ayah_dict[surah_number]:
                ayah_dict[surah_number][ayah_number] = list()
            if first_ayah_count == "":
                first_ayah_count = ayah_number

            ayah_dict[surah_number][ayah_number].append(words_list)

            ayah_count += 1
            if (ayah_length_per_parts <= ayah_count
                    or list(dict(surah).keys())[-1] == ayah_number):
                surah_name = surah_name_list[int(surah_number) - 1]
                with open(
                        f"{destination_to_save}/{surah_name}_ayah_{first_ayah_count}_to_ayah_{ayah_number}.json",
                        "w") as f:
                    json.dump(ayah_dict, f, indent=4, ensure_ascii=False)
                ayah_dict = dict()
                ayah_count = 0
                first_ayah_count = ""


surah_name_list = []
with open("surah_list.json", "r") as f:
    surah_name_list = list(json.load(f))

with open("simplified_script/simplified_indopak_script.json", "r") as f:
    simplified_script = json.load(f)
    make_parts_of_scripts(
        simplified_script=simplified_script,
        surah_name_list=surah_name_list,
        ayah_length_per_parts=10,
        destination_to_save="quran_parts/indopak_script",
    )

with open("simplified_script/simplified_qpc_hafs_tajweed.json", "r") as f:
    simplified_script = json.load(f)
    make_parts_of_scripts(
        simplified_script=simplified_script,
        surah_name_list=surah_name_list,
        ayah_length_per_parts=10,
        destination_to_save="quran_parts/qpc_hafs_tajweed",
    )

print("Done")
