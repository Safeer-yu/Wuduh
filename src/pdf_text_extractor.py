import fitz
import re
import unicodedata
from pathlib import Path
from collections import Counter


def get_repeated_lines(doc, min_repeat_ratio=0.4):
    """
    Detect repeated lines across many pages
    (likely headers/footers).
    """

    num_pages = len(doc)
    line_counts = Counter()

    for page in doc:
        lines = page.get_text().splitlines()

        # Count once per page
        for line in set(lines):
            stripped = line.strip()

            if stripped:
                line_counts[stripped] += 1

    threshold = num_pages * min_repeat_ratio

    repeated = {
        line
        for line, count in line_counts.items()
        if count >= threshold
    }

    return repeated


def normalize_unicode(text):
    """
    Fix common PDF unicode / ligature issues.
    """

    text = unicodedata.normalize("NFKC", text)

    return text


def remove_repeated_lines(text, repeated_lines):
    """
    Remove detected headers/footers.
    """

    lines = text.splitlines()

    cleaned = [
        line
        for line in lines
        if line.strip() not in repeated_lines
    ]

    return "\n".join(cleaned)


def remove_page_numbers(text):
    """
    Remove standalone page numbers like:
    4
    5
    39-40
    """

    lines = text.splitlines()

    cleaned = [
        line
        for line in lines
        if not re.fullmatch(r"\d+(-\d+)?", line.strip())
    ]

    return "\n".join(cleaned)


def merge_broken_lines(text):
    """
    Merge PDF-broken sentence lines while
    preserving paragraph structure.
    """

    lines = text.splitlines()

    merged = []
    buffer = ""

    for line in lines:

        line = line.strip()

        # Empty line = paragraph break
        if not line:

            if buffer:
                merged.append(buffer)
                buffer = ""

            continue

        # New logical section
        if re.match(r"^(Article\s*\(\d+\)|►)", line):

            if buffer:
                merged.append(buffer)

            merged.append(line)
            buffer = ""

            continue

        # Continue sentence
        if buffer and not re.search(r"[.!?:;]$", buffer):

            # Avoid joining bullet lists weirdly
            if not re.match(r"^[a-zA-Z0-9(]", line):
                merged.append(buffer)
                buffer = line
            else:
                buffer += " " + line

        else:

            if buffer:
                merged.append(buffer)

            buffer = line

    if buffer:
        merged.append(buffer)

    return "\n\n".join(merged)


def deduplicate_paragraphs(text):
    """
    Remove duplicate paragraphs.
    """

    paragraphs = text.split("\n\n")

    seen = set()
    unique = []

    for p in paragraphs:

        normalized = re.sub(r"\s+", " ", p.strip())

        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(p.strip())

    return "\n\n".join(unique)


def normalize_whitespace(text):
    """
    Final cleanup.
    """

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def clean_text(text, repeated_lines):

    text = normalize_unicode(text)

    text = remove_repeated_lines(text, repeated_lines)

    text = remove_page_numbers(text)

    text = merge_broken_lines(text)

    text = deduplicate_paragraphs(text)

    text = normalize_whitespace(text)

    return text


def extract_text_pymupdf(pdf_path):

    doc = fitz.open(pdf_path)

    repeated_lines = get_repeated_lines(doc)

    full_text = ""

    for page in doc:

        page_text = page.get_text()

        full_text += "\n" + page_text

    doc.close()

    cleaned_text = clean_text(full_text, repeated_lines)

    return full_text, cleaned_text


def process_all_pdfs(input_dir, raw_output_dir, cleaned_output_dir):

    input_dir = Path(input_dir)

    raw_output_dir = Path(raw_output_dir)
    cleaned_output_dir = Path(cleaned_output_dir)

    raw_output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files\n")

    for pdf_path in pdf_files:

        print(f"Processing: {pdf_path.name}")

        raw_text, cleaned_text = extract_text_pymupdf(pdf_path)

        raw_output_path = raw_output_dir / (pdf_path.stem + ".txt")

        cleaned_output_path = (
            cleaned_output_dir / (pdf_path.stem + ".txt")
        )

        raw_output_path.write_text(
            raw_text,
            encoding="utf-8"
        )

        cleaned_output_path.write_text(
            cleaned_text,
            encoding="utf-8"
        )

        print(
            f"  → Raw: {len(raw_text):,} chars | "
            f"Cleaned: {len(cleaned_text):,} chars"
        )

    print("\nDone.")


if __name__ == "__main__":

    process_all_pdfs(
        input_dir="data/raw/eng",

        raw_output_dir="data/extracted_raw/eng",

        cleaned_output_dir="data/processed/eng"
    )