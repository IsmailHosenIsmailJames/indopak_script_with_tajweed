import difflib
import re
import sys
sys.path.append("/home/ismail/dev/indopak_script_with_tajweed")
from transfer_tags import parse_qpc_and_spans, transfer_tags_span_based

# Strings from inspect_word.py output

# QPC String
qpc_word = "<rule class=ham_wasl>ٱ</rule><rule class=laam_shamsiyah>ل</rule>ضّ<rule class=madda_necessary>َا</rule>ٓلّ<rule class=madda_permissible>ِي</rule>نَ"

# IndoPak String (Clean)
# From inspect_word.py Step 173: "الضَّآلِّيۡنَ" + marks
indo_word = "الضَّآلِّيۡنَ" 
# Note: Copy paste might miss invisible chars.
# I will use unicode escapes to be precise if needed, but let's try literal first.
# actually inspect_word showed 200F (RLM) at end.

print("--- Debugging ---")
clean_qpc, spans = parse_qpc_and_spans(qpc_word)
print(f"Clean QPC: {clean_qpc}")
print(f"Spans: {spans}")

clean_indo = re.sub(r'<[^>]+>', '', indo_word)
print(f"Clean Indo: {clean_indo}")

matcher = difflib.SequenceMatcher(None, clean_qpc, clean_indo)
print("\n--- Opcodes ---")
for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    print(f"{tag} qpc[{i1}:{i2}] '{clean_qpc[i1:i2]}' -> indo[{j1}:{j2}] '{clean_indo[j1:j2]}'")

print("\n--- Result ---")
res = transfer_tags_span_based(qpc_word, clean_indo)
print(f"Result: {res}")
