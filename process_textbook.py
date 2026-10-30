import re
import sys

def extract_content(input_path, output_path):
    with open(input_path, "r") as f:
        lines = f.readlines()

    cleaned_lines = []

    start_collecting = False
    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Start at Biochemistry
        if line.strip() == "###### **Biochemistry**":
            if not start_collecting: # Only the first instance
                start_collecting = True

        if not start_collecting:
            continue

        # Stop at SECTION IV TOP-RATED REVIEW RESOURCES
        if "**TOP-RATED REVIEW RESOURCES**" in line or (re.search(r'\*\*SECTION IV\*\*', stripped_line) and "740" in stripped_line):
            break

        if line.strip() == "S E C T I O N I V":
             break
        if line.strip() == "###### **Top-Rated Review Resources**":
             break

        # Remove standard fluff artifacts:
        if re.search(r'FAS1_2025_.*\.indd', line, re.IGNORECASE):
            continue

        # Running headers like: **CARDIOVASCULAR** ` CARDIOVASCULAR—PHYSIOLOGY
        if re.search(r'\*\*.*?\*\*\s*`\s*.*?—.*?', line):
            continue

        # Other weird headers with <mark> and ~~
        if re.search(r'~~.*?~~\s*<mark>`.*?<\/mark>', line, re.IGNORECASE):
            continue
        if re.search(r'~~.*?~~\s*<mark>`.*?', line, re.IGNORECASE):
            continue

        # Remove SECTION heading footers/headers e.g. "280 **SECTION III**"
        if re.search(r'^\d+\s+\*\*SECTION [IV]+\*\*.*', line, re.IGNORECASE):
            continue
        if re.search(r'^\*\*SECTION [IV]+\*\*\s+\d+.*', line, re.IGNORECASE):
            continue
        if re.match(r'^\*\*SECTION [IV]+\*\*$', stripped_line):
            continue
        if re.search(r'^\*\*SECTION III [A-Za-z\- ]+\*\*$', stripped_line, re.IGNORECASE):
            continue
        if re.search(r'^\*\*SECTION III\*\*', stripped_line, re.IGNORECASE):
            continue
        if re.search(r'^> \*\*SECTION III\*\* \d+', stripped_line, re.IGNORECASE):
            continue
        if re.search(r'^\d+ \*\*SECTION III\*\*', stripped_line, re.IGNORECASE):
            continue
        if re.search(r'^\*\*SECTION II\*\*', stripped_line, re.IGNORECASE):
            continue
        if re.search(r'^> \*\*SECTION II\*\* \d+', stripped_line, re.IGNORECASE):
            continue
        if re.search(r'^\d+ \*\*SECTION II\*\*', stripped_line, re.IGNORECASE):
            continue

        # Lines with just date and time
        if re.match(r'^\d{1,2}\/\d{1,2}\/\d{2,4}\s+\d{1,2}:\d{2}\s+[AP]M', stripped_line):
            continue

        # Page numbers
        if re.match(r'^\d+$', stripped_line):
            continue

        # "https://ebookmed.ir" watermark
        if re.search(r'https://ebookmed\.ir', line):
            continue

        # Clean some common artifacts like "H I G H - Y I E L D P R I N C I P L E S I N"
        if re.sub(r'[^A-Z]', '', stripped_line) == 'HIGHYIELDPRINCIPLESIN':
            continue

        if re.sub(r'[^A-Z]', '', stripped_line) == 'HIGHYIELDORGANSYSTEMS':
            continue

        # We also want to remove quotes and "How to use" indices at the start of sections
        if stripped_line.startswith("_“") and stripped_line.endswith("”_"):
             # A quote
             continue
        if re.match(r'^—[A-Za-z\s]+', stripped_line) and "—" in stripped_line:
             # Quote author
             continue
        if stripped_line.startswith("—"):
             continue

        # Remove small tables containing chapters and page numbers at the beginning of chapters
        if re.match(r'^\|`[A-Za-z]+|\d+\|$', stripped_line) or re.match(r'^\|`?[A-Za-z\s]+|\d+\|$', stripped_line):
             pass # Will handle below

        cleaned_lines.append(line)

    # Let's filter out the index tables
    final_lines = []
    in_index_table = False
    for line in cleaned_lines:
        stripped_line = line.strip()
        if re.match(r'^\|`?[A-Za-z\s]+\|\d+\|$', stripped_line) or \
           re.match(r'^\|[A-Za-z\s]+\|\d+\|$', stripped_line) or \
           re.match(r'^\|`?[A-Za-z\s]+\|\|$', stripped_line) or \
           re.match(r'^\|\|[A-Za-z\s]+\|$', stripped_line) or \
           stripped_line == "|---|---|":
             continue

        final_lines.append(line)

    final_final_lines = []
    prev_empty = False
    for line in final_lines:
        if not line.strip():
            if prev_empty:
                continue
            prev_empty = True
        else:
            prev_empty = False
        final_final_lines.append(line)

    with open(output_path, "w") as f:
        f.writelines(final_final_lines)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_textbook.py <input_markdown> <output_markdown>")
        sys.exit(1)

    extract_content(sys.argv[1], sys.argv[2])
    print(f"Successfully processed {sys.argv[1]} into {sys.argv[2]}")
