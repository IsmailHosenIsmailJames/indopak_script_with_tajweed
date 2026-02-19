import json
import difflib
import re
import sys
import os
import unicodedata

def parse_qpc_and_spans(qpc_word):
    """
    Parses QPC word, separating tags from text and identifying tag spans.
    Returns:
        clean_text: str
        spans: list of distinct tag spans [{'start': int, 'end': int, 'open': str, 'close': str}]
               Note: end is inclusive index of the last character covered.
    """
    # Regex to capture tags
    # We need to handle nesting and proper open/close matching.
    # While regex split works for loose parsing, a stack is better for pairing.
    
    tokens = re.split(r'(<[^>]+>)', qpc_word)
    tokens = [t for t in tokens if t]
    
    clean_text = ""
    spans = []
    stack = [] # Stores (clean_start_index, open_tag_string)
    
    current_idx = 0
    
    for token in tokens:
        if token.startswith('<') and token.endswith('>'):
            if token.startswith('</'):
                # Closing tag
                if stack:
                    start_idx, open_tag = stack.pop()
                    if current_idx > 0:
                        # Span ends at current_idx - 1 (previous character)
                        # If start_idx == current_idx, it means empty span <r></r>. 
                        # We generally ignore empty spans or attach to nothing.
                        if current_idx > start_idx:
                            spans.append({
                                'start': start_idx,
                                'end': current_idx - 1,
                                'open': open_tag,
                                'close': token
                            })
                        else:
                             # Empty span logic: e.g. <r></r>
                             # Ignore for now as usually tajweed applies to letters
                             pass
                else:
                    # Unbalanced closing tag?
                    pass
            elif token.endswith('/>'):
                # Self closing - rare in this data?
                pass
            else:
                # Opening tag
                stack.append((current_idx, token))
        else:
            # Text
            length = len(token)
            clean_text += token
            current_idx += length
            
    # Handle unclosed tags? (Should not happen in valid data)
    
    return clean_text, spans

def transfer_tags_span_based(qpc_word, indopak_word):
    qpc_text, qpc_spans = parse_qpc_and_spans(qpc_word)
    indopak_text = indopak_word # Assume clean
    
    matcher = difflib.SequenceMatcher(None, qpc_text, indopak_text)
    
    # Build mapping: QPC Index -> Set of IndoPak Indices
    qpc_to_indo = {i: set() for i in range(len(qpc_text))}
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                qpc_to_indo[i1 + k].add(j1 + k)
        elif tag == 'replace':
            # Map all QPC chars in this range to ALL IndoPak chars in this range
            target_indices = set(range(j1, j2))
            for k in range(i1, i2):
                qpc_to_indo[k].update(target_indices)
        elif tag == 'delete':
            # No mapping
            pass
        elif tag == 'insert':
            # No source mapping
            pass
            
    # Determine New Spans
    new_spans = []
    
    for span in qpc_spans:
        target_indices = set()
        for k in range(span['start'], span['end'] + 1):
            if k in qpc_to_indo:
                target_indices.update(qpc_to_indo[k])
                
        if target_indices:
            new_start = min(target_indices)
            new_end = max(target_indices)
            
            # Heuristic: If the tag starts with a combining mark (diacritic)
            # that belongs to a letter BEFORE the span, move start forward.
            # BUT preserve diacritics that are intentional parts of the rule:
            #   1. If the original QPC span started with Mn (e.g. kasrah in
            #      madda_permissible ِي), keep them.
            #   2. If skipping would eliminate ALL characters (e.g. ٰ for
            #      madda_normal where TATWEEL was deleted), restore and keep.
            orig_starts_with_mark = (
                span['start'] < len(qpc_text) and
                unicodedata.category(qpc_text[span['start']]) == 'Mn'
            )
            
            if not orig_starts_with_mark:
                saved_start = new_start
                while new_start <= new_end and new_start < len(indopak_text):
                    char = indopak_text[new_start]
                    if unicodedata.category(char) == 'Mn':
                        new_start += 1
                    else:
                        break
                # If skipping eliminated everything, the span IS about
                # the diacritics (e.g. ٰ for madda_normal) — restore.
                if new_start > new_end:
                    new_start = saved_start
            
            # Guard: skip span if start got pushed past end (prevents orphaned tags)
            if new_start > new_end:
                continue
            
            # Add to list
            new_spans.append({
                'start': new_start,
                'end': new_end,
                'open': span['open'],
                'close': span['close'],
                'orig_start': span['start'],
                'orig_len': span['end'] - span['start']
            })
            
    # Apply spans to IndoPak text
    # Convert to insertion points:
    # (index, priority, string)
    # Open tag: insert at `start`. Priority: 1 (after close tags of prev char)
    # Close tag: insert at `end + 1`. Priority: 0 (before open tags of next char)
    
    instructions = []
    for s in new_spans:
        # Priority:
        # We want nesting to assume "outer" tags enclose "inner" tags.
        # If two spans have same start/end, restore original nesting?
        # QPC: <A><B>x</B></A>. Spans: A(0,0), B(0,0).
        # A starts at 0, B starts at 0. A ends at 0, B ends at 0.
        # Open A, Open B, Char, Close B, Close A.
        # In sorted list:
        # At 0: Open A, Open B.
        # At 1: Close B, Close A.
        
        # Sort keys:
        # Position
        # Type (Close before Open at same position? No, tags wrap content.
        # <r>X</r>Y<r>Z</r>
        # 0: Open <r>
        # 1: Close </r>
        # 1: Open <r>
        # 2: Close </r>
        # So at index 1 (between X and Y), Close comes before Open.
        
        instructions.append({
            'pos': s['start'],
            'type': 'open',
            'str': s['open'],
            'span_len': s['end'] - s['start'], # Larger length = Outer?
            'id': id(s) 
        })
        instructions.append({
            'pos': s['end'] + 1,
            'type': 'close',
            'str': s['close'],
            'span_len': s['end'] - s['start'],
            'id': id(s)
        })

    # Sorting
    def sort_key(instr):
        # 1. Position
        # 2. Type: Close (0) before Open (1)
        # 3. Nesting logic:
        #    For Open: Outer spans (longer) before Inner spans (shorter).
        #    For Close: Inner spans (shorter) before Outer spans (longer).
        type_order = 0 if instr['type'] == 'close' else 1
        
        len_order = 0
        if instr['type'] == 'open':
            # Longest first -> descending length
            len_order = -instr['span_len']
        else:
            # Shortest first -> ascending length
            len_order = instr['span_len']
            
        return (instr['pos'], type_order, len_order)
        
    instructions.sort(key=sort_key)
    
    # Reconstruct
    res = ""
    current_idx = 0
    instr_idx = 0
    
    while current_idx <= len(indopak_text):
        # Apply instructions at this index
        while instr_idx < len(instructions) and instructions[instr_idx]['pos'] == current_idx:
            res += instructions[instr_idx]['str']
            instr_idx += 1
        
        # Add character
        if current_idx < len(indopak_text):
            res += indopak_text[current_idx]
        
        current_idx += 1
        
    return res

def process_file_v2(indopak_path, qpc_path, output_path):
    print(f"Processing {os.path.basename(indopak_path)}...")
    
    try:
        with open(indopak_path, 'r', encoding='utf-8') as f:
            indopak_data = json.load(f)
        with open(qpc_path, 'r', encoding='utf-8') as f:
            qpc_data = json.load(f)
            
        modified_data = {}
        
        for surah_key, ayahs in indopak_data.items():
            modified_data[surah_key] = {}
            if surah_key not in qpc_data:
                modified_data[surah_key] = ayahs
                continue
                
            for ayah_key, indopak_words in ayahs.items():
                if ayah_key not in qpc_data[surah_key]:
                     modified_data[surah_key][ayah_key] = indopak_words
                     continue
                
                qpc_words = qpc_data[surah_key][ayah_key]
                new_words = []
                
                for i in range(len(indopak_words)):
                    if i < len(qpc_words):
                        # Clean IndoPak word in case it was already modified
                        clean_indopak = re.sub(r'<[^>]+>', '', indopak_words[i])
                        new_word = transfer_tags_span_based(qpc_words[i], clean_indopak)
                        new_words.append(new_word)
                    else:
                        new_words.append(indopak_words[i])
                
                modified_data[surah_key][ayah_key] = new_words
        
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(modified_data, f_out, ensure_ascii=False, indent=4)
            
        print(f"Completed {os.path.basename(indopak_path)}")

    except Exception as e:
        print(f"Error processing {indopak_path}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    base_path = "/home/ismail/dev/indopak_script_with_tajweed"
    indopak_dir = os.path.join(base_path, "quran_parts/indopak_script")
    qpc_dir = os.path.join(base_path, "quran_parts/qpc_hafs_tajweed")
    output_dir = os.path.join(base_path, "quran_parts/indopak_with_tajweed_output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all matching files
    files = [f for f in os.listdir(indopak_dir) if f.endswith('.json')]
    files.sort() # Ensure consistent order
    
    print(f"Found {len(files)} files to process.")
    print(f"Output directory: {output_dir}")
    
    for filename in files:
        indo_abs = os.path.join(indopak_dir, filename)
        qpc_abs = os.path.join(qpc_dir, filename)
        output_abs = os.path.join(output_dir, filename)
        
        if os.path.exists(qpc_abs):
            process_file_v2(indo_abs, qpc_abs, output_abs)
        else:
            print(f"Skipping {filename}: No corresponding QPC file found.")
