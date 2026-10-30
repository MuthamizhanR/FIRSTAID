# FIRSTAID Knowledge Base

This project parses the raw USMLE Step 1 Markdown textbook and structures it into a format optimized for Obsidian, and provides a web application to view it.

## How to use

1. Run the `process_textbook.py` script to generate a single cleaned Markdown file, stripping all fluff, table of contents, footers, headers, and page numbers:
```
python process_textbook.py "First Aid for the USMLE Step 1 2025 35th Edition_compressed_unlocked_Master.md" knowledge_base.md
```

2. Run the `split_chapters.py` script to break the textbook into hierarchical, cross-linked Markdown files suitable for an Obsidian vault:
```
python split_chapters.py knowledge_base.md
```
This will create an `obsidian_vault` directory with folders for every major topic (e.g. `Biochemistry`, `Immunology`, `Cardiovascular`) containing their sub-topics, along with a `Master_Index.md` file. It automatically scans topics and applies cross-linking logic for standard Obsidian [[Link]] compatibility.

Note: The `obsidian_vault` is added to `.gitignore` so it is generated locally and not tracked.

3. Start the Flask application to view the knowledge base in a modern web UI:
```
pip install flask markdown werkzeug
python app.py
```
Then navigate to `http://localhost:5000` to view the knowledge base.
