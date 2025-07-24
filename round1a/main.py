# main.py in round1a/ - FINAL MULTILINGUAL VERSION

import fitz
import os
import json
import re
from collections import Counter

# --- CONFIGURATION ---
INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'
MIN_HEADING_CANDIDATE_LENGTH = 3 # Adjusted for languages with dense characters

def get_document_stats(doc):
    """Analyzes the document to find the most common font size (body text)."""
    font_sizes = Counter()
    if doc.page_count == 0:
        return 12
        
    for page in doc:
        text_page = page.get_text("dict", flags=0)
        for block in text_page["blocks"]:
            if block['type'] == 0 and "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes[round(span["size"])] += 1
    
    return font_sizes.most_common(1)[0][0] if font_sizes else 12

def is_likely_heading_text(text):
    """General filter to exclude common non-heading text, made more language-agnostic."""
    if len(text.strip()) < MIN_HEADING_CANDIDATE_LENGTH:
        return False
    if re.match(r'^[.\-_• ]+$', text): # Filter out junk lines
        return False
    if "http:" in text or "https:" in text: # Filter URLs
        return False
    return True

def extract_structure(pdf_path):
    """Extracts the title and headings using a generalized, multilingual-aware model."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"title": os.path.basename(pdf_path), "outline": []}

    if doc.page_count == 0:
        return {"title": os.path.basename(pdf_path), "outline": []}

    body_font_size = get_document_stats(doc)
    
    candidates = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            if b[6] == 0: # Text blocks
                text = re.sub(r'\s+', ' ', b[4]).strip()

                if not is_likely_heading_text(text):
                    continue
                
                block_dict = page.get_text("dict", clip=b[:4], flags=0)["blocks"]
                if not (block_dict and block_dict[0]['lines'] and block_dict[0]['lines'][0]['spans']):
                    continue
                
                span = block_dict[0]['lines'][0]['spans'][0]
                size = round(span['size'])
                
                # Universal boldness check using font flags
                is_bold = (span['flags'] & 2**4) > 0
                
                if size > body_font_size:
                    score = (size - body_font_size) * 2
                    if is_bold:
                        score += 5
                    
                    # Numbered headings are common across many languages
                    if re.match(r'^\d+(\.\d+)*\s', text) or re.match(r'^[A-Z]\.\s', text):
                        score += 5
                        
                    candidates.append({'text': text, 'score': score, 'page': page_num + 1})

    if not candidates:
        return {"title": os.path.basename(pdf_path), "outline": []}

    # Cluster scores to determine levels
    unique_scores = sorted(list(set(c['score'] for c in candidates)), reverse=True)
    score_to_level = {}
    level_map = ["H1", "H2", "H3", "H4", "H5"]
    for i, score in enumerate(unique_scores[:len(level_map)]):
        score_to_level[score] = level_map[i]
        
    outline = []
    processed_text = set()
    for c in candidates:
        if c['score'] in score_to_level:
            text = c['text']
            if text in processed_text: continue
            
            outline.append({'level': score_to_level[c['score']], 'text': text, 'page': c['page']})
            processed_text.add(text)

    outline.sort(key=lambda x: (x['page'], {'H1':1, 'H2':2, 'H3':3, 'H4':4, 'H5':5}.get(x['level'], 99)))

    # Title extraction logic
    title = ""
    first_page_candidates = [c for c in candidates if c['page'] == 1]
    if first_page_candidates:
        title = max(first_page_candidates, key=lambda x: x['score'])['text']
        outline = [item for item in outline if item['text'] != title]
    
    if not title:
        title = os.path.basename(pdf_path)

    doc.close()
    return {"title": title, "outline": outline}

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, filename)
            print(f"Processing {pdf_path}...")
            structure = extract_structure(pdf_path)
            if structure:
                output_filename = os.path.splitext(filename)[0] + '.json'
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=4)
                print(f"Successfully created {output_path}")