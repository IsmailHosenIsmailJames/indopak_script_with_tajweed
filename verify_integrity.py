import os
import json
import re

def strip_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def verify_integrity(source_dir, tagged_dir, error_log_path):
    print(f"Verifying integrity...")
    print(f"Source: {source_dir}")
    print(f"Tagged: {tagged_dir}")
    
    errors = []
    
    source_files = set(f for f in os.listdir(source_dir) if f.endswith('.json'))
    tagged_files = set(f for f in os.listdir(tagged_dir) if f.endswith('.json'))
    
    # Check for missing files
    missing_in_tagged = source_files - tagged_files
    for f in missing_in_tagged:
        errors.append({'file': f, 'error': 'Missing in output directory'})
        
    common_files = source_files.intersection(tagged_files)
    common_files_list = sorted(list(common_files))
    
    print(f"Checking {len(common_files_list)} files...")
    
    for filename in common_files_list:
        source_path = os.path.join(source_dir, filename)
        tagged_path = os.path.join(tagged_dir, filename)
        
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            with open(tagged_path, 'r', encoding='utf-8') as f:
                tagged_data = json.load(f)
                
            for surah_key, ayahs in source_data.items():
                if surah_key not in tagged_data:
                    errors.append({'file': filename, 'key': surah_key, 'error': 'Missing Surah in output'})
                    continue
                
                for ayah_key, source_words in ayahs.items():
                    if ayah_key not in tagged_data[surah_key]:
                        errors.append({'file': filename, 'key': f"{surah_key}:{ayah_key}", 'error': 'Missing Ayah in output'})
                        continue
                        
                    tagged_words = tagged_data[surah_key][ayah_key]
                    
                    if len(source_words) != len(tagged_words):
                         errors.append({'file': filename, 'key': f"{surah_key}:{ayah_key}", 'error': 'Word count mismatch', 'expected': len(source_words), 'got': len(tagged_words)})
                         continue
                         
                    for i in range(len(source_words)):
                        # Strip tags from both to compare raw text content
                        clean_source = strip_tags(source_words[i])
                        clean_tagged = strip_tags(tagged_words[i])
                        
                        # Normalize? (e.g. NFC)
                        # clean_source = unicodedata.normalize('NFC', clean_source)
                        # clean_tagged = unicodedata.normalize('NFC', clean_tagged)
                        
                        if clean_source != clean_tagged:
                            errors.append({
                                'file': filename,
                                'key': f"{surah_key}:{ayah_key}:{i}",
                                'error': 'Text mismatch',
                                'source': clean_source,
                                'tagged': clean_tagged,
                                'original_tagged': tagged_words[i]
                            })

        except Exception as e:
            errors.append({'file': filename, 'error': f"Exception during verification: {str(e)}"})
            
    if errors:
        print(f"Found {len(errors)} errors.")
        with open(error_log_path, 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=4)
        print(f"Errors saved to {error_log_path}")
    else:
        print("Verification successful! No text corruption found.")
        if os.path.exists(error_log_path):
             os.remove(error_log_path) # Clean up old log

if __name__ == "__main__":
    base_path = "/Users/ismailhosen/dev/indopak_script_with_tajweed"
    # Note: Using the original indopak script directory as source.
    # Even if it has tags (due to previous overwrite), strip_tags(source) will clean it.
    source_dir = os.path.join(base_path, "quran_parts/indopak_script")
    tagged_dir = os.path.join(base_path, "quran_parts/indopak_with_tajweed_output")
    error_log = "verification_errors.json"
    
    verify_integrity(source_dir, tagged_dir, error_log)
