import os
import re
from flask import Flask, render_template, request, abort
import markdown

app = Flask(__name__)
VAULT_DIR = "obsidian_vault"

def get_vault_structure():
    structure = {}
    if not os.path.exists(VAULT_DIR):
        return structure

    for item in os.listdir(VAULT_DIR):
        item_path = os.path.join(VAULT_DIR, item)
        if os.path.isdir(item_path):
            files = [f[:-3] for f in os.listdir(item_path) if f.endswith('.md')]
            structure[item] = sorted(files)

    return dict(sorted(structure.items()))

def convert_obsidian_links(html_content, structure):
    file_map = {}
    for folder, files in structure.items():
        for file in files:
            file_map[file.lower()] = folder

    def replace_link(match):
        inner = match.group(1)
        parts = inner.split('|')
        page_name = parts[0].strip()
        display_text = parts[1].strip() if len(parts) > 1 else page_name

        target_folder = file_map.get(page_name.lower())
        if target_folder:
            url = f"/topic/{target_folder}/{page_name}"
            return f'<a href="{url}" class="internal-link">{display_text}</a>'
        return f'<span class="broken-link">{display_text}</span>'

    pattern = re.compile(r'\[\[([^\]]+)\]\]')
    return pattern.sub(replace_link, html_content)

@app.route('/')
def index():
    structure = get_vault_structure()
    return render_template('index.html', structure=structure, current_folder=None, current_file=None, content=None)

@app.route('/topic/<folder>/<file>')
def view_topic(folder, file):
    structure = get_vault_structure()

    # Securely join paths
    folder = os.path.normpath(folder)
    file = os.path.normpath(file)
    if '..' in folder or '..' in file or folder.startswith('/') or file.startswith('/'):
        abort(400)

    filepath = os.path.join(VAULT_DIR, folder, f"{file}.md")

    if not os.path.exists(filepath):
        return "File not found", 404

    with open(filepath, "r") as f:
        md_content = f.read()

    # Render markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Process Obsidian links
    html_content = convert_obsidian_links(html_content, structure)

    return render_template('index.html', structure=structure, current_folder=folder, current_file=file, content=html_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
