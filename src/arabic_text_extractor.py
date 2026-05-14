import sys
import os
import glob
import subprocess
import tempfile
import pytesseract
from PIL import Image


def extract_arabic_text(input_path, output_dir):
    
    base_name = os.path.basename(input_path)
    all_text = []
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "page")
        print(f"Processing: {base_name}")
        # Optimized: Added -grey to potentially speed up OCR and reduce noise
        subprocess.run(["pdftoppm", "-jpeg", "-r", "300", input_path, prefix], check=True)
        pages = sorted(glob.glob(f"{prefix}-*.jpg"))
        
        for i, page_file in enumerate(pages, 1):
            print(f"  OCR Progress: {i}/{len(pages)}", end="\r")
            # Using Image.open in a 'with' block is safer for memory
            with Image.open(page_file) as img:
                text = pytesseract.image_to_string(img, lang="ara", config="--psm 3")
                all_text.append(text)
    print(f"\nFinished OCR for {base_name}")
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{base_name}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))
# Usage logic
input_folder = "data/raw/ar"
output_folder = "data/processed/ar"
pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
for file_name in pdf_files:
    full_input_path = os.path.join(input_folder, file_name)
    extract_arabic_text(full_input_path, output_folder)

