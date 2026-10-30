import re
import os
import sys

def split_into_chapters(input_path, output_dir):
    with open(input_path, "r") as f:
        lines = f.readlines()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_main = "General"
    current_sub = "Introduction"

    content_buffer = []
    sections = {} # main_topic -> {sub_topic: content_string}

    def sanitize(name):
        name = re.sub(r'<[^>]+>', '', name)
        name = name.replace('`', '')
        name = name.strip()
        name = re.sub(r'[^A-Za-z0-9\s\-]+', '', name)
        return name.strip()

    def save_current_section():
        if not content_buffer:
            return

        main_sanitized = sanitize(current_main)
        sub_sanitized = sanitize(current_sub)

        if main_sanitized not in sections:
            sections[main_sanitized] = {}

        if sub_sanitized not in sections[main_sanitized]:
             sections[main_sanitized][sub_sanitized] = []

        sections[main_sanitized][sub_sanitized].extend(content_buffer)
        content_buffer.clear()

    for line in lines:
        stripped = line.strip()

        mark_match = re.search(r'###### <mark>`\s*([A-Za-z\s]+)—([A-Za-z\s]+)<\/mark>', stripped, re.IGNORECASE)
        if mark_match:
            save_current_section()
            current_main = mark_match.group(1).strip().title()
            current_sub = mark_match.group(2).strip().title()

            content_buffer.append(f"# {current_main} - {current_sub}\n\n")
            continue

        chapter_match = re.match(r'^###### \*\*(.+)\*\*$', stripped)
        if chapter_match:
            title = chapter_match.group(1).strip()
            content_buffer.append(f"## {title}\n\n")
            continue

        if stripped.startswith("###### "):
             line = line.replace("###### ", "### ", 1)
        elif stripped.startswith("##### "):
             line = line.replace("##### ", "## ", 1)
        elif stripped.startswith("#### "):
             line = line.replace("#### ", "## ", 1)

        content_buffer.append(line)

    save_current_section()

    # Extract topics and subtopics for cross-linking
    topics = []
    for main, subs in sections.items():
        topics.append(main)
        for sub in subs.keys():
            topics.append(sub)

    # Sort topics by length descending to match longest first
    topics = sorted(list(set(topics)), key=len, reverse=True)

    def cross_link(text, current_sub):
        for topic in topics:
            if topic.lower() == current_sub.lower():
                continue

            # Replace occurrences of topic (case-insensitive) with [[topic]]
            # We use a negative lookbehind/lookahead to avoid replacing inside existing links or partial words
            pattern = re.compile(r'(?<!\[\[)\b(' + re.escape(topic) + r')\b(?!\]\])', re.IGNORECASE)

            # Simple approach: only link the first occurrence per file to avoid clutter
            def repl(match):
                return f"[[{topic}|{match.group(1)}]]"

            text = pattern.sub(repl, text, count=5)

        return text

    # Write to files
    for main, subs in sections.items():
        main_dir = os.path.join(output_dir, main)
        if not os.path.exists(main_dir):
            os.makedirs(main_dir)

        for sub, content_list in subs.items():
            content = "".join(content_list)
            content = cross_link(content, sub)

            filepath = os.path.join(main_dir, f"{sub}.md")
            with open(filepath, "w") as f:
                f.write(content)

    # Create master index
    with open(os.path.join(output_dir, "Master_Index.md"), "w") as f:
        f.write("# Master Index\n\n")
        for main in sorted(sections.keys()):
            f.write(f"## [[{main}]]\n")
            for sub in sorted(sections[main].keys()):
                # Link to the specific subtopic file
                f.write(f"- [[{sub}]]\n")

    print(f"Split {input_path} into chapters with cross-linking in {output_dir}")

import process_textbook
process_textbook.extract_content("First Aid for the USMLE Step 1 2025 35th Edition_compressed_unlocked_Master.md", "knowledge_base.md")
split_into_chapters("knowledge_base.md", "obsidian_vault")
os.remove("knowledge_base.md")
