# main.py in round1a/ - FINAL VERSION WITH CORRECTED FILTERING

import fitz
import os
import json
import re
from collections import Counter

INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'

def get_document_stats(doc):
    """Analyzes the document to find the most common font size (body text)."""
    font_sizes = Counter()
    if doc.page_count == 0:
        return 12
    for page in doc:
        text_page = page.get_text("dict", flags=0)
        for block in text_page["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes[round(span["size"])] += 1
    if not font_sizes:
        return 12
    return font_sizes.most_common(1)[0][0]

def is_likely_a_content_heading(text):
    """Filters out common non-content text. This version is less aggressive."""
    text_lower = text.lower()
    # Filter out text that is very short or is likely a page number
    if len(text.strip()) < 3 or text.strip().isdigit():
        return False
    # Filter out specific known non-content headers that are unlikely to be main content
    if text_lower in ["appendix", "references", "bibliography", "contents", "figure"]:
        return False
    # Filter out URLs
    if "http:" in text_lower or "https:" in text_lower:
        return False
    return True

def extract_structure(pdf_path):
    """Extracts the title and headings (H1, H2, H3) with semantic filtering."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return None

    body_font_size = get_document_stats(doc)
    potential_headings = []
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            if b[6] == 0:
                text = re.sub(r'\s+', ' ', b[4]).strip()
                if not text or not is_likely_a_content_heading(text):
                    continue
                
                block_dict = page.get_text("dict", clip=b[:4], flags=0)["blocks"]
                if not block_dict or not block_dict[0]['lines'] or not block_dict[0]['lines'][0]['spans']:
                    continue
                
                span = block_dict[0]['lines'][0]['spans'][0]
                size = round(span['size'])
                is_span_bold = (span['flags'] & 2**4) > 0
                
                if size > body_font_size:
                    score = size + (5 if is_span_bold else 0)
                    potential_headings.append({'text': text, 'score': score, 'page': page_num + 1})

    if not potential_headings:
        return {"title": os.path.basename(pdf_path), "outline": []}

    unique_scores = sorted(list(set(h['score'] for h in potential_headings)), reverse=True)
    score_to_level = {}
    if len(unique_scores) > 0: score_to_level[unique_scores[0]] = "H1"
    if len(unique_scores) > 1: score_to_level[unique_scores[1]] = "H2"
    if len(unique_scores) > 2: score_to_level[unique_scores[2]] = "H3"

    outline = []
    processed_headings = set()
    for h in potential_headings:
        if h['score'] in score_to_level:
            level = score_to_level[h['score']]
            text = h['text']
            if text not in processed_headings:
                outline.append({'level': level, 'text': text, 'page': h['page']})
                processed_headings.add(text)

    outline.sort(key=lambda x: (x['page'], {'H1': 1, 'H2': 2, 'H3': 3}.get(x['level'], 4)))

    title = os.path.basename(pdf_path)
    # A better title extraction logic
    if outline:
        # Prefer the first H1 as a title, otherwise use the first outline item's text
        if outline[0]["level"] == "H1":
             title = outline.pop(0)["text"]
        else:
             # Find a suitable candidate for title (e.g., first item on first page)
             if outline[0]["page"] < 3:
                  title = outline[0]["text"]


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