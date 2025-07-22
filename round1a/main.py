# main.py in round1a/

import fitz  # PyMuPDF library
import os
import json
from collections import Counter

# Define the input and output directories as specified in the hackathon document
# These paths are used inside the Docker container
INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'

def get_font_statistics(doc):
    """Analyzes the document to find font sizes and their frequency."""
    font_counts = Counter()
    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXT_INHIBIT_SPACES)
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Round the font size to the nearest integer
                        font_size = round(span["size"])
                        font_counts[font_size] += 1
    return font_counts

def extract_structure(pdf_path):
    """
    Extracts the title and headings (H1, H2, H3) from a PDF.
    This logic uses font size as a primary indicator for headings.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return None

    # Get font statistics to identify potential heading sizes
    font_stats = get_font_statistics(doc)
    
    # Filter out very small font sizes to find the most common body text size
    # This helps in distinguishing body text from headings
    filtered_stats = {size: count for size, count in font_stats.items() if size > 8}
    if not filtered_stats:
        # If no text is found or all text is too small, return empty
        return {"title": os.path.basename(pdf_path), "outline": []}

    # The most frequent font size is likely the body text
    body_font_size = max(filtered_stats, key=filtered_stats.get)
    
    # Identify potential heading sizes: any font size larger than the body text
    heading_sizes = sorted([size for size in filtered_stats if size > body_font_size], reverse=True)

    # Assign heading levels based on font size (H1 > H2 > H3)
    size_to_level = {}
    if len(heading_sizes) > 0:
        size_to_level[heading_sizes[0]] = "H1"
    if len(heading_sizes) > 1:
        size_to_level[heading_sizes[1]] = "H2"
    if len(heading_sizes) > 2:
        size_to_level[heading_sizes[2]] = "H3"
    
    title = os.path.basename(pdf_path) # Default title is the filename
    title_found = False
    outline = []

    # Iterate through each page to extract text and identify headings
    for page_num, page in enumerate(doc):
        # Extract text blocks with detailed information
        blocks = page.get_text("dict", flags=fitz.TEXT_INHIBIT_SPACES)["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    # We assume a heading is a single line of text
                    span = line["spans"][0]
                    text = span["text"].strip()
                    font_size = round(span["size"])

                    # Check if the text is a potential heading
                    if font_size in size_to_level and text:
                        level = size_to_level[font_size]
                        
                        # Logic to find the main title (often the first H1)
                        if not title_found and level == "H1":
                            title = text
                            title_found = True
                        else:
                            outline.append({"level": level, "text": text, "page": page_num + 1})
    
    doc.close()
    
    return {"title": title, "outline": outline}


if __name__ == '__main__':
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Process all PDF files in the input directory
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, filename)
            
            print(f"Processing {pdf_path}...")
            structure = extract_structure(pdf_path)
            
            if structure:
                # Create the output JSON filename
                output_filename = os.path.splitext(filename)[0] + '.json'
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                
                # Write the JSON output
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=4)
                
                print(f"Successfully created {output_path}")